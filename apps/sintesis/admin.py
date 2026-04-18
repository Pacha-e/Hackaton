from django.contrib import admin
from .models import SintesisPQRSD


@admin.register(SintesisPQRSD)
class SintesisAdmin(admin.ModelAdmin):
    list_display = ('pqrsd', 'fecha_generacion', 'generado_por_ia')
    readonly_fields = ('fecha_generacion',)
