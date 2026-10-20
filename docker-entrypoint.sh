#!/bin/bash
set -e

export PYTHONUNBUFFERED=1

if [ "${USE_SQLITE:-True}" != "True" ] && [ "${USE_SQLITE:-True}" != "true" ]; then
    until python - <<'PY'
import os
import sys

import psycopg

try:
    conn = psycopg.connect(
        dbname=os.getenv('POSTGRES_DB', 'bookstore'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
        host=os.getenv('POSTGRES_HOST', 'db'),
        port=os.getenv('POSTGRES_PORT', '5432'),
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
    do
        echo "PostgreSQL is not ready yet. Retrying..."
        sleep 2
    done
fi

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn --config gunicorn.conf.py bookstore.wsgi:application
