#!/bin/bash

# set env for cron
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

# start cron
/etc/init.d/cron start

# Start Gunicorn
exec gunicorn --bind :3000 --workers 4 --chdir /usr/src/app/infoscience_exports wsgi:application
