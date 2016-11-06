from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from inventario.models import *

admin.site.register(Import_Imventario, ImportExportModelAdmin)

class producto_admin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
admin.site.register(Producto)

class bodega_admin(admin.ModelAdmin):
    list_display = ('nombre', 'encargado')
admin.site.register(Bodega)

admin.site.register(Bodega_Detalle)