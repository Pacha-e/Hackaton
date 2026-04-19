"""
LangGraph agent stub — falls back to gemini_service when full agent unavailable.
"""
from .gemini_service import clasificar_pqrsd


def procesar_pqrsd_con_agente(pqrsd):
    clasif = clasificar_pqrsd(pqrsd)
    return {
        'clasificacion': clasif,
        'sintesis': {},
    }
