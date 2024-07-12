from .base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

for config in TEMPLATES:
    config['OPTIONS']['debug'] = DEBUG

ALLOWED_HOSTS = ["*"]

# Testing
# Nose has been desactivated because it's in maintenance mode
# and not really compatible with the new pythons
# An alternative is still to be find
# INSTALLED_APPS += ('django_nose',)
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# NOSE_ARGS = [
#     BASE_DIR,
#     '--nologcapture',
#     '--with-coverage',
#     '--cover-package={}'.format(BASE_DIR)
# ]

# for test verification at the moment
INFOSCIENCE_SITE_URL = 'https://infoscience.epfl.ch'

# as we don't have invenio in backend, send here for logged out confirmation
LOGOUT_URL = "{}/logged-out/".format(SITE_PATH)

# no auth for tests
AUTHENTICATION_BACKENDS = ('exports.test.auth_backends.TestcaseUserBackend', )

REMOTE_SELENIUM_SERVER = 'http://selenium:4444/wd/hub'
