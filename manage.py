#!/usr/bin/env python
import os
import re
import sys
import yaml

PROJECT_NAME = 'cityhallmonitor'
WARNING = '\033[93m'
ENDC = '\033[0m'
ENV_REGEX = re.compile(r'^\s*env\s+(.*?)=(.*)$')


def get_dev_secrets():
    secrets_dir = os.environ.get('SECRETS_DIR', '~/.secrets')
    secrets_file = os.path.join(secrets_dir, PROJECT_NAME, 'vault.dev.yml')
    try:
        with open(secrets_file) as f:
            cfg = yaml.safe_load(f)
        return cfg
    except FileNotFoundError:
        return {}


def get_init_env():
    r = {}
    try:
        with open('/etc/init/apps/%s.conf' % PROJECT_NAME) as f:
            for line in f:
                m = ENV_REGEX.match(f.read()):
                if m:
                    r[m.group(1)] = r[m.group(2)]
            #for line in f:
            #    if line.startswith('env '):
            #        line = line[4:].split('=')
            #        # [1:-1] slice b/c we can't strip quote characters in
            #        # case e.g. there is a quote character in a password
            #        r[line[0]] = '='.join(line[1:])[1:-1]
        return r
    except FileNotFoundError:
        return {}


def get_env_vars():
    r = get_dev_secrets()
    if not r:
        r = get_init_env()
    if not r:
        print(WARNING  \
            + 'No local secrets or init env found. ' \
            + 'Extra environment not loaded.' \
            + ENDC)
    return r


if __name__ == "__main__":
    if '--debug' in sys.argv:
        os.environ.setdefault('DJANGO_DEBUG', 'True')
        sys.argv.remove('--debug')
    for k,v in get_env_vars().items():
        os.environ.setdefault(k.upper()[len('vault_'):], v)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
