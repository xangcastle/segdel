from __future__ import unicode_literals

import datetime
from string import upper

import app
from app.numero_letras import numero_a_letras
from django.db import models
from django.db.models import Sum, Max
from django.contrib.auth.models import User


def format_fecha(fecha):
    return "%s-%s-%s" % (fecha.year, fecha.month, fecha.day)


def get_media_url(self, filename):
    clase = self.__class__.__name__
    code = str(self.id)
    return '%s/%s/%s' % (clase, code, filename)


# region OTROS
class Import(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=20)
    nombre = models.CharField(max_length=165)
    identificacion = models.CharField(max_length=65)
    telefono = models.CharField(max_length=50)
    celular = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.TextField(max_length=600)
    contacto = models.CharField(max_length=150)
    email = models.CharField(max_length=100, null=True, blank=True)
    nodoc = models.CharField(max_length=15, null=True, blank=True, verbose_name="numero de documento")
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    monto = models.FloatField(null=True, blank=True)
    impuesto = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    abono = models.FloatField(null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)

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
        cliente = self.get_cliente()
        empresa = self.get_empresa()
        if not self.impuesto:
            self.impuesto = 0.0
        if self.nodoc:
            documento, create = Documento_Cobro.objects.get_or_create(cliente=cliente, empresa=empresa,
                                                                      monto=self.monto, impuesto=self.impuesto,
                                                                      total=self.total,
                                                                      fecha=self.fecha, nodoc=self.nodoc,
                                                                      descripcion=self.descripcion)

            if self.abono > 0:
                if usuario:
                    now = datetime.datetime.now()
                    Documento_Abono.objects.create(documento=documento, monto_abono=self.abono,
                                                   fecha_abono=now, usuario=usuario)
        self.delete()


class Empresa(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)

    def __unicode__(self):
        return "%s-%s" % (self.numero_ruc, self.razon_social)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to=get_media_url, null=True)
    empresa = models.ForeignKey(Empresa, null=True, blank=True)

    def imagen_url(self):
        if self.foto:
            return self.foto.url
        else:
            return "/media/foto-no-disponible.jpg"

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
    identificacion = models.CharField(max_length=65)
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
    serie = models.CharField(max_length=25, null=True, blank=True, verbose_name="Serie de Recibos")
    numero_inicial = models.PositiveIntegerField(null=True, blank=True, verbose_name="Numero Inicial para los recibos")
    activo = models.BooleanField(default=True, null=False)

    class Meta:
        verbose_name_plural = "vendedores"

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
# region CONTABILIDAD



class Moneda(models.Model):
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=4)
    activo = models.BooleanField(default=True)
    principal = models.BooleanField(default=False)



class Tipo_Cambio(models.Model):
    moneda = models.ForeignKey(Moneda, null=True, blank=True)
    cambio = models.FloatField(null=False)
    fecha = models.DateField(null=False)


# endregion
# region INVENTARIO




