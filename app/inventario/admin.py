from app.models import Import_Imventario, Producto, Vendedor, Moneda
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

class import_producto(ImportExportModelAdmin):
    list_display = ('producto_codigo', 'producto_nombre', 'producto_precio', 'producto_marca', 'producto_medida')

    actions = ['action_integrar',]
    def action_integrar(self, request, queryset):
        for r in Import_Imventario.objects.all():
            r.save()


admin.site.register(Import_Imventario, import_producto)

class producto_admin(admin.ModelAdmin):
    list_display = ('codigo','nombre', 'precio', 'marca', 'categoria')
    list_filter = ('categoria', 'marca')
    search_fields = ('codigo', 'nombre', 'marca__marca')
admin.site.register(Producto, producto_admin)

class vendedor_admin(admin.ModelAdmin):
    admin.site.register(Vendedor)

class moneda_admin(admin.ModelAdmin):
    admin.site.register(Moneda)
