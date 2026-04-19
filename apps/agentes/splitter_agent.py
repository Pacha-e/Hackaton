"""
M4: SplitterAgent — Divide PQRSDs compuestas en sub-PQRSDs atómicas.
Modelo: claude-sonnet-4-6 (requiere comprensión semántica profunda)
"""
import json
import logging
from .base import BaseAgent, SONNET
from .contracts import PipelineContext

logger = logging.getLogger(__name__)

SYSTEM = """Eres el agente divisor del sistema PQRSD de la Alcaldía de Medellín.
Analiza si una PQRSD contiene múltiples reclamos independientes que deben tramitarse
por separado ante diferentes secretarías.

Responde SOLO con un JSON válido con esta estructura exacta:
{
  "dividida": <true|false>,
  "sub_pqrsds": [
    {
      "tipo": "<peticion|queja|reclamo|denuncia|sugerencia|felicitacion>",
      "asunto": "<resumen en máximo 15 palabras>",
      "descripcion": "<descripción específica de este reclamo, máximo 500 caracteres>",
      "competencia_sugerida": "<área de la alcaldía: movilidad|espacio_publico|ambiente|salud|educacion|vivienda|servicios_publicos|seguridad|otro>",
      "requiere_ubicacion": <true|false>
    }
  ]
}

Si dividida=false → sub_pqrsds debe ser lista vacía []

Criterios para dividir:
- La PQRSD menciona problemas claramente distintos (ej: hueco en la calle Y también basura acumulada)
- Cada problema pertenece a una competencia diferente
- Cada sub-PQRSD debe poder tramitarse de forma independiente

NO dividir si:
- El problema es uno solo aunque se mencione con múltiples síntomas
- Los problemas son de la misma secretaría
- La descripción es vaga y no permite separar con certeza"""


class SplitterAgent(BaseAgent):
    model = SONNET
    name = 'SplitterAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from apps.pqrsd.models import PQRSD

        prompt = f"""Tipo: {ctx.tipo}
Asunto: {ctx.asunto}
Canal: {ctx.canal}
Descripción:
---
{ctx.descripcion_raw}
---

¿Contiene esta PQRSD múltiples reclamos independientes que requieran trámites separados?"""

        raw = self.call(SYSTEM, prompt, temperature=0.2)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else {'dividida': False, 'sub_pqrsds': []}

        ctx.dividida = data.get('dividida', False)
        sub_pqrsds_raw = data.get('sub_pqrsds', [])

        if ctx.dividida and len(sub_pqrsds_raw) > 1 and ctx.pqrsd_id:
            from datetime import date, timedelta
            sub_ids = []
            for idx, sub in enumerate(sub_pqrsds_raw):
                sub_pqrsd = PQRSD.objects.create(
                    tipo=sub.get('tipo', ctx.tipo),
                    canal_entrada=ctx.canal,
                    asunto=sub.get('asunto', f'Sub-PQRSD {idx + 1}'),
                    descripcion=sub.get('descripcion', ''),
                    nombre_ciudadano=ctx.ciudadano.nombre,
                    email_ciudadano=ctx.ciudadano.email,
                    telefono_ciudadano=ctx.ciudadano.telefono,
                    documento_ciudadano=ctx.ciudadano.documento,
                    anonimo=ctx.ciudadano.anonimo,
                    barrio=ctx.ubicacion.barrio,
                    comuna=ctx.ubicacion.comuna,
                    observaciones_internas=f'Generada automáticamente desde {ctx.radicado} (ítem {idx + 1})',
                )
                sub_ids.append({
                    'pqrsd_id': sub_pqrsd.pk,
                    'radicado': sub_pqrsd.radicado,
                    'asunto': sub.get('asunto', ''),
                    'competencia_sugerida': sub.get('competencia_sugerida', ''),
                    'requiere_ubicacion': sub.get('requiere_ubicacion', False),
                })
                logger.info(f'[SplitterAgent] Sub-PQRSD creada: {sub_pqrsd.radicado}')

            ctx.sub_pqrsds = sub_ids

            # Marcar la PQRSD original como dividida
            PQRSD.objects.filter(pk=ctx.pqrsd_id).update(
                observaciones_internas=f'Dividida en {len(sub_ids)} sub-PQRSDs: {", ".join(s["radicado"] for s in sub_ids)}',
                estado='en_tramite',
            )
            logger.info(f'[SplitterAgent] PQRSD {ctx.radicado} dividida en {len(sub_ids)} sub-PQRSDs')
        else:
            ctx.dividida = False
            ctx.sub_pqrsds = []

        return ctx
