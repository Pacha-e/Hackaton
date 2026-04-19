"""
Servicio de clasificación IA — modo simulado.
La sugerencia siempre requiere validación del funcionario humano (Ley 1755/2015).
"""
import logging

logger = logging.getLogger(__name__)


def clasificar_pqrsd(pqrsd):
    from apps.conocimiento.models import Dependencia
    dep = Dependencia.objects.filter(activa=True).first()
    return {
        'dependencia_id': dep.pk if dep else None,
        'dependencia_nombre': dep.sigla if dep else 'N/A',
        'tipo_sugerido': pqrsd.tipo,
        'prioridad_sugerida': 'media',
        'confianza': 40,
        'razon': 'Clasificación automática preliminar. El funcionario debe validar manualmente.',
        'prompt': 'N/A',
        'respuesta_cruda': 'N/A',
        'modelo': 'simulado',
    }
