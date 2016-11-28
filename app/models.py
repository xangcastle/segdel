from __future__ import unicode_literals

import datetime
from string import upper
from app.numero_letras import numero_a_letras
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

User.add_to_class('foto', models.ImageField(upload_to="", null=True))


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


