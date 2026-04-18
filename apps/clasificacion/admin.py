from django.contrib import admin
from .models import ClasificacionIA


@admin.register(ClasificacionIA)
class ClasificacionIAAdmin(admin.ModelAdmin):
    list_display = ('pqrsd', 'tipo_sugerido', 'confianza', 'aceptada', 'validado_por', 'fecha_clasificacion')
    list_filter = ('tipo_sugerido', 'aceptada', 'modelo_usado')
    readonly_fields = ('fecha_clasificacion', 'prompt_enviado', 'respuesta_cruda')
