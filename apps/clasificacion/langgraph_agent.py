import json
import logging
from typing import TypedDict, Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from django.conf import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# 1. Definimos el Estado (Memoria del Agente)
class AgentState(TypedDict):
    asunto: str
    descripcion: str
    canal: str
    dependencias_texto: str
    
    # Salidas del agente
    clasificacion: Optional[Dict[str, Any]]
    sintesis: Optional[Dict[str, Any]]
    
    # Metadatos del flujo
    errores: List[str]


# 2. Definimos las estructuras esperadas (Pydantic para Structured Output)
class ClasificacionOutput(BaseModel):
    dependencia_id: int = Field(description="ID numérico de la dependencia más competente")
    dependencia_nombre: str = Field(description="Sigla de la dependencia")
    tipo_sugerido: str = Field(description="peticion, queja, reclamo, sugerencia, denuncia o correspondencia")
    prioridad_sugerida: str = Field(description="baja, media, alta o urgente")
    confianza: int = Field(description="Porcentaje de confianza (0-100)")
    razon: str = Field(description="Explicación breve de la clasificación")

class SintesisOutput(BaseModel):
    resumen_ejecutivo: str = Field(description="2-3 oraciones que resumen todo")
    problema_central: str = Field(description="Descripción del problema principal")
    accion_requerida: str = Field(description="Qué debe hacer la Alcaldía (infinitivo)")
    lugar_mencionado: str = Field(default="No especificado")
    fecha_hecho: str = Field(default="No especificada")
    entidades_mencionadas: List[str] = Field(default=[])
    normativa_aplicable: str = Field(description="Leyes o decretos relevantes")


# 3. Inicializamos el LLM
def get_llm():
    api_key = settings.GEMINI_API_KEY
    if not api_key or "REEMPLAZAR" in api_key:
        raise ValueError("GEMINI_API_KEY no configurada. El agente requiere API conectada.")
    
    # modelo flash - gratuito y rápido
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1, # Temperatura baja = respuestas lógicas y estructuradas
        api_key=api_key
    )

# 4. NODOS DEL GRAFO
def nodo_clasificar(state: AgentState):
    """Nodo responsable de clasificar la PQRSD"""
    logger.info("--- NODO: CLASIFICAR ---")
    llm = get_llm()
    
    # Usamos .with_structured_output de LangChain para forzar JSON perfecto
    llm_structured = llm.with_structured_output(ClasificacionOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un experto clasificador de PQRSD para la Alcaldía de Medellín.\n\nDEPENDENCIAS DISPONIBLES:\n{dependencias_texto}"),
        ("human", "Analiza esto:\nAsunto: {asunto}\nDescripción: {descripcion}\nCanal: {canal}")
    ])
    
    chain = prompt | llm_structured
    
    try:
        resultado = chain.invoke({
            "dependencias_texto": state["dependencias_texto"],
            "asunto": state["asunto"],
            "descripcion": state["descripcion"],
            "canal": state["canal"]
        })
        return {"clasificacion": resultado.dict()}
    except Exception as e:
        logger.error(f"Error clasificando: {e}")
        return {"errores": state.get("errores", []) + [str(e)]}

def nodo_sintetizar(state: AgentState):
    """Nodo responsable de resumir y extraer info clave"""
    logger.info("--- NODO: SINTETIZAR ---")
    llm = get_llm()
    llm_structured = llm.with_structured_output(SintesisOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente legal que resume radicados PQRSD. Genera síntesis ejecutivas estructuradas."),
        ("human", "Resume este caso:\nAsunto: {asunto}\nDescripción: {descripcion}")
    ])
    
    chain = prompt | llm_structured
    
    try:
        resultado = chain.invoke({
            "asunto": state["asunto"],
            "descripcion": state["descripcion"]
        })
        
        # Mapeo a tu formato de capas 
        sintesis_dict = resultado.dict()
        sintesis_final = {
            "resumen_ejecutivo": sintesis_dict["resumen_ejecutivo"],
            "problema_central": sintesis_dict["problema_central"],
            "accion_requerida": sintesis_dict["accion_requerida"],
            "datos_contextuales": {
                "lugar_mencionado": sintesis_dict["lugar_mencionado"],
                "fecha_hecho": sintesis_dict["fecha_hecho"]
            },
            "entidades_mencionadas": sintesis_dict["entidades_mencionadas"],
            "normativa_aplicable": sintesis_dict["normativa_aplicable"]
        }
        return {"sintesis": sintesis_final}
    except Exception as e:
        logger.error(f"Error sintetizando: {e}")
        return {"errores": state.get("errores", []) + [str(e)]}


# 5. ENSAMBLE DEL GRAFO LANGGRAPH
def construir_agente():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("clasificar", nodo_clasificar)
    workflow.add_node("sintetizar", nodo_sintetizar)
    
    # Definimos el flujo secuencial (En paralelo también funcionaría, pero aquí lo haremos paso a paso)
    workflow.set_entry_point("clasificar")
    workflow.add_edge("clasificar", "sintetizar")
    workflow.add_edge("sintetizar", END)
    
    # Compilar el orquestador
    agent_app = workflow.compile()
    return agent_app

# 6. FUNCIÓN DE ENVOLTORIO
def procesar_pqrsd_con_agente(pqrsd_obj) -> dict:
    """Llama al agente compilado y lo invoca obteniendo clasificación y síntesis"""
    from apps.conocimiento.models import Dependencia
    
    deps_activas = Dependencia.objects.filter(activa=True)
    deps_texto = "\n".join([
        f"- ID {d.pk} | {d.sigla}: {d.nombre}. Competencias: {d.competencias[:150]}" 
        for d in deps_activas
    ])
    
    estado_inicial = {
        "asunto": pqrsd_obj.asunto,
        "descripcion": pqrsd_obj.descripcion,
        "canal": pqrsd_obj.canal_entrada,
        "dependencias_texto": deps_texto,
        "errores": []
    }
    
    agente = construir_agente()
    
    # config para name / tags en la trazabilidad (observabilidad Langsmith / Langfuse)
    config = {
        "configurable": {"thread_id": f"pqrsd_{pqrsd_obj.radicado}"},
        "tags": ["hackaton-omega", "pqrsd-pipeline"]
    }
    
    # Ejecutamos el flujo completo de grafos
    resultado_final = agente.invoke(estado_inicial, config=config)
    return resultado_final
