import io
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_pdf_receipt_view(context):
    template_path = 'pdf_receipt.html'
    template = get_template(template_path)
    html = template.render(context)

    buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
