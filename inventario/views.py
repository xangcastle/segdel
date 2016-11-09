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
        no_fac = int(Pedido.objects.all().aggregate(Max('no_fac'))['no_fac__max'])
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



class proformas(TemplateView):
    template_name = "inventario/proformas.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(proformas, self).render_to_response(context)


def render_listado_pedido(request):
    pedidos = Pedido.objects.all()
    html = render_to_string('inventario/partial/_pedidos.html', {'pedidos': pedidos})
    return HttpResponse(html)

def render_nuevo_pedido(request):
    vendedores = Vendedor.objects.filter(activo=True)
    clientes = Cliente.objects.all()
    html = render_to_string('inventario/partial/_pedido.html', {'vendedores': vendedores, 'clientes': clientes})
    return HttpResponse(html)

@csrf_exempt
def add_nuevo_pedido(request):
    data = []
    obj_json = {}
    id_cliente = request.POST.get('cliente')
    id_vendedor = request.POST.get('vendedor')
    detalles = request.POST.getlist('id')
    cantidades = request.POST.getlist('cantidad')
    comentario = request.POST.get('comentario')

    if not id_vendedor:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Vendedor invalido"
    elif not id_cliente:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Cliente invalido"
    else:
        try:
            vendedor = Vendedor.objects.get(id=id_vendedor)
        except:
            vendedor = None
        try:
            cliente = Cliente.objects.get(id=id_cliente)
        except:
            cliente = None

        if not vendedor:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Vendedor no encontrado"
        elif not cliente:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Cliente no encontrado"
        else:
            try:
                no_pedido = int(Pedido.objects.all().aggregate(Max('no_pedido'))['no_pedido__max']) + 1
            except:
                no_pedido = 1

            pedido = Pedido.objects.create(
                no_pedido=no_pedido,
                cliente=cliente,
                vendedor=vendedor,
                comentario=comentario,
                stotal=0,
                impuesto=0,
                total=0,
                usuario_creacion=request.user
            )
            pedido.save()
            stotal = 0
            for i in range(len(detalles)):
                id_detalle = int(detalles[i])
                try:
                    detalle = Bodega_Detalle.objects.get(id=id_detalle)
                except:
                    detalle = None

                pedido_detalle = Pedido_Detalle.objects.create(
                    pedido=pedido,
                    producto=detalle.producto,
                    bodega=detalle.bodega,
                    cantidad=float(cantidades[i]),
                    valor=float(cantidades[i]) * detalle.producto.precio
                )
                pedido_detalle.save()
                stotal += pedido_detalle.valor

            pedido.stotal = stotal
            pedido.impuesto = stotal * 0.15
            pedido.total = stotal + (stotal * 0.15)
            pedido.save()

            obj_json['code'] = 200
            obj_json['mensaje'] = "Pedido registrado exitosamente!"
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


def anular_nuevo_pedido(request):
    data = []
    obj_json = {}
    id_pedido = request.POST.get('id_pedido')
    if not id_pedido:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Pedido invalido"
    else:
        try:
            pedido = Pedido.objects.get(id=id_pedido)
        except:
            pedido = None

        if not pedido:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Pedido no encontrado"
        else:
            pedido.anulado = True
            pedido.save()
            obj_json['code'] = 200
            obj_json['mensaje'] = "Peido anulado!"
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')

def mostrar_pedido_pdf(request):
    data = []
    obj_json = {}
    id_pedido = request.GET.get('id_pedido')
    if not id_pedido:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Pedido invalido"
    else:
        try:
            pedido = Pedido.objects.get(id=id_pedido)
        except:
            pedido = None

        if not pedido:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Pedido no encontrado"
        else:
            pedido_detalle = Pedido_Detalle.objects.filter(pedido=pedido)
            return render_to_pdf(
                'inventario/plantilla_pedido.html',
                {
                    'pagesize': 'A4',
                    'pedido': pedido,
                    'pedido_detalle': pedido_detalle,
                }
            )

        data.append(obj_json)
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')
