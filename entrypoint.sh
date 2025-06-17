#!/bin/bash

set -e


# [검증용 출력] 필요한 환경변수들 확인
echo "===== ENV 확인 시작 ====="
echo "DB_HOST               = ${DB_HOST}"
echo "DB_PORT               = ${DB_PORT}"
echo "DB_NAME               = ${DB_NAME}"
echo "DB_USER               = ${DB_USER}"
# 민감정보는 로그에 남기지 않는 게 좋지만, 테스트용이라면 아래도 확인 가능
echo "AWS_STORAGE_BUCKET    = ${AWS_STORAGE_BUCKET_NAME}"
echo "AWS_S3_CUSTOM_DOMAIN  = ${AWS_S3_CUSTOM_DOMAIN}"
echo "===== ENV 확인 끝 ====="



echo "🛠️ Waiting for DB to be ready..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "⏳ Waiting for database..."
  sleep 1
done

echo "🚀 Running migrations..."
python manage.py migrate core
python manage.py migrate

echo "🚀 Collect static files..."
python manage.py collectstatic --noinput

echo "🧙 Starting server..."
exec "$@"
