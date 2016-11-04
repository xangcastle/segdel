from __future__ import unicode_literals

from django.db import models

class Import(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)
    producto_codigo = models.CharField(max_length=10)
    producto_nombre = models.CharField(max_length=200)
    producto_existencia = models.FloatField()
    producto_marca = models.CharField(max_length=100)
    producto_categoria = models.CharField(max_length=100)
    producto_medida = models.CharField(max_length=100)

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

    def get_producto(self):
        o = None
        try:
            o = Producto.objects.get(codigo=self.producto_codigo)
        except:
            o, create = Producto.objects.get_or_create(
                codigo=self.identificacion,
                nombre=self.nombre,
                categoria=self.telefono,
                empresa=self.get_empresa(),
                medida=self.telefono,
                marca=self.direccion,)
        return o

    def save(self, *args, **kwargs):
        Factura(cliente=self.get_cliente(), empresa=self.get_empresa(),
            monto=self.monto, fecha=self.fecha, nodoc=self.nodoc).save()

class Empresa(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)

    def __unicode__(self):
        return "%s-%s" % (self.numero_ruc, self.razon_social)

class Producto_Marca(models.Model):
    marca = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % (self.marca)

class Producto_Categoria(models.Model):
    categoria = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % (self.categoria)

class Producto_Medida(models.Model):
    medida = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % (self.medida)

class Producto(models.Model):
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Producto_Categoria)
    medida = models.ForeignKey(Producto_Medida)
    marca = models.ForeignKey(Producto_Marca)
    empresa = models.ForeignKey(Empresa)

    def __unicode__(self):
        return "%s" % (self.medida)