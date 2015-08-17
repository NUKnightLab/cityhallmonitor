"""
Common Django settings for cityhallmonitor project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
from os.path import abspath, dirname, join


CORE_ROOT = dirname(dirname(abspath(__file__)))

PROJECT_ROOT = dirname(CORE_ROOT)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Application definition

STATIC_ROOT = '/tmp/cityhallmonitor-static'

STATICFILES_DIRS = (
    join(PROJECT_ROOT, 'static'),
)

FIXTURE_DIRS = (
    join(PROJECT_ROOT, 'fixtures'),
)

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


EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'

EMAIL_PORT = 25

EMAIL_USE_TLS = True

# Email address used for sending subscription-related emails
DEFAULT_FROM_EMAIL = 'KnightLab@northwestern.edu'
