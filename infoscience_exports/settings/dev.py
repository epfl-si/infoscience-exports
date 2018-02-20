from .test import *  # noqa

DEBUG = True

SITE_URL = 'https://127.0.0.1:8000'

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

INSTALLED_APPS += ('debug_toolbar',
                   'django_extensions',
                   )
MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'infoscience_exports',
        'USER': 'django',
        'PASSWORD': get_env_variable('DATABASE_PASSWORD_DEV'),
        'HOST': 'postgres',
        'PORT': '',
    },
    'mock': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mock_infoscience_exports',
        'USER': 'django',
        'PASSWORD': get_env_variable('DATABASE_PASSWORD_DEV'),
        'HOST': 'postgres',
        'PORT': '',
        'ATOMIC_REQUESTS': 'True',
    }
}

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
