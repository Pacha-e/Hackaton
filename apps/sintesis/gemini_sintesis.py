"""
Genera síntesis estructurada en 3 capas usando Gemini 1.5 Flash.
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def generar_sintesis(pqrsd):
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key.startswith('REEMPLAZAR'):
        return _sintesis_simulada(pqrsd)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""Analiza esta solicitud ciudadana y genera una síntesis estructurada para funcionarios de la Alcaldía de Medellín.

SOLICITUD:
Tipo: {pqrsd.get_tipo_display()}
Asunto: {pqrsd.asunto}
Descripción: {pqrsd.descripcion[:2000]}

Responde ÚNICAMENTE con JSON válido:
{{
  "resumen_ejecutivo": "<2-3 oraciones que resumen todo — máximo 60 palabras>",
  "problema_central": "<descripción del problema o solicitud central>",
  "accion_requerida": "<qué debe hacer la Alcaldía — verbo en infinitivo>",
  "datos_contextuales": {{
    "lugar_mencionado": "<lugar si aplica>",
    "fecha_hecho": "<fecha del hecho si se menciona>",
    "monto_involucrado": "<monto si aplica>",
    "numero_afectados": "<cuántas personas si se menciona>"
  }},
  "entidades_mencionadas": ["<entidad1>", "<entidad2>"],
  "normativa_aplicable": "<leyes, decretos o normas relevantes — ej: Ley 1755/2015, Decreto 883/2015>",
  "recomendacion_respuesta": "<sugerencia de cómo responder — el funcionario decide>"
}}"""

        response = model.generate_content(prompt)
        texto = response.text.strip()
        if texto.startswith('```'):
            texto = texto.split('```')[1]
            if texto.startswith('json'):
                texto = texto[4:]
        return json.loads(texto)

    except Exception as e:
        logger.error(f"Error generando síntesis con Gemini: {e}")
        return _sintesis_simulada(pqrsd)


def _sintesis_simulada(pqrsd):
    return {
        'resumen_ejecutivo': f'Ciudadano solicita {pqrsd.get_tipo_display().lower()} relacionado con: {pqrsd.asunto}. Canal: {pqrsd.get_canal_entrada_display()}. Requiere revisión y respuesta en plazo legal.',
        'problema_central': pqrsd.descripcion[:500],
        'accion_requerida': 'Revisar, clasificar y dar respuesta dentro del plazo establecido por la Ley 1755/2015.',
        'datos_contextuales': {'lugar_mencionado': pqrsd.barrio or pqrsd.comuna or 'No especificado'},
        'entidades_mencionadas': [],
        'normativa_aplicable': 'Ley 1755/2015 — Derecho de Petición; Decreto Municipal 883/2015.',
        'recomendacion_respuesta': 'Síntesis simulada (API key no configurada). Revisar manualmente.',
    }
