from django import forms
from .models import PQRSD


class PQRSDCiudadanoForm(forms.ModelForm):
    acepta_politica = forms.BooleanField(
        required=True,
        label='Acepto la política de tratamiento de datos personales (Ley 1581/2012)'
    )

    class Meta:
        model = PQRSD
        fields = [
            'tipo', 'canal_entrada', 'anonimo',
            'nombre_ciudadano', 'email_ciudadano', 'telefono_ciudadano',
            'documento_ciudadano', 'comuna', 'barrio',
            'asunto', 'descripcion', 'archivo_adjunto',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Describa detalladamente su solicitud, incluyendo fechas, lugares y hechos relevantes...'}),
            'asunto': forms.TextInput(attrs={'placeholder': 'Resuma brevemente el tema de su solicitud'}),
        }

    def clean(self):
        cleaned = super().clean()
        anonimo = cleaned.get('anonimo')
        email = cleaned.get('email_ciudadano')
        nombre = cleaned.get('nombre_ciudadano')
        if not anonimo:
            if not email:
                self.add_error('email_ciudadano', 'El correo es obligatorio para peticiones no anónimas.')
            if not nombre:
                self.add_error('nombre_ciudadano', 'El nombre es obligatorio para peticiones no anónimas.')
        return cleaned
