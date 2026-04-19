"""
M10: OrchestratorAgent — Conductor del pipeline completo PQRSD.
Modelo: claude-sonnet-4-6 (coordinación, decisiones de flujo condicional)
Escala a 100+ PQRSD/día/secretaría ejecutando agentes en el orden correcto.
"""
import logging
from .contracts import PipelineContext, CiudadanoData, UbicacionData
from .intake_agent import IntakeAgent
from .filter_agent import FilterAgent
from .splitter_agent import SplitterAgent
from .router_agent import RouterAgent
from .knowledge_agent import KnowledgeAgent
from .response_agent import ResponseAgent
from .privacy_agent import PrivacyAgent
from .delivery_agent import DeliveryAgent
from .sla_agent import SLAAgent

logger = logging.getLogger(__name__)


class PQRSDPipeline:
    """
    Pipeline principal. Cada agente recibe y devuelve PipelineContext.
    Los agentes se ejecutan con .execute() que captura errores sin romper el pipeline.

    Orden:
      M1 Intake → M3 Filter → [stop si inadmisible]
      → M8 SLA → M4 Splitter → M2 Router → M9 Privacy
      → M6 Knowledge → M5 Response → M7 Delivery
    """

    def __init__(self):
        self.intake = IntakeAgent()
        self.filter = FilterAgent()
        self.sla = SLAAgent()
        self.splitter = SplitterAgent()
        self.router = RouterAgent()
        self.privacy = PrivacyAgent()
        self.knowledge = KnowledgeAgent()
        self.response = ResponseAgent()
        self.delivery = DeliveryAgent()

    def run(self, canal: str, descripcion_raw: str, **kwargs) -> PipelineContext:
        ctx = PipelineContext(
            canal=canal,
            descripcion_raw=descripcion_raw,
            ciudadano=CiudadanoData(
                nombre=kwargs.get('nombre', ''),
                email=kwargs.get('email', ''),
                telefono=kwargs.get('telefono', ''),
                documento=kwargs.get('documento', ''),
                anonimo=kwargs.get('anonimo', False),
            ),
            ubicacion=UbicacionData(
                barrio=kwargs.get('barrio', ''),
                comuna=kwargs.get('comuna', ''),
                direccion=kwargs.get('direccion', ''),
            ),
        )

        # Si viene una PQRSD ya existente (re-procesamiento)
        if kwargs.get('pqrsd_id'):
            ctx.pqrsd_id = kwargs['pqrsd_id']
            ctx.radicado = kwargs.get('radicado', '')

        logger.info(f'[Pipeline] Iniciando pipeline canal={canal}')

        # M1: Normalizar entrada
        ctx = self.intake.execute(ctx)

        # M3: Filtro de admisibilidad
        ctx = self.filter.execute(ctx)
        if not ctx.admisible:
            logger.info(f'[Pipeline] {ctx.radicado} rechazada: {ctx.motivo_rechazo}')
            return ctx  # Stop temprano

        # M8: Calcular SLA antes de procesar (para cumplir desde el inicio)
        ctx = self.sla.execute(ctx)

        # M4: División en sub-PQRSDs si aplica
        ctx = self.splitter.execute(ctx)

        if ctx.dividida and ctx.sub_pqrsds:
            # Procesar cada sub-PQRSD de forma independiente (pipeline recursivo)
            logger.info(f'[Pipeline] {ctx.radicado} dividida en {len(ctx.sub_pqrsds)} sub-PQRSDs')
            for sub in ctx.sub_pqrsds:
                self._procesar_sub_pqrsd(sub, ctx)
            return ctx

        # M2: Enrutar a secretaría competente
        ctx = self.router.execute(ctx)

        # M9: Habeas Data — anonimizar antes de responder
        ctx = self.privacy.execute(ctx)

        # M6: Recuperar precedentes relevantes
        ctx = self.knowledge.execute(ctx)

        # M5: Generar respuesta humanizada (Opus)
        ctx = self.response.execute(ctx)

        # M7: Entregar al ciudadano
        ctx = self.delivery.execute(ctx)

        logger.info(
            f'[Pipeline] {ctx.radicado} completada — '
            f'agentes={ctx.agentes_ejecutados}, errores={len(ctx.errores)}'
        )
        return ctx

    def _procesar_sub_pqrsd(self, sub: dict, ctx_padre: PipelineContext):
        """Procesa una sub-PQRSD heredando datos del ciudadano del padre."""
        sub_ctx = PipelineContext(
            canal=ctx_padre.canal,
            pqrsd_id=sub['pqrsd_id'],
            radicado=sub['radicado'],
            asunto=sub['asunto'],
            descripcion_raw=sub.get('descripcion', ctx_padre.descripcion_raw),
            ciudadano=ctx_padre.ciudadano,
            ubicacion=ctx_padre.ubicacion,
        )
        try:
            sub_ctx = self.sla.execute(sub_ctx)
            sub_ctx = self.router.execute(sub_ctx)
            sub_ctx = self.privacy.execute(sub_ctx)
            sub_ctx = self.knowledge.execute(sub_ctx)
            sub_ctx = self.response.execute(sub_ctx)
            sub_ctx = self.delivery.execute(sub_ctx)
        except Exception as e:
            logger.error(f'[Pipeline] Error en sub-PQRSD {sub["radicado"]}: {e}')


# Instancia singleton reutilizable (cliente Anthropic se inicializa lazy por agente)
_pipeline: PQRSDPipeline | None = None


def get_pipeline() -> PQRSDPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = PQRSDPipeline()
    return _pipeline


def procesar_pqrsd(canal: str, descripcion: str, **kwargs) -> PipelineContext:
    """Entry point de alto nivel para procesar una PQRSD desde cualquier vista/tarea."""
    return get_pipeline().run(canal, descripcion, **kwargs)
