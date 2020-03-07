#!/bin/sh

python3 manage.py migrate
python3 manage.py collectstatic --no-input --clear

gunicorn hookah_crm.wsgi:application -b 0.0.0.0:8080 -w 2 --timeout=120 --graceful-timeout=120 --max-requests=1024