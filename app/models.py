from __future__ import unicode_literals

from django.db import models


class Import(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)
    nombre = models.CharField(max_length=165)
    identificacion = models.CharField(max_length=14)
    telefono = models.CharField(max_length=50)
    direccion = models.TextField(max_length=600)
    monto = models.FloatField()
    fecha = models.DateField()

    class Meta:
        verbose_name = "opcion"
        verbose_name_plural = "importacion de datos"

    def get_empresa(self):
        o = None
        try:
            o = Empresa.objects.get(numero_ruc=self.numero_ruc)
        except:
            o, create = Empresa.objects.get_or_create(
                numero_ruc=self.numero_ruc,
                razon_social=self.razon_social)
        return o

    def get_cliente(self):
        o = None
        try:
            o = Cliente.objects.get(identificacion=self.identificacion)
        except:
            o, create = Cliente.objects.get_or_create(
                identificacion=self.identificacion,
                nombre=self.nombre, telefono=self.telefono,
                direccion=self.direccion)
        return o

    def save(self, *args, **kwargs):
        Factura(cliente=self.get_cliente(), empresa=self.get_empresa(),
            monto=self.monto, fecha=self.fecha).save()

class Empresa(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)

    def __unicode__(self):
        return "%s-%s" % (self.numero_ruc, self.razon_social)


class Cliente(models.Model):
    identificacion = models.CharField(max_length=14)
    nombre = models.CharField(max_length=165)
    telefono = models.CharField(max_length=50)
    direccion = models.TextField(max_length=600)

    def __unicode__(self):
        return "%s-%s" % (self.identificacion, self.nombre)


class Factura(models.Model):
    empresa = models.ForeignKey(Empresa)
    cliente = models.ForeignKey(Cliente)
    monto = models.FloatField()
    fecha = models.DateField()

    def __unicode__(self):
        return "%s-%s" % (self.cliente, str(self.monto))
