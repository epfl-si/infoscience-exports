#!/usr/bin/env bash
python /usr/src/app/infoscience_exports/manage.py createcachetable
exec gunicorn -w 3 -b 0.0.0.0:3000 --threads 5 --max-requests 500 --max-requests-jitter 30 --chdir /usr/src/app/infoscience_exports wsgi:application
