from .base import *

try:
    from .dev_secrets import *
except ModuleNotFoundError:  # pragma: no cover
    pass

# Turn on debug mode
DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'some_key'

ACCOUNT_EMAIL_VERIFICATION = "optional"

DEFAULT_FROM_EMAIL = 'info@localhost'
