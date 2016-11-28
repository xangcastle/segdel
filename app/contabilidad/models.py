from app.models import *
from django.db import models


class base_contabilidad(models.Model):
    class Meta:
        app_label = "contabilidad"
        abstract = True


class Moneda(base_contabilidad):
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=4)
    activo = models.BooleanField(default=True)


class Tipo_Cambio(base_contabilidad):
    moneda = models.ForeignKey(Moneda)
    cambio = models.FloatField(null=False)
    fecha = models.DateField(null=False)
