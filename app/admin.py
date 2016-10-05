from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

admin.site.register(Import, ImportExportModelAdmin)
class empresa_admin(admin.ModelAdmin):
    list_display = ('numero_ruc', 'razon_social')
admin.site.register(Empresa)
class cliente_admin(admin.ModelAdmin):
    list_display = ('identificacion', 'nombre', 'telefono', 'direccion')
admin.site.register(Cliente, cliente_admin)
class factura_admin(admin.ModelAdmin):
    list_display = ('empresa', 'cliente', 'fecha', 'monto')
    list_filter = ('empresa', 'cliente')
admin.site.register(Factura, factura_admin)
