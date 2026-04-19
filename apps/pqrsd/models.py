from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date


def _calcular_fecha_limite(tipo: str) -> date:
    dias = 10 if tipo == 'peticion_info' else 30 if tipo == 'peticion_concepto' else 15
    hoy = date.today()
    habiles = 0
    d = hoy
    while habiles < dias:
        d += timedelta(days=1)
        if d.weekday() < 5:
            habiles += 1
    return d


class PQRSD(models.Model):
    TIPO_CHOICES = [
        ('peticion', 'Petición'),
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('sugerencia', 'Sugerencia'),
        ('denuncia', 'Denuncia'),
        ('correspondencia', 'Correspondencia'),
    ]
    ESTADO_CHOICES = [
        ('radicada', 'Radicada'),
        ('en_clasificacion', 'En Clasificación'),
        ('clasificada', 'Clasificada'),
        ('en_tramite', 'En Trámite'),
        ('respondida', 'Respondida'),
        ('cerrada', 'Cerrada'),
    ]
    CANAL_CHOICES = [
        ('web', 'Portal Web'),
        ('email', 'Correo Electrónico'),
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('presencial', 'Presencial'),
    ]
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    radicado = models.CharField(max_length=25, unique=True, editable=False)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='radicada')
    canal_entrada = models.CharField(max_length=20, choices=CANAL_CHOICES)
    anonimo = models.BooleanField(default=False)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')

    # Ciudadano
    nombre_ciudadano = models.CharField(max_length=200, blank=True)
    email_ciudadano = models.EmailField(blank=True)
    telefono_ciudadano = models.CharField(max_length=20, blank=True)
    documento_ciudadano = models.CharField(max_length=20, blank=True)
    comuna = models.CharField(max_length=100, blank=True)
    barrio = models.CharField(max_length=100, blank=True)

    # Contenido original
    asunto = models.CharField(max_length=300)
    descripcion = models.TextField()
    archivo_adjunto = models.FileField(upload_to='adjuntos/', blank=True, null=True)

    # Dependencia
    dependencia_sugerida = models.ForeignKey(
        'conocimiento.Dependencia', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='pqrsds_sugeridas'
    )
    dependencia_asignada = models.ForeignKey(
        'conocimiento.Dependencia', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='pqrsds_asignadas'
    )
    confianza_clasificacion = models.FloatField(null=True, blank=True)
    clasificacion_validada = models.BooleanField(default=False)
    validado_por = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='validaciones'
    )

    # Funcionario responsable
    funcionario_asignado = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='pqrsds_asignadas'
    )

    # SLA
    fecha_radicacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    observaciones_funcionario = models.TextField(blank=True)

    # Trazabilidad omnicanal (Chatwoot, etc.) — no sustituye radicado oficial
    omnicanal_meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-fecha_radicacion']
        verbose_name = 'PQRSD'
        verbose_name_plural = 'PQRSDs'

    def save(self, *args, **kwargs):
        if not self.radicado:
            self.radicado = self._generar_radicado()
        if not self.fecha_limite:
            self.fecha_limite = _calcular_fecha_limite(self.tipo)
        super().save(*args, **kwargs)

    def _generar_radicado(self):
        from django.utils import timezone as tz
        now = tz.now()
        last = PQRSD.objects.count() + 1
        return f"MDE-{now.year}{now.month:02d}-{last:05d}"

    def dias_restantes(self):
        if self.fecha_limite:
            return (self.fecha_limite - date.today()).days
        return None

    def en_alerta(self):
        dias = self.dias_restantes()
        return dias is not None and 0 <= dias <= 3

    def vencida(self):
        dias = self.dias_restantes()
        return dias is not None and dias < 0

    def get_estado_badge(self):
        badges = {
            'radicada': 'secondary',
            'en_clasificacion': 'warning',
            'clasificada': 'info',
            'en_tramite': 'primary',
            'respondida': 'success',
            'cerrada': 'dark',
        }
        return badges.get(self.estado, 'secondary')

    def __str__(self):
        return f"{self.radicado} — {self.get_tipo_display()}"
