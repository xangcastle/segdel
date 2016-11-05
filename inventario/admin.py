from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from inventario.models import *

admin.site.register(Import_Imventario, ImportExportModelAdmin)
