from django.db import models
from django.contrib.auth.models import User


class ClasificacionIA(models.Model):
    pqrsd = models.OneToOneField('pqrsd.PQRSD', on_delete=models.CASCADE, related_name='clasificacion_ia')
    prompt_enviado = models.TextField()
    respuesta_cruda = models.TextField()
    dependencias_sugeridas = models.JSONField(default=list)
    tipo_sugerido = models.CharField(max_length=20, blank=True)
    prioridad_sugerida = models.CharField(max_length=10, blank=True)
    razon_clasificacion = models.TextField(blank=True)
    confianza = models.FloatField(null=True, blank=True)
    modelo_usado = models.CharField(max_length=100, default='gemini-1.5-flash')
    fecha_clasificacion = models.DateTimeField(auto_now_add=True)

    # Validación humana
    validado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    aceptada = models.BooleanField(null=True, blank=True)
    comentario_validacion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Clasificación IA'
        verbose_name_plural = 'Clasificaciones IA'

    def __str__(self):
        return f"Clasificación IA de {self.pqrsd.radicado}"
