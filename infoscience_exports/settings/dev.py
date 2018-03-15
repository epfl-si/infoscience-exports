# flake8: noqa
from .test import *

DEBUG = True

TEQUILA_SERVER_URL = "https://test-tequila.epfl.ch"

ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS').split(',') \
    + [ "127.0.0.1",
        "localhost",
        "idevelopsrv25.epfl.ch",
        "test-infoscience.epfl.ch",
        "infoscience.epfl.ch",
    ]

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

INSTALLED_APPS += ('debug_toolbar',
                   'django_extensions',
                   )
MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

LOGGING['loggers'] = {
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
    return True

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}
