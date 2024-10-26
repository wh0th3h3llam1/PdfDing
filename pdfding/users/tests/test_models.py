from django.contrib.auth.models import User
from django.test import TestCase


class TestProfile(TestCase):
    def test_dark_mode_str(self):
        user = User.objects.create_user(username='user', password='12345', email='a@a.com')
        user.profile.dark_mode = 'Dark'
        user.profile.save()

        self.assertEqual(user.profile.dark_mode_str, 'dark')
