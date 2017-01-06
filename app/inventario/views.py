import json

from app.dbmanager import *
from django.core import serializers
from django.db.models import Max
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from app.html_to_pdf import render_to_pdf
from app.models import *


# region PRODUCTOS
class catalogo_productos(TemplateView):
    template_name = "inventario/productos.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        return super(catalogo_productos, self).render_to_response(context)


@csrf_exempt
def get_productos(request):
    data = []
    filtro = request.GET.get('q')
    if not filtro:
    # productos = Producto.objects.values('codigo', 'nombre', 'precio', 'imagen', 'categoria', 'marca').distinct()
        productos = local_sql_exec('SELECT DISTINCT codigo, nombre, precio, imagen, marca, ' +
                               '(select sum(existencia) from inventario_bodega_detalle where producto_id in ' +
                               '(select p.id from inventario_producto p where  p.codigo =p1.codigo)) as cantidad ' +
                               'FROM inventario_producto p1 INNER  JOIN inventario_producto_categoria ' +
                               'on p1.categoria_id=inventario_producto_categoria.id ' +
                               'INNER JOIN inventario_producto_marca ' +
                               'on p1.marca_id=inventario_producto_marca.id LIMIT 100')
    else:
        productos = local_sql_exec('SELECT DISTINCT codigo, nombre, precio, imagen, marca, ' +
                                   '(select sum(existencia) from inventario_bodega_detalle where producto_id in ' +
                                   '(select p.id from inventario_producto p where  p.codigo =p1.codigo)) as cantidad ' +
                                   'FROM inventario_producto p1 INNER  JOIN inventario_producto_categoria ' +
                                   'on p1.categoria_id=inventario_producto_categoria.id ' +
                                   'INNER JOIN inventario_producto_marca ' +
                                   'on p1.marca_id=inventario_producto_marca.id ' +
                                   'WHERE codigo ILIKE \'%' + filtro + '%\' OR nombre ILIKE \'%' + filtro + '%\' '
                                   'OR marca ILIKE \'%' + filtro + '%\' LIMIT 100')
    if productos:
        for p in productos:
            pro = {'codigo': p.codigo,
                   'nombre': p.nombre,
                   'precio': p.precio,
                   'marca': p.marca,
                   'existencia': p.cantidad,
                   'imagen': "/media/" + p.imagen if p.imagen != "" else "/media/foto-no-disponible.jpg",}
            data.append(pro)
        # data = serializers.serialize('json', productos)
        # struct = json.loads(data)
        data = json.dumps(data)
    else:
        data = None
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_productos_autocomplete(request):

    query = request.POST.get('query')
    data = []
    if query:
        # productos = Producto.objects.values('codigo', 'nombre', 'precio', 'imagen', 'categoria', 'marca').distinct()
        productos = local_sql_exec('SELECT DISTINCT p1.id, codigo, nombre, precio, imagen, marca, ' +
                                   '(select sum(existencia) from inventario_bodega_detalle where producto_id in ' +
                                   '(select p.id from inventario_producto p where  p.codigo =p1.codigo)) as cantidad, ' +
                                   'ibd.id as id_detalle ' +
                                   'FROM inventario_producto p1 INNER  JOIN inventario_producto_categoria ' +
                                   'on p1.categoria_id=inventario_producto_categoria.id ' +
                                   'INNER JOIN inventario_producto_marca ' +
                                   'on p1.marca_id=inventario_producto_marca.id ' +
                                   'INNER JOIN inventario_bodega_detalle ibd on p1.id = ibd.producto_id  '
                                   'WHERE codigo ILIKE \'%' + query + '%\' OR nombre ILIKE \'%' + query + '%\' ' +
                                   'AND (select sum(existencia) from inventario_bodega_detalle where producto_id in ' +
                                   '(select p.id from inventario_producto p where  p.codigo =p1.codigo)) >0 '
                                   'OR marca ILIKE \'%' + query + '%\' LIMIT 20')
        if productos:
            for p in productos:
                pro = {'value': p.id,
                       'text': p.nombre + "; " + p.marca + "; " + str(p.precio),
                       'imagen': "/media/" + p.imagen if p.imagen != "" else "/media/foto-no-disponible.jpg",
                       'id_detalle': p.id_detalle,
                       'nombre': p.nombre,
                       'marca': p.marca,
                       'precio': p.precio,
                       'existencia': p.cantidad}
                data.append(pro)
            data = json.dumps(data)
        else:
            productos = local_sql_exec('SELECT DISTINCT p1.id, codigo, nombre, precio, imagen, marca, serie, ' +
                                       '(select sum(existencia) from inventario_bodega_detalle where producto_id in ' +
                                       '(select p.id from inventario_producto p where  p.codigo =p1.codigo)) as cantidad, ' +
                                       'ibd.id as id_detalle ' +
                                       'FROM inventario_producto p1 INNER  JOIN inventario_producto_categoria ' +
                                       'on p1.categoria_id=inventario_producto_categoria.id ' +
                                       'INNER JOIN inventario_producto_marca ' +
                                       'on p1.marca_id=inventario_producto_marca.id ' +
                                       'INNER JOIN inventario_bodega_detalle ibd on p1.id = ibd.producto_id  '
                                       'WHERE codigo ILIKE \'%' + query + '%\' OR nombre ILIKE \'%' + query + '%\' ' +
                                       'OR serie ILIKE \'%' + query + '%\'' +
                                       'AND (select sum(existencia) from inventario_bodega_detalle where producto_id in ' +
                                       '(select p.id from inventario_producto p where  p.codigo =p1.codigo)) >0 '
                                       'OR marca ILIKE \'%' + query + '%\' LIMIT 20')
            if productos:
                for p in productos:
                    pro = {'value': p.id,
                           'text': p.nombre + "; " + p.marca + "; " + str(p.precio),
                           'imagen': "/media/" + p.imagen if p.imagen != "" else "/media/foto-no-disponible.jpg",
                           'id_detalle': p.id_detalle,
                           'nombre': p.nombre,
                           'marca': p.marca,
                           'precio': p.precio,
                           'existencia': p.cantidad}
                    data.append(pro)
                data = json.dumps(data)
            else:
                data = None
    else:
        data = None
    return HttpResponse(data, content_type='application/json')


