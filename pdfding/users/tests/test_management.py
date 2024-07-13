from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase


class TestManagement(TestCase):
    def test_make_admin(self):
        User.objects.create_user(username='user', password='12345', email='a@a.com')
        call_command('make_admin', email='a@a.com')
        user = User.objects.get(email='a@a.com')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
