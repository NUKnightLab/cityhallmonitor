"""
common.py are settings that don't tend to change from project to project and
will generally remain stable throughout development.

Import this file in your project-specific settings and override things as
necessary. If you need to make a change to this file, consider whether the
change applies to all of our Django projects.

Django settings docs:
https://docs.djangoproject.com/en/1.8/topics/settings/
https://docs.djangoproject.com/en/1.8/ref/settings/

*** DEVELOPER NOTES ***

This project uses a modified manage.py for handling debug toggling

For DEBUG mode, pass --debug to manage.py, or set DJANGO_DEBUG=True in your
environment variables instead of setting DEBUG=True in this file.
"""
from os.path import abspath, dirname, join
from os import environ as env

PROJECT_NAME = env['PROJECT_NAME']
ADMINS = (
    ('Knight Lab', 'knightlab@northwestern.edu'),
)
MANAGERS = ADMINS
CORE_ROOT = dirname(dirname(abspath(__file__)))
PROJECT_ROOT = dirname(CORE_ROOT)

# SECURITY WARNING: don't run with debug turned on in production!
# Avoid changing DEBUG here. Instead use the --debug manage.py flag, or
# set the environment variable DJANGO_DEBUG=True
DEBUG = True if env.get('DJANGO_DEBUG', '').lower() == 'true' else False

SECRET_KEY = env['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = env['APPLICATION_DOMAINS'].split()
WSGI_APPLICATION = 'core.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# static

# Static hosted in S3, thus STATIC_ROOT only used for collectstatic
STATIC_ROOT = env['STATIC_TMPDIR']
STATICFILES_DIRS = (
    join(PROJECT_ROOT, 'static'),
)
STATIC_URL = env['STATIC_URL']

FIXTURE_DIRS = (
    join(PROJECT_ROOT, 'fixtures'),
)

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            '()': '%s.formatter.UtcFormatter' % PROJECT_NAME,
            'format': '%(asctime)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO'
        }
    }
}
