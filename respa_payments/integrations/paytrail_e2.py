import re
import urllib
from hashlib import sha256
from respa_payments.payments import PaymentIntegration


class PaytrailE2Integration(PaymentIntegration):
    def remove_special_chars(self, text):
        return re.sub('[^A-Za-z0-9- "\',()\[\]{}*\/+\-_,.:&!?@#$£=*;~]+', '_', text)

    def get_data(self):
        data = {
            # 'MERCHANT_AUTH_HASH': self.order.merchant_auth_hash,
            # 'MERCHANT_ID': self.order.merchant_id,
            'URL_SUCCESS': self.url_success,
            'URL_CANCEL': self.url_cancel,
            # 'URL_NOTIFY': self.order.url_notify,
            'ORDER_NUMBER': self.order.payment_service_order_number,
            # 'PARAMS_IN': self.order.params_in,
            # 'PARAMS_OUT': self.order.params_out,
            # 'PAYMENT_METHODS': self.order.payment_methods,
            'ITEM_TITLE[0]': self.order.product_name,
            # 'ITEM_ID[0]': self.order.item_id,
            'ITEM_QUANTITY[0]': 1,
            'ITEM_UNIT_PRICE[0]': self.order.sku.price,
            'ITEM_VAT_PERCENT[0]': self.order.sku.vat,
            # 'ITEM_DISCOUNT_PERCENT[0]': self.order.item_discount_percent,
            # 'ITEM_TYPE[0]': self.order.item_type,
            'PAYER_PERSON_PHONE': self.order.reserver_phone_number,
            'PAYER_PERSON_EMAIL': self.order.reserver_email_address,
            'PAYER_PERSON_FIRSTNAME': self.order.reserver_name,
            'PAYER_PERSON_LASTNAME': self.order.reserver_name,
            'PAYER_PERSON_ADDR_STREET': self.order.reserver_address_street,
            'PAYER_PERSON_ADDR_POSTAL_CODE': self.order.reserver_address_zip,
            'PAYER_PERSON_ADDR_TOWN': self.order.reserver_address_city,
        }

        # auth_code =
        # data['MERCHANT_AUTH_HASH'] + '|' + \
        # data['MERCHANT_ID'] + '|' + \
        # data['URL_CANCEL'] + '|' + \
        # data['URL_NOTIFY'] + '|' + \
        # str(data['ORDER_NUMBER']) + '|' + \
        # data['PARAMS_IN'] + '|' + \
        # data['PARAMS_OUT'] + '|' + \
        # str(data['PAYMENT_METHODS']) + '|' + \
        # data['ITEM_TITLE[0]'] + '|' + \
        # str(data['ITEM_ID[0]']) + '|' + \
        # str(data['ITEM_QUANTITY[0]']) + '|' + \
        # str(data['ITEM_UNIT_PRICE[0]']) + '|' + \
        # str(data['ITEM_VAT_PERCENT[0]']) + '|' + \
        # str(data['ITEM_DISCOUNT_PERCENT[0]']) + '|' + \
        # str(data['ITEM_TYPE[0]']) + '|' + \
        # data['PAYER_PERSON_PHONE'] + '|' + \
        # data['PAYER_PERSON_EMAIL'] + '|' + \
        # data['PAYER_PERSON_FIRSTNAME'] + '|' + \
        # data['PAYER_PERSON_LASTNAME'] + '|' + \
        # data['PAYER_PERSON_ADDR_STREET'] + '|' + \
        # data['PAYER_PERSON_ADDR_POSTAL_CODE'] + '|' + \
        # data['PAYER_PERSON_ADDR_TOWN']

        auth_code = data['URL_SUCCESS'] + '|' + \
            data['URL_CANCEL'] + '|' + \
            str(data['ORDER_NUMBER']) + '|' + \
            data['ITEM_TITLE[0]'] + '|' + \
            str(data['ITEM_QUANTITY[0]']) + '|' + \
            str(data['ITEM_UNIT_PRICE[0]']) + '|' + \
            str(data['ITEM_VAT_PERCENT[0]']) + '|' + \
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
