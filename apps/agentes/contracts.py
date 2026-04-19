"""
Contratos de datos compartidos entre todos los agentes del pipeline PQRSD.
Cada agente recibe un PipelineContext y devuelve uno actualizado.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CiudadanoData:
    nombre: str = ''
    email: str = ''
    telefono: str = ''
    documento: str = ''
    anonimo: bool = False


@dataclass
class UbicacionData:
    barrio: str = ''
    comuna: str = ''
    direccion: str = ''
    lat: Optional[float] = None
    lng: Optional[float] = None


@dataclass
class PrecedenteData:
    id: str = ''
    similitud: float = 0.0
    respuesta_base: str = ''
    normativa: str = ''
    usado_veces: int = 0


@dataclass
class PipelineContext:
    # Identificación
    radicado: str = ''
    pqrsd_id: Optional[int] = None

    # Entrada
    canal: str = 'web'
    tipo: str = 'peticion'
    asunto: str = ''
    descripcion_raw: str = ''
    ciudadano: CiudadanoData = field(default_factory=CiudadanoData)

    # Filtro (M3)
    admisible: bool = True
    motivo_rechazo: Optional[str] = None
    radicado_duplicado: Optional[str] = None
    notificacion_ciudadano: str = ''

    # División (M4)
    dividida: bool = False
    sub_pqrsds: list = field(default_factory=list)

    # Clasificación (M2)
    secretaria_asignada: str = ''
    secretaria_id: Optional[int] = None
    confianza_clasificacion: float = 0.0
    requiere_revision_humana: bool = False
    ubicacion: UbicacionData = field(default_factory=UbicacionData)
    fecha_limite: str = ''

    # Conocimiento (M6)
    precedentes: list = field(default_factory=list)

    # Respuesta (M5)
    respuesta_texto: str = ''
    respuesta_generada: bool = False

    # Privacidad (M9)
    pii_detectada: list = field(default_factory=list)
    descripcion_anonimizada: str = ''
    consentimiento_registrado: bool = False

    # Entrega (M7)
    entregada: bool = False
    canal_exitoso: str = ''
    intentos_entrega: int = 0

    # SLA (M8)
    dias_restantes: int = 0
    estado_sla: str = 'en_tiempo'

    # Control del pipeline
    errores: list = field(default_factory=list)
    agentes_ejecutados: list = field(default_factory=list)
