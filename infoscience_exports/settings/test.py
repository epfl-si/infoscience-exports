from .base import *  # noqa

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

# Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'infoscience_exports',
        'USER': 'django',
        # docker container 'postgres' not used in test
        'HOST': 'localhost',
        'PORT': '',
    },
    'mock': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mock_infoscience_exports',
        'USER': 'django',
        # docker container 'postgres' not used in test
        'HOST': 'localhost',
        'PORT': '',
        'ATOMIC_REQUESTS': 'True',
    }
}

# Testing
INSTALLED_APPS += ('django_nose',)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    BASE_DIR,
    '--nologcapture',
    '--with-coverage',
    '--with-progressive',
    '--cover-package={}'.format(BASE_DIR)
]
