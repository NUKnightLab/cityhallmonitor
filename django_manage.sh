#!/bin/sh
# setup the environment and call manage.py
. ~/env/cityhallmonitor/bin/activate
. ./env.sh
./manage.py $@
