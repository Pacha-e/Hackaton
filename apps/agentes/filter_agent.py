"""
M3: FilterAgent — Admisibilidad previa a enrutamiento.
Modelo: claude-haiku-4-5 (decisión binaria, alto volumen)
"""
import json
import logging
from .base import BaseAgent, HAIKU
from .contracts import PipelineContext

logger = logging.getLogger(__name__)

SYSTEM = """Eres el agente de filtro del sistema PQRSD de la Alcaldía de Medellín.
Evalúa si una PQRSD es admisible según tres criterios.

Responde SOLO con un JSON válido con esta estructura exacta:
{
  "admisible": <true|false>,
  "motivo": "<codigo_motivo>",
  "explicacion": "<mensaje claro para el ciudadano, máximo 200 caracteres>",
  "radicado_duplicado": "<radicado existente o vacío>"
}

Códigos de motivo (solo si admisible=false):
- "lenguaje_inadmisible": insultos, injurias, amenazas, lenguaje denigrante
- "duplicado": misma solicitud ya radicada (mismo lugar/problema)
- "falta_claridad": demasiado vago para tramitar

Si admisible=true → motivo="" y explicacion="" y radicado_duplicado=""

Sé estricto con lenguaje ofensivo. Para claridad: un hueco en una calle sin dirección sí es suficiente.
Para duplicados: usa los radicados previos que se te proporcionan."""


class FilterAgent(BaseAgent):
    model = HAIKU
    name = 'FilterAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from apps.pqrsd.models import PQRSD

        # Buscar duplicados recientes (últimos 90 días, misma dependencia/asunto similar)
        duplicados_recientes = []
        if ctx.asunto:
            from datetime import date, timedelta
            hace_90_dias = date.today() - timedelta(days=90)
            candidatos = PQRSD.objects.filter(
                created_at__date__gte=hace_90_dias,
            ).exclude(pk=ctx.pqrsd_id).values('radicado', 'asunto', 'descripcion')[:10]
            duplicados_recientes = list(candidatos)

        duplicados_str = ''
        if duplicados_recientes:
            duplicados_str = '\nPQRSDs recientes en el sistema:\n' + '\n'.join(
                f"- {d['radicado']}: {d['asunto']}" for d in duplicados_recientes
            )

        prompt = f"""Tipo: {ctx.tipo}
Asunto: {ctx.asunto}
Descripción:
---
{ctx.descripcion_raw}
---{duplicados_str}

Evalúa la admisibilidad de esta PQRSD."""

        raw = self.call(SYSTEM, prompt, temperature=0.1)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else {'admisible': True}

        ctx.admisible = data.get('admisible', True)

        if not ctx.admisible:
            ctx.motivo_rechazo = data.get('motivo', '')
            ctx.notificacion_ciudadano = data.get('explicacion', '')
            ctx.radicado_duplicado = data.get('radicado_duplicado', '') or None

            # Actualizar estado en DB si existe
            if ctx.pqrsd_id:
                PQRSD.objects.filter(pk=ctx.pqrsd_id).update(
                    estado='rechazada',
                    observaciones_internas=f"Filtro automático: {ctx.motivo_rechazo} — {ctx.notificacion_ciudadano}",
                )
            logger.info(f'[FilterAgent] PQRSD {ctx.radicado} rechazada: {ctx.motivo_rechazo}')
        else:
            logger.info(f'[FilterAgent] PQRSD {ctx.radicado} admisible')

        return ctx
