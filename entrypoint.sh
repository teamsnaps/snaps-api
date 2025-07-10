#!/bin/bash

set -e


# [Verification output] Check required environment variables
echo "===== ENV CHECK START ====="
echo "DB_HOST               = ${DB_HOST}"
echo "DB_PORT               = ${DB_PORT}"
echo "DB_NAME               = ${DB_NAME}"
echo "DB_USER               = ${DB_USER}"
# It's best not to leave sensitive information in logs, but for testing purposes, you can also check the following
echo "AWS_STORAGE_BUCKET    = ${AWS_STORAGE_BUCKET_NAME}"
echo "AWS_S3_CUSTOM_DOMAIN  = ${AWS_S3_CUSTOM_DOMAIN}"
echo "===== ENV CHECK END ====="

sleep 1

#echo "🛠️ Waiting for DB to be ready..."
#until nc -z "$DB_HOST" "$DB_PORT"; do
#  echo "⏳ Waiting for database..."
#  sleep 1
#done

echo "🚀 Running migrations..."
python manage.py migrate core
python manage.py migrate

echo "🚀 Collect static files..."
python manage.py collectstatic --noinput

echo "🧙 Starting server..."
exec "$@"
