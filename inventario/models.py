from __future__ import unicode_literals

from string import upper

from app.numero_letras import numero_a_letras
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

from app.models import *


def get_media_url(model, filename):
    clase = model.__class__.__name__
    code = str(model.id)
    return '%s/%s/%s' % (clase, code, filename)


class Import_Imventario(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)
    producto_codigo = models.CharField(max_length=10)
    producto_serie = models.CharField(max_length=50)
    producto_nombre = models.CharField(max_length=200)
    producto_existencia = models.FloatField(null=False, default=0)
    producto_costo = models.FloatField(null=False, default=0)
    producto_precio = models.FloatField(null=False, default=0)
    producto_marca = models.CharField(max_length=100)
    producto_categoria = models.CharField(max_length=100)
    producto_medida = models.CharField(max_length=100)
    bodega = models.CharField(max_length=100)

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

    def get_bodega(self):
        o = None
        try:
            o = Bodega.objects.get(nombre=self.bodega)
        except:
            o, create = Bodega.objects.get_or_create(
                nombre=self.bodega)
        return o

    def get_producto(self):
        producto = None
        try:
            producto = Producto.objects.get(codigo=self.producto_codigo, serie=self.producto_serie)
            producto.costo_promedio = (producto.costo_promedio + self.producto_costo) / 2
            producto.save()
        except:
            producto, create = Producto.objects.get_or_create(
                codigo=self.producto_codigo,
                serie=self.producto_serie,
                nombre=self.producto_nombre,
                categoria=self.get_categoria(),
                empresa=self.get_empresa(),
                medida=self.get_medida(),
                marca=self.get_marca(),
                costo_promedio=self.producto_costo,
                precio=self.producto_precio)

        # REGISTRO DE LA EXISTENCIA
        bodega = self.get_bodega()
        detalle = None
        try:
            detalle = Bodega_Detalle.objects.get(bodega=bodega, producto=producto)
            detalle.existencia += self.producto_existencia
            detalle.save()
        except:
            detalle, create = Bodega_Detalle.objects.get_or_create(bodega=bodega, producto=producto,
                                                                   existencia=self.producto_existencia)

        return producto

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
    serie = models.CharField(max_length=50)  # REGISTRO DE PRODUCTOS POR SERIE
    nombre = models.CharField(max_length=200)
    costo_promedio = models.FloatField(default=0, null=False)
    precio = models.FloatField(default=0, null=False)
    categoria = models.ForeignKey(Producto_Categoria)
    medida = models.ForeignKey(Producto_Medida)
    marca = models.ForeignKey(Producto_Marca)
    empresa = models.ForeignKey(Empresa)
    imagen = models.ImageField(upload_to=get_media_url, null=True, blank=True)

    class Meta:
        verbose_name = "opcion"
        verbose_name_plural = "Productos del Invetnario"

    def __unicode__(self):
        return "%s %s" % (self.codigo, self.nombre)


class Bodega(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    encargado = models.ForeignKey(User, null=True)

    def __unicode__(self):
        return "%s" % (self.nombre)


class Bodega_Detalle(models.Model):
    bodega = models.ForeignKey(Bodega, null=False)
    producto = models.ForeignKey(Producto, null=False)
    existencia = models.FloatField(default=0.0, null=False)

    class Meta:
        verbose_name = "opcion"
        verbose_name_plural = "Detalle de bodegas"

    def __unicode__(self):
        return "%s %s-%s" % (self.bodega.nombre, self.producto, self.existencia)

    def factura_detalles(self):
        return Factura_Detalle.objects.filter(bodega=self.bodega,
                                              producto=self.producto)  # hace falta validar que la factura no este anulada

    def cant_disponible(self):
        if self.factura_detalles():
            return self.existencia - self.factura_detalles().aggregate(Sum('cantidad'))['cantidad__sum']
        else:
            return self.existencia


class Forma_Pago(models.Model):
    forma_pago = models.CharField(max_length=50)
    activo = models.BooleanField(null=False, default=True)

    def __unicode__(self):
        return self.forma_pago


class Factura(models.Model):
    no_fac = models.CharField(max_length=10)
    serie = models.CharField(max_length=2, default="A")
    cliente = models.ForeignKey(Cliente, null=False, related_name="inventario_factura_cliente")
    stotal = models.FloatField(null=False)
    impuesto = models.FloatField(null=False)
    total = models.FloatField(null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="factura_usuario_creacion")
    anulada = models.BooleanField(default=False)
    fecha_anulacion = models.DateTimeField(null=True)
    usuario_anulacion = models.ForeignKey(User, null=True, related_name="factura_usuario_anulacion")
    comentario = models.CharField(max_length=200, null=True)
    fecha_vence = models.DateTimeField(null=True, blank=True)


class Factura_Detalle(models.Model):
    factura = models.ForeignKey(Factura, null=False)
    producto = models.ForeignKey(Producto, null=False)
    bodega = models.ForeignKey(Bodega, null=False)
    cantidad = models.FloatField(null=False)
    valor = models.FloatField(null=False)
    entregado = models.BooleanField(default=False, null=False)


class Factura_Abono(models.Model):
    factura = models.ForeignKey(Factura)
    monto_abono = models.FloatField(null=False)
    fecha_abono = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, null=True)


class Pedido(models.Model):
    no_pedido = models.CharField(max_length=10)
    cliente = models.ForeignKey(Cliente, null=False)
    vendedor = models.ForeignKey(Vendedor, null=False, related_name="pedido_usuario_vendedor")
    stotal = models.FloatField(null=False)
    impuesto = models.FloatField(null=False)
    total = models.FloatField(null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="pedido_usuario_creacion")
    anulado = models.BooleanField(default=False)
    fecha_anulacion = models.DateTimeField(null=True)
    usuario_anulacion = models.ForeignKey(User, null=True, related_name="pedido_usuario_anulacion")
    comentario = models.CharField(max_length=200, null=True)


class Pedido_Detalle(models.Model):
    pedido = models.ForeignKey(Pedido, null=False)
    producto = models.ForeignKey(Producto, null=False)
    bodega = models.ForeignKey(Bodega, null=False)
    cantidad = models.FloatField(null=False)
    valor = models.FloatField(null=False)


class Recibo_Provicional(models.Model):
    no_recibo = models.IntegerField(null=False)
    cliente = models.ForeignKey(Cliente)
    monto = models.FloatField(null=False)
    forma_pago = models.ForeignKey(Forma_Pago)
    cancelacion = models.BooleanField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="Recibo_Provicional_User_Creacion")
    comentario = models.CharField(max_length=600, null=True)
    fecha_cobro_ck = models.DateTimeField(null=True, blank=True)

    def monto_letras(self):
        return "%s NETOS" % (upper(numero_a_letras(self.monto)))
