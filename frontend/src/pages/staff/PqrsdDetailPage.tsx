import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { staffApi, citizenApi } from '@/lib/api'
import type { PQRSD, Dependencia } from '@/types'
import { StaffSidebar } from '@/components/layout/StaffSidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { PageLoader } from '@/components/ui/spinner'
import { EstadoBadge } from '@/components/staff/EstadoBadge'
import { PriorityBadge } from '@/components/staff/PriorityBadge'
import { CanalIcon } from '@/components/staff/CanalIcon'
import { Badge } from '@/components/ui/badge'
import {
  ArrowLeft, User, MapPin, Calendar, Clock, AlertTriangle,
  CheckCircle, XCircle, Brain, FileText, Building2, Zap
} from 'lucide-react'
import { formatDate, formatDateTime } from '@/lib/utils'

export default function PqrsdDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const numId = parseInt(id || '0')

  const [newEstado, setNewEstado] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [classifying, setClassifying] = useState(false)
  const [validating, setValidating] = useState(false)
  const [genSynthesis, setGenSynthesis] = useState(false)
  const [selectedDep, setSelectedDep] = useState('')
  const [validComment, setValidComment] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const { data: pqrsd, isLoading } = useQuery<PQRSD>({
    queryKey: ['pqrsd', numId],
    queryFn: async () => {
      const { data } = await staffApi.getPqrsd(numId)
      return data
    },
  })

  const { data: deps } = useQuery<Dependencia[]>({
    queryKey: ['dependencias'],
    queryFn: async () => {
      const { data } = await citizenApi.getDependencias()
      return data
    },
  })

  const updateEstadoMutation = useMutation({
    mutationFn: (data: { estado: string; observaciones?: string; dependencia_asignada?: number }) =>
      staffApi.updateEstado(numId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['pqrsd', numId] })
      qc.invalidateQueries({ queryKey: ['stats'] })
      setSuccessMsg('Estado actualizado correctamente.')
      setTimeout(() => setSuccessMsg(''), 3000)
    },
  })

  const handleClassify = async () => {
    setClassifying(true)
    try {
      await staffApi.classify(numId)
      qc.invalidateQueries({ queryKey: ['pqrsd', numId] })
      setSuccessMsg('Clasificación IA generada. Valida la sugerencia abajo.')
    } catch {
      setSuccessMsg('Error al clasificar. Intenta de nuevo.')
    } finally {
      setClassifying(false)
      setTimeout(() => setSuccessMsg(''), 4000)
    }
  }

  const handleValidate = async (aceptada: boolean) => {
    setValidating(true)
    try {
      await staffApi.validateClassification(numId, {
        aceptada,
        comentario: validComment,
        dependencia_id: selectedDep ? parseInt(selectedDep) : undefined,
      })
      qc.invalidateQueries({ queryKey: ['pqrsd', numId] })
      setSuccessMsg(`Clasificación ${aceptada ? 'aceptada' : 'rechazada'}.`)
    } catch {
      setSuccessMsg('Error al validar. Intenta de nuevo.')
    } finally {
      setValidating(false)
      setTimeout(() => setSuccessMsg(''), 3000)
    }
  }

  const handleGenerateSynthesis = async () => {
    setGenSynthesis(true)
    try {
      await staffApi.generateSynthesis(numId)
      qc.invalidateQueries({ queryKey: ['pqrsd', numId] })
      setSuccessMsg('Síntesis generada exitosamente.')
    } catch {
      setSuccessMsg('Error al generar la síntesis.')
    } finally {
      setGenSynthesis(false)
      setTimeout(() => setSuccessMsg(''), 3000)
    }
  }

  if (isLoading) return (
    <div className="flex h-screen">
      <StaffSidebar />
      <div className="flex-1"><PageLoader /></div>
    </div>
  )

  if (!pqrsd) return (
    <div className="flex h-screen">
      <StaffSidebar />
      <div className="flex-1 p-8"><p>PQRSD no encontrada.</p></div>
    </div>
  )

  const estadoOptions = [
    { value: 'radicada', label: 'Radicada' },
    { value: 'en_clasificacion', label: 'En Clasificación' },
    { value: 'clasificada', label: 'Clasificada' },
    { value: 'en_tramite', label: 'En Trámite' },
    { value: 'respondida', label: 'Respondida' },
    { value: 'cerrada', label: 'Cerrada' },
  ]

  return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-4 sticky top-0 z-10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate(-1)}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-500"
              >
                <ArrowLeft className="h-4 w-4" />
              </button>
              <div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm text-slate-500">{pqrsd.radicado}</span>
                  <EstadoBadge estado={pqrsd.estado} />
                  <PriorityBadge prioridad={pqrsd.prioridad} />
                  {pqrsd.vencida && (
                    <Badge variant="danger" className="animate-pulse-alert">
                      <AlertTriangle className="h-3 w-3" /> Vencida
                    </Badge>
                  )}
                  {pqrsd.en_alerta && !pqrsd.vencida && (
                    <Badge variant="warning">
                      <AlertTriangle className="h-3 w-3" /> Alerta SLA
                    </Badge>
                  )}
                </div>
                <h1 className="text-lg font-bold text-slate-800 mt-0.5">{pqrsd.asunto}</h1>
              </div>
            </div>
          </div>
        </div>

        {successMsg && (
          <div className="mx-6 mt-4 flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg p-3">
            <CheckCircle className="h-4 w-4 text-blue-500" />
            <p className="text-sm text-blue-700">{successMsg}</p>
          </div>
        )}

        <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column — main info */}
          <div className="lg:col-span-2 space-y-4">
            {/* Metadata */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <FileText className="h-4 w-4" /> Información general
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Tipo</p>
                  <p className="font-medium">{pqrsd.tipo_label}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">Canal de entrada</p>
                  <CanalIcon canal={pqrsd.canal_entrada} showLabel size="sm" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">Fecha radicación</p>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" />
                    <p className="font-medium">{formatDateTime(pqrsd.fecha_radicacion)}</p>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">Fecha límite</p>
                  <div className={`flex items-center gap-1 ${pqrsd.vencida ? 'text-red-600' : pqrsd.en_alerta ? 'text-amber-600' : ''}`}>
                    <Clock className="h-3.5 w-3.5" />
                    <p className="font-medium">{formatDate(pqrsd.fecha_limite)}</p>
                    {pqrsd.dias_restantes !== null && (
                      <span className="text-xs">({pqrsd.dias_restantes}d)</span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Descripción</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{pqrsd.descripcion}</p>
              </CardContent>
            </Card>

            {/* Citizen */}
            {!pqrsd.anonimo && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm flex items-center gap-2">
                    <User className="h-4 w-4" /> Ciudadano
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-3 text-sm">
                  {pqrsd.nombre_ciudadano && (
                    <div>
                      <p className="text-xs text-slate-500">Nombre</p>
                      <p className="font-medium">{pqrsd.nombre_ciudadano}</p>
                    </div>
                  )}
                  {pqrsd.documento_ciudadano && (
                    <div>
                      <p className="text-xs text-slate-500">Documento</p>
                      <p className="font-medium">{pqrsd.documento_ciudadano}</p>
                    </div>
                  )}
                  {pqrsd.email_ciudadano && (
                    <div>
                      <p className="text-xs text-slate-500">Email</p>
                      <p className="font-medium">{pqrsd.email_ciudadano}</p>
                    </div>
                  )}
                  {pqrsd.telefono_ciudadano && (
                    <div>
                      <p className="text-xs text-slate-500">Teléfono</p>
                      <p className="font-medium">{pqrsd.telefono_ciudadano}</p>
                    </div>
                  )}
                  {pqrsd.comuna && (
                    <div>
                      <p className="text-xs text-slate-500">Ubicación</p>
                      <p className="font-medium flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-slate-400" />
                        {pqrsd.comuna}{pqrsd.barrio && ` — ${pqrsd.barrio}`}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* AI Classification */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Brain className="h-4 w-4 text-purple-500" /> Clasificación IA
                  </CardTitle>
                  {!pqrsd.clasificacion_ia && (
                    <Button size="sm" onClick={handleClassify} loading={classifying} variant="outline">
                      <Zap className="h-3.5 w-3.5" />
                      Clasificar
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {pqrsd.clasificacion_ia ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-3 gap-3 text-sm">
                      <div className="bg-purple-50 rounded-lg p-3">
                        <p className="text-xs text-purple-600 mb-1">Tipo sugerido</p>
                        <p className="font-semibold text-purple-800">{pqrsd.clasificacion_ia.tipo_sugerido}</p>
                      </div>
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs text-blue-600 mb-1">Prioridad sugerida</p>
                        <p className="font-semibold text-blue-800">{pqrsd.clasificacion_ia.prioridad_sugerida}</p>
                      </div>
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs text-blue-600 mb-1">Confianza IA</p>
                        <p className="font-semibold text-blue-800">{pqrsd.clasificacion_ia.confianza}%</p>
                      </div>
                    </div>
                    <div className="bg-slate-50 rounded-lg p-3">
                      <p className="text-xs text-slate-500 mb-1">Razón de clasificación</p>
                      <p className="text-sm text-slate-700">{pqrsd.clasificacion_ia.razon_clasificacion}</p>
                    </div>

                    {/* Validation */}
                    {pqrsd.clasificacion_ia.aceptada === null ? (
                      <div className="border border-amber-200 bg-amber-50 rounded-lg p-4 space-y-3">
                        <p className="text-sm font-semibold text-amber-700 flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4" />
                          Requiere validación humana
                        </p>
                        <p className="text-xs text-amber-600">
                          Departamento sugerido: <strong>{pqrsd.dependencia_sugerida_info?.nombre || 'Sin sugerencia'}</strong>
                        </p>
                        <Select
                          options={(deps || []).map(d => ({ value: String(d.id), label: `${d.sigla} — ${d.nombre}` }))}
                          placeholder="Cambiar departamento (opcional)"
                          value={selectedDep}
                          onChange={e => setSelectedDep(e.target.value)}
                        />
                        <Textarea
                          placeholder="Comentario de validación (opcional)"
                          rows={2}
                          value={validComment}
                          onChange={e => setValidComment(e.target.value)}
                        />
                        <div className="flex gap-2">
                          <Button
                            onClick={() => handleValidate(true)}
                            loading={validating}
                            className="flex-1"
                            size="sm"
                          >
                            <CheckCircle className="h-4 w-4" />
                            Aceptar
                          </Button>
                          <Button
                            variant="danger"
                            onClick={() => handleValidate(false)}
                            loading={validating}
                            className="flex-1"
                            size="sm"
                          >
                            <XCircle className="h-4 w-4" />
                            Rechazar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className={`flex items-center gap-2 p-3 rounded-lg ${pqrsd.clasificacion_ia.aceptada ? 'bg-blue-50 border border-blue-200' : 'bg-red-50 border border-red-200'}`}>
                        {pqrsd.clasificacion_ia.aceptada
                          ? <CheckCircle className="h-4 w-4 text-blue-500" />
                          : <XCircle className="h-4 w-4 text-red-500" />
                        }
                        <span className="text-sm font-medium">
                          {pqrsd.clasificacion_ia.aceptada ? 'Clasificación aceptada' : 'Clasificación rechazada'}
                          {pqrsd.clasificacion_ia.validado_por_nombre && ` por ${pqrsd.clasificacion_ia.validado_por_nombre}`}
                        </span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <Brain className="h-8 w-8 text-slate-300 mx-auto mb-2" />
                    <p className="text-sm text-slate-500">Sin clasificación IA. Haz clic en "Clasificar" para analizar esta solicitud.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* AI Synthesis */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <FileText className="h-4 w-4 text-blue-500" /> Síntesis IA
                  </CardTitle>
                  {!pqrsd.sintesis && (
                    <Button size="sm" onClick={handleGenerateSynthesis} loading={genSynthesis} variant="outline">
                      <Zap className="h-3.5 w-3.5" />
                      Generar síntesis
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {pqrsd.sintesis ? (
                  <div className="space-y-3">
                    <div className="bg-blue-50 rounded-lg p-3">
                      <p className="text-xs text-blue-600 font-medium mb-1">Resumen ejecutivo</p>
                      <p className="text-sm text-blue-800">{pqrsd.sintesis.resumen_ejecutivo}</p>
                    </div>
                    {pqrsd.sintesis.problema_central && (
                      <div className="bg-slate-50 rounded-lg p-3">
                        <p className="text-xs text-slate-500 mb-1">Problema central</p>
                        <p className="text-sm">{pqrsd.sintesis.problema_central}</p>
                      </div>
                    )}
                    {pqrsd.sintesis.accion_requerida && (
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs text-blue-600 mb-1">Acción requerida</p>
                        <p className="text-sm text-blue-800">{pqrsd.sintesis.accion_requerida}</p>
                      </div>
                    )}
                    {pqrsd.sintesis.normativa_aplicable && (
                      <div className="bg-purple-50 rounded-lg p-3">
                        <p className="text-xs text-purple-600 mb-1">Normativa aplicable</p>
                        <p className="text-sm text-purple-800">{pqrsd.sintesis.normativa_aplicable}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <FileText className="h-8 w-8 text-slate-300 mx-auto mb-2" />
                    <p className="text-sm text-slate-500">Sin síntesis. Haz clic en "Generar síntesis" para crear un resumen IA.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right column — actions */}
          <div className="space-y-4">
            {/* Assignment */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Building2 className="h-4 w-4" /> Dependencia asignada
                </CardTitle>
              </CardHeader>
              <CardContent>
                {pqrsd.dependencia_asignada_info ? (
                  <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
                    <p className="font-semibold text-blue-800">{pqrsd.dependencia_asignada_info.sigla}</p>
                    <p className="text-xs text-blue-600">{pqrsd.dependencia_asignada_info.nombre}</p>
                    {pqrsd.dependencia_asignada_info.email_contacto && (
                      <p className="text-xs text-blue-500 mt-1">{pqrsd.dependencia_asignada_info.email_contacto}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-amber-600 flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Sin asignar
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Change state */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Cambiar estado</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Select
                  options={estadoOptions}
                  placeholder="Selecciona nuevo estado..."
                  value={newEstado}
                  onChange={e => setNewEstado(e.target.value)}
                />
                <Textarea
                  placeholder="Observaciones (opcional)"
                  rows={3}
                  value={observaciones}
                  onChange={e => setObservaciones(e.target.value)}
                />
                {newEstado === 'clasificada' && (
                  <Select
                    options={(deps || []).map(d => ({ value: String(d.id), label: `${d.sigla} — ${d.nombre}` }))}
                    placeholder="Asignar dependencia..."
                    value={selectedDep}
                    onChange={e => setSelectedDep(e.target.value)}
                  />
                )}
                <Button
                  className="w-full"
                  disabled={!newEstado}
                  loading={updateEstadoMutation.isPending}
                  onClick={() => updateEstadoMutation.mutate({
                    estado: newEstado,
                    observaciones,
                    dependencia_asignada: selectedDep ? parseInt(selectedDep) : undefined,
                  })}
                >
                  Actualizar estado
                </Button>
              </CardContent>
            </Card>

            {/* Notes */}
            {pqrsd.observaciones_funcionario && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Observaciones del funcionario</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-700">{pqrsd.observaciones_funcionario}</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
