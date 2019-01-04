from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from resources.models.base import ModifiableModel
from resources.models.resource import DurationSlot


class Sku(ModifiableModel):
    duration_slot = models.ForeignKey(DurationSlot, db_index=True, null=True, on_delete=models.SET_NULL)
    price = models.DecimalField(verbose_name=_('Price'), max_digits=6, decimal_places=2, default=0.00)
    vat = models.DecimalField(verbose_name=_('VAT'), max_digits=6, decimal_places=2, default=24.00)
    name = models.CharField(verbose_name=_('Name'), max_length=200)
    date_start = models.DateTimeField(verbose_name=_('Date start'), default=timezone.now)
    date_end = models.DateTimeField(verbose_name=_('Date end'), default=timezone.now)

    class Meta:
        verbose_name = _('Stock keeping unit')
        verbose_name_plural = _('Stock keeping units')

    def __str__(self):
        return self.name


class Order(ModifiableModel):
    sku = models.ForeignKey(Sku, db_index=True, null=True, on_delete=models.SET_NULL)
    order_code = models.CharField(verbose_name=_('Order code'), max_length=32)
    verification_code = models.CharField(verbose_name=_('Verification code'), max_length=40, null=False,
                                         blank=True, default='foo')
    reserver_name = models.CharField(verbose_name=_('Reserver name'), max_length=100, blank=True)
    reserver_email_address = models.EmailField(verbose_name=_('Reserver email address'), blank=True)
    reserver_phone_number = models.CharField(verbose_name=_('Reserver phone number'), max_length=30, blank=True)
    reserver_address_street = models.CharField(verbose_name=_('Reserver address street'), max_length=100, blank=True)
    reserver_address_zip = models.CharField(verbose_name=_('Reserver address zip'), max_length=30, blank=True)
    reserver_address_city = models.CharField(verbose_name=_('Reserver address city'), max_length=100, blank=True)
    product_name = models.CharField(verbose_name=_('Product name'), max_length=100, blank=True)
    order_process_started = models.DateTimeField(verbose_name=_('Order process started'), default=timezone.now)
    order_process_success = models.DateTimeField(verbose_name=_('Order process success'), blank=True, null=True)
    order_process_failure = models.DateTimeField(verbose_name=_('Order process failure'), blank=True, null=True)
    order_process_notified = models.DateTimeField(verbose_name=_('Order process notified'), blank=True, null=True)
    order_process_report_seen = models.DateTimeField(
        verbose_name=_('Order process notified'), blank=True, null=True
    )
    payment_service_order_number = models.IntegerField(blank=True, null=True)
    payment_service_timestamp = models.CharField(
        verbose_name=_('Payment service timestamp'),
        max_length=100,
        blank=True, null=True
    )
    payment_service_paid = models.CharField(
        verbose_name=_('Payment service paid'), max_length=100, blank=True, null=True
    )
    payment_service_method = models.IntegerField(blank=True, null=True)
    payment_service_return_authcode = models.CharField(
        verbose_name=_('Payment service return authcode'),
        max_length=100, blank=True,
        null=True
    )
    finished = models.DateTimeField(verbose_name=_('Order finished'), blank=True, null=True)
