from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from inventario.models import *

admin.site.register(Import_Imventario, ImportExportModelAdmin)

class producto_admin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'costo_promedio', 'precio', 'categoria',
        'medida', 'marca')
    list_filter = ('empresa', 'marca', 'categoria')
    search_fields = ('codigo', 'nombre')
admin.site.register(Producto, producto_admin)

class bodega_admin(admin.ModelAdmin):
    list_display = ('nombre', 'encargado')
admin.site.register(Bodega, bodega_admin)

admin.site.register(Bodega_Detalle)
