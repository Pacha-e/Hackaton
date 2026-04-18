from django.contrib import admin
from .models import PerfilFuncionario


@admin.register(PerfilFuncionario)
class PerfilFuncionarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'dependencia', 'cargo')
    list_filter = ('rol', 'dependencia')
