#!/bin/bash
set -e

if [ ! -f db.sqlite3 ]; then
  echo "SQLite database file not found in the project root."
  exit 1
fi

set -a
source .env
set +a

echo "Exporting data from SQLite..."
USE_SQLITE=True python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.Permission > /tmp/bookstore_sqlite.json

echo "Applying PostgreSQL migrations..."
USE_SQLITE=False python manage.py migrate --noinput

echo "Loading exported data into PostgreSQL..."
USE_SQLITE=False python manage.py loaddata /tmp/bookstore_sqlite.json

echo "Migration completed successfully."
