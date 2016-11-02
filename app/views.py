from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import json
from app.models import *


class index(TemplateView):
    template_name = "app/index.html"


class cobranza(TemplateView):
    template_name = "app/cobranza.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['clientes'] = Cliente.objects.all()
        return super(cobranza, self).render_to_response(context)


class cobranza_cliente(TemplateView):
    template_name = "app/cobranza_cliente.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        if request.GET.get('id'):
            id_cliente = int(request.GET.get('id'))
            context['cliente'] = Cliente.objects.get(id=id_cliente)
            context['facturas'] = Factura.objects.all().filter(cliente=Cliente.objects.get(id=id_cliente))
        return super(cobranza_cliente, self).render_to_response(context)


@csrf_exempt
def add_comentario_cliente(request):
    data = []
    obj_json = {}
    comentario = request.POST.get('comentario');
    id_cliente = request.POST.get('id_cliente');
    id_usuario = request.POST.get('id_usuario');
    if id_usuario:
        try:
            usuario = User.objects.get(id=id_usuario)
        except Exception as e:
            usuario = None
    else:
        usuario = request.user

    if not comentario:
        obj_json['code'] = "400"
        obj_json['mensaje'] = "ERROR: comentario invalido";
    elif not id_cliente:
        obj_json['code'] = "400"
        obj_json['mensaje'] = "ERROR: Cliente invalido";
    elif not usuario:
        obj_json['code'] = "400"
        obj_json['mensaje'] = "ERROR: Usuario invalido";
    else:
        try:
            cliente = Cliente.objects.get(id=int(id_cliente))
        except Exception as e:
            obj_json['code'] = "500"
            obj_json['mensaje'] = "ERROR: Cliente no encontrado"
            cliente = None

        if cliente:
            comentario = Comentario.objects.create(usuario=usuario, descripcion=comentario)
            comentario.save()

            cliente.comentarios.add(comentario)
            cliente.save()
            obj_json['code'] = "200"
            obj_json['mensaje'] = "Comentario registrado exitosamente!"

    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')
