import os
from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

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
