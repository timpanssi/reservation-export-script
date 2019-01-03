from respa_payments import settings
from rest_framework import serializers
from respa_payments.api import OrderSerializer


class PaymentIntegration(object):
    def __init__(self, order):
        self.api_url = settings.PAYMENT_API_URL
        self.url_success = settings.URL_SUCCESS
        self.url_failed = settings.URL_FAILED
        self.url_cancel = settings.URL_CANCEL
        self.order = order

    def get_data(self):
        return OrderSerializer(self.order).data

    def is_valid(self):
        return True
