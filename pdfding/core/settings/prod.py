import os

from .base import *

# security related settings
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = [os.environ.get('HOST_NAME', '')]

SECRET_KEY = os.environ.get('SECRET_KEY')

if os.environ.get('CSRF_COOKIE_SECURE', 'TRUE') == 'TRUE':
    CSRF_COOKIE_SECURE = True
if os.environ.get('SESSION_COOKIE_SECURE', 'TRUE') == 'TRUE':
    SESSION_COOKIE_SECURE = True

if os.environ.get('SECURE_SSL_REDIRECT', 'TRUE') == 'TRUE':
    SECURE_SSL_REDIRECT = True
if os.environ.get('SECURE_HSTS_SECONDS', 'TRUE') == 'TRUE':
    SECURE_HSTS_SECONDS = True

# mail settings
DEFAULT_FROM_EMAIL = f'info@{ALLOWED_HOSTS}'

# authentication settings

ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.environ.get('ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'https')
if os.environ.get('ACCOUNT_EMAIL_VERIFICATION') == 'TRUE':
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
else:
    ACCOUNT_EMAIL_VERIFICATION = 'optional'

# configure the oidc provider
if os.environ.get('OIDC_CLIENT_ID', None):
    # enable social logins only
    if os.environ.get('OIDC_ONLY', 'False') == 'TRUE':
        SOCIALACCOUNT_ONLY = True
    SOCIALACCOUNT_PROVIDERS = {
        'openid_connect': {
            'EMAIL_AUTHENTICATION': True,
            # Optional PKCE defaults to False, but may be required by your provider
            # Applies to all APPS.
            'OAUTH_PKCE_ENABLED': True,
            'APPS': [
                {
                    'provider_id': 'oidc',
                    'name': 'OIDC',
                    'client_id': os.environ['OIDC_CLIENT_ID'],
                    'secret': os.environ['OIDC_CLIENT_SECRET'],
                    'settings': {
                        'server_url': os.environ['OIDC_AUTH_URL'],
                        # Optional token endpoint authentication method.
                        # May be one of 'client_secret_basic', 'client_secret_post'
                        # If omitted, a method from the server's
                        # token auth methods list is used
                        # 'token_auth_method': 'client_secret_basic',
                    },
                }
            ],
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'NOTSET',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'NOTSET',
        },
        'django.request': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'ERROR'
        }
    }
}