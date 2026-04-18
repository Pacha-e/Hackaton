from django.db import models
from django.contrib.auth.models import User


class PerfilFuncionario(models.Model):
    ROL_CHOICES = [
        ('enlace', 'Enlace PQRSD'),
        ('asesor_juridico', 'Asesor Jurídico'),
        ('director', 'Director de Dependencia'),
        ('admin', 'Administrador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_funcionario')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='enlace')
    dependencia = models.ForeignKey(
        'conocimiento.Dependencia', null=True, blank=True, on_delete=models.SET_NULL
    )
    cargo = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_rol_display()})"
