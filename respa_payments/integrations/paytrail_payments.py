import datetime
import hmac
import json
import requests
import typing
from hashlib import sha256

import resources
from respa_payments.payments import PaymentIntegration
from respa_payments import models, settings
from respa_payments.integrations.paytrail_utils import generate_order_number


class PaytrailPaymentsIntegration(PaymentIntegration):
    service = 'VARAUS'

    def order_post_handler(self, order_dict):
        super(PaytrailPaymentsIntegration, self).order_post_handler(order_dict)

        order = typing.cast(models.Order, models.Order.objects.get(pk=order_dict.get('id')))
        reservation = typing.cast(resources.models.Reservation, order.reservation)
        sku = typing.cast(models.Sku, order.sku)
        resource = typing.cast(resources.models.Reservation, reservation.resource)

        # https://docs.paytrail.com/#/?id=request
        body = {
            "stamp": str(order.pk),
            "reference": generate_order_number(self.service, resource.name, order.pk),
            "amount": int(sku.price * 100),  # Convert euros to cents
            "currency": "EUR",
            "language": "FI",
            "items": [
                {
                    "productCode": str(sku.pk),
                    "unitPrice": int(sku.price * 100),  # Convert euros to cents
                    "vatPercentage": int(sku.vat),
                    "units": 1,
                }
            ],
            "customer": {
                "email": reservation.reserver_email_address or '',
                "firstName": reservation.reserver_name or '',
                "lastName": reservation.reserver_name or '',
                "phone": reservation.reserver_phone_number or '',
                "vatId": reservation.reserver_id or '',
                "companyName": reservation.company or '',
            },
            "invoicingAddress": {
                "streetAddress": reservation.billing_address_street or reservation.reserver_address_street or '',
                "postalCode": reservation.billing_address_zip or reservation.reserver_address_zip or '',
                "city": reservation.billing_address_city or reservation.reserver_address_city or '',
                "country": "FI",
            },
            "redirectUrls": {
                "success": self.url_success,
                "cancel": self.url_cancel,
            },
            "callbackUrls": {
                "success": self.url_success,
                "cancel": self.url_cancel,
            }
        }

        headers = {
            "checkout-account": settings.MERCHANT_ID,
            "checkout-algorithm": "sha256",
            "checkout-method": 'POST',
            "checkout-nonce": '564635208570151',
            "checkout-timestamp": datetime.datetime.now().isoformat(),
            # "platform-name": "hmlvaraukset",
        }

        headers['signature'] = self._calculate_hmac(secret=settings.MERCHANT_AUTH_HASH, params=headers, body=body)

        response = requests.post(url=self.api_url, headers=headers, json=body)

        data =  response.json()

        if data.get('status') == 'error':
            raise Exception(data.get('message'))

        return {'redirect_url': data.get('href', '/')}

    def payment_callback_handler(self):
        callback_data = super(PaytrailPaymentsIntegration, self).payment_callback_handler()

        # https://docs.paytrail.com/#/?id=redirect-and-callback-url-signing
        calculated_signature = self._calculate_hmac(secret=settings.MERCHANT_AUTH_HASH, params=self.request.GET.dict())

        if calculated_signature != self.request.GET.get('signature', None):
            raise Exception('Signatures does not match.')

        callback_data['payment_service_amount'] = (int(self.request.GET.get('checkout-amount')) / 100)
        callback_data['payment_service_return_authcode'] = self.request.GET.get('signature')
        callback_data['payment_service_status'] = self.request.GET.get('checkout-status')
        callback_data['payment_service_success'] = self.request.GET.get('checkout-status') == 'ok'
        callback_data['payment_service_currency'] = 'EUR'

        return callback_data

    def _calculate_hmac(self, secret, params, body=''):
        payload = params.keys()
        payload = filter(lambda x: x[:9] == 'checkout-', payload)
        payload = sorted(payload)
        payload = map(lambda x: '{}:{}'.format(x, params[x]), payload)
        payload = list(payload)

        if body:
            payload.append(json.dumps(body))
        else:
            payload.append(body)

        payload = '\n'.join(payload)

        return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
