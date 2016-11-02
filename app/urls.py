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
    url(r'^add_abono_factura/', add_abono_factura,
        name='add_abono_factura'),
]
