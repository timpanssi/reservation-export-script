from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from resources.models.resource import Resource
from resources.api.resource import ResourceSerializer
from respa_payments.models import Order, Sku
from respa_payments import settings
from rest_framework import serializers
from django.utils.module_loading import import_string
from django.utils import timezone


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
            payment = self.payment_integration(order)
            if payment.is_valid():
                response_data = payment.get_data()
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(payment.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(order.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteOrderView(APIView):
    permission_classes = (permissions.AllowAny,)

    def __init__(self):
        self.payment_integration = import_string(settings.INTEGRATION_CLASS)

    def post(self, request):
        order_data = request.data['order']
        try:
            order = Order.objects.get(pk=order_data['id'])
            order.order_process_success = order_data.get('success') or timezone.now()
            order.order_process_failure = order_data.get('failure')
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        order = OrderSerializer(order, data=order_data, partial=True)
        if order.is_valid():
            order.save()
            return Response(order.data, status=status.HTTP_201_CREATED)
        return Response(order.errors, status=status.HTTP_400_BAD_REQUEST)
