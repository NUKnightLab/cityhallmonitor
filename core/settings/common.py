from os.path import abspath, dirname, join
from os import environ as env
import sys
"""
Django settings docs:
https://docs.djangoproject.com/en/1.8/topics/settings/
https://docs.djangoproject.com/en/1.8/ref/settings/

*** DEVELOPER NOTES ***

For DEBUG mode, pass --debug to manage.py, or set DJANGO_DEBUG=True in your
environment variables instead of setting DEBUG=True in this file.

This project uses a modified manage.py that will load secrets from a file
called vault.dev.yml in the project-specific secrets directory. If you need
secrets for development, they will not be provided by version control. You
should copy the vault.dev.yml.example file and fill in the values to be
loaded by manage.py.
"""

PROJECT_NAME = 'cityhallmonitor'


ADMINS = (
    ('Knight Lab', 'knightlab@northwestern.edu'),
)

MANAGERS = ADMINS

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cityhallmonitor',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

CORE_ROOT = dirname(dirname(abspath(__file__)))
PROJECT_ROOT = dirname(CORE_ROOT)

# DocumentCloud credentials kept in secrets. Developers, see note at top of this file.
DOCUMENT_CLOUD_USERNAME = env.get('DOCUMENT_CLOUD_USERNAME')
DOCUMENT_CLOUD_PASSWORD = env.get('DOCUMENT_CLOUD_PASSWORD')
DOCUMENT_CLOUD_ACCOUNT = env.get('DOCUMENT_CLOUD_ACCOUNT')
DOCUMENT_CLOUD_PROJECT = env.get('DOCUMENT_CLOUD_PROJECT')

# SECURITY WARNING: don't run with debug turned on in production!
# Avoid changing DEBUG here. Instead use the --debug manage.py flag, or
# set the environment variable DJANGO_DEBUG=True
DEBUG = True if env.get('DJANGO_DEBUG', '').lower() == 'true' else False

SECRET_KEY = env.get('SECRET_KEY', 'development')

ALLOWED_HOSTS = env.get('ALLOWED_HOSTS', 'localhost|127.0.0.1').split('|')
WSGI_APPLICATION = 'deploy.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# static

# Static hosted in S3, thus STATIC_ROOT only used for collectstatic
STATIC_ROOT = join(env.get('TMPDIR', '/tmp'), '%s_static' % PROJECT_NAME)
STATICFILES_DIRS = (
    join(PROJECT_ROOT, 'static'),
)
STATIC_URL = env.get('STATIC_URL', '/static/')

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


# email: used for sending subscription-related emails

EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'knightlab.cityhallmonitor@gmail.com'
# Email credentials kept in secrets. Developers, see note at top of this file.
EMAIL_HOST_USER = env.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.get('EMAIL_HOST_PASSWORD')
# Domain for links sent in emails from management commands
DOMAIN_URL = 'https://cityhallmonitor.knightlab.com'

# databases

# for using sqlite3 in dev, the getter defaults should be changed accordingly
DATABASES = {
    'default': {
        'ENGINE': env.get(
            'DEFAULT_DB_ENGINE',
            'django.db.backends.postgresql_psycopg2' # postgres
            # 'django.db.backends.sqlite3' # sqlite3
        ),
        'NAME': env.get(
            'DEFAULT_DB_NAME',
            PROJECT_NAME # postgres
            # join(BASE_DIR, 'db.sqlite3') # sqlite3
        ),
        'USER': env.get('DEFAULT_DB_USER', PROJECT_NAME),
        'PASSWORD': env.get('DEFAULT_DB_PASSWORD', PROJECT_NAME),
        'HOST': env.get('DEFAULT_DB_HOST', '127.0.0.1'),
        'PORT': env.get(
            'DEFAULT_DB_PORT',
            '5432' # postgres
            # '' # sqlite3
        )
    }
}

# logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            '()': 'cityhallmonitor.formatter.UtcFormatter',
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
        # Configure handlers for management commands per-environment
        # pull_data
        # pull_attachments
        # pull_pdfs
        # get_descriptions
        # process_alerts
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO'
        }
        # Configure loggers for management commands per-environ:
        # cityhallmonitor.management.commands.pull_data
        # cityhallmonitor.management.commands.pull_attachments
        # cityhallmonitor.management.commands.pull_pdfs
        # cityhallmonitor.management.commands.get_descriptions
        # cityhallmonitor.management.commands.process_alerts
    }
}
