from .common import *
from os import environ as env

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

# databases

DATABASES = {
    'default': {
        'ENGINE': env['DB_ENGINE__DEFAULT'],
        'NAME': env['DB_NAME__DEFAULT'],
        'USER': env['DB_USER__DEFAULT'],
        'PASSWORD': env['DB_PASSWORD__DEFAULT'],
        'HOST': env['DB_HOST__DEFAULT'],
        'PORT': env['DB_PORT__DEFAULT']
    }
}

# DocumentCloud

DOCUMENT_CLOUD_USERNAME = env['DOCUMENT_CLOUD_USERNAME']
DOCUMENT_CLOUD_PASSWORD = env['DOCUMENT_CLOUD_PASSWORD']
DOCUMENT_CLOUD_ACCOUNT = env['DOCUMENT_CLOUD_ACCOUNT']
DOCUMENT_CLOUD_PROJECT = env['DOCUMENT_CLOUD_PROJECT']

# email: used for sending subscription-related emails

EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'knightlab.cityhallmonitor@gmail.com'
EMAIL_HOST_USER = env['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']
# Domain for links sent in emails from management commands
DOMAIN_URL = 'https://cityhallmonitor.knightlab.com'
