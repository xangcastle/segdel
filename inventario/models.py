from __future__ import unicode_literals

from django.db import models

from app.models import Empresa


class Import_Imventario(models.Model):
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

    def get_medida(self):
        o = None
        try:
            o = Producto_Medida.objects.get(medida=self.producto_medida)
        except:
            o, create = Producto_Medida.objects.get_or_create(
                medida=self.producto_medida)
        return o

    def get_marca(self):
        o = None
        try:
            o = Producto_Marca.objects.get(medida=self.producto_marca)
        except:
            o, create = Producto_Marca.objects.get_or_create(
                marca=self.producto_marca)
        return o

    def get_categoria(self):
        o = None
        try:
            o = Producto_Categoria.objects.get(categoria=self.producto_categoria)
        except:
            o, create = Producto_Categoria.objects.get_or_create(
                categoria=self.producto_categoria)
        return o

    def get_producto(self):
        o = None
        try:
            o = Producto.objects.get(codigo=self.producto_codigo)
        except:
            o, create = Producto.objects.get_or_create(
                codigo=self.producto_codigo,
                nombre=self.producto_nombre,
                categoria=self.get_categoria(),
                empresa=self.get_empresa(),
                medida=self.get_medida(),
                marca=self.get_marca(),)
        return o

    def save(self, *args, **kwargs):
        self.get_producto()

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