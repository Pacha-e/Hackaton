"""
Persistencia de clasificación IA (Gemini) sobre un PQRSD.
Usado por la API REST y por webhooks (p. ej. Chatwoot).
"""
from apps.conocimiento.models import Dependencia
from apps.clasificacion.models import ClasificacionIA
from apps.pqrsd.models import PQRSD
from .gemini_service import clasificar_pqrsd


def clasificar_y_persistir(pqrsd: PQRSD):
    """
    Ejecuta Gemini (o simulación), guarda ClasificacionIA y actualiza PQRSD.
    Retorna (instancia ClasificacionIA, dict resultado crudo de clasificar_pqrsd).
    """
    resultado = clasificar_pqrsd(pqrsd)

    dep = None
    if resultado.get('dependencia_id'):
        try:
            dep = Dependencia.objects.get(pk=resultado['dependencia_id'])
        except Dependencia.DoesNotExist:
            pass

    clasificacion, _ = ClasificacionIA.objects.get_or_create(pqrsd=pqrsd)
    clasificacion.prompt_enviado = resultado.get('prompt', '')
    clasificacion.respuesta_cruda = resultado.get('respuesta_cruda', '')
    clasificacion.tipo_sugerido = resultado.get('tipo_sugerido', pqrsd.tipo)
    clasificacion.prioridad_sugerida = resultado.get('prioridad_sugerida', 'media')
    clasificacion.razon_clasificacion = resultado.get('razon', '')
    clasificacion.confianza = resultado.get('confianza', 0)
    clasificacion.modelo_usado = resultado.get('modelo', 'simulado')
    clasificacion.dependencias_sugeridas = [resultado.get('dependencia_id')]
    clasificacion.save()

    if dep:
        pqrsd.dependencia_sugerida = dep
    pqrsd.confianza_clasificacion = resultado.get('confianza', 0)
    if pqrsd.estado == 'radicada':
        pqrsd.estado = 'en_clasificacion'
    pqrsd.save()

    return clasificacion, resultado, dep
