#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true
exec gunicorn --bind 0.0.0.0:8001 --workers 2 project_b.wsgi:application
