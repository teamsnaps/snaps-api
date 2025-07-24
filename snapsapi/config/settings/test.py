import django.test.runner

from .base import *

ALLOWED_HOSTS = []

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 테스트 환경에서 FCM 초기화 방지
FIREBASE_ADMIN_INITIALIZED = False


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# TEST_RUNNER = django.test.runner.DiscoverRunner

# 테스트 속도 향상을 위한 설정
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 캐싱 비활성화
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
