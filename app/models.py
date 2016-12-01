from __future__ import unicode_literals

import datetime
from string import upper

from app.numero_letras import numero_a_letras
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

User.add_to_class('foto', models.ImageField(upload_to="", null=True))


def get_media_url(self, filename):
    clase = self.__class__.__name__
    code = str(self.id)
    return '%s/%s/%s' % (clase, code, filename)

# region OTROS
class Import(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)
    nombre = models.CharField(max_length=165)
    identificacion = models.CharField(max_length=14)
    telefono = models.CharField(max_length=50)
    celular = models.CharField(max_length=50)
    direccion = models.TextField(max_length=600)
    contacto = models.CharField(max_length=150)
    nodoc = models.CharField(max_length=15, null=True, verbose_name="numero de documento")
    descripcion = models.CharField(max_length=500)
    monto = models.FloatField()
    impuesto = models.FloatField()
    total = models.FloatField()
    abono = models.FloatField()
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
            o = Cliente.objects.get(identificacion=self.identificacion, nombre=self.nombre,
                                    empresa=self.get_empresa())
        except:
            o, create = Cliente.objects.get_or_create(
                empresa=self.get_empresa(),
                identificacion=self.identificacion,
                nombre=self.nombre,
                telefono=self.telefono,
                celular=self.celular,
                direccion=self.direccion,
                contacto=self.contacto)
        return o

    def save(self, *args, **kwargs):
        li = []
        li.append(kwargs.pop('user', 1))
        usuario = User.objects.get(id=li[0])

        factura, create = Documento_Cobro.objects.get_or_create(cliente=self.get_cliente(), empresa=self.get_empresa(),
                                                                monto=self.monto, impuesto=self.impuesto,
                                                                total=self.total,
                                                                fecha=self.fecha, nodoc=self.nodoc,
                                                                descripcion=self.descripcion)

        if self.abono > 0:
            if usuario:
                now = datetime.datetime.now()
                Documento_Abono.objects.create(factura=factura, monto_abono=self.abono,
                                               fecha_abono=now, usuario=usuario)


class Empresa(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)

    def __unicode__(self):
        return "%s-%s" % (self.numero_ruc, self.razon_social)


class Gestion_Resultado(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nombre


class Tipo_Gestion(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    resultados = models.ManyToManyField(Gestion_Resultado, blank=True)

    def __unicode__(self):
        return self.nombre


class Gestion(models.Model):
    tipo_gestion = models.ForeignKey(Tipo_Gestion)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, null=True, related_name='usuario_creacion')
    fecha_completa = models.DateTimeField(null=True)
    usuario_completa = models.ForeignKey(User, null=True, blank=True, related_name='usuario_completa')
    resultado = models.ForeignKey(Gestion_Resultado, null=True, blank=True)
    descripcion = models.TextField(max_length=400, null=True)
    descripcion_resultado = models.CharField(max_length=400, null=True)
    programacion = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.tipo_gestion.nombre, self.descripcion)


class Comentario(models.Model):
    descripcion = models.CharField(max_length=400)
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User)


class Cliente(models.Model):
    identificacion = models.CharField(max_length=14)
    nombre = models.CharField(max_length=165)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    celular = models.CharField(max_length=50, null=True, blank=True)
    contacto = models.CharField(max_length=150, null=True, blank=True)
    direccion = models.TextField(max_length=600, null=True, blank=True)
    gestiones = models.ManyToManyField(Gestion)
    comentarios = models.ManyToManyField(Comentario)
    empresa = models.ForeignKey(Empresa, null=False)

    def __unicode__(self):
        return "%s-%s" % (self.identificacion, self.nombre)

    def documentos(self):
        return Documento_Cobro.objects.filter(cliente=self)

    def documentos_abonos(self):
        return Documento_Abono.objects.filter(documento__in=self.documentos())

    def saldo_cliente(self):
        if self.documentos() and self.documentos_abonos():
            return self.documentos().aggregate(Sum('total'))['total__sum'] - \
                   self.documentos_abonos().aggregate(Sum('monto_abono'))['monto_abono__sum']
        elif self.documentos():
            return self.documentos().aggregate(Sum('total'))['total__sum']
        else:
            return 0.0


class Vendedor(models.Model):
    usuario = models.ForeignKey(User, null=False)
    activo = models.BooleanField(default=True, null=False)

    def __unicode__(self):
        return '%s | %s' % (self.usuario.get_full_name(), self.usuario.get_username())


