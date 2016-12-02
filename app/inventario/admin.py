from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

admin.site.register(Import_Imventario, ImportExportModelAdmin)

class producto_admin(admin.ModelAdmin):
    list_display = ('codigo','nombre', 'precio', 'serie')
    list_filter = ('codigo', 'nombre', 'serie')
admin.site.register(Producto, producto_admin)

class vendedor_admin(admin.ModelAdmin):
    admin.site.register(Vendedor)

class moneda_admin(admin.ModelAdmin):
    admin.site.register(Moneda)