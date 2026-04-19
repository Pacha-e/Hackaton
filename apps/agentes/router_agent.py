"""
M2: RouterAgent — Clasifica y enruta a la secretaría competente (Decreto 883/2015).
Modelo: claude-sonnet-4-6 (razonamiento semántico sobre 26 dependencias)
"""
import json
import logging
from .base import BaseAgent, SONNET
from .contracts import PipelineContext

logger = logging.getLogger(__name__)

# 26 dependencias bajo Decreto Municipal 883/2015
SECRETARIAS_CONTEXT = """
SECRETARÍAS Y DEPENDENCIAS — Decreto 883/2015, Alcaldía de Medellín:

SDEC: Secretaría de Desarrollo Económico — empleo, comercio, industria, turismo, emprendimiento
SDIS: Secretaría de Inclusión Social — pobreza, familias vulnerables, adultos mayores, discapacidad
SSPM: Secretaría de Seguridad y Convivencia — policía, violencia, convivencia ciudadana, delincuencia
SMOT: Secretaría de Movilidad — tránsito, señalización, semáforos, transporte público, ciclovías
SOMA: Secretaría de Medio Ambiente — contaminación, animales, árboles, ruido, residuos peligrosos
SSALUD: Secretaría de Salud — hospitales, vacunas, EPS, salud pública, epidemias
SEDU: Secretaría de Educación — colegios, docentes, matrículas, infraestructura educativa
SVIVIENDA: Secretaría de Vivienda — subsidios vivienda, asentamientos, mejoramiento barrial
SOPUB: Secretaría de Obras Públicas — huecos, vías, andenes, puentes, infraestructura vial
EPM: EPM (Empresas Públicas Medellín) — agua, energía, gas, alumbrado público, alcantarillado
METRO: Metro de Medellín — sistema metro, tranvía, metrocable, buses integrados
EMVARIAS: Emvarias — recolección basuras, aseo urbano, reciclaje
PERSONERIA: Personería de Medellín — derechos ciudadanos, quejas contra funcionarios
CONTRALORIA: Contraloría de Medellín — corrupción, manejo recursos públicos
SDEPORTES: Secretaría de Deportes — parques, canchas, polideportivos, eventos deportivos
SCULTURA: Secretaría de Cultura — bibliotecas, patrimonio, eventos culturales, arte
SGENERO: Secretaría de las Mujeres — violencia de género, equidad, programas para mujeres
SJUVENTUD: Secretaría de la Juventud — programas jóvenes, empleo juvenil, espacios juveniles
STIC: Secretaría de TIC — gobierno digital, trámites en línea, conectividad
SHACIEN: Secretaría de Hacienda — impuestos, predial, industria y comercio, deudas municipales
SGENERAL: Secretaría General — contratos, licitaciones, trámites administrativos generales
SGESTION: Secretaría de Gestión Humana — empleados municipales, quejas sobre funcionarios
SPLANEA: Secretaría de Planeación — urbanismo, licencias de construcción, POT
DAPARD: DAPARD — desastres naturales, emergencias, inundaciones, deslizamientos
INDER: INDER — parques, recreación, deporte comunitario, escuelas deportivas
METROPOL: Área Metropolitana — planificación regional, transporte metropolitano
"""

SYSTEM = f"""Eres el agente de enrutamiento del sistema PQRSD de la Alcaldía de Medellín.
Asigna cada PQRSD a la secretaría/dependencia más competente según el Decreto Municipal 883/2015.

{SECRETARIAS_CONTEXT}

Responde SOLO con un JSON válido con esta estructura exacta:
{{
  "secretaria_codigo": "<código de la secretaría, ej: SOPUB>",
  "secretaria_nombre": "<nombre completo>",
  "confianza": <0.0 a 1.0>,
  "requiere_revision_humana": <true|false>,
  "razonamiento": "<máximo 100 caracteres explicando por qué>",
  "requiere_ubicacion": <true|false>,
  "tipo_ubicacion": "<vial|barrio|establecimiento|ninguna>"
}}

requiere_revision_humana=true si confianza < 0.75 o si aplican 2+ secretarías igualmente.
requiere_ubicacion=true para problemas físicos (huecos, basura, alumbrado, obras, etc.)."""


class RouterAgent(BaseAgent):
    model = SONNET
    name = 'RouterAgent'

    def run(self, ctx: PipelineContext) -> PipelineContext:
        from apps.pqrsd.models import PQRSD
        from apps.conocimiento.models import Dependencia

        prompt = f"""Tipo: {ctx.tipo}
Asunto: {ctx.asunto}
Canal: {ctx.canal}
Descripción:
---
{ctx.descripcion_raw}
---
Ubicación mencionada: {ctx.ubicacion.direccion or 'No especificada'}

¿A qué secretaría/dependencia debe enrutarse esta PQRSD?"""

        raw = self.call(SYSTEM, prompt, temperature=0.2)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else {}

        codigo = data.get('secretaria_codigo', '')
        ctx.secretaria_asignada = data.get('secretaria_nombre', codigo)
        ctx.confianza_clasificacion = float(data.get('confianza', 0.5))
        ctx.requiere_revision_humana = data.get('requiere_revision_humana', True)

        # Marcar si necesita captura de ubicación
        if data.get('requiere_ubicacion') and not ctx.ubicacion.direccion:
            ctx.notificacion_ciudadano = (
                ctx.notificacion_ciudadano or ''
            ) + ' Para procesar su solicitud necesitamos la dirección exacta del problema.'

        # Resolver dependencia en DB
        try:
            dep = Dependencia.objects.filter(
                codigo__iexact=codigo
            ).first() or Dependencia.objects.filter(
                nombre__icontains=codigo
            ).first()
            if dep:
                ctx.secretaria_id = dep.pk
                ctx.secretaria_asignada = dep.nombre
        except Exception:
            pass

        # Actualizar PQRSD en DB
        if ctx.pqrsd_id:
            update_fields = {}
            if ctx.secretaria_id:
                update_fields['dependencia_asignada_id'] = ctx.secretaria_id
            if ctx.confianza_clasificacion < 0.75:
                update_fields['estado'] = 'pendiente'
            PQRSD.objects.filter(pk=ctx.pqrsd_id).update(**update_fields)

        logger.info(
            f'[RouterAgent] PQRSD {ctx.radicado} → {ctx.secretaria_asignada} '
            f'(confianza={ctx.confianza_clasificacion:.0%})'
        )
        return ctx
