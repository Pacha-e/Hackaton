"""
M1: IntakeAgent — Normaliza PQRSDs desde cualquier canal al esquema unificado.
Modelo: claude-haiku-4-5 (alto volumen, tarea estructurada)
"""
import json
import logging
from .base import BaseAgent, HAIKU
from .contracts import PipelineContext, CiudadanoData

logger = logging.getLogger(__name__)

SYSTEM = """Eres el agente de recepción del sistema PQRSD de la Alcaldía de Medellín.
Tu tarea es normalizar un mensaje ciudadano (de cualquier canal: web, email, WhatsApp, Instagram, presencial)
al esquema estándar de la plataforma.

Responde SOLO con un JSON válido con esta estructura exacta:
{
  "tipo": "<peticion|queja|reclamo|denuncia|sugerencia|felicitacion>",
  "asunto": "<resumen en máximo 15 palabras>",
  "descripcion_normalizada": "<texto limpio, sin saludos ni despedidas, máximo 1000 caracteres>",
  "anonimo": <true|false>,
  "ciudadano": {
    "nombre": "<nombre o vacío si anónimo>",
    "email": "<email o vacío>",
    "telefono": "<teléfono o vacío>",
    "documento": "<cédula o vacío>"
  },
  "ubicacion_mencionada": "<dirección, barrio o calle mencionada, o vacío>"
}

Reglas:
- Si el mensaje no menciona nombre ni datos → anonimo: true
- tipo debe ser el más apropiado según el contenido
- No inventes datos que no estén en el mensaje"""


class IntakeAgent(BaseAgent):
    model = HAIKU
    name = 'IntakeAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from apps.pqrsd.models import PQRSD

        prompt = f"""Canal de entrada: {ctx.canal}
Mensaje del ciudadano:
---
{ctx.descripcion_raw}
---
Normaliza este mensaje al esquema estándar."""

        raw = self.call(SYSTEM, prompt, temperature=0.1)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else {}

        ctx.tipo = data.get('tipo', 'peticion')
        ctx.asunto = data.get('asunto', ctx.descripcion_raw[:80])
        ctx.descripcion_raw = data.get('descripcion_normalizada', ctx.descripcion_raw)

        c = data.get('ciudadano', {})
        ctx.ciudadano = CiudadanoData(
            nombre=c.get('nombre', ''),
            email=c.get('email', ''),
            telefono=c.get('telefono', ''),
            documento=c.get('documento', ''),
            anonimo=data.get('anonimo', False),
        )

        if data.get('ubicacion_mencionada'):
            ctx.ubicacion.direccion = data['ubicacion_mencionada']

        # Crear PQRSD en DB si no existe
        if not ctx.pqrsd_id:
            from datetime import date, timedelta
            pqrsd = PQRSD.objects.create(
                tipo=ctx.tipo,
                canal_entrada=ctx.canal,
                asunto=ctx.asunto,
                descripcion=ctx.descripcion_raw,
                nombre_ciudadano=ctx.ciudadano.nombre,
                email_ciudadano=ctx.ciudadano.email,
                telefono_ciudadano=ctx.ciudadano.telefono,
                documento_ciudadano=ctx.ciudadano.documento,
                anonimo=ctx.ciudadano.anonimo,
                barrio=ctx.ubicacion.barrio,
                comuna=ctx.ubicacion.comuna,
            )
            ctx.pqrsd_id = pqrsd.pk
            ctx.radicado = pqrsd.radicado
            logger.info(f'[IntakeAgent] PQRSD creada: {ctx.radicado}')

        return ctx
