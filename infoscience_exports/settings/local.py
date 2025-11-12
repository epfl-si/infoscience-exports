# flake8: noqa
from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS').split(',') \
                + [ "127.0.0.1",
                    "localhost",
                    "infoscience.epfl.ch",
                    ]

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

INSTALLED_APPS += ('debug_toolbar',
                   'django_extensions',
                   )
MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

SECRET_KEY = get_env_variable('SECRET_KEY')

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "local/infoscience-exports.db",
    }
}

LOGGING['loggers'] = {
    'django.utils.autoreload': {
        'level': 'ERROR',
        'handlers': ['console'],
        'propagate': False,
    },
    'django.db': {
        'handlers': ['null'],
        'level': 'DEBUG',
        'propagate': False
    },
    'django.request': {
        'handlers': ['console'],
        'level': 'ERROR',
        'propagate': True
    },
    'django': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True
    },
    # added not to display traceback because is_popup not found
    # see https://stackoverflow.com/questions/34797884/getting-error-with-is-popup-variable-in-django-1-9
    'django.template': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    },
    'infoscience_exports': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True
    },
    'exports': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True
    }
}


def show_toolbar(request):
    patterns = [
        "/preview/",
        "/compare/",
    ]

    if any(p in request.path for p in patterns):
        return False
    elif request.path.startswith('/publication-exports/') and request.path.split('/')[-2].isdigit():
        return False
    return True

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

INTERNAL_IPS = [
    "127.0.0.1",
]
