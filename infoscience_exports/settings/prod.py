# flake8: noqa
from .base import *

SECRET_KEY = get_env_variable('SECRET_KEY')

SESSION_COOKIE_AGE = 24*60*60  # default is 2 weeks, it is really too much

MIDDLEWARE = ('whitenoise.middleware.WhiteNoiseMiddleware',) + MIDDLEWARE

# Things coming from k8s may need to be proxied from https to http
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Template
# https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

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
    'django.request': {
        'handlers': ['mail_admins', 'file'],
        'level': 'ERROR',
        'propagate': True
    },
    'infoscience_exports': {
        'handlers': ['file'],
        'level': 'INFO',
        'propagate': True
    },
    'exports': {
        'handlers': ['file'],
        'level': 'INFO',
        'propagate': True
    },
    'migration': {
        'handlers': ['migration_file'],
        'level': 'DEBUG',
        'propagate': True
    }
}
