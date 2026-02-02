#!/usr/bin/env bash
set -e

# Wait for DB if env provided
if [[ -n "$DB_HOST" ]]; then
  echo "Waiting for database at $DB_HOST:${DB_PORT:-3306}..."
  for i in {1..30}; do
    nc -z "$DB_HOST" "${DB_PORT:-3306}" && break
    sleep 1
  done
fi

cd /app/bar_galileo

# Apply migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

exec "$@"
