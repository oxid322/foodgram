#!/bin/sh

sleep 5

# Применение миграций
python3 manage.py migrate --noinput

# Сбор статических файлов
python3 manage.py collectstatic --noinput

# Копирование статических файлов
cp -r /app/collected_static/. /backend_static/static/

# Запуск Gunicorn
exec gunicorn --bind 0.0.0.0:80 backend.wsgi