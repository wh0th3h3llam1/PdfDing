from .base import *  # noqa: F401 F403

try:
    from .dev_secrets import *  # noqa: F401 F403
except ModuleNotFoundError:  # pragma: no cover
    pass

# Turn on debug mode
DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'some_key'

ACCOUNT_EMAIL_VERIFICATION = "optional"

DEFAULT_FROM_EMAIL = 'info@localhost'
