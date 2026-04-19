"""
Clase base para todos los agentes del pipeline PQRSD.
"""
import logging
from django.conf import settings
from .contracts import PipelineContext

logger = logging.getLogger(__name__)

HAIKU = 'claude-haiku-4-5-20251001'
SONNET = 'claude-sonnet-4-6'
OPUS = 'claude-opus-4-7'


class BaseAgent:
    model: str = SONNET
    name: str = 'BaseAgent'

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._client

    def call(self, system: str, prompt: str, temperature: float = 0.3, max_tokens: int = 2048) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{'role': 'user', 'content': prompt}],
        )
        return response.content[0].text

    def run(self, ctx: PipelineContext) -> PipelineContext:
        raise NotImplementedError

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        try:
            ctx = self.run(ctx)
            ctx.agentes_ejecutados.append(self.name)
        except Exception as e:
            logger.error(f'[{self.name}] Error: {e}')
            ctx.errores.append({'agente': self.name, 'error': str(e)})
        return ctx
