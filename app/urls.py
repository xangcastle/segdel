from django.conf.urls import url
from .views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(index.as_view()),
        name='index'),
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




]
