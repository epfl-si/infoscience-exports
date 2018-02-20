from .base import *  # noqa

SITE_URL = 'https://epfl-export.tind.io'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
# https://devcenter.heroku.com/articles/getting-started-with-django
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECRET_KEY = get_env_variable('SECRET_KEY')

# Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'infoscience_exports',
        'USER': 'django',
        'PASSWORD': get_env_variable('DATABASE_PASSWORD_PROD'),
        'HOST': 'postgres',
        'PORT': '',
    },
    'mock': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mock_infoscience_exports',
        'USER': 'django',
        'PASSWORD': get_env_variable('DATABASE_PASSWORD_PROD'),
        'HOST': 'postgres',
        'PORT': '',
        'ATOMIC_REQUESTS': 'True',
    }
}

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

# Site
# https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# Template
# https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

LOGGING['handlers'].update({
    'graylog': {
        "level": 'DEBUG',
        "class": 'graypy.GELFHandler',
        "host": '127.0.0.1',
        "port": 12201,
    },
    'file': {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': '/var/log/django/infoscience_exports.log',
        'maxBytes': 1024*1024*5,  # 5 MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
})

LOGGING['loggers'] = {
    'django.request': {
        'handlers': ['mail_admins'],
        'level': 'ERROR',
        'propagate': True
    },
    'infoscience_exports': {
        'handlers': ['file', 'graylog'],
        'level': 'INFO',
        'propagate': True
    },
    'exports': {
        'handlers': ['file', 'graylog'],
        'level': 'INFO',
        'propagate': True
    }
}
