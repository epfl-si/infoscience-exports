import os
from os.path import join

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_env_variable(var_name):
    """Get the environment variable or return exception."""
    environ_var = os.environ.get(var_name)

    if not environ_var:
        error_msg = "Set the {} environment variable".format(var_name)
        raise ImproperlyConfigured(error_msg)

    return environ_var


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',            # utilities for rest apis
    'rest_framework.authtoken',  # token authentication
    'bootstrap4',
    'django_tequila',

    # Your apps
    'exports',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_tequila.middleware.TequilaMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Set DEBUG to False as a default for safety
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

SECRET_KEY = 'Not a secret'
WSGI_APPLICATION = 'wsgi.application'

# Allow for less strict handling of urls
APPEND_SLASH = True

# Migrations
MIGRATION_MODULES = {
    'sites': 'contrib.sites.migrations'
}

# Email
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MANAGERS = (
    ("Author", 'mister_x@epfl.ch'),
)

# General
TIME_ZONE = 'Europe/Zurich'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_L10N = True
USE_TZ = True
LOGIN_REDIRECT_URL = '/'

# Static Files
STATIC_ROOT = join(os.path.dirname(BASE_DIR), 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Media files
MEDIA_ROOT = join(os.path.dirname(BASE_DIR), 'media')
MEDIA_URL = '/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d' +
                      ' %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    }
}

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# Django Tequila
AUTHENTICATION_BACKENDS = ('django_tequila.django_backend.TequilaBackend',)
TEQUILA_SERVICE_NAME = "Infoscience exports"

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGIN_REDIRECT_IF_NOT_ALLOWED = "/not_allowed"
LOGOUT_URL = '/logged-out'

AUTH_USER_MODEL = 'exports.User'