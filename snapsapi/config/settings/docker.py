from .base import *

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'snaps',
        # 'USER': 'snaps',
        # 'PASSWORD': 'LVezKqVJJVnC0j7',
        # 'HOST': 'localhost', 또는 RDS, Cloud SQL 주소
        # 'PORT': '5432',
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
    }
}