import os

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse

import pdfkit

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)

    pwd = os.path.dirname(__file__)
    css = pwd + '/static/app/bootstrap/css/bootstrap.css'
    pdfkit.from_string(html, 'out.pdf', css=css)
    pdf = open("out.pdf")
    response = HttpResponse(pdf.read(), content_type='application/pdf')
    pdf.close()
    return response
