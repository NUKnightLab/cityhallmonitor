"""
Staging Django settings for cityhallmonitor project.

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
    os.path.normpath(os.path.join(PROJECT_ROOT, '../secrets/cityhallmonitor/prd'))
)
from secrets import *


# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = False

ALLOWED_HOSTS = ['cityhallmonitor.knightlab.com']


# Application definition
# extend base.py settings

WSGI_APPLICATION = 'conf.prd.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cityhallmonitor_prd',
        'USER': 'cityhallmonitor',
        'PASSWORD': 'cityhallmonitor',
        'HOST': 'rds-pgis.knilab.com',
        'PORT': '5432'
    }
}


# Static files (CSS, JavaScript, Images)

STATIC_URL = '//media.knightlab.com/cityhallmonitor/'

# Domain for links sent in emails from management commands

DOMAIN_URL = 'http://cityhallmonitor.knightlab.com'

# Logging overrides

LOGGING['handlers'].update({
    'pull_data': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/pull_data.log'
    },
    'pull_sponsors': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/pull_sponsors.log'
    },
    'pull_attachments': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/pull_attachments.log'
    },
    'pull_pdfs': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/pull_pdfs.log'
    },
    'get_descriptions': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/get_descriptions.log'
    },
    'process_alerts': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/process_alerts.log'
    },
    'update_dc_data': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/update_dc_data.log'
    },
    'audit_db': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/audit_db.log'
    },
    'audit_dc': {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'formatter': 'verbose',
        'filename': '/home/apps/log/cityhallmonitor/audit_dc.log'
    }
})

LOGGING['loggers'].update({
    'cityhallmonitor.management.commands.pull_data': {
        'handlers': ['pull_data'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.pull_sponsors': {
        'handlers': ['pull_sponsors'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.pull_attachments': {
        'handlers': ['pull_attachments'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.pull_pdfs': {
        'handlers': ['pull_pdfs'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.get_descriptions': {
        'handlers': ['get_descriptions'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.process_alerts': {
        'handlers': ['process_alerts'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.update_dc_data': {
        'handlers': ['update_dc_data'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.audit_db': {
        'handlers': ['audit_db'],
        'level': 'DEBUG'
    },
    'cityhallmonitor.management.commands.audit_dc': {
        'handlers': ['audit_dc'],
        'level': 'DEBUG'
    }    
})
