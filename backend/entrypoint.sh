#!/bin/sh
python3 manage.py migrate --noinput

python3 manage.py collectstatic --noinput

cp -r /app/collected_static/. /backend_static/static/

exec gunicorn --bind 0.0.0.0:80 backend.wsgi:application