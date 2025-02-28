#!/bin/sh
python manage.py migrate --noinput

RUN python manage.py collectstatic --noinput

RUN cp -r /app/collected_static/. /backend_static/static/

exec gunicorn --bind 0.0.0.0:80 backend.wsgi:application