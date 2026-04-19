import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { staffApi } from '@/lib/api'
import type { InboxMessage } from '@/types'
import { StaffSidebar } from '@/components/layout/StaffSidebar'
import { Button } from '@/components/ui/button'
import { PageLoader } from '@/components/ui/spinner'
import { EstadoBadge } from '@/components/staff/EstadoBadge'
import { PriorityBadge } from '@/components/staff/PriorityBadge'
import { CanalIcon } from '@/components/staff/CanalIcon'
import {
  Inbox, AlertTriangle, RefreshCw, ArrowRight, CheckCircle, Circle
} from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'

const CANALES = [
  { value: '', label: 'Todos los canales' },
  { value: 'whatsapp', label: 'WhatsApp', color: 'bg-green-500' },
  { value: 'email', label: 'Email', color: 'bg-purple-500' },
  { value: 'web', label: 'Web', color: 'bg-blue-500' },
  { value: 'instagram', label: 'Instagram', color: 'bg-pink-500' },
  { value: 'presencial', label: 'Presencial', color: 'bg-orange-500' },
]

export default function InboxPage() {
  const [selectedCanal, setSelectedCanal] = useState('')
  const [soloNoLeidos, setSoloNoLeidos] = useState(false)
  const qc = useQueryClient()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['inbox', selectedCanal, soloNoLeidos],
    queryFn: async () => {
      const params: Record<string, string> = {}
      if (selectedCanal) params.canal = selectedCanal
      if (soloNoLeidos) params.no_leidos = '1'
      const { data } = await staffApi.getInbox(params)
      return data as { count: number; results: InboxMessage[] }
    },
    refetchInterval: 15000,
  })

  const messages = data?.results || []

  return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Inbox className="h-5 w-5 text-[#00a859]" />
              <div>
                <h1 className="text-xl font-bold text-slate-800">Bandeja Multicanal</h1>
                <p className="text-sm text-slate-500">
                  {data?.count || 0} mensajes
                  {soloNoLeidos ? ' sin leer' : ' en total'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSoloNoLeidos(!soloNoLeidos)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                  soloNoLeidos
                    ? 'bg-[#00a859] border-[#00a859] text-white'
                    : 'bg-white border-slate-300 text-slate-600 hover:border-[#00a859]'
                }`}
              >
                <Circle className="h-3 w-3" />
                Sin leer
              </button>
              <button
                onClick={() => refetch()}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-500"
                title="Actualizar"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <div className="flex h-[calc(100vh-73px)]">
          {/* Canal sidebar */}
          <div className="w-52 bg-white border-r border-slate-200 p-3 space-y-1">
            <p className="text-xs font-semibold text-slate-400 uppercase px-2 mb-2">Canales</p>
            {CANALES.map((canal) => {
              const count = canal.value
                ? messages.filter(m => m.canal === canal.value).length
                : messages.length
              return (
                <button
                  key={canal.value}
                  onClick={() => setSelectedCanal(canal.value)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedCanal === canal.value
                      ? 'bg-[#00a859] text-white'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {canal.color && (
                      <div className={`w-2 h-2 rounded-full ${canal.color}`} />
                    )}
                    {canal.label}
                  </div>
                  {count > 0 && (
                    <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full ${
                      selectedCanal === canal.value ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {count}
                    </span>
                  )}
                </button>
              )
            })}
          </div>

          {/* Message list */}
          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <PageLoader />
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64">
                <Inbox className="h-10 w-10 text-slate-300 mb-3" />
                <p className="text-slate-500 text-sm">No hay mensajes en esta bandeja.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {messages.map((msg) => (
                  <Link
                    key={msg.id}
                    to={`/staff/pqrsd/${msg.id}`}
                    className={`flex items-start gap-4 p-4 hover:bg-slate-50 transition-colors group ${
                      !msg.leido ? 'bg-blue-50/30' : ''
                    } ${msg.vencida ? 'bg-red-50/40' : msg.en_alerta ? 'bg-amber-50/40' : ''}`}
                  >
                    {/* Read indicator */}
                    <div className="mt-1 shrink-0">
                      {!msg.leido
                        ? <div className="w-2.5 h-2.5 bg-blue-500 rounded-full" />
                        : <div className="w-2.5 h-2.5 bg-transparent rounded-full" />
                      }
                    </div>

                    {/* Canal icon */}
                    <CanalIcon canal={msg.canal} />

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className={`text-sm font-medium truncate ${!msg.leido ? 'text-slate-900' : 'text-slate-700'}`}>
                          {msg.remitente}
                        </span>
                        <span className="text-xs text-slate-400 shrink-0 ml-2">
                          {formatRelativeTime(msg.timestamp)}
                        </span>
                      </div>
                      <p className={`text-sm truncate mb-1 ${!msg.leido ? 'font-semibold text-slate-800' : 'text-slate-600'}`}>
                        {msg.asunto}
                      </p>
                      <p className="text-xs text-slate-400 truncate">{msg.preview}</p>
                      <div className="flex items-center gap-2 mt-1.5">
                        <EstadoBadge estado={msg.estado} />
                        <PriorityBadge prioridad={msg.prioridad} />
                        {msg.vencida && (
                          <span className="flex items-center gap-0.5 text-xs text-red-600 font-medium">
                            <AlertTriangle className="h-3 w-3" /> Vencida
                          </span>
                        )}
                        {msg.en_alerta && !msg.vencida && (
                          <span className="flex items-center gap-0.5 text-xs text-amber-600">
                            <AlertTriangle className="h-3 w-3" /> {msg.dias_restantes}d
                          </span>
                        )}
                        {msg.clasificacion_validada && (
                          <span className="flex items-center gap-0.5 text-xs text-emerald-600">
                            <CheckCircle className="h-3 w-3" /> Clasificado
                          </span>
                        )}
                      </div>
                    </div>

                    <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-[#00a859] transition-colors mt-1 shrink-0" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
