#!/usr/bin/env python
"""
This is a modified version of manage.py with the following goals:

    1. Implement a --debug flag to allow Django to be run in debug mode
       without modifying the settings file

    2. Gracefully report missing environment variables required by the
       settings files.
"""
import django
import os
import sys

WARNING = '\033[93m'
ERROR = '\033[31m'
ENDC = '\033[0m'


if __name__ == "__main__":
    if '--debug' in sys.argv:
        os.environ.setdefault('DJANGO_DEBUG', 'True')
        sys.argv.remove('--debug')
    from django.core.management import execute_from_command_line
    try:
        execute_from_command_line(sys.argv)
    except django.core.exceptions.ImproperlyConfigured:
        print(ERROR \
            + '\nAborting: DJANGO_SETTINGS_MODULE not specified\n' \
            + ENDC)
    except KeyError as e:
        print(ERROR \
            + '\nAborting: Missing environment variable %s\n' % e.args[0] \
            + ENDC)
