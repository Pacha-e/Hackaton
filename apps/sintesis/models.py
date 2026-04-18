from django.db import models


class SintesisPQRSD(models.Model):
    pqrsd = models.OneToOneField('pqrsd.PQRSD', on_delete=models.CASCADE, related_name='sintesis')

    # Capa 1: Resumen ejecutivo (2-3 líneas — lo que lee el funcionario en 10 segundos)
    resumen_ejecutivo = models.TextField()

    # Capa 2: Datos estructurados
    problema_central = models.TextField()
    accion_requerida = models.TextField()
    datos_contextuales = models.JSONField(default=dict)  # {lugar, fecha_hecho, monto, etc.}
    entidades_mencionadas = models.JSONField(default=list)

    # Capa 3: Análisis jurídico y precedentes
    normativa_aplicable = models.TextField(blank=True)
    precedentes_similares = models.ManyToManyField('conocimiento.PrecedenteRespuesta', blank=True)
    recomendacion_respuesta = models.TextField(blank=True)

    fecha_generacion = models.DateTimeField(auto_now_add=True)
    generado_por_ia = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Síntesis PQRSD'
        verbose_name_plural = 'Síntesis PQRSD'

    def __str__(self):
        return f"Síntesis de {self.pqrsd.radicado}"
