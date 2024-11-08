from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class DisableSignupAccountAdapter(DefaultAccountAdapter):
    """Adapter for disabling user signup depending on the SIGNUP_CLOSED setting."""

    def is_open_for_signup(self, request):
        """Disable user signup depending on the SIGNUP_CLOSED setting."""

        return not settings.SIGNUP_CLOSED
