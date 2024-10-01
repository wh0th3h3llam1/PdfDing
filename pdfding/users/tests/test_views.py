from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from pdf.models import Pdf, Tag
from users.forms import EmailForm, PdfsPerPageForm, ThemeForm
from users.models import Profile


class TestAuthRelated(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse('pdf_overview'))

        self.assertRedirects(response, f'/accountlogin/?next={reverse('pdf_overview')}', status_code=302)

    def test_login(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)

    def test_password_reset(self):
        response = self.client.get(reverse('password_reset'))

        self.assertEqual(response.status_code, 200)

    def test_password_reset_done(self):
        response = self.client.get(reverse('password_reset_done'))

        self.assertEqual(response.status_code, 200)

    def test_oidc_login(self):
        response = self.client.get(reverse('oidc_login'))

        self.assertEqual(response.status_code, 200)

    def test_oidc_callback(self):
        response = self.client.get(reverse('oidc_callback'))

        self.assertEqual(response.status_code, 200)


class TestProfileViews(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username=self.username, password=self.password, email='a@a.com')
        self.client.login(username=self.username, password=self.password)

    def test_settings(self):
        # test without social account
        response = self.client.get(reverse('profile-settings'))
        self.assertEqual(response.context['uses_social'], False)

        # test with social account
        social_account = SocialAccount.objects.create(user=self.user)
        self.user.socialaccount_set.set([social_account])

        response = self.client.get(reverse('profile-settings'))
        self.assertEqual(response.context['uses_social'], True)

    def test_change_settings_get_no_htmx(self):
        response = self.client.get(reverse('profile-setting-change', kwargs={'field_name': 'email'}))

        # target_status_code=302 because the '/' will redirect to the pdf overview
        self.assertRedirects(response, '/', status_code=302, target_status_code=302)

    def test_change_settings_email_get_htmx(self):
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.get(reverse('profile-setting-change', kwargs={'field_name': 'email'}), **headers)

        self.assertIsInstance(response.context['form'], EmailForm)
        self.assertEqual({'email': 'a@a.com'}, response.context['form'].initial)

    def test_change_settings_dark_mode_get_htmx(self):
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.get(reverse('profile-setting-change', kwargs={'field_name': 'theme'}), **headers)

        self.assertIsInstance(response.context['form'], ThemeForm)
        self.assertEqual({'dark_mode': 'Light', 'theme_color': 'Green'}, response.context['form'].initial)

    def test_change_settings_pdfs_per_page_get_htmx(self):
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.get(reverse('profile-setting-change', kwargs={'field_name': 'pdfs_per_page'}), **headers)

        self.assertIsInstance(response.context['form'], PdfsPerPageForm)
        self.assertEqual({'pdfs_per_page': 25}, response.context['form'].initial)

    def test_change_settings_post_invalid_form(self):
        # follow=True is needed for getting the message
        response = self.client.post(reverse('profile-setting-change', kwargs={'field_name': 'email'}), follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(message.message, 'Form not valid')
        self.assertEqual(message.tags, 'warning')

    def test_change_settings_email_post_email_exists(self):
        User.objects.create_user(username='other_user', password=self.password, email='a@b.com')
        # follow=True is needed for getting the message
        response = self.client.post(
            reverse('profile-setting-change', kwargs={'field_name': 'email'}), data={"email": 'a@b.com'}, follow=True
        )
        message = list(response.context['messages'])[0]

        self.assertEqual(message.message, 'a@b.com is already in use.')
        self.assertEqual(message.tags, 'warning')

    @patch('users.views.send_email_confirmation')
    def test_change_settings_email_post_correct(self, mock_send):
        self.client.post(reverse('profile-setting-change', kwargs={'field_name': 'email'}), data={'email': 'a@c.com'})

        # get the user and check if email was changed
        user = User.objects.get(username=self.username)
        mock_send.assert_called()
        self.assertEqual(user.email, 'a@c.com')

    def test_change_settings_dark_mode_post_correct(self):
        self.assertEqual(self.user.profile.dark_mode, 'Light')
        self.assertEqual(self.user.profile.theme_color, 'Green')
        self.client.post(
            reverse('profile-setting-change', kwargs={'field_name': 'theme'}),
            data={'dark_mode': 'Dark', 'theme_color': 'Blue'},
        )

        # get the user and check if dark mode was changed
        user = User.objects.get(username=self.username)
        self.assertEqual(user.profile.dark_mode, 'Dark')
        self.assertEqual(user.profile.theme_color, 'Blue')

    def test_change_settings_pdfs_per_page_post_correct(self):
        self.assertEqual(self.user.profile.dark_mode, 'Light')
        self.assertEqual(self.user.profile.theme_color, 'Green')
        self.client.post(
            reverse('profile-setting-change', kwargs={'field_name': 'pdfs_per_page'}), data={'pdfs_per_page': 10}
        )

        # get the user and check if dark mode was changed
        user = User.objects.get(username=self.username)
        self.assertEqual(user.profile.pdfs_per_page, 10)

    def test_delete_post(self):
        # in this test we test that the user is successfully deleted
        # we also test that the associated profile, pdfs, and tags are also deleted
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf_1')
        tags = [Tag.objects.create(name='tag', owner=pdf.owner)]
        pdf.tags.set(tags)

        for model_class in [Profile, Pdf, Tag]:
            # assert there is a profile, pdf and tag
            self.assertEqual(model_class.objects.all().count(), 1)

        # follow=True is needed for getting the message
        response = self.client.post(reverse('profile-delete'), follow=True)
        message = list(response.context['messages'])[0]

        self.assertFalse(User.objects.filter(username=self.username).exists())
        self.assertEqual(message.message, 'Your Account was successfully deleted.')
        self.assertEqual(message.tags, 'success')
        for model_class in [Profile, Pdf, Tag]:
            # assert there is no profile, pdf and tag
            self.assertEqual(model_class.objects.all().count(), 0)
