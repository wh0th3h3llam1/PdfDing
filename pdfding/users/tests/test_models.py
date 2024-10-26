from django.contrib.auth.models import User
from django.test import TestCase


class TestProfile(TestCase):
    # override_settings is not working with this test as the models default value is not overwritten
    # therefore do not change the theme defined in dev.py
    def test_default_theme(self):
        user = User.objects.create_user(username='user', password='12345', email='a@a.com')

        self.assertEqual(user.profile.dark_mode, 'Dark')
        self.assertEqual(user.profile.theme_color, 'Red')

    def test_dark_mode_str(self):
        user = User.objects.create_user(username='user', password='12345', email='a@a.com')
        user.profile.dark_mode = 'Dark'
        user.profile.save()

        self.assertEqual(user.profile.dark_mode_str, 'dark')
