"""
M7: DeliveryAgent — Envía respuesta al ciudadano y verifica entrega.
Modelo: claude-haiku-4-5 (lógica de canal, no requiere razonamiento complejo)
"""
import logging
from .base import BaseAgent, HAIKU
from .contracts import PipelineContext

logger = logging.getLogger(__name__)


class DeliveryAgent(BaseAgent):
    model = HAIKU
    name = 'DeliveryAgent'

    # Canales en orden de preferencia
    CANAL_PRIORITY = ['email', 'whatsapp', 'web', 'instagram', 'presencial']

    def run(self, ctx: PipelineContext) -> PipelineContext:
        if not ctx.respuesta_generada or not ctx.respuesta_texto:
            logger.warning(f'[DeliveryAgent] Sin respuesta generada para {ctx.radicado}')
            return ctx

        canales_disponibles = self._detectar_canales(ctx)

        if not canales_disponibles:
            # PQRSD anónima sin contacto: solo disponible en portal
            ctx.entregada = True
            ctx.canal_exitoso = 'portal'
            ctx.intentos_entrega = 0
            self._marcar_entregada(ctx, 'portal')
            logger.info(f'[DeliveryAgent] {ctx.radicado}: solo portal (anónimo sin contacto)')
            return ctx

        # Intentar entrega en cada canal disponible (prioridad: email > whatsapp > web > ...)
        for canal in self.CANAL_PRIORITY:
            if canal not in canales_disponibles:
                continue

            ctx.intentos_entrega += 1
            exito = self._enviar(canal, ctx)

            if exito:
                ctx.entregada = True
                ctx.canal_exitoso = canal
                self._marcar_entregada(ctx, canal)
                logger.info(f'[DeliveryAgent] {ctx.radicado}: entregado por {canal}')
                break
        else:
            logger.error(f'[DeliveryAgent] {ctx.radicado}: falló entrega en todos los canales')

        return ctx

    def _detectar_canales(self, ctx: PipelineContext) -> list:
        canales = []
        if ctx.ciudadano.email:
            canales.append('email')
        if ctx.ciudadano.telefono:
            canales.append('whatsapp')
        if ctx.canal in ('web', 'instagram'):
            canales.append(ctx.canal)
        return canales

    def _enviar(self, canal: str, ctx: PipelineContext) -> bool:
        """
        Simula envío por canal. En producción: integrar con SMTP, Twilio/Meta API, etc.
        Retorna True si exitoso.
        """
        try:
            if canal == 'email' and ctx.ciudadano.email:
                self._enviar_email(ctx)
                return True
            elif canal == 'whatsapp' and ctx.ciudadano.telefono:
                # Stub: integrar con Meta Cloud API o Twilio
                logger.info(f'[DeliveryAgent] WhatsApp stub → {ctx.ciudadano.telefono[:4]}****')
                return True
            elif canal in ('web', 'instagram'):
                # Disponible en portal de consulta
                return True
        except Exception as e:
            logger.error(f'[DeliveryAgent] Error enviando por {canal}: {e}')
        return False

    def _enviar_email(self, ctx: PipelineContext):
        from django.core.mail import send_mail
        from django.conf import settings

        asunto_email = f'[Alcaldía de Medellín] PQRSD {ctx.radicado} — Acuse de recibo'
        send_mail(
            subject=asunto_email,
            message=ctx.respuesta_texto,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'pqrsd@medellin.gov.co'),
            recipient_list=[ctx.ciudadano.email],
            fail_silently=False,
        )

    def _marcar_entregada(self, ctx: PipelineContext, canal: str):
        if ctx.pqrsd_id:
            from apps.pqrsd.models import PQRSD
            PQRSD.objects.filter(pk=ctx.pqrsd_id).update(
                canal_entrega=canal,
                respuesta_entregada=True,
            )
