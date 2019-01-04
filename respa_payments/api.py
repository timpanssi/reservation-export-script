from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_string
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework import serializers
from resources.models.resource import Resource
from resources.api.resource import ResourceSerializer
from respa_payments.models import Order, Sku
from respa_payments import settings


class PaymentResourceSerializer(ResourceSerializer):
    class Meta:
        model = Resource
        exclude = ('reservation_requested_notification_extra', 'reservation_confirmed_notification_extra',
                   'access_code_type', 'reservation_metadata_set')


class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sku
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderView(APIView):
    permission_classes = (permissions.AllowAny,)

    def __init__(self):
        self.payment_integration = import_string(settings.INTEGRATION_CLASS)

    def post(self, request):
        order_data = request.data['order']
        order = OrderSerializer(data=order_data)
        if order.is_valid():
            order = order.save()
            # unique = order.pk
            # verification_uuid = order.verification_uuid
            payment = self.payment_integration(order=order)
            return Response(payment.get_data(), status=status.HTTP_201_CREATED)
        return Response(order.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteOrderView(APIView):
    permission_classes = (permissions.AllowAny,)

    def __init__(self):
        self.payment_integration = import_string(settings.INTEGRATION_CLASS)

    def get(self, request):
        self.order_id = request.GET.get('id')
        self.verification_code = request.GET.get('verification_code')
        self.payment = self.payment_integration(callback_request=request)
        self.callback_data = self.payment.get_callback_data()
        if self.validate():
            return HttpResponseRedirect(self.callback_data.get('redirect_url') + '?code=' + self.verification_code)
        # return HttpResponseRedirect(self.callback_data.get('redirect_url'))

    def validate(self):
        try:
            order = Order.objects.get(pk=self.order_id, verification_code=self.verification_code)
        except Exception as e:
            raise ValidationError(_(e))

        payment_integration_response = self.payment.is_valid()
        if not payment_integration_response:
            raise ValidationError(_('The payment did not validate.'))

        order = OrderSerializer(order, data=self.callback_data, partial=True)
        if order.is_valid():
            order.save()
            return True
        raise ValidationError(_('The payment did not validate.'))