# endregion

# region FACTURACION
class facturacion(TemplateView):
    template_name = "inventario/facturacion.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(facturacion, self).render_to_response(context)


def render_listado_factura(request):
    facturas = Factura.objects.all()
    html = render_to_string('inventario/partial/_facturas.html', {'facturas': facturas})
    return HttpResponse(html)


@csrf_exempt
def render_listado_factura_select(request):
    id_cliente = request.POST.get('id_cliente')
    if not id_cliente:
        return
    else:
        try:
            cliente = Cliente.objects.get(id=id_cliente)
        except:
            cliente = None

        if not cliente:
            return
        else:
            facturas = Factura.objects.filter(cliente=cliente, anulada=False)
            html = render_to_string('cartera/partial/_facturas_select.html', {'facturas': facturas})
            return HttpResponse(html)


def render_nueva_factura(request):
    vendedores = Vendedor.objects.filter(activo=True)
    clientes = Cliente.objects.all()
    vendedor = request.user
    html = render_to_string('inventario/partial/_factura.html',
                            {'vendedores': vendedores,
                             'clientes': clientes,
                             'actual_vendedor': vendedor})

    return HttpResponse(html)


@csrf_exempt
def add_nueva_factura(request):
    data = []
    obj_json = {}
    id_cliente = request.POST.get('cliente')
    detalles = request.POST.getlist('id')
    cantidades = request.POST.getlist('cantidad')

    try:
        cliente = Cliente.objects.get(id=id_cliente)
    except:
        cliente = None

    vendedor = request.user  # User.objects.get(id=id_vendedor) HAY QUE HACER QUE EL VENDEDOR SE SELECCIONE DE UNA LISTA
    try:
        no_fac = int(Pedido.objects.all().aggregate(Max('no_fac'))['no_fac__max'])
    except:
        no_fac = 1

    moneda = Moneda.objects.get(principal=True)

    factura = Factura.objects.create(
        no_fac=no_fac,
        cliente=cliente,
        stotal=0,
        impuesto=0,
        total=0,
        usuario_creacion=vendedor,
        moneda=moneda,
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


class facturar(TemplateView):
    template_name = "inventario/facturar.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(facturar, self).render_to_response(context)


# endregion


def render_listado_producto(request):
    bodega_detalles = Bodega_Detalle.objects.all()
    html = render_to_string('inventario/partial/_productos.html', {'bodega_detalles': bodega_detalles})
    return HttpResponse(html)


# region PEDIDOS
class proformas(TemplateView):
    template_name = "inventario/proformas.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(proformas, self).render_to_response(context)


def render_listado_pedido(request):
    pedidos = Pedido.objects.filter(usuario_creacion=request.user, cerrado=False).order_by('-no_pedido')
    html = render_to_string('inventario/partial/_pedidos.html', {'pedidos': pedidos})
    return HttpResponse(html)


def render_nuevo_pedido(request):
    vendedores = Vendedor.objects.filter(activo=True)
    clientes = Cliente.objects.all()
    vendedor = Vendedor.objects.get(usuario=request.user)
    html = render_to_string('inventario/partial/_pedido.html',
                            {'vendedores': vendedores,
                             'clientes': clientes,
                             'actual_vendedor': vendedor})
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
                no_pedido = next_pedido()
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


# endregion

# region RECIBOS PROVICIONALES
class recibos_provicionales(TemplateView):
    template_name = "cartera/recibos_provicionales.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super(recibos_provicionales, self).render_to_response(context)


def render_listado_recibo(request):
    recibos = Recibo_Provicional.objects.filter(usuario_creacion=request.user, cerrado=False).order_by('-no_recibo')
    html = render_to_string('cartera/partial/_recibos_provicionales.html', {'recibos': recibos})
    return HttpResponse(html)


@csrf_exempt
def render_nuevo_recibo(request):
    user = User.objects.get(id=request.GET.get('user', ''))
    vendedor = Vendedor.objects.get(usuario=user)
    clientes = Cliente.objects.all()
    formas_pago = Forma_Pago.objects.filter(activo=True)
    no_recibo = get_no_recibo(user)
    html = render_to_string('cartera/partial/_recibo_provicional.html', {'vendedor': vendedor,
                                                                         'clientes': clientes,
                                                                         'formas_pago': formas_pago,
                                                                         'no_recibo': no_recibo})
    return HttpResponse(html)


@csrf_exempt
def add_nuevo_recibo(request):
    data = []
    obj_json = {}
    id_cliente = request.POST.get('cliente')
    monto = request.POST.get('monto')
    comentario = request.POST.get('comentario')
    id_forma_pago = request.POST.get('forma_pago')
    fecha_pos_cambio_ck = request.POST.get('fecha_pos_cambio_ck')
    referencia = request.POST.get('referencia')
    facturas = request.POST.getlist('factura')

    cancelacion = request.POST.get('cancelacion')

    if not cancelacion:
        cancelacion = False

    if cancelacion == 'on':
        cancelacion = True
    else:
        cancelacion = False

    if not referencia:
        referencia = ""

    if not id_cliente:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Cliente invalido"
    elif not id_forma_pago:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Forma de pago invalida"
    elif not monto:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Monto Invalido"
    else:
        try:
            cliente = Cliente.objects.get(id=id_cliente)
        except:
            cliente = None

        try:
            forma_pago = Forma_Pago.objects.get(id=id_forma_pago)
        except:
            forma_pago = None

        if not cliente:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Cliente no encontrado"
        elif not forma_pago:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Forma de pago no encontrada"
        else:
            try:
                no_recibo = int(Recibo_Provicional.objects.all().aggregate(Max('no_recibo'))['no_recibo__max']) + 1
            except:
                no_recibo = 1

            recibo = Recibo_Provicional.objects.create(
                cliente=cliente,
                no_recibo=no_recibo,
                monto=monto,
                forma_pago=forma_pago,
                cancelacion=cancelacion,
                usuario_creacion=request.user,
                comentario=comentario
                #fecha_cobro_ck=fecha_pos_cambio_ck
            )
            recibo.referencia = referencia
            recibo.save()

            obj_json['code'] = 200
            obj_json['mensaje'] = "Recibo registrado exitosamente!"
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


def mostrar_recibo_provicional_pdf(request):
    data = []
    obj_json = {}
    id_recibo = request.GET.get('id_recibo')
    if not id_recibo:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Pedido invalido"
    else:
        try:
            recibo = Recibo_Provicional.objects.get(id=id_recibo)
        except:
            recibo = None

        if not recibo:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Pedido no encontrado"
        else:
            return render_to_pdf(
                'cartera/plantilla_recibo_provicional.html',
                {
                    'pagesize': 'A4',
                    'recibo': recibo,
                }
            )

        data.append(obj_json)
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')


@csrf_exempt
def execute_import_inventario(request):
    data = []
    obj_json = {}

    items = Import_Imventario.objects.all()
    for item in items:
        item.save()

    obj_json['code'] = 200
    obj_json['mensaje'] = "Importacion exitosa!"
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')

def anular_recibo(request):
    data = []
    obj_json = {}
    id_recibo = request.POST.get('id_recibo')
    if not id_recibo:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Recibo invalido"
    else:
        try:
            recibo = Recibo_Provicional.objects.get(id=id_recibo)
        except:
            recibo = None

        if not recibo:
            obj_json['code'] = 400
            obj_json['mensaje'] = "Recibo no encontrado"
        else:
            recibo.anulado = True
            recibo.save()
            obj_json['code'] = 200
            obj_json['mensaje'] = "Recibo anulado!"
    data.append(obj_json)
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')
