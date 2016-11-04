from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

class Import(models.Model):
    razon_social = models.CharField(max_length=255)
    numero_ruc = models.CharField(max_length=14)
    nombre = models.CharField(max_length=165)
    identificacion = models.CharField(max_length=14)
    telefono = models.CharField(max_length=50)
    direccion = models.TextField(max_length=600)
    nodoc = models.CharField(max_length=15, null=True, verbose_name="numero de documento")
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
            monto=self.monto, fecha=self.fecha, nodoc=self.nodoc).save()


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
    fecha_creacion = models.DateField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, null=True, related_name='usuario_creacion')
    fecha_completa = models.DateField(auto_now=True)
    usuario_completa = models.ForeignKey(User, null=True, blank=True, related_name='usuario_completa')
    resultado = models.ForeignKey(Gestion_Resultado, null=True, blank=True)
    comentario = models.CharField(max_length=400, null=True),
    descripcion_resultado = models.CharField(max_length=400, null=True)


    def __unicode__(self):
        return "%s - %s" % (self.tipo_gestion.nombre, self.descripcion)

class Comentario(models.Model):
    descripcion = models.CharField(max_length=400)
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User)


class Cliente(models.Model):
    identificacion = models.CharField(max_length=14)
    nombre = models.CharField(max_length=165)
    telefono = models.CharField(max_length=50)
    direccion = models.TextField(max_length=600)
    gestiones = models.ManyToManyField(Gestion)
    comentarios = models.ManyToManyField(Comentario)

    def __unicode__(self):
        return "%s-%s" % (self.identificacion, self.nombre)

    def facturas(self):
        return Factura.objects.filter(cliente=self)

    def saldo_cliente(self):
        return self.facturas().aggregate(Sum('saldo_factura'))['saldo_factura__sum']



class Factura(models.Model):
    nodoc = models.CharField(max_length=15, null=True, verbose_name="numero de documento")
    empresa = models.ForeignKey(Empresa)
    cliente = models.ForeignKey(Cliente)
    monto = models.FloatField()
    fecha = models.DateField()
    fecha_vence=models.DateField(null=True, blank=True)
    pagada = models.BooleanField(default=False)

    @property
    def abonos(self):
        return Factura_Abono.objects.all().filter(factura=self)

    @property
    def saldo_factura(self):
        '''
        esta funcion regresa el saldo dela facturara (monto) menos todos los abonos a la factura
        '''
        if Factura_Abono.objects.all().filter(factura=self):
            return self.monto - Factura_Abono.objects.all().filter(factura=self).aggregate(Sum('monto_abono'))['monto_abono__sum']
        else:
            return self.monto

    @staticmethod
    def facturas_pendientes(cliente):
        factresult=[]
        facturas = Factura.objects.all().filter(cliente=cliente)
        for factura in facturas:
            if factura.saldo_factura > 0:
                factresult.append(factura)
        return factresult

class Factura_Abono(models.Model):
    factura = models.ForeignKey(Factura)
    monto_abono = models.FloatField(null = False)
    fecha_abono = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, null = True)
