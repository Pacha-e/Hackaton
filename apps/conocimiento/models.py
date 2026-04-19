from django.db import models
from django.utils import timezone


class SyncLog(models.Model):
    fuente = models.CharField(max_length=100, default='medata')
    registros_importados = models.PositiveIntegerField(default=0)
    ejecutado_en = models.DateTimeField(default=timezone.now)
    exitoso = models.BooleanField(default=True)
    error_msg = models.TextField(blank=True)

    class Meta:
        ordering = ['-ejecutado_en']
        verbose_name = 'Log de Sincronización'
        verbose_name_plural = 'Logs de Sincronización'

    def __str__(self):
        estado = 'OK' if self.exitoso else 'ERROR'
        return f"[{estado}] {self.fuente} — {self.registros_importados} registros ({self.ejecutado_en:%Y-%m-%d %H:%M})"


class Dependencia(models.Model):
    nombre = models.CharField(max_length=200)
    sigla = models.CharField(max_length=30)
    descripcion = models.TextField()
    competencias = models.TextField(help_text="Lista de competencias separadas por punto y coma")
    keywords = models.TextField(help_text="Palabras clave para clasificación IA, separadas por coma")
    email_contacto = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Dependencia'
        verbose_name_plural = 'Dependencias'

    def __str__(self):
        return f"{self.sigla} — {self.nombre}"

    def keywords_lista(self):
        return [k.strip() for k in self.keywords.split(',') if k.strip()]


class PrecedenteRespuesta(models.Model):
    TIPO_CHOICES = [
        ('peticion', 'Petición'),
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('sugerencia', 'Sugerencia'),
        ('denuncia', 'Denuncia'),
        ('correspondencia', 'Correspondencia'),
    ]

    dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE, related_name='precedentes')
    tipo_pqrsd = models.CharField(max_length=20, choices=TIPO_CHOICES)
    pregunta_frecuente = models.TextField()
    respuesta_base = models.TextField()
    normativa_aplicable = models.TextField(blank=True)
    usado_veces = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-usado_veces']
        verbose_name = 'Precedente de Respuesta'
        verbose_name_plural = 'Precedentes de Respuesta'

    def __str__(self):
        return f"[{self.dependencia.sigla}] {self.pregunta_frecuente[:80]}"
