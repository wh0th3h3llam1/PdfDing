from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.test import TestCase

from users.models import Profile


class TestSignals(TestCase):
    def test_user_postsave(self):
        input_mail = 'a@a.com'

        # this will not create an email address object
        user = User.objects.create_user(username='user', password='12345', email=input_mail)
        # so we need to create it
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)

        # check that the profile exists
        profile = Profile.objects.get(user=user)
        self.assertEqual(str(profile), input_mail)

        change_mail = 'a@b.com'
        user.email = change_mail
        user.save()
        email_address = EmailAddress.objects.get_primary(user)

        self.assertEqual(email_address.email, change_mail)
        self.assertFalse(email_address.verified)
