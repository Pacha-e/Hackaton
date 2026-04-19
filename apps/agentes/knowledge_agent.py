"""
M6: KnowledgeAgent — Recupera precedentes relevantes del banco de conocimiento.
Modelo: claude-sonnet-4-6 (ranking semántico de precedentes)
"""
import json
import logging
from .base import BaseAgent, SONNET
from .contracts import PipelineContext, PrecedenteData

logger = logging.getLogger(__name__)

SYSTEM = """Eres el agente de conocimiento del sistema PQRSD de la Alcaldía de Medellín.
Tu tarea es identificar qué precedentes del banco de conocimiento son más relevantes
para responder la PQRSD actual, y calcular un score de similitud para cada uno.

Se te proporcionará la PQRSD actual y una lista de precedentes disponibles.

Responde SOLO con un JSON válido con esta estructura exacta:
{
  "precedentes_relevantes": [
    {
      "id": "<id del precedente>",
      "similitud": <0.0 a 1.0>,
      "razonamiento": "<máximo 80 caracteres por qué es relevante>"
    }
  ],
  "normativa_aplicable": "<leyes, decretos o acuerdos aplicables, máximo 200 caracteres>",
  "contexto_adicional": "<información contextual útil para la respuesta, máximo 300 caracteres>"
}

Incluye solo precedentes con similitud > 0.5. Máximo 3 precedentes.
Si no hay precedentes relevantes → precedentes_relevantes: []"""


class KnowledgeAgent(BaseAgent):
    model = SONNET
    name = 'KnowledgeAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from apps.conocimiento.models import PrecedenteRespuesta

        # Cargar precedentes de la secretaría asignada (o todos si no hay)
        qs = PrecedenteRespuesta.objects.filter(activo=True)
        if ctx.secretaria_id:
            qs = qs.filter(dependencia_id=ctx.secretaria_id)
        if not qs.exists():
            qs = PrecedenteRespuesta.objects.filter(activo=True)

        precedentes_db = list(qs.values('id', 'tipo_pqrsd', 'pregunta_frecuente', 'respuesta_base', 'normativa_aplicable', 'usado_veces')[:20])

        if not precedentes_db:
            logger.info(f'[KnowledgeAgent] Sin precedentes disponibles para {ctx.radicado}')
            return ctx

        precedentes_str = '\n'.join(
            f"ID={p['id']} | tipo={p['tipo_pqrsd']} | problema={p['pregunta_frecuente'][:100]} | usado={p['usado_veces']}x"
            for p in precedentes_db
        )

        prompt = f"""PQRSD actual:
Tipo: {ctx.tipo}
Secretaría: {ctx.secretaria_asignada}
Asunto: {ctx.asunto}
Descripción:
---
{ctx.descripcion_raw[:600]}
---

Precedentes disponibles:
{precedentes_str}

¿Cuáles precedentes son más relevantes para responder esta PQRSD?"""

        raw = self.call(SYSTEM, prompt, temperature=0.1)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else {}

        precedentes_relevantes = data.get('precedentes_relevantes', [])
        precedente_map = {str(p['id']): p for p in precedentes_db}

        ctx.precedentes = []
        for item in precedentes_relevantes:
            pid = str(item.get('id', ''))
            if pid in precedente_map:
                p = precedente_map[pid]
                ctx.precedentes.append(PrecedenteData(
                    id=pid,
                    similitud=float(item.get('similitud', 0.5)),
                    respuesta_base=p.get('respuesta_base', ''),
                    normativa=p.get('normativa_aplicable', ''),
                    usado_veces=p.get('usado_veces', 0),
                ))
                # Incrementar contador de uso
                PrecedenteRespuesta.objects.filter(pk=int(pid)).update(
                    usado_veces=p['usado_veces'] + 1
                )

        # Guardar normativa aplicable en el contexto (lo usará ResponseAgent)
        if data.get('normativa_aplicable'):
            ctx.fecha_limite = ctx.fecha_limite or data['normativa_aplicable'][:50]

        logger.info(f'[KnowledgeAgent] {len(ctx.precedentes)} precedentes relevantes para {ctx.radicado}')
        return ctx
