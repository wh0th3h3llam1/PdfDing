from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class TestLoginRequired(TestCase):
    def test_admin_required(self):
        response = self.client.get(reverse('admin_overview'))

        self.assertEqual(response.status_code, 404)


class TestAdminViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password', email='a@a.com')
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.client = Client()

        self.client.login(username='admin', password='password')

    def test_overview(self):
        for i in range(1, 4):
            User.objects.create_user(username=f'user_{i}', password='12345', email=f'{i}_b@a.com')

        # get the users that have the email {i}_b@a.com
        # also sort them oldest to newest
        response = self.client.get(f'{reverse('admin_overview')}?q=_b@a.com&sort=oldest')
        user_names = [user.email for user in response.context['page_obj']]

        self.assertEqual(user_names, ['1_b@a.com', '2_b@a.com', '3_b@a.com'])
        self.assertEqual(response.context['raw_search_query'], '_b@a.com')
        self.assertEqual(response.context['sorting_query'], 'oldest')
        self.assertEqual(response.context['number_of_users'], 4)
        self.assertEqual(response.context['number_of_pdfs'], 0)

        # test admin search also add some spaces
        response = self.client.get(f'{reverse('admin_overview')}?q=@a++++%23admins')
        user_names = [user.email for user in response.context['page_obj']]

        self.assertEqual(user_names, ['a@a.com'])
        self.assertEqual(response.context['raw_search_query'], '@a    #admins')
        self.assertEqual(response.context['sorting_query'], '')

    def test_remove_admin_rights(self):
        headers = {'HTTP_HX-Request': 'true'}
        self.client.post(reverse('admin_adjust_rights', kwargs={'user_id': self.user.id}), **headers)

        user = User.objects.get(id=self.user.id)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_add_admin_rights(self):
        user = User.objects.create_user(username='non_admin', password='12345', email='non_admin@a.com')

        headers = {'HTTP_HX-Request': 'true'}
        self.client.post(reverse('admin_adjust_rights', kwargs={'user_id': user.id}), **headers)

        user = User.objects.get(id=user.id)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_adjust_admin_rights_no_htmx(self):
        response = self.client.post(reverse('admin_adjust_rights', kwargs={'user_id': self.user.id}))
        self.assertRedirects(response, reverse('admin_overview'), status_code=302)

    def test_delete_htmx(self):
        headers = {'HTTP_HX-Request': 'true'}
        User.objects.get(id=self.user.id)
        self.client.delete(reverse('admin_delete_profile', kwargs={'user_id': self.user.id}), **headers)

        with self.assertRaisesRegex(User.DoesNotExist, 'User matching query does not exist.'):
            User.objects.get(id=self.user.id)

    def test_delete_no_htmx(self):
        response = self.client.delete(reverse('admin_delete_profile', kwargs={'user_id': self.user.id}))
        self.assertRedirects(response, reverse('admin_overview'), status_code=302)
