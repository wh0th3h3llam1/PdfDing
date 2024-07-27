import os

from .base import *  # noqa: F401 F403

# security related settings
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# web security settings
ALLOWED_HOSTS = [os.environ.get('HOST_NAME')]

if os.environ.get('HOST_NAME'):
    host_name = os.environ.get('HOST_NAME')
    CSRF_TRUSTED_ORIGINS = [f'https://{host_name}', f'http://{host_name}']

SECRET_KEY = os.environ.get('SECRET_KEY')

if os.environ.get('CSRF_COOKIE_SECURE', 'TRUE') == 'TRUE':
    CSRF_COOKIE_SECURE = True
if os.environ.get('SESSION_COOKIE_SECURE', 'TRUE') == 'TRUE':
    SESSION_COOKIE_SECURE = True
if os.environ.get('SECURE_SSL_REDIRECT') == 'TRUE':
    SECURE_SSL_REDIRECT = True
if os.environ.get('SECURE_HSTS_SECONDS'):
    SECURE_HSTS_SECONDS = os.environ.get('SECURE_HSTS_SECONDS')

# mail settings
if os.environ.get('EMAIL_BACKEND') == 'SMTP':
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get('SMTP_HOST')
    EMAIL_PORT = os.environ.get('SMTP_PORT', 587)
    EMAIL_HOST_USER = os.environ.get('SMTP_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD')
    if os.environ.get('SMTP_USE_TLS') == 'TRUE':
        EMAIL_USE_TLS = True
    if os.environ.get('SMTP_USE_SSL') == 'TRUE':
        EMAIL_USE_SSL = True

DEFAULT_FROM_EMAIL = f'info@{ALLOWED_HOSTS[0]}'

# authentication settings
ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.environ.get('ACCOUNT_DEFAULT_HTTP_PROTOCOL', 'https')
if os.environ.get('ACCOUNT_EMAIL_VERIFICATION') == 'TRUE':
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
else:
    ACCOUNT_EMAIL_VERIFICATION = 'optional'

# configure the oidc provider
if os.environ.get('OIDC_ENABLE') == 'TRUE':
    # enable social logins only
    if os.environ.get('OIDC_ONLY') == 'TRUE':
        SOCIALACCOUNT_ONLY = True
        ACCOUNT_EMAIL_VERIFICATION = 'none'
    SOCIALACCOUNT_PROVIDERS = {
        'openid_connect': {
            'EMAIL_AUTHENTICATION': True,
            # Optional PKCE defaults to False, but may be required by your provider
            # Applies to all APPS.
            'OAUTH_PKCE_ENABLED': True,
            'APPS': [
                {
                    'provider_id': 'oidc',
                    'name': os.environ.get('OIDC_PROVIDER_NAME', 'OIDC').upper(),
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
        'verbose': {'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'},
    },
    'handlers': {'console': {'level': 'NOTSET', 'class': 'logging.StreamHandler', 'formatter': 'verbose'}},
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'NOTSET',
        },
        'django.request': {'handlers': ['console'], 'propagate': False, 'level': 'ERROR'},
    },
}
