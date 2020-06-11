import io
import time
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from xhtml2pdf import pisa

from respa_payments.integrations.paytrail_e2_utils import generate_order_number
from respa_payments.models import Order


def render_pdf_receipt_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponseNotFound(_('The requested order object was not found'))

    pdf_name = 'varaukset_hameenlinna_kuitti_{0}.pdf'.format(time.strftime('%Y-%m-%d'))
    reservation_period = '{0} - {1}'.format(
        order.reservation.begin.strftime('%d.%m.%Y'),
        order.reservation.end.strftime('%d.%m.%Y')
    )
    order_number = generate_order_number('VARAUS', order.reservation.resource.name, order.id)
    reservation_name = '{0} ({1})'.format(
        order.reservation.resource.name,
        order.reservation.resource.unit.name
    )
    share_of_tax = str(round((order.sku.price / 100 * order.sku.vat), 2))

    context = {
        'timestamp': time.strftime('%d.%m.%Y %H:%M'),
        'reservation_name': reservation_name,
        'reservation_period': reservation_period,
        'payment_price': '{0} euroa'.format(order.sku.price),
        'payment_vat': '{0} %'.format(order.sku.vat),
        'share_of_tax': '{0} euroa'.format(share_of_tax),
        'payment_success_time': order.order_process_success.strftime('%d.%m.%Y %H:%M'),
        'reserver_name': order.reservation.reserver_name,
        'order_number': order_number,
    }
    template_path = 'pdf_receipt.html'
    template = get_template(template_path)
    html = template.render(context)

    buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(pdf_name)
    return response
