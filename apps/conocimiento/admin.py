from django.contrib import admin
from .models import Dependencia, PrecedenteRespuesta


@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nombre', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre', 'sigla', 'keywords')


@admin.register(PrecedenteRespuesta)
class PrecedenteAdmin(admin.ModelAdmin):
    list_display = ('dependencia', 'tipo_pqrsd', 'usado_veces', 'activo')
    list_filter = ('dependencia', 'tipo_pqrsd', 'activo')
    search_fields = ('pregunta_frecuente', 'respuesta_base')
