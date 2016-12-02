from django.conf.urls import include, url

from django.conf import settings
from django.conf.urls.static import static
from inventario.views import *
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^cobranza/', login_required(cobranza.as_view()),
        name='cobranza'),
    url(r'^cobranza_cliente/', login_required(cobranza_cliente.as_view()),
        name='cobranza_cliente'),
    url(r'^add_comentario_cliente/', add_comentario_cliente,
        name='add_comentario_cliente'),
    url(r'^get_comentario_cliente/', get_cliente_comentarios,
        name='get_cliente_comentarios'),
    url(r'^get_facturas_pendientes/', get_facturas_pendientes,
        name='get_facturas_pendientes'),
    url(r'^render_add_abono_factura/', render_add_abono_factura,
        name='render_add_abono_factura'),
    url(r'^add_abono_factura/', add_abono_factura,
        name='add_abono_factura'),
    url(r'^mostrar_estado_cuenta/', mostrar_estado_cuenta,
        name='mostrar_estado_cuenta'),


    url(r'^render_gestiones/', render_gestiones,
        name='render_gestiones'),
    url(r'^get_tipo_gestion_resultado/', get_tipo_gestion_resultado,
        name='get_tipo_gestion_resultado'),
    url(r'^render_add_gestion/', render_add_gestion,
        name='render_add_gestion'),
    url(r'^render_edit_gestion/', render_edit_gestion,
        name='render_edit_gestion'),
    url(r'^render_finish_gestion/', render_finish_gestion,
        name='render_finish_gestion'),
    url(r'^add_new_cliente_gestion/', add_new_cliente_gestion,
        name='add_new_cliente_gestion'),
    url(r'^edit_cliente_gestion/', edit_cliente_gestion,
        name='edit_cliente_gestion'),
    url(r'^finish_cliente_gestion/', finish_cliente_gestion,
        name='finish_cliente_gestion'),

    url(r'^productos/', login_required(catalogo_productos.as_view()),
        name='catalogo_productos'),
    url(r'^get_productos/', login_required(get_productos),
        name='get_productos'),


    url(r'^facturacion/', login_required(facturacion.as_view()),
        name='facturacion'),
    url(r'^facturar/', login_required(facturar.as_view()),
        name='facturar'),

    url(r'^render_listado_factura/', login_required(render_listado_factura),
        name='render_listado_factura'),
    url(r'^render_nueva_factura/', login_required(render_nueva_factura),
        name='render_nueva_factura'),
    url(r'^add_nueva_factura/', login_required(add_nueva_factura),
        name='add_nueva_factura'),
    url(r'^anular_nueva_factura/', login_required(anular_nueva_factura),
        name='anular_nueva_factura'),
    url(r'^mostrar_factura_pdf/', login_required(mostrar_factura_pdf),
        name='mostrar_factura_pdf'),
    url(r'^render_listado_producto/', login_required(render_listado_producto),
        name='render_listado_producto'),

    url(r'^proformas/', login_required(proformas.as_view()),
        name='proformas'),
    url(r'^render_listado_pedido/', login_required(render_listado_pedido),
        name='render_listado_pedido'),
    url(r'^render_nuevo_pedido/', login_required(render_nuevo_pedido),
        name='render_nuevo_pedido'),
    url(r'^add_nuevo_pedido/', login_required(add_nuevo_pedido),
        name='add_nuevo_pedido'),
    url(r'^anular_nuevo_pedido/', login_required(anular_nuevo_pedido),
        name='anular_nuevo_pedido'),
    url(r'^mostrar_pedido_pdf/', login_required(mostrar_pedido_pdf),
        name='mostrar_pedido_pdf'),

    url(r'^lrecibo_provicional/', login_required(recibos_provicionales.as_view()),
        name='lrecibo_provicional'),
    url(r'^render_listado_recibo/', login_required(render_listado_recibo),
        name='render_listado_recibo'),
    url(r'^render_nuevo_recibo/', login_required(render_nuevo_recibo),
        name='render_nuevo_recibo'),
    url(r'^add_nuevo_recibo/', login_required(add_nuevo_recibo),
        name='add_nuevo_recibo'),
    url(r'^mostrar_recibo_provicional_pdf/', login_required(mostrar_recibo_provicional_pdf),
        name='mostrar_recibo_provicional_pdf'),

]
