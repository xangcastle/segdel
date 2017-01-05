from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

admin.site.register(Import, ImportExportModelAdmin)
class base_tabular(admin.TabularInline):
    extra = 0
    classes = ('grp-collapse grp-open',)

#class empresa_admin(admin.ModelAdmin):
#    list_display = ('numero_ruc', 'razon_social')
#admin.site.register(Empresa)

#class gestion_resultado_admin(admin.ModelAdmin):
#    list_display = ('nombre', 'activo')
#admin.site.register(Gestion_Resultado)

#class tipo_gestion_admin(admin.ModelAdmin):
#    list_display = ('nombre', 'activo')
#admin.site.register(Tipo_Gestion)

#class gestion_admin(admin.ModelAdmin):
#    list_display = ('tipo_gestion', 'usuario_creacion', 'fecha_creacion','resultado','descripcion')
#admin.site.register(Gestion)


class cliente_admin(ImportExportModelAdmin):
    list_display = ('identificacion', 'nombre', 'telefono', 'direccion')
    list_filter = ('identificacion', 'nombre', 'telefono')

    def get_actions(self, request):
        actions = super(cliente_admin, self).get_actions(request)
        if request.user.username[0].upper() != 'J':
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

admin.site.register(Cliente, cliente_admin)

admin.site.register(Forma_Pago)

class recibo_admin(admin.ModelAdmin):
    date_hierarchy = "fecha_creacion"
    list_display = ("no_recibo", "cliente", "forma_pago", "monto", "comentario", "referencia", "cerrado")
    list_filter = ("usuario_creacion", "forma_pago", "cerrado")
    search_fields = ("cliente", 'no_recibo', "comentario")
admin.site.register(Recibo_Provicional, recibo_admin)


class pedido_admin(admin.ModelAdmin):
    date_hierarchy = "fecha_creacion"
    list_display = ("no_pedido", "cliente", "total", "comentario", "vendedor", "cerrado", "anulado")
    list_filter = ("usuario_creacion", "cerrado")
    search_fields = ("cliente", "no_pedido", "comentario")

admin.site.register(Pedido, pedido_admin)

#class documento_cobro_admin(admin.ModelAdmin):
#    list_display = ('empresa', 'cliente', 'fecha', 'monto')
#    list_filter = ('empresa', 'cliente')
#admin.site.register(Documento_Cobro, documento_cobro_admin)
