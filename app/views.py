from datetime import datetime

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import json
from django.http import HttpResponseRedirect
from app.models import *
from datetime import datetime


def inicio(request):
    return HttpResponseRedirect("/app")


class index(TemplateView):
    template_name = "app/index.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['total_cartera'] = Factura.objects.all().aggregate(Sum('monto'))['monto__sum'] - \
        Factura_Abono.objects.all().aggregate(Sum('monto_abono'))['monto_abono__sum']
        return super(index, self).render_to_response(context)


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
            cliente =  Cliente.objects.get(id=id_cliente)
            context['cliente'] = cliente
            # hace falta agregar que la factura tenga saldo pendiente > 0
            context['facturas'] = Factura.facturas_pendientes(cliente)
            context['comentarios'] = Cliente.objects.get(id=id_cliente).comentarios.all()
        return super(cobranza_cliente, self).render_to_response(context)


def get_cliente_comentarios(request):
    if request.GET.get('id'):
        id_cliente = int(request.GET.get('id'))
        comentarios = Cliente.objects.get(id=id_cliente).comentarios.all()
    html = render_to_string('app/partial/_comentarios.html', {'comentarios': comentarios})
    return HttpResponse(html)


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


def get_facturas_pendientes(request):
    if request.GET.get('id'):
        id_cliente = int(request.GET.get('id'))
        cliente = Cliente.objects.get(id=id_cliente)
        facturas = Factura.facturas_pendientes(cliente)
    html = render_to_string('app/partial/_facturas_pendientes.html', {'facturas': facturas})
    return HttpResponse(html)


def render_add_abono_factura(request):
    id_factura = request.GET.get('id_factura')
    is_cacelacion = bool(request.GET.get('is_cacelacion'))
    id_usuario = request.GET.get('id_usuario')
    if id_usuario:
        try:
            usuario = User.objects.get(id=id_usuario)
        except Exception as e:
            usuario = None
    else:
        usuario = request.user

    if not is_cacelacion:
        is_cacelacion = False

    if not id_factura:
        html = "<div class='alert alert-danger'>" \
               "<strong>ERROR!</strong> Factura no encontrada.</div>"
    elif not usuario:
        html = "<div class='alert alert-danger'>" \
               "<strong>ERROR!</strong> Usuario invalido inicie sesion nuevamente.</div>"
    else:
        try:
            factura = Factura.objects.get(id=int(id_factura))
        except Exception as e:
            factura = None

        if not factura:
            html = "<div class='alert alert-danger'>" \
                   "<strong>ERROR!</strong> Factura no encontrada.</div>"
        else:
            html = render_to_string('app/partial/_abono_factura.html', {'factura': factura,
                                                                        'is_cacelacion': is_cacelacion})

    return HttpResponse(html)


def add_abono_factura(request):
    data = []
    obj_json = {}
    id_doc = request.POST.get('id_doc')
    monto = request.POST.get('monto')
    id_usuario = request.POST.get('id_usuario')
    if id_usuario:
        try:
            usuario = User.objects.get(id=id_usuario)
        except Exception as e:
            usuario = None
    else:
        usuario = request.user

    if not id_doc:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Documento invalido"
    elif not monto:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Monto invalido"
    elif not usuario:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Usuario invalido"
    else:
        try:
            factura = Factura.objects.get(id=int(id_doc))
        except Exception as e:
            obj_json['code'] = 500
            obj_json['mensaje'] = "ERROR: Documento no encontrado"
            factura = None

        if factura:
            abono = Factura_Abono.objects.create(usuario=usuario, monto_abono=float(monto), factura=factura)
            abono.save()
            obj_json['code'] = 200
            obj_json['mensaje'] = "Pago registrado exitosamente!"

    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')

def render_gestiones(request):
    if request.GET.get('id_cliente'):
        id_cliente = int(request.GET.get('id_cliente'))
        gestiones = Cliente.objects.get(id=id_cliente).gestiones.all()
    html = render_to_string('app/partial/_gestiones.html', {'gestiones': gestiones})
    return HttpResponse(html)

def render_add_gestion(request):
    tipo_gestiones = Tipo_Gestion.objects.filter(activo=True)
    html = render_to_string('app/partial/_gestion_add.html', {'tipo_gestiones': tipo_gestiones})
    return HttpResponse(html)

def render_edit_gestion(request):
    if request.GET.get('id_gestion'):
        id_gestion = int(request.GET.get('id_gestion'))
        gestion = Gestion.objects.get(id=id_gestion)
    tipo_gestiones = Tipo_Gestion.objects.filter(activo=True)
    html = render_to_string('app/partial/_gestion_edit.html', {'gestion':gestion, 'tipo_gestiones': tipo_gestiones})
    return HttpResponse(html)

def render_finish_gestion(request):
    if request.GET.get('id_gestion'):
        id_gestion = int(request.GET.get('id_gestion'))
        gestion = Gestion.objects.get(id=id_gestion)
    tipo_gestiones = Tipo_Gestion.objects.filter(activo=True)
    resultados = gestion.tipo_gestion.resultados.all()
    html = render_to_string('app/partial/_gestion_finish.html', {'gestion':gestion, 'tipo_gestiones': tipo_gestiones,
                                                               'resultados':resultados})
    return HttpResponse(html)

