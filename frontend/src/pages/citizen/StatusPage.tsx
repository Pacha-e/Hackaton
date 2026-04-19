import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { PublicNavbar } from '@/components/layout/PublicNavbar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { citizenApi } from '@/lib/api'
import type { PQRSDStatus } from '@/types'
import { Search, Clock, CheckCircle, AlertTriangle, XCircle, FileText } from 'lucide-react'
import { formatDate, formatDateTime } from '@/lib/utils'

const estadoConfig: Record<string, { label: string; icon: typeof CheckCircle; color: string; bg: string }> = {
  radicada: { label: 'Radicada', icon: FileText, color: 'text-slate-600', bg: 'bg-slate-100' },
  en_clasificacion: { label: 'En Clasificación', icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
  clasificada: { label: 'Clasificada', icon: CheckCircle, color: 'text-blue-600', bg: 'bg-blue-100' },
  en_tramite: { label: 'En Trámite', icon: Clock, color: 'text-indigo-600', bg: 'bg-indigo-100' },
  respondida: { label: 'Respondida', icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-100' },
  cerrada: { label: 'Cerrada', icon: CheckCircle, color: 'text-slate-500', bg: 'bg-slate-100' },
}

const timelineSteps = ['radicada', 'en_clasificacion', 'clasificada', 'en_tramite', 'respondida']

export default function StatusPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [radicado, setRadicado] = useState(searchParams.get('radicado') || '')
  const [pqrsd, setPqrsd] = useState<PQRSDStatus | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const search = async () => {
    if (!radicado.trim()) return
    setLoading(true)
    setError('')
    try {
      setSearchParams({ radicado })
      const { data } = await citizenApi.getStatus(radicado.trim().toUpperCase())
      setPqrsd(data)
    } catch {
      setError('No se encontró ninguna solicitud con ese número de radicado.')
      setPqrsd(null)
    } finally {
      setLoading(false)
    }
  }

  const currentStepIndex = pqrsd ? timelineSteps.indexOf(pqrsd.estado) : -1
  const cfg = pqrsd ? estadoConfig[pqrsd.estado] : null
  const Icon = cfg?.icon || FileText

  return (
    <div className="min-h-screen bg-slate-50">
      <PublicNavbar />

      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-[#00a859]/10 rounded-xl flex items-center justify-center mx-auto mb-3">
            <Search className="h-6 w-6 text-[#00a859]" />
          </div>
          <h1 className="text-2xl font-bold text-slate-800 mb-1">Consultar Estado de PQRSD</h1>
          <p className="text-slate-500 text-sm">Ingresa tu número de radicado para ver el estado de tu solicitud</p>
        </div>

        {/* Search box */}
        <div className="flex gap-2 mb-8">
          <Input
            placeholder="Ej: MDE-202601-00001"
            value={radicado}
            onChange={e => setRadicado(e.target.value.toUpperCase())}
            onKeyDown={e => e.key === 'Enter' && search()}
            className="font-mono uppercase"
          />
          <Button onClick={search} loading={loading} className="shrink-0">
            <Search className="h-4 w-4" />
            Buscar
          </Button>
        </div>

        {error && (
          <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <XCircle className="h-5 w-5 text-red-500 shrink-0" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {pqrsd && (
          <div className="space-y-4">
            {/* Status header */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Radicado</p>
                    <p className="font-mono font-bold text-lg text-slate-800">{pqrsd.radicado}</p>
                  </div>
                  <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${cfg?.bg}`}>
                    <Icon className={`h-4 w-4 ${cfg?.color}`} />
                    <span className={`text-sm font-medium ${cfg?.color}`}>{pqrsd.estado_label}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs text-slate-500">Tipo</p>
                    <p className="text-sm font-medium text-slate-700">{pqrsd.tipo_label}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Asunto</p>
                    <p className="text-sm font-medium text-slate-700 line-clamp-2">{pqrsd.asunto}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Fecha de radicación</p>
                    <p className="text-sm font-medium text-slate-700">{formatDate(pqrsd.fecha_radicacion)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Dependencia asignada</p>
                    <p className="text-sm font-medium text-slate-700">{pqrsd.dependencia_nombre || 'Pendiente de asignación'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* SLA indicator */}
            {pqrsd.fecha_limite && (
              <Card>
                <CardContent className="pt-5 pb-5 space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-slate-700">Plazo de respuesta (Ley 1755/2015)</span>
                    <span className={`font-bold ${pqrsd.vencida ? 'text-red-600' : pqrsd.en_alerta ? 'text-amber-600' : 'text-[#00a859]'}`}>
                      {pqrsd.vencida
                        ? 'Vencido'
                        : pqrsd.estado === 'respondida'
                        ? 'Respondido'
                        : `${pqrsd.dias_restantes} días restantes`}
                    </span>
                  </div>

                  {pqrsd.estado !== 'respondida' && pqrsd.estado !== 'cerrada' && (
                    <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          pqrsd.vencida
                            ? 'bg-red-500 w-full'
                            : pqrsd.en_alerta
                            ? 'bg-amber-500'
                            : 'bg-[#00a859]'
                        }`}
                        style={{
                          width: pqrsd.vencida
                            ? '100%'
                            : `${Math.max(5, 100 - ((pqrsd.dias_restantes ?? 15) / 15) * 100)}%`,
                        }}
                      />
                    </div>
                  )}

                  {pqrsd.vencida ? (
                    <div className="flex items-center gap-2 text-xs text-red-600">
                      <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                      El plazo ha expirado. La entidad está obligada a responder inmediatamente.
                    </div>
                  ) : pqrsd.en_alerta ? (
                    <div className="flex items-center gap-2 text-xs text-amber-600">
                      <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                      Vence el {formatDate(pqrsd.fecha_limite)}. La entidad está en proceso de respuesta.
                    </div>
                  ) : pqrsd.estado === 'respondida' ? (
                    <div className="flex items-center gap-2 text-xs text-emerald-600">
                      <CheckCircle className="h-3.5 w-3.5 shrink-0" />
                      Respondida el {formatDateTime(pqrsd.fecha_respuesta)}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Clock className="h-3.5 w-3.5 shrink-0" />
                      Fecha límite: {formatDate(pqrsd.fecha_limite)}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Timeline */}
            <Card>
              <CardContent className="pt-5 pb-5">
                <h3 className="text-sm font-semibold text-slate-700 mb-4">Progreso de tu solicitud</h3>
                <div className="flex items-center">
                  {timelineSteps.map((step, i) => {
                    const done = i <= currentStepIndex
                    const current = i === currentStepIndex
                    const cfg2 = estadoConfig[step]
                    return (
                      <div key={step} className="flex items-center flex-1 last:flex-none">
                        <div className="flex flex-col items-center">
                          <div className={`w-7 h-7 rounded-full flex items-center justify-center border-2 transition-colors ${
                            done
                              ? 'bg-[#00a859] border-[#00a859]'
                              : 'bg-white border-slate-300'
                          } ${current ? 'ring-2 ring-[#00a859]/30' : ''}`}>
                            {done ? (
                              <CheckCircle className="h-4 w-4 text-white" />
                            ) : (
                              <div className="w-2 h-2 bg-slate-300 rounded-full" />
                            )}
                          </div>
                          <span className={`text-xs mt-1 text-center w-16 leading-tight ${done ? 'text-[#00a859] font-medium' : 'text-slate-400'}`}>
                            {cfg2?.label}
                          </span>
                        </div>
                        {i < timelineSteps.length - 1 && (
                          <div className={`flex-1 h-0.5 mx-1 mb-4 ${i < currentStepIndex ? 'bg-[#00a859]' : 'bg-slate-200'}`} />
                        )}
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Example notice */}
        {!pqrsd && !error && (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500">Ingresa tu número de radicado para consultar el estado de tu solicitud.</p>
            <p className="text-xs text-slate-400 mt-1">Formato: MDE-AAAAMM-NNNNN</p>
          </div>
        )}
      </div>
    </div>
  )
}
