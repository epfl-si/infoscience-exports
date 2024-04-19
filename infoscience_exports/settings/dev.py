# flake8: noqa
from .test import *

DEBUG = True

# Django Tequila
TEQUILA_SERVER_URL = "https://tequila.epfl.ch"
TEQUILA_STRONG_AUTHENTICATION = True
# reset backend from test to dev
AUTHENTICATION_BACKENDS = ('django_tequila.django_backend.TequilaBackend',)


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

LOGGING['handlers'].update({
    'file': {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/django/infoscience_exports.log',
        'maxBytes': 1024*1024*5,  # 5 MB
        'backupCount': 5,
        'formatter': 'verbose',
    },
    'migration_file': {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/django/infoscience_exports_migration.log',
        'maxBytes': 1024*1024*5,  # 5 MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
})

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
    },
    'migration': {
        'handlers': ['migration_file', 'console'],
        'level': 'DEBUG',
        'propagate': True
    },
    'migration.skipped': {
        'handlers': [],
        'level': 'INFO',
        'propagate': False
    },
    'migration.search': {
        'handlers': [],
        'level': 'INFO',
        'propagate': False
    },
    'django_tequila': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True
    }
}


def show_toolbar(request):
    patterns = [
        "/preview/",  # ignore preview as it create an infinite loop
    ]
    return not any(p in request.path for p in patterns)


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}
