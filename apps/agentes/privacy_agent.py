"""
M9: PrivacyAgent — Habeas Data, anonimización PII y registro de consentimiento (Ley 1581/2012).
Modelo: claude-sonnet-4-6 (detección PII + anonimización semántica)
"""
import json
import logging
import re as stdlib_re
from .base import BaseAgent, SONNET
from .contracts import PipelineContext

logger = logging.getLogger(__name__)

SYSTEM = """Eres el agente de privacidad del sistema PQRSD de la Alcaldía de Medellín.
Tu tarea es detectar y anonimizar Datos Personales Identificables (PII) en el texto de una PQRSD
según la Ley 1581/2012 de Protección de Datos Personales de Colombia.

Responde SOLO con un JSON válido con esta estructura exacta:
{
  "pii_detectada": [
    {
      "tipo": "<nombre|cedula|telefono|email|direccion_exacta|cuenta_bancaria|salud|otro>",
      "valor_original": "<texto exacto encontrado>",
      "nivel_riesgo": "<alto|medio|bajo>"
    }
  ],
  "descripcion_anonimizada": "<texto con PII reemplazada por placeholders como [NOMBRE], [CEDULA], [TELEFONO], [EMAIL], [DIRECCION]>",
  "requiere_consentimiento": <true|false>,
  "bases_legales": "<base legal para el tratamiento, ej: Art. 10 Ley 1581/2012 — función pública>"
}

PII de ALTO riesgo: cédula, cuenta bancaria, datos de salud, datos de menores
PII de MEDIO riesgo: nombre completo, teléfono, email, dirección exacta
PII de BAJO riesgo: nombre de pila solo, barrio general

Si el ciudadano es anónimo → la descripción puede tener datos de terceros mencionados (anonimizar también).
requiere_consentimiento=false para PQRSDs (base legal: función pública — Art. 10 Ley 1581/2012)."""

# Patrones regex para PII obvia (complementa detección LLM)
_CEDULA = stdlib_re.compile(r'\b\d{6,10}\b')
_TELEFONO = stdlib_re.compile(r'\b(?:\+57\s?)?3\d{9}\b|\b\(?0?[1-9]\)?\s?\d{6,7}\b')
_EMAIL = stdlib_re.compile(r'\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b', stdlib_re.I)


class PrivacyAgent(BaseAgent):
    model = SONNET
    name = 'PrivacyAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        texto = ctx.descripcion_raw

        # Pre-detección regex (rápida, sin LLM)
        pii_regex = []
        if _CEDULA.search(texto):
            pii_regex.append('cédula detectada por regex')
        if _TELEFONO.search(texto):
            pii_regex.append('teléfono detectado por regex')
        if _EMAIL.search(texto):
            pii_regex.append('email detectado por regex')

        prompt = f"""Ciudadano anónimo: {ctx.ciudadano.anonimo}
Nombre ciudadano: {ctx.ciudadano.nombre or 'No proporcionado'}
Email ciudadano: {ctx.ciudadano.email or 'No proporcionado'}
Teléfono ciudadano: {ctx.ciudadano.telefono or 'No proporcionado'}

Descripción de la PQRSD a analizar:
---
{texto[:1200]}
---
{'Alertas regex: ' + ', '.join(pii_regex) if pii_regex else ''}

Detecta PII y genera la versión anonimizada."""

        raw = self.call(SYSTEM, prompt, temperature=0.1)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            match = stdlib_re.search(r'\{.*\}', raw, stdlib_re.DOTALL)
            data = json.loads(match.group()) if match else {}

        ctx.pii_detectada = data.get('pii_detectada', [])
        ctx.descripcion_anonimizada = data.get('descripcion_anonimizada', texto)
        ctx.consentimiento_registrado = True  # Base legal: función pública Art. 10

        # Log PII de alto riesgo
        alto_riesgo = [p for p in ctx.pii_detectada if p.get('nivel_riesgo') == 'alto']
        if alto_riesgo:
            logger.warning(
                f'[PrivacyAgent] PII alto riesgo en {ctx.radicado}: '
                f'{[p["tipo"] for p in alto_riesgo]}'
            )

        # Persistir descripción anonimizada en DB (para reportes públicos)
        if ctx.pqrsd_id and ctx.descripcion_anonimizada:
            from apps.pqrsd.models import PQRSD
            PQRSD.objects.filter(pk=ctx.pqrsd_id).update(
                descripcion_anonimizada=ctx.descripcion_anonimizada,
            )

        logger.info(
            f'[PrivacyAgent] {ctx.radicado}: {len(ctx.pii_detectada)} PII detectados'
        )
        return ctx
