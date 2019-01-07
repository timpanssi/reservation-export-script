from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured, ValidationError
from respa_payments import settings
from rest_framework import serializers
from respa_payments.api import OrderSerializer
from respa_payments.models import Order


class PaymentIntegration(object):
    def __init__(self, **kwargs):
        self.request = kwargs.get('request', None)
        self.api_url = settings.PAYMENT_API_URL
        self.url_notify = settings.URL_NOTIFY
        self.url_failed = settings.URL_FAILED
        self.url_cancel = settings.URL_CANCEL
        self.url_redirect_callback = settings.URL_REDIRECT_CALLBACK
        self.errors = []
        self.order = None
        self.callback_data = None

    def save_post_data(self):
        order = OrderSerializer(data=self.request.data.get('order'))
        if order.is_valid():
            self.order = order.save()
            self.post_data = self.construct_post_data()
            return self.order
        return order.errors

    def construct_post_data(self):
        self.url_success = '{}?id={}&verification_code={}'.format(
            settings.URL_SUCCESS, self.order.pk, self.order.verification_code)
        return OrderSerializer(self.order).data

    def save_callback_data(self):
        self.construct_callback_data()
        if self.is_valid():
            self.order = self.order_serializer.save()
            return True
        return True

    def construct_callback_data(self):
        self.callback_data = {
            'redirect_url': self.url_redirect_callback or '',
        }
        return self.callback_data

    def is_valid(self):
        order_id = self.request.GET.get('id')
        verification_code = self.request.GET.get('verification_code')
        try:
            self.order = Order.objects.get(pk=order_id, verification_code=verification_code)
        except Order.DoesNotExist as e:
            raise ValidationError(_(e))

        self.order_serializer = OrderSerializer(self.order, data=self.callback_data, partial=True)
        if self.order_serializer.is_valid():
            return True
        else:
            self.errors = self.order_serializer.errors
