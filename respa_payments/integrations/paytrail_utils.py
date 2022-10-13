import unicodedata


def generate_order_number(service, resource_name, order_id):
    return service + '+' + unicode_to_paytrail(resource_name) + '+' + str(order_id)


def unicode_to_paytrail(string):
    return str(unicodedata.normalize('NFD', string).encode('ascii', 'ignore'), 'utf-8')
