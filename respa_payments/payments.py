from respa_payments import settings
from rest_framework import serializers
from respa_payments.api import OrderSerializer


class PaymentIntegration(object):
    def __init__(self, **kwargs):
        self.order = kwargs.get('order', None)
        self.callback_request = kwargs.get('callback_request', None)
        self.api_url = settings.PAYMENT_API_URL

    def get_data(self):
        self.url_success = '{}?id={}&verification_code={}'.format(
            settings.URL_SUCCESS, self.order.pk, self.order.verification_code)
        self.url_notify = settings.URL_NOTIFY
        self.url_failed = settings.URL_FAILED
        self.url_cancel = settings.URL_CANCEL
        return OrderSerializer(self.order).data

    def get_callback_data(self):
        return self.callback_request

    def is_valid(self):
        return True
