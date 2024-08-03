from .base import *  # noqa: F401 F403

try:
    # set the minio acces and secret key and the SOCIALACCOUNT_PROVIDERS in dev_secrets
    from .dev_secrets import *  # noqa: F401 F403
except ModuleNotFoundError:  # pragma: no cover
    pass

# Turn on debug mode
DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'some_key'  # nosec B105

ACCOUNT_EMAIL_VERIFICATION = "optional"

DEFAULT_FROM_EMAIL = 'info@localhost'

BACKUP_ENABLE = False
BACKUP_SECURE = False
BACKUP_ENDPOINT = '127.0.0.1:9000'
BACKUP_BUCKET_NAME = 'pdfding'
BACKUP_SCHEDULE = '*/1 * * * *'

# check if minio access and secret keys are set in dev_secrets
if 'BACKUP_ACCESS_KEY' not in locals():
    BACKUP_ACCESS_KEY = 'add_access_key'
if 'BACKUP_SECRET_KEY' not in locals():
    BACKUP_SECRET_KEY = 'add_access_key'  # nosec
