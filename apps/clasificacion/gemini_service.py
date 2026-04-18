"""
Servicio de clasificación con Google Gemini 1.5 Flash.
Retorna sugerencias de dependencia y tipo — la decisión final siempre es del funcionario.
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def _construir_prompt(pqrsd, dependencias) -> str:
    deps_texto = "\n".join(
        f"- ID {d.pk} | {d.sigla}: {d.nombre}. Competencias: {d.competencias[:200]}"
        for d in dependencias
    )
    return f"""Eres un asistente para la Alcaldía de Medellín. Analiza la siguiente solicitud ciudadana y sugiere la clasificación más apropiada.

SOLICITUD:
Asunto: {pqrsd.asunto}
Descripción: {pqrsd.descripcion[:1500]}
Canal de entrada: {pqrsd.canal_entrada}

DEPENDENCIAS DISPONIBLES:
{deps_texto}

INSTRUCCIONES:
1. Sugiere la dependencia más competente para tramitar esta solicitud.
2. Determina el tipo: peticion, queja, reclamo, sugerencia, denuncia o correspondencia.
3. Sugiere la prioridad: baja, media, alta o urgente.
4. Explica brevemente tu razonamiento.
5. Indica un porcentaje de confianza (0-100).

IMPORTANTE: Esta es una SUGERENCIA para el funcionario humano. Responde ÚNICAMENTE con JSON válido con esta estructura:
{{
  "dependencia_id": <id numérico>,
  "dependencia_nombre": "<sigla>",
  "tipo_sugerido": "<tipo>",
  "prioridad_sugerida": "<prioridad>",
  "confianza": <0-100>,
  "razon": "<explicación breve de máximo 3 oraciones>"
}}"""


def clasificar_pqrsd(pqrsd):
    """
    Llama a Gemini 1.5 Flash para clasificar una PQRSD.
    Retorna dict con la clasificación o None si falla.
    """
    from apps.conocimiento.models import Dependencia

    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key.startswith('REEMPLAZAR'):
        logger.warning("GEMINI_API_KEY no configurada — usando clasificación simulada")
        return _clasificacion_simulada(pqrsd)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        dependencias = Dependencia.objects.filter(activa=True)
        prompt = _construir_prompt(pqrsd, dependencias)

        response = model.generate_content(prompt)
        texto = response.text.strip()

        # Limpiar markdown si Gemini lo envuelve en ```json
        if texto.startswith('```'):
            texto = texto.split('```')[1]
            if texto.startswith('json'):
                texto = texto[4:]

        resultado = json.loads(texto)
        resultado['prompt'] = prompt
        resultado['respuesta_cruda'] = response.text
        resultado['modelo'] = 'gemini-1.5-flash'
        return resultado

    except Exception as e:
        logger.error(f"Error llamando a Gemini: {e}")
        return _clasificacion_simulada(pqrsd)


def _clasificacion_simulada(pqrsd):
    """Fallback cuando no hay API key — asigna la primera dependencia activa."""
    from apps.conocimiento.models import Dependencia
    dep = Dependencia.objects.filter(activa=True).first()
    return {
        'dependencia_id': dep.pk if dep else None,
        'dependencia_nombre': dep.sigla if dep else 'N/A',
        'tipo_sugerido': pqrsd.tipo,
        'prioridad_sugerida': 'media',
        'confianza': 40,
        'razon': 'Clasificación simulada (API key no configurada). El funcionario debe validar manualmente.',
        'prompt': 'N/A — modo simulado',
        'respuesta_cruda': 'N/A — modo simulado',
        'modelo': 'simulado',
    }
