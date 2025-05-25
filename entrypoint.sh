#!/bin/bash

set -e

#echo "🛠️ Waiting for DB to be ready..."
#until nc -z "$DB_HOST" "$DB_PORT"; do
#  echo "⏳ Waiting for database..."
#  sleep 1
#done

echo "🚀 Running migrations..."
python manage.py migrate core
python manage.py migrate
python manage.py collectstatic --noinput

echo "🧙 Starting server..."
exec "$@"
