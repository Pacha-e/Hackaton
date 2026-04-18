from django.contrib import admin
from .models import PQRSD


@admin.register(PQRSD)
class PQRSDAdmin(admin.ModelAdmin):
    list_display = ('radicado', 'tipo', 'estado', 'canal_entrada', 'dependencia_asignada', 'fecha_radicacion', 'fecha_limite')
    list_filter = ('tipo', 'estado', 'canal_entrada', 'prioridad', 'clasificacion_validada')
    search_fields = ('radicado', 'nombre_ciudadano', 'asunto', 'descripcion')
    readonly_fields = ('radicado', 'fecha_radicacion')
    date_hierarchy = 'fecha_radicacion'
