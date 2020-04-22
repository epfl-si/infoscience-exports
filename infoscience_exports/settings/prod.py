# flake8: noqa
from .base import *

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
# https://devcenter.heroku.com/articles/getting-started-with-django
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECRET_KEY = get_env_variable('SECRET_KEY')

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True

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
