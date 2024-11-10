from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from users.models import Profile


class TestSignals(TestCase):
    @override_settings(DEFAULT_THEME='dark', DEFAULT_THEME_COLOR='Gray')
    def test_user_postsave(self):
        input_mail = 'a@a.com'

        user = User.objects.create_user(username='user', password='12345', email=input_mail)

        # check that the profile exists
        profile = Profile.objects.get(user=user)
        self.assertEqual(str(profile), input_mail)
        self.assertEqual(profile.dark_mode, 'Dark')
        self.assertEqual(profile.theme_color, 'Gray')

        # check that email address object does not exist yet:
        email_address = EmailAddress.objects.get_primary(user)

        with self.assertRaises(AttributeError):
            email_address.email

        # check that email address object is created when saving:
        user.save()
        email_address = EmailAddress.objects.get_primary(user)

        self.assertEqual(email_address.email, input_mail)
        self.assertFalse(email_address.verified)

        # check that the email was changed
        change_mail = 'a@b.com'
        user.email = change_mail
        user.save()
        email_address = EmailAddress.objects.get_primary(user)

        self.assertEqual(email_address.email, change_mail)
        self.assertFalse(email_address.verified)
