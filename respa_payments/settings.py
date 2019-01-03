from django.conf import settings

PAYMENT_API_HEADERS = getattr(settings, 'RESPA_PAYMENTS_API_HEADERS', '')
INTEGRATION_CLASS = getattr(settings, 'RESPA_PAYMENTS_INTEGRATION_CLASS', '')
PAYMENT_API_URL = getattr(settings, 'RESPA_PAYMENTS_API_URL', '')
URL_SUCCESS = getattr(settings, 'RESPA_PAYMENTS_URL_SUCCESS', '')
URL_FAILED = getattr(settings, 'RESPA_PAYMENTS_URL_FAILED', '')
URL_CANCEL = getattr(settings, 'RESPA_PAYMENTS_URL_CANCEL', '')
