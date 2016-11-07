import json

from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from app.html_to_pdf import render_to_pdf
from inventario.models import *


class facturacion(TemplateView):
    template_name = "inventario/facturacion.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        # context['clientes'] = Fa.objects.all()
        return super(facturacion, self).render_to_response(context)


def render_listado_factura(request):
    facturas = Factura.objects.all()
    html = render_to_string('inventario/partial/_facturas.html', {'facturas': facturas})
    return HttpResponse(html)


def render_nueva_factura(request):
    facturas = Factura.objects.all()
    html = render_to_string('inventario/partial/_factura.html')
    return HttpResponse(html)


@csrf_exempt
def add_nueva_factura(request):
    data = []
    obj_json = {}
    cliente = request.POST.get('cliente')
    id_vendedor = request.POST.get('vendedor')
    detalles = request.POST.getlist('id')
    cantidades = request.POST.getlist('cantidad')

    vendedor = request.user  # User.objects.get(id=id_vendedor) HAY QUE HACER QUE EL VENDEDOR SE SELECCIONE DE UNA LISTA
    try:
        no_fac = float(Factura.objects.all().aggregate(Max('no_fac')))
    except:
        no_fac = 1

    factura = Factura.objects.create(
        no_fac=no_fac,
        cliente=cliente,
        stotal=0,
        impuesto=0,
        total=0,
        usuario_creacion=vendedor
    )
    factura.save()
    stotal = 0
    for i in range(len(detalles)):
        id_detalle = int(detalles[i])
        try:
            detalle = Bodega_Detalle.objects.get(id=id_detalle)
        except:
            detalle = None

        factura_detalle = Factura_Detalle.objects.create(
            factura=factura,
            producto=detalle.producto,
            bodega=detalle.bodega,
            cantidad=float(cantidades[i]),
            valor=float(cantidades[i]) * detalle.producto.precio
        )
        factura_detalle.save()
        stotal += factura_detalle.valor

    factura.stotal = stotal
    factura.impuesto = stotal * 0.15
    factura.total = stotal + (stotal * 0.15)
    factura.save()

    obj_json['code'] = 200
    obj_json['mensaje'] = "Factura registrada exitosamente!"
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


def anular_nueva_factura(request):
    data = []
    obj_json = {}
    id_factura = request.POST.get('id_factura')
    if not id_factura:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Factura invalida"
    else:
        try:
            factura = Factura.objects.get(id=id_factura)
        except:
            factura = None

        if not factura:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Factura no encontrada"
        else:
            factura.anulada = True
            factura.save()
            obj_json['code'] = 200
            obj_json['mensaje'] = "Factura anulada!"
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


def mostrar_factura_pdf(request):
    data = []
    obj_json = {}
    id_factura = request.GET.get('id_factura')
    if not id_factura:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Factura invalida"
    else:
        try:
            factura = Factura.objects.get(id=id_factura)
        except:
            factura = None

        if not factura:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Factura no encontrada"
        else:
            factura_detalle = Factura_Detalle.objects.filter(factura=factura)
            return render_to_pdf(
                'inventario/plantilla_factura.html',
                {
                    'pagesize': 'A4',
                    'factura': factura,
                    'factura_detalle': factura_detalle,
                }
            )

        data.append(obj_json)
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')


def render_listado_producto(request):
    bodega_detalles = Bodega_Detalle.objects.all()
    html = render_to_string('inventario/partial/_productos.html', {'bodega_detalles': bodega_detalles})
    return HttpResponse(html)
