import datetime
import hmac
import json
import requests
import typing
from hashlib import sha256
from django.conf import settings

import resources


class PaytrailPaymentsIntegration(object):

    def __init__(self, **kwargs):
        self.payment_data = kwargs.get('payment_data', None)
        self.api_url = settings.BERTH_PAYMENTS_API_URL


    """ pick user attributes and construct a request to PayTrail"""
    def payment_post(self):

        headers = {
            "checkout-account": settings.BERTH_PAYMENTS_PAYTRAIL_MERCHANT_ID,
            "checkout-algorithm": "sha256",
            "checkout-method": 'POST',
            "checkout-nonce": '564635208570151',
            "checkout-timestamp": datetime.datetime.now().isoformat(),
            # "platform-name": "hmlvaraukset",
        }

        headers["signature"] = self._calculate_hmac(
            secret=settings.BERTH_PAYMENTS_PAYTRAIL_MERCHANT_SECRET,
            params=headers,
            body=self.payment_data,
        )

        response = requests.post(url=self.api_url, headers=headers, json=self.payment_data)

        data =  response.json()

        if data.get('status') == 'error':
            raise Exception(data.get('message'))

        return {'url': data.get('href', '/')}

    @classmethod
    def payment_callback_handler(cls, request_from_paytrail):

        # https://docs.paytrail.com/#/?id=redirect-and-callback-url-signing
        calculated_signature = cls._calculate_hmac(
            secret=settings.BERTH_PAYMENTS_PAYTRAIL_MERCHANT_SECRET,
            params=request_from_paytrail.GET.dict()
        )

        if calculated_signature != request_from_paytrail.GET.get('signature', None):
            raise Exception('Signatures does not match.')

        return calculated_signature

    @classmethod
    def _calculate_hmac(cls, secret, params, body=''):
        payload = params.keys()
        # All query params beginning with checkout- are included in the signature calculation
        # https://docs.paytrail.com/#/?id=redirect-and-callback-url-parameters
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
