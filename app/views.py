from django.views.generic import TemplateView


class index(TemplateView):
    template_name = "app/index.html"


class cobranza(TemplateView):
    template_name = "app/cobranza.html"
