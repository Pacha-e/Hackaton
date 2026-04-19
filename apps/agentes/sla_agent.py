"""
M8: SLAAgent — Calcula y registra plazos legales según Ley 1755/2015.
Modelo: claude-haiku-4-5 (lógica determinista, sin razonamiento complejo)
"""
import logging
from datetime import date, timedelta
from .base import BaseAgent, HAIKU
from .contracts import PipelineContext

logger = logging.getLogger(__name__)

# Plazos en días hábiles — Ley 1755/2015
PLAZOS_HABILES = {
    'peticion': 15,       # Art. 14 — petición general
    'peticion_info': 10,  # Art. 25 — información
    'queja': 15,
    'reclamo': 15,
    'denuncia': 15,
    'sugerencia': 30,
    'felicitacion': 30,
}

# Días feriados nacionales Colombia 2026 (aproximados)
FESTIVOS_2026 = {
    date(2026, 1, 1), date(2026, 1, 12), date(2026, 3, 23), date(2026, 4, 2),
    date(2026, 4, 3), date(2026, 5, 1), date(2026, 5, 18), date(2026, 6, 8),
    date(2026, 6, 15), date(2026, 6, 29), date(2026, 7, 20), date(2026, 8, 7),
    date(2026, 8, 17), date(2026, 10, 12), date(2026, 11, 2), date(2026, 11, 16),
    date(2026, 12, 8), date(2026, 12, 25),
}


def _sumar_dias_habiles(desde: date, dias: int) -> date:
    actual = desde
    contados = 0
    while contados < dias:
        actual += timedelta(days=1)
        if actual.weekday() < 5 and actual not in FESTIVOS_2026:
            contados += 1
    return actual


def _dias_habiles_restantes(desde: date, hasta: date) -> int:
    if hasta <= desde:
        return 0
    contados = 0
    actual = desde
    while actual < hasta:
        actual += timedelta(days=1)
        if actual.weekday() < 5 and actual not in FESTIVOS_2026:
            contados += 1
    return contados


class SLAAgent(BaseAgent):
    model = HAIKU
    name = 'SLAAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        hoy = date.today()
        plazo_dias = PLAZOS_HABILES.get(ctx.tipo, 15)
        fecha_limite = _sumar_dias_habiles(hoy, plazo_dias)

        ctx.fecha_limite = fecha_limite.isoformat()
        dias_restantes = _dias_habiles_restantes(hoy, fecha_limite)
        ctx.dias_restantes = dias_restantes

        if dias_restantes <= 0:
            ctx.estado_sla = 'vencida'
        elif dias_restantes <= 3:
            ctx.estado_sla = 'en_alerta'
        else:
            ctx.estado_sla = 'en_tiempo'

        # Actualizar DB
        if ctx.pqrsd_id:
            from apps.pqrsd.models import PQRSD
            PQRSD.objects.filter(pk=ctx.pqrsd_id).update(
                fecha_limite=fecha_limite,
            )

        logger.info(
            f'[SLAAgent] {ctx.radicado}: límite={ctx.fecha_limite}, '
            f'restantes={dias_restantes}d, estado={ctx.estado_sla}'
        )
        return ctx
