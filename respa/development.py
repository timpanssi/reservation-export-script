from respa.settings import *

DEBUG = True

SECRET_KEY = 'foo'

SITE_ID = 1
ALLOWED_HOSTS = ['*']

DATABASES = {
  'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'HOST': 'localhost',
    'PORT': '5432',
    'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'OPTIONS': {'sslmode': 'disable', },
    'ATOMIC_REQUESTS': True,
  }
}

SECURE_SSL_REDIRECT = False

PAYTRAIL_MERCHANT_ID = '375917'
PAYTRAIL_MERCHANT_SECRET = 'SAIPPUAKAUPPIAS'

RESPA_PAYMENTS_PAYTRAIL_MERCHANT_ID = PAYTRAIL_MERCHANT_ID
RESPA_PAYMENTS_PAYTRAIL_MERCHANT_AUTH_HASH = PAYTRAIL_MERCHANT_SECRET
RESPA_PAYMENTS_INTEGRATION_CLASS = 'respa_payments.integrations.paytrail_payments.PaytrailPaymentsIntegration'
RESPA_PAYMENTS_API_URL = 'https://services.paytrail.com/payments'
RESPA_PAYMENTS_URL_SUCCESS = 'https://varaukset.haltudemo.fi/v1/rp/order-callback/'
RESPA_PAYMENTS_URL_FAILED = 'https://varaukset.haltudemo.fi/v1/rp/order-callback/'
RESPA_PAYMENTS_URL_CANCEL = 'https://varaukset.haltudemo.fi/v1/rp/order-callback/'
RESPA_PAYMENTS_URL_REDIRECT_CALLBACK = 'https://varaukset.haltudemo.fi/varaamo/'

BERTH_PAYMENTS_PAYTRAIL_MERCHANT_ID = PAYTRAIL_MERCHANT_ID
BERTH_PAYMENTS_PAYTRAIL_MERCHANT_SECRET = PAYTRAIL_MERCHANT_SECRET