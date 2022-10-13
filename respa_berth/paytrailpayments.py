from django.conf import settings

class PaytrailArguments(object):

  service = 'VARAUS'
  product='VENEPAIKKA'

  def __init__(self, purchase, **kwargs):
    self.stamp = self._get_order_stamp(purchase)
    self.reference = self._get_order_number(purchase, **kwargs)
    self.__dict__.update(kwargs)
    self.currency = "EUR"
    self.language = "FI"
    self.callbackDelay= getattr(settings, 'BERTH_PAYMENTS_PAYTRAIL_CALLBACK_DELAY', 60)
    self.amount = self._get_order_total_amount()

  def _get_order_number(self, purchase, **kwargs):
    # Support only a single item. Abandon product_type from the information ending to the PayTrail API
    return self.service + '+' + self.product + '+' + str(kwargs['items'][0].pop('product_type')) + '+' + str(purchase.pk)

  def _get_order_stamp(self, purchase):
    return str(purchase.pk)

  def _get_order_total_amount(self):
    amount = 0
    for item in self.items:
      amount += int(item['unitPrice'])
      # Convert euros to cents
      item['unitPrice'] = 100 * item['unitPrice']
    return 100 * amount

  def get_payment_data(self):
    # TODO: ADD DICT CHECKING
    return dict(self.__dict__)
