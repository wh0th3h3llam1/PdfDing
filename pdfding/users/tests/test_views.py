from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import ThemeForm, EmailForm


class TestLoginRequired(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse('profile-settings'))

        self.assertRedirects(response, f'/accountlogin/?next={reverse('profile-settings')}', status_code=302)


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

    def test_change_email_get_no_htmx(self):
        response = self.client.get(reverse('profile-emailchange'))

        # target_status_code=302 because the '/' will redirect to the pdf overview
        self.assertRedirects(response, '/', status_code=302, target_status_code=302)

    def test_change_email_get_htmx(self):
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.get(reverse('profile-emailchange'), **headers)

        self.assertIsInstance(response.context['form'], EmailForm)

    def test_change_email_post_invalid_form(self):
        # follow=True is needed for getting the message
        response = self.client.post(reverse('profile-emailchange'), follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(message.message, 'Form not valid')
        self.assertEqual(message.tags, 'warning')

    def test_change_email_post_email_exists(self):
        User.objects.create_user(username='other_user', password=self.password, email='a@b.com')
        # follow=True is needed for getting the message
        response = self.client.post(reverse('profile-emailchange'), data={"email": 'a@b.com'}, follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(message.message, 'a@b.com is already in use.')
        self.assertEqual(message.tags, 'warning')

    @patch('users.views.send_email_confirmation')
    def test_change_email_post_correct(self, mock_send):
        self.client.post(reverse('profile-emailchange'), data={'email': 'a@c.com'})

        # get the user and check if email was changed
        user = User.objects.get(username=self.username)
        mock_send.assert_called()
        self.assertEqual(user.email, 'a@c.com')

    def test_change_dark_mode_get_no_htmx(self):
        response = self.client.get(reverse('profile-theme-change'))

        # target_status_code=302 because the '/' will redirect to the pdf overview
        self.assertRedirects(response, '/', status_code=302, target_status_code=302)

    def test_change_dark_mode_get_htmx(self):
        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.get(reverse('profile-theme-change'), **headers)

        self.assertIsInstance(response.context['form'], ThemeForm)

    def test_change_dark_mode_post_invalid_form(self):
        # follow=True is needed for getting the message
        response = self.client.post(reverse('profile-theme-change'), data={'dark_mode': 'Blue'}, follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(message.message, 'Form not valid')
        self.assertEqual(message.tags, 'warning')

    def test_change_dark_mode_post_correct(self):
        self.assertEqual(self.user.profile.dark_mode, 'Light')
        self.assertEqual(self.user.profile.theme_color, 'Green')
        self.client.post(reverse('profile-theme-change'), data={'dark_mode': 'Dark', 'theme_color': 'Blue'})

        # get the user and check if dark mode was changed
        user = User.objects.get(username=self.username)
        self.assertEqual(user.profile.dark_mode, 'Dark')
        self.assertEqual(user.profile.theme_color, 'Blue')

    def test_delete_post(self):
        # follow=True is needed for getting the message
        response = self.client.post(reverse('profile-delete'), follow=True)
        message = list(response.context['messages'])[0]

        self.assertFalse(User.objects.filter(username=self.username).exists())
        self.assertEqual(message.message, 'Your Account was successfully deleted.')
        self.assertEqual(message.tags, 'success')
