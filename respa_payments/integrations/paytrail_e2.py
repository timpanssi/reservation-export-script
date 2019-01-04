import re
import urllib
from hashlib import sha256
from respa_payments.payments import PaymentIntegration
from respa_payments import settings


class PaytrailE2Integration(PaymentIntegration):
    def __init__(self, **kwargs):
        super(PaytrailE2Integration, self).__init__(**kwargs)
        self.merchant_id = settings.MERCHANT_ID
        self.merchant_auth_hash = settings.MERCHANT_AUTH_HASH
        self.complete_redirect_url = settings.FRONTEND_URL
        self.payment_methods = '1,2,3,5,6,10,50,51,52,61'
        self.params_out = 'PAYMENT_ID,TIMESTAMP,STATUS'
        self.params_in = (
                    'MERCHANT_ID,'
                    'URL_SUCCESS,'
                    'URL_CANCEL,'
                    'URL_NOTIFY,'
                    'ORDER_NUMBER,'
                    'PARAMS_IN,'
                    'PARAMS_OUT,'
                    'PAYMENT_METHODS,'
                    'ITEM_TITLE[0],'
                    'ITEM_ID[0],'
                    'ITEM_QUANTITY[0],'
                    'ITEM_UNIT_PRICE[0],'
                    'ITEM_VAT_PERCENT[0],'
                    'ITEM_DISCOUNT_PERCENT[0],'
                    'ITEM_TYPE[0],'
                    'PAYER_PERSON_PHONE,'
                    'PAYER_PERSON_EMAIL,'
                    'PAYER_PERSON_FIRSTNAME,'
                    'PAYER_PERSON_LASTNAME,'
                    'PAYER_PERSON_ADDR_STREET,'
                    'PAYER_PERSON_ADDR_POSTAL_CODE,'
                    'PAYER_PERSON_ADDR_TOWN')

    def get_callback_data(self):
        data = {
            'redirect_url': self.complete_redirect_url or '',
            'payment_service_order_number': self.callback_request.GET.get('ORDER_NUMBER', None),
            'payment_service_timestamp': self.callback_request.GET.get('TIMESTAMP', None),
            'payment_service_paid': self.callback_request.GET.get('PAID', None),
            'payment_service_method': self.callback_request.GET.get('METHOD', None),
            'payment_service_return_authcode': self.callback_request.GET.get('RETURN_AUTHCODE', None),
        }
        return data

    def get_data(self):
        super(PaytrailE2Integration, self).get_data()
        data = {
            'MERCHANT_AUTH_HASH': self.merchant_auth_hash,
            'MERCHANT_ID': self.merchant_id,
            'URL_SUCCESS': self.url_success,
            'URL_CANCEL': self.url_cancel,
            'URL_NOTIFY': self.url_notify,
            'ORDER_NUMBER': self.order.payment_service_order_number,
            'PARAMS_IN': self.params_in,
            'PARAMS_OUT': self.params_out,
            'PAYMENT_METHODS': self.payment_methods,
            'ITEM_TITLE[0]': self.order.product_name,
            'ITEM_ID[0]': self.order.pk,
            'ITEM_QUANTITY[0]': 1,
            'ITEM_UNIT_PRICE[0]': self.order.sku.price,
            'ITEM_VAT_PERCENT[0]': self.order.sku.vat,
            'ITEM_DISCOUNT_PERCENT[0]': 0,
            'ITEM_TYPE[0]': 1,
            'PAYER_PERSON_PHONE': self.order.reserver_phone_number,
            'PAYER_PERSON_EMAIL': self.order.reserver_email_address,
            'PAYER_PERSON_FIRSTNAME': self.order.reserver_name,
            'PAYER_PERSON_LASTNAME': self.order.reserver_name,
            'PAYER_PERSON_ADDR_STREET': self.order.reserver_address_street,
            'PAYER_PERSON_ADDR_POSTAL_CODE': self.order.reserver_address_zip,
            'PAYER_PERSON_ADDR_TOWN': self.order.reserver_address_city,
        }

        auth_code = data['MERCHANT_AUTH_HASH'] + '|' + \
            data['MERCHANT_ID'] + '|' + \
            data['URL_SUCCESS'] + '|' + \
            data['URL_CANCEL'] + '|' + \
            data['URL_NOTIFY'] + '|' + \
            str(data['ORDER_NUMBER']) + '|' + \
            data['PARAMS_IN'] + '|' + \
            data['PARAMS_OUT'] + '|' + \
            str(data['PAYMENT_METHODS']) + '|' + \
            data['ITEM_TITLE[0]'] + '|' + \
            str(data['ITEM_ID[0]']) + '|' + \
            str(data['ITEM_QUANTITY[0]']) + '|' + \
            str(data['ITEM_UNIT_PRICE[0]']) + '|' + \
            str(data['ITEM_VAT_PERCENT[0]']) + '|' + \
            str(data['ITEM_DISCOUNT_PERCENT[0]']) + '|' + \
            str(data['ITEM_TYPE[0]']) + '|' + \
            data['PAYER_PERSON_PHONE'] + '|' + \
            data['PAYER_PERSON_EMAIL'] + '|' + \
            data['PAYER_PERSON_FIRSTNAME'] + '|' + \
            data['PAYER_PERSON_LASTNAME'] + '|' + \
            data['PAYER_PERSON_ADDR_STREET'] + '|' + \
            data['PAYER_PERSON_ADDR_POSTAL_CODE'] + '|' + \
            data['PAYER_PERSON_ADDR_TOWN']

        auth_hash = sha256()
        auth_hash.update(auth_code.encode())
        data['AUTHCODE'] = auth_hash.hexdigest().upper()
        query_string = urllib.parse.urlencode(data, doseq=True)
        return {'redirect_url': self.api_url + '?' + query_string}

    def is_valid(self):
        try:
            # Validate success callback
            str_to_check = '%(PAYMENT_ID)s|%(TIMESTAMP)s|%(STATUS)s' % self.callback_request.GET
            str_to_check += '|%s' % self.merchant_auth_hash
            checksum = sha256(str_to_check.encode('utf-8')).hexdigest().upper()
            return checksum == self.callback_request.GET.get('RETURN_AUTHCODE')
        except KeyError:
            try:
                # Validate failure callback
                str_to_check = '%(PAYMENT_ID)s|%(TIMESTAMP)s|%(STATUS)s' % self.callback_request.GET
                str_to_check += '|%s' % self.merchant_auth_hash
                checksum = sha256(str_to_check.encode('utf-8')).hexdigest().upper()
                return checksum == self.callback_request.GET.get('RETURN_AUTHCODE')
            except KeyError:
                return False
