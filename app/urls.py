from django.conf.urls import url
from .views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(index.as_view()),
        name='index'),
    url(r'^cobranza/', login_required(cobranza.as_view()),
        name='cobranza'),
]
