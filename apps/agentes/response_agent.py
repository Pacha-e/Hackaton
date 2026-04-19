"""
M5: ResponseAgent — Genera respuesta humanizada basada en precedentes y normativa.
Modelo: claude-opus-4-7 (calidad máxima, respuesta ciudadana — zero hallucination policy)
"""
import logging
from .base import BaseAgent, OPUS
from .contracts import PipelineContext

logger = logging.getLogger(__name__)

SYSTEM = """Eres el agente de redacción de respuestas del sistema PQRSD de la Alcaldía de Medellín.
Redactas respuestas oficiales humanizadas para ciudadanos que han radicado PQRSDs.

REGLAS ANTI-ALUCINACIÓN (ABSOLUTAS):
1. SOLO usa información explícitamente proporcionada en el contexto (precedentes, normativa, datos de la PQRSD)
2. NUNCA inventes fechas, nombres de funcionarios, números de decreto, ni compromisos específicos no documentados
3. Si no tienes información suficiente para una respuesta sustantiva → redacta confirmación de recibo y traslado
4. No prometas acciones que la alcaldía no pueda cumplir

FORMATO DE RESPUESTA:
- Saludo personalizado (si tiene nombre) o impersonal (si anónimo)
- Confirmación de recibo con radicado
- Explicación clara de qué secretaría/dependencia atiende su caso y por qué
- Pasos que seguirá el trámite
- Plazo de respuesta según ley (menciona el artículo exacto solo si fue proporcionado)
- Cierre con canales de seguimiento
- Tono: cálido, claro, sin tecnicismos, ≤350 palabras
- Idioma: español colombiano

IMPORTANTE: Si el ciudadano es anónimo, omite el saludo nominal y no reveles datos de contacto."""


class ResponseAgent(BaseAgent):
    model = OPUS
    name = 'ResponseAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        # Construir contexto de precedentes
        precedentes_str = ''
        if ctx.precedentes:
            precedentes_str = '\n\nPRECEDENTES RELEVANTES (usa como referencia, no copies textualmente):\n'
            for p in ctx.precedentes[:2]:  # máximo 2 para no saturar
                precedentes_str += f'- Similitud {p.similitud:.0%}: {p.respuesta_base[:300]}\n'
                if p.normativa:
                    precedentes_str += f'  Normativa: {p.normativa}\n'

        nombre = ctx.ciudadano.nombre if not ctx.ciudadano.anonimo and ctx.ciudadano.nombre else None
        canal_seguimiento = (
            f'portal ciudadano con su radicado {ctx.radicado}'
            if ctx.ciudadano.anonimo
            else f'portal ciudadano (radicado {ctx.radicado})'
               + (f', email {ctx.ciudadano.email}' if ctx.ciudadano.email else '')
               + (f' o teléfono {ctx.ciudadano.telefono}' if ctx.ciudadano.telefono else '')
        )

        prompt = f"""DATOS DE LA PQRSD:
Radicado: {ctx.radicado}
Tipo: {ctx.tipo}
Asunto: {ctx.asunto}
Canal de ingreso: {ctx.canal}
Ciudadano: {nombre or 'Anónimo'}
Correo: {ctx.ciudadano.email or 'No proporcionado'}
Secretaría asignada: {ctx.secretaria_asignada}
Fecha límite de respuesta: {ctx.fecha_limite or 'A confirmar por secretaría'}
Canal de seguimiento: {canal_seguimiento}

DESCRIPCIÓN DE LA SOLICITUD:
{ctx.descripcion_raw[:800]}
{precedentes_str}

INSTRUCCIÓN: Redacta la respuesta oficial de acuse de recibo y traslado a secretaría.
Recuerda: solo afirma lo que está documentado arriba."""

        ctx.respuesta_texto = self.call(SYSTEM, prompt, temperature=0.4, max_tokens=800)
        ctx.respuesta_generada = True

        # Actualizar PQRSD en DB
        if ctx.pqrsd_id:
            from apps.pqrsd.models import PQRSD
            PQRSD.objects.filter(pk=ctx.pqrsd_id).update(
                respuesta_automatica=ctx.respuesta_texto,
                estado='en_tramite',
            )

        logger.info(f'[ResponseAgent] Respuesta generada para {ctx.radicado} ({len(ctx.respuesta_texto)} chars)')
        return ctx
