from django.shortcuts import render
from django.views.generic import TemplateView


class cobranza(TemplateView):
    template_name = "inventario/facturacion.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['clientes'] = Fa.objects.all()
        return super(cobranza, self).render_to_response(context)
