#!/bin/sh
set -e

if [ -n "$DB_HOST" ]; then
  echo "Waiting for database at $DB_HOST:${DB_PORT:-3306}..."
  i=0
  while ! nc -z "$DB_HOST" "${DB_PORT:-3306}"; do
    i=$(( i + 1 ))
    if [ $i -ge 30 ]; then break; fi
    sleep 1
  done
fi

cd /app
python manage.py migrate --noinput

# Setup site_images module and permissions
python manage.py setup_site_images

# Collect static files
python manage.py collectstatic --noinput
exec "$@"
