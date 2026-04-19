"""
Servicio de síntesis IA — modo simulado.
"""
import logging

logger = logging.getLogger(__name__)


def generar_sintesis(pqrsd):
    return {
        'resumen_ejecutivo': f'Ciudadano solicita {pqrsd.get_tipo_display().lower()} relacionado con: {pqrsd.asunto}. Canal: {pqrsd.get_canal_entrada_display()}. Requiere revisión y respuesta en plazo legal.',
        'problema_central': pqrsd.descripcion[:500],
        'accion_requerida': 'Revisar, clasificar y dar respuesta dentro del plazo establecido por la Ley 1755/2015.',
        'datos_contextuales': {'lugar_mencionado': pqrsd.barrio or pqrsd.comuna or 'No especificado'},
        'entidades_mencionadas': [],
        'normativa_aplicable': 'Ley 1755/2015 — Derecho de Petición; Decreto Municipal 883/2015.',
        'recomendacion_respuesta': 'Revisar manualmente y dar respuesta formal al ciudadano.',
    }