class Import_Imventario(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)
    producto_codigo = models.CharField(max_length=50)
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
        verbose_name_plural = "importacion de productos"

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
        #ESTA VALIDACION SE REALIZA DEBIDO A QUE DIO UN ERROR AL ENCONTRAR DOS PRODUCTOS CON EL MISMO CODIGO
        try:
            producto, create = Producto.objects.get_or_create(
                codigo=self.producto_codigo,
                serie=self.producto_serie,
                empresa=self.get_empresa())
        except:
            producto = Producto.objects.filter(
                codigo=self.producto_codigo,
                serie=self.producto_serie,
                empresa=self.get_empresa()).first()
        if producto:
            producto.nombre = self.producto_nombre
            producto.categoria = self.get_categoria()
            producto.medida = self.get_medida()
            producto.marca = self.get_marca()
            producto.costo_promedio = self.producto_costo
            producto.precio = self.producto_precio
            # producto.costo_promedio = (producto.costo_promedio + self.producto_costo) / 2
            producto.save()

            # REGISTRO DE LA EXISTENCIA
            bodega = self.get_bodega()
            detalle , create = Bodega_Detalle.objects.get_or_create(bodega=bodega, producto=producto)
            # detalle.existencia += self.producto_existencia
            detalle.existencia = self.producto_existencia
            detalle.save()
            return producto

    def save(self, *args, **kwargs):
        self.get_producto()
        self.delete()


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
    codigo = models.CharField(max_length=50)
    serie = models.CharField(max_length=50, null=True, blank=True)  # REGISTRO DE PRODUCTOS POR SERIE
    nombre = models.CharField(max_length=200)
    costo_promedio = models.FloatField(default=0, null=False)
    precio = models.FloatField(default=0, null=False)
    categoria = models.ForeignKey(Producto_Categoria, null=True, blank=True)
    medida = models.ForeignKey(Producto_Medida, null=True, blank=True)
    marca = models.ForeignKey(Producto_Marca, null=True, blank=True)
    empresa = models.ForeignKey(Empresa)
    imagen = models.ImageField(upload_to=get_media_url, null=True, blank=True)
    activo = models.BooleanField(default=True, null=False)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "Productos del Inventario"

    def __unicode__(self):
        return "%s %s" % (self.codigo, self.nombre)

    def imagen_url(self):
        if self.imagen:
            return self.imagen.url
        else:
            return "/media/foto-no-disponible.jpg"


class Bodega(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    encargado = models.ForeignKey(User, null=True)

    def __unicode__(self):
        return "%s" % (self.nombre)



class Bodega_Detalle(models.Model):
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


class Forma_Pago(models.Model):
    forma_pago = models.CharField(max_length=50)
    activo = models.BooleanField(null=False, default=True)

    class Meta:
        verbose_name = "Forma de pago"
        verbose_name_plural = "formas de pago"

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
    moneda = models.ForeignKey(Moneda)

    @property
    def abonos(self):
        return Factura_Abono.objects.all().filter(factura=self)

    @property
    def saldo_factura(self):
        '''
        esta funcion regresa el saldo dela facturara (monto) menos todos los abonos a la factura
        '''
        if Factura_Abono.objects.all().filter(factura=self):
            return self.total - Factura_Abono.objects.all().filter(factura=self).aggregate(Sum('monto_abono'))[
                'monto_abono__sum']
        else:
            return self.total


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
    #no_pedido = models.CharField(max_length=10)
    no_pedido = models.IntegerField(null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=False)
    vendedor = models.ForeignKey(Vendedor, null=False, related_name="pedido_usuario_vendedor")
    stotal = models.FloatField(null=False, verbose_name="subtotal")
    impuesto = models.FloatField(null=False)
    total = models.FloatField(null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="pedido_usuario_creacion")
    anulado = models.BooleanField(default=False)
    fecha_anulacion = models.DateTimeField(null=True)
    usuario_anulacion = models.ForeignKey(User, null=True, related_name="pedido_usuario_anulacion")
    comentario = models.CharField(max_length=200, null=True)
    cerrado = models.BooleanField(default=False)


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
    referencia = models.CharField(max_length=20, null=True, blank=True)
    cerrado = models.BooleanField(default=False)
    anulado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Recibo Provicional"
        verbose_name_plural = "Recibos Provicionales de Caja"

    def monto_letras(self):
        return "%s NETOS" % (upper(numero_a_letras(self.monto)))


def get_no_recibo(user):
    no_recibo = 1
    v = Vendedor.objects.filter(usuario=user).first()
    if v:
        try:
            no_recibo = int(Recibo_Provicional.objects.filter(usuario_creacion=user).aggregate(Max('no_recibo'))['no_recibo__max']) + 1
        except:
            no_recibo = v.numero_inicial
    return no_recibo


def next_pedido():
    return int(Pedido.objects.all().aggregate(Max('no_pedido'))['no_pedido__max']) + 1