def add_new_cliente_gestion(request):
    data = []
    obj_json = {}
    id_cliente = request.POST.get('id_cliente')
    id_tipo_gestion = request.POST.get('id_tipo_gestion')
    descripcion = request.POST.get('descripcion')
    str_programacion = request.POST.get('programacion')
    id_usuario = request.POST.get('id_usuario')
    if id_usuario:
        try:
            usuario = User.objects.get(id=id_usuario)
        except Exception as e:
            usuario = None
    else:
        usuario = request.user

    if id_tipo_gestion:
        try:
            tipo_gestion = Tipo_Gestion.objects.get(id=id_cliente)
        except Exception as e:
            tipo_gestion = None
    else:
        tipo_gestion = None

    if id_cliente:
        try:
            cliente = Cliente.objects.get(id=id_cliente)
        except Exception as e:
            cliente = None
    else:
        cliente = None

    if str_programacion:
        programacion = datetime.strptime(str_programacion, '%Y-%M-%d')
    else:
        programacion = None

    if not cliente:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Cliente invalido"
    elif not tipo_gestion:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Tipo gestion invalida"
    elif not usuario:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Usuario invalido"
    else:
        gestion = Gestion.objects.create(tipo_gestion=tipo_gestion, usuario_creacion=usuario,
                                         descripcion=descripcion, programacion=programacion)
        gestion.save()

        cliente.gestiones.add(gestion)
        cliente.save()

        obj_json['code'] = 200
        obj_json['mensaje'] = "Gestion registrada exitosamente!"

    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')

def edit_cliente_gestion(request):
    data = []
    obj_json = {}
    id_gestion = request.POST.get('id_gestion')
    id_cliente = request.POST.get('id_cliente')
    id_tipo_gestion = request.POST.get('id_tipo_gestion')
    descripcion = request.POST.get('descripcion')
    str_programacion = request.POST.get('programacion')
    id_usuario = request.POST.get('id_usuario')
    if id_usuario:
        try:
            usuario = User.objects.get(id=id_usuario)
        except Exception as e:
            usuario = None
    else:
        usuario = request.user

    if id_tipo_gestion:
        try:
            tipo_gestion = Tipo_Gestion.objects.get(id=id_tipo_gestion)
        except Exception as e:
            tipo_gestion = None
    else:
        tipo_gestion = None

    if id_cliente:
        try:
            cliente = Cliente.objects.get(id=id_cliente)
        except Exception as e:
            cliente = None
    else:
        cliente = None

    if str_programacion:
        programacion = datetime.strptime(str_programacion, '%Y-%M-%d')
    else:
        programacion = None

    if not cliente:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Cliente invalido"
    elif not tipo_gestion:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Tipo gestion invalida"
    elif not usuario:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Usuario invalido"
    elif not id_gestion:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Gestion invalida"
    else:

        gestion = Gestion.objects.get(id=id_gestion)
        if not gestion:
            obj_json['code'] = 400
            obj_json['mensaje'] = "ERROR: Gestion no encontrada"
        else:
            gestion.tipo_gestion=tipo_gestion
            gestion.usuario_creacion=usuario
            gestion.descripcion=descripcion
            gestion.programacion=programacion
            gestion.fecha_creacion = datetime.now()
            gestion.save()

            obj_json['code'] = 200
            obj_json['mensaje'] = "Gestion registrada exitosamente!"

    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')

def finish_cliente_gestion(request):
    data = []
    obj_json = {}
    id_gestion = request.POST.get('id_gestion')
    id_resultado = request.POST.get('id_resultado')
    descripcion = request.POST.get('descripcion')
    id_usuario = request.POST.get('id_usuario')
    if id_usuario:
        try:
            usuario = User.objects.get(id=id_usuario)
        except Exception as e:
            usuario = None
    else:
        usuario = request.user

    if id_resultado:
        try:
            resultado = Gestion_Resultado.objects.get(id=id_resultado)
        except Exception as e:
            resultado = None
    else:
        resultado = None


    if not id_resultado:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Resultado gestion invalida"
    elif not usuario:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Usuario invalido"
    elif not id_gestion:
        obj_json['code'] = 400
        obj_json['mensaje'] = "ERROR: Gestion invalida"
    else:

        gestion = Gestion.objects.get(id=id_gestion)
        if not gestion:
            obj_json['code'] = 400
            obj_json['mensaje'] = "ERROR: Gestion no encontrada"
        else:
            gestion.usuario_completa=usuario
            gestion.descripcion_resultado=descripcion
            gestion.resultado=resultado
            gestion.fecha_completa = datetime.now()
            gestion.save()

            obj_json['code'] = 200
            obj_json['mensaje'] = "Gestion finalizada exitosamente!"

    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
def get_tipo_gestion_resultado(request):
    id_tipo = request.POST.get('id_tipo')
    if id_tipo:
        try:
            tipo_gestion = Tipo_Gestion.objects.get(id=id_tipo)
        except Exception as e:
            tipo_gestion = None

    resultado = tipo_gestion.resultados.all()
    data = serializers.serialize("json", resultado)
    return HttpResponse(data, content_type='application/json')
