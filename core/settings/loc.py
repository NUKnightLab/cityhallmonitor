"""
Local Django settings for cityhallmonitor project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import os
import sys
from .base import *

# Import secrets

sys.path.append(
    os.path.normpath(os.path.join(PROJECT_ROOT, '../secrets/cityhallmonitor/loc'))
)
from secrets import *


# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

ALLOWED_HOSTS = []


# Application definition
# extend base.py settings

WSGI_APPLICATION = 'conf.loc.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cityhallmonitor',
        'USER': 'cityhallmonitor',
        'PASSWORD': 'default',
        'HOST': '127.0.0.1',
        'PORT': ''
    }
}


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

# Domain for links sent in emails from management commands

DOMAIN_URL = 'http://127.0.0.1:8000'

# Logging overrides

LOGGING['loggers'].update({
    'cityhallmonitor.management.commands.pull_data': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.pull_sponsors': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.pull_attachments': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.pull_pdfs': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.get_descriptions': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.update_dc_data': {
        'handlers': ['console'],
        'level': 'DEBUG'
    }

})
    
    

