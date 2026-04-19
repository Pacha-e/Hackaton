export interface Dependencia {
  id: number
  nombre: string
  sigla: string
  descripcion: string
  competencias: string
  email_contacto: string
  telefono: string
  activa: boolean
}

export interface ClasificacionIA {
  id: number
  tipo_sugerido: string
  prioridad_sugerida: string
  razon_clasificacion: string
  confianza: number | null
  modelo_usado: string
  fecha_clasificacion: string
  validado_por: number | null
  validado_por_nombre: string | null
  fecha_validacion: string | null
  aceptada: boolean | null
  comentario_validacion: string
  dependencias_sugeridas: number[]
}

export interface Sintesis {
  id: number
  resumen_ejecutivo: string
  problema_central: string
  accion_requerida: string
  datos_contextuales: Record<string, unknown>
  entidades_mencionadas: string[]
  normativa_aplicable: string
  recomendacion_respuesta: string
  fecha_generacion: string
  generado_por_ia: boolean
}

export interface PQRSD {
  id: number
  radicado: string
  tipo: string
  tipo_label: string
  estado: string
  estado_label: string
  canal_entrada: string
  canal_label: string
  prioridad: string
  prioridad_label: string
  anonimo: boolean
  nombre_ciudadano: string
  email_ciudadano: string
  telefono_ciudadano: string
  documento_ciudadano: string
  comuna: string
  barrio: string
  asunto: string
  descripcion: string
  archivo_adjunto: string | null
  dependencia_asignada: number | null
  dependencia_asignada_info: Dependencia | null
  dependencia_asignada_nombre: string | null
  dependencia_sugerida: number | null
  dependencia_sugerida_info: Dependencia | null
  confianza_clasificacion: number | null
  clasificacion_validada: boolean
  funcionario_asignado: number | null
  funcionario_nombre: string | null
  fecha_radicacion: string
  fecha_limite: string | null
  fecha_respuesta: string | null
  observaciones_funcionario: string
  clasificacion_ia: ClasificacionIA | null
  sintesis: Sintesis | null
  dias_restantes: number | null
  en_alerta: boolean
  vencida: boolean
}

export interface PQRSDStatus {
  radicado: string
  tipo: string
  tipo_label: string
  estado: string
  estado_label: string
  asunto: string
  fecha_radicacion: string
  fecha_limite: string | null
  fecha_respuesta: string | null
  dependencia_nombre: string | null
  clasificacion_validada: boolean
  dias_restantes: number | null
  en_alerta: boolean
  vencida: boolean
}

export interface Stats {
  total: number
  radicadas: number
  en_clasificacion: number
  clasificadas: number
  en_tramite: number
  respondidas: number
  cerradas: number
  sin_clasificar: number
  alertas: number
  vencidas: number
  por_canal: Record<string, number>
  por_tipo: Record<string, number>
}

export interface InboxMessage {
  id: number
  radicado: string
  canal: string
  canal_label: string
  remitente: string
  asunto: string
  preview: string
  timestamp: string
  estado: string
  prioridad: string
  leido: boolean
  clasificacion_validada: boolean
  dias_restantes: number | null
  en_alerta: boolean
  vencida: boolean
}

export interface Choice {
  value: string
  label: string
}

export interface Choices {
  tipo: Choice[]
  estado: Choice[]
  canal: Choice[]
  prioridad: Choice[]
}

export interface AuthUser {
  authenticated: boolean
  id?: number
  username?: string
  fullName?: string
  isStaff?: boolean
}
