#!/usr/bin/env python
import os
import sys
import yaml

PROJECT_NAME = 'cityhallmonitor'
WARNING = '\033[93m'
ENDC = '\033[0m'


def get_secrets():
    secrets_dir = os.environ.get('SECRETS_DIR', '~/.secrets')
    secrets_file = os.path.join(secrets_dir, PROJECT_NAME, 'vault.dev.yml')
    try:
        with open(secrets_file) as f:
            cfg = yaml.safe_load(f)
        return cfg
    except FileNotFoundError:
        print(WARNING  \
            + 'vault.dev.yml file not found. ' \
            + 'Local development secrets not loaded.' \
            + ENDC)
        return {}


if __name__ == "__main__":
    if '--debug' in sys.argv:
        os.environ.setdefault('DJANGO_DEBUG', 'True')
        sys.argv.remove('--debug')
    for k,v in get_secrets().items():
        os.environ.setdefault(k.upper()[len('vault_'):], v)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