class Documento_Cobro(models.Model):
    nodoc = models.CharField(max_length=15, null=True, verbose_name="numero de documento")
    descripcion = models.CharField(max_length=300, null=True, blank=True)
    empresa = models.ForeignKey(Empresa)
    cliente = models.ForeignKey(Cliente)
    monto = models.FloatField()
    impuesto = models.FloatField()
    total = models.FloatField()
    fecha = models.DateField()
    fecha_vence = models.DateField(null=True, blank=True)
    pagada = models.BooleanField(default=False)

    @property
    def abonos(self):
        return Documento_Abono.objects.all().filter(documento=self)

    @property
    def saldo_factura(self):
        '''
        esta funcion regresa el saldo dela facturara (monto) menos todos los abonos a la factura
        '''
        if Documento_Abono.objects.all().filter(documento=self):
            return self.total - Documento_Abono.objects.all().filter(documento=self).aggregate(Sum('monto_abono'))[
                'monto_abono__sum']
        else:
            return self.total

    @staticmethod
    def facturas_pendientes(cliente):
        factresult = []
        facturas = Documento_Cobro.objects.all().filter(cliente=cliente)
        for factura in facturas:
            if factura.saldo_factura > 0:
                factresult.append(factura)
        return factresult


class Documento_Abono(models.Model):
    documento = models.ForeignKey(Documento_Cobro)
    monto_abono = models.FloatField(null=False)
    fecha_abono = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, null=True)


# endregion
#region CONTABILIDAD

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

#endregion
# region INVENTARIO

class base_inventario(models.Model):
    class Meta:
        app_label = "inventario"
        abstract = True


class Import_Imventario(base_inventario):
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


class Producto_Marca(base_inventario):
    marca = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % (self.marca)


class Producto_Categoria(base_inventario):
    categoria = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % (self.categoria)


class Producto_Medida(base_inventario):
    medida = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % (self.medida)


class Producto(base_inventario):
    codigo = models.CharField(max_length=10)
    serie = models.CharField(max_length=50, null=True, blank=True)  # REGISTRO DE PRODUCTOS POR SERIE
    nombre = models.CharField(max_length=200)
    costo_promedio = models.FloatField(default=0, null=False)
    precio = models.FloatField(default=0, null=False)
    categoria = models.ForeignKey(Producto_Categoria)
    medida = models.ForeignKey(Producto_Medida)
    marca = models.ForeignKey(Producto_Marca)
    empresa = models.ForeignKey(Empresa)
    imagen = models.ImageField(upload_to=get_media_url, null=True, blank=True)
    activo = models.BooleanField(default=True, null=False)

    class Meta:
        app_label = "inventario"
        verbose_name = "opcion"
        verbose_name_plural = "Productos del Invetnario"

    def __unicode__(self):
        return "%s %s" % (self.codigo, self.nombre)

    def imagen_url(self):
        if self.imagen:
            return self.imagen.url
        else:
            return "/media/foto-no-disponible.jpg"


class Bodega(base_inventario):
    nombre = models.CharField(max_length=100, null=False)
    encargado = models.ForeignKey(User, null=True)

    def __unicode__(self):
        return "%s" % (self.nombre)

    class Meta:
        app_label = "inventario"



class Bodega_Detalle(base_inventario):
    bodega = models.ForeignKey(Bodega, null=False)
    producto = models.ForeignKey(Producto, null=False)
    existencia = models.FloatField(default=0.0, null=False)


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


class Forma_Pago(base_inventario):
    forma_pago = models.CharField(max_length=50)
    activo = models.BooleanField(null=False, default=True)

    def __unicode__(self):
        return self.forma_pago


class Factura(base_inventario):
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
    moneda = models.ForeignKey(Moneda)


class Factura_Detalle(base_inventario):
    factura = models.ForeignKey(Factura, null=False)
    producto = models.ForeignKey(Producto, null=False)
    bodega = models.ForeignKey(Bodega, null=False)
    cantidad = models.FloatField(null=False)
    valor = models.FloatField(null=False)
    entregado = models.BooleanField(default=False, null=False)


class Factura_Abono(base_inventario):
    factura = models.ForeignKey(Factura)
    monto_abono = models.FloatField(null=False)
    fecha_abono = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, null=True)


class Pedido(base_inventario):
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


class Pedido_Detalle(base_inventario):
    pedido = models.ForeignKey(Pedido, null=False)
    producto = models.ForeignKey(Producto, null=False)
    bodega = models.ForeignKey(Bodega, null=False)
    cantidad = models.FloatField(null=False)
    valor = models.FloatField(null=False)


class Recibo_Provicional(base_inventario):
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


# endregion


