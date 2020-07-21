from respa.settings import *

DEBUG = True

SECRET_KEY = 'foo'

SITE_ID = 1
ALLOWED_HOSTS = ['*']

DATABASES = {
  'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'HOST': 'postgresql',
    'PORT': '5432',
    'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'OPTIONS': {'sslmode': 'disable', },
    'ATOMIC_REQUESTS': True,
  }
}

SECURE_SSL_REDIRECT = False
