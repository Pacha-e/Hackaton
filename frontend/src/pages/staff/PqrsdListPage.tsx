import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { staffApi, citizenApi } from '@/lib/api'
import type { PQRSD, Dependencia, Choices } from '@/types'
import { StaffSidebar } from '@/components/layout/StaffSidebar'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { TableRowSkeleton } from '@/components/ui/skeleton'
import { EstadoBadge } from '@/components/staff/EstadoBadge'
import { PriorityBadge } from '@/components/staff/PriorityBadge'
import { CanalIcon } from '@/components/staff/CanalIcon'
import { Search, Filter, AlertTriangle, ArrowRight, RotateCcw } from 'lucide-react'
import { formatDate, formatRelativeTime } from '@/lib/utils'

export default function PqrsdListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [search, setSearch] = useState(searchParams.get('q') || '')

  const filters = {
    q: searchParams.get('q') || '',
    estado: searchParams.get('estado') || '',
    tipo: searchParams.get('tipo') || '',
    canal: searchParams.get('canal') || '',
    dependencia: searchParams.get('dependencia') || '',
    prioridad: searchParams.get('prioridad') || '',
    alertas: searchParams.get('alertas') || '',
    sin_clasificar: searchParams.get('sin_clasificar') || '',
  }

  const updateFilter = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next)
  }

  const clearFilters = () => {
    setSearch('')
    setSearchParams({})
  }

  const { data, isLoading } = useQuery({
    queryKey: ['pqrsd', 'list', Object.fromEntries(searchParams)],
    queryFn: async () => {
      const { data } = await staffApi.listPqrsd(Object.fromEntries(searchParams))
      return data as { count: number; results: PQRSD[] }
    },
  })

  const { data: deps } = useQuery<Dependencia[]>({
    queryKey: ['dependencias'],
    queryFn: async () => {
      const { data } = await citizenApi.getDependencias()
      return data
    },
  })

  const { data: choices } = useQuery<Choices>({
    queryKey: ['choices'],
    queryFn: async () => {
      const { data } = await citizenApi.getChoices()
      return data
    },
  })

  const hasFilters = Object.values(filters).some(Boolean)

  return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-slate-800">PQRSD Recibidas</h1>
              <p className="text-sm text-slate-500">
                {data ? `${data.count} solicitudes` : 'Cargando...'}
                {filters.alertas === '1' && ' — Solo alertas SLA'}
                {filters.sin_clasificar === '1' && ' — Sin clasificar'}
              </p>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-4">
          {/* Filters */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
              <Filter className="h-4 w-4" />
              Filtros
              {hasFilters && (
                <button onClick={clearFilters} className="ml-auto flex items-center gap-1 text-xs text-slate-400 hover:text-red-500">
                  <RotateCcw className="h-3 w-3" />
                  Limpiar
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="flex gap-2 flex-1 min-w-[200px]">
                <Input
                  placeholder="Buscar por radicado, asunto, ciudadano..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && updateFilter('q', search)}
                />
                <Button variant="outline" onClick={() => updateFilter('q', search)} size="md">
                  <Search className="h-4 w-4" />
                </Button>
              </div>
              <Select
                options={choices?.estado || []}
                placeholder="Estado"
                value={filters.estado}
                onChange={e => updateFilter('estado', e.target.value)}
                className="w-36"
              />
              <Select
                options={choices?.tipo || []}
                placeholder="Tipo"
                value={filters.tipo}
                onChange={e => updateFilter('tipo', e.target.value)}
                className="w-36"
              />
              <Select
                options={choices?.canal || []}
                placeholder="Canal"
                value={filters.canal}
                onChange={e => updateFilter('canal', e.target.value)}
                className="w-36"
              />
              <Select
                options={choices?.prioridad || []}
                placeholder="Prioridad"
                value={filters.prioridad}
                onChange={e => updateFilter('prioridad', e.target.value)}
                className="w-32"
              />
              <Select
                options={(deps || []).map(d => ({ value: String(d.id), label: d.sigla }))}
                placeholder="Dependencia"
                value={filters.dependencia}
                onChange={e => updateFilter('dependencia', e.target.value)}
                className="w-40"
              />
            </div>

            {/* Quick filter chips */}
            <div className="flex flex-wrap gap-2">
              {[
                { label: '⚠ Solo alertas', key: 'alertas', value: '1', danger: true },
                { label: '📋 Sin clasificar', key: 'sin_clasificar', value: '1', danger: false },
                { label: '🔴 Urgente', key: 'prioridad', value: 'urgente', danger: true },
              ].map(chip => {
                const active = filters[chip.key as keyof typeof filters] === chip.value
                return (
                  <button
                    key={chip.key}
                    onClick={() => updateFilter(chip.key, active ? '' : chip.value)}
                    className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                      active
                        ? 'bg-[#00a859] border-[#00a859] text-white'
                        : 'bg-white border-slate-300 text-slate-600 hover:border-[#00a859] hover:text-[#00a859]'
                    }`}
                  >
                    {chip.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Table */}
          {isLoading ? (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50">
                    {['Canal','Radicado','Asunto','Estado','Prioridad','SLA','Dependencia','Fecha',''].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: 6 }).map((_, i) => <TableRowSkeleton key={i} />)}
                </tbody>
              </table>
            </div>
          ) : !data?.results.length ? (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
              <Search className="h-10 w-10 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-500">No se encontraron solicitudes con los filtros seleccionados.</p>
              <button onClick={clearFilters} className="mt-2 text-sm text-[#00a859] hover:underline">Limpiar filtros</button>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Canal</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Radicado</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Asunto</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Estado</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Prioridad</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">SLA</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Dependencia</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Fecha</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {data.results.map((p) => (
                    <tr
                      key={p.id}
                      className={`border-b border-slate-50 hover:bg-slate-50 transition-colors ${
                        p.vencida ? 'bg-red-50/50' : p.en_alerta ? 'bg-amber-50/50' : ''
                      }`}
                    >
                      <td className="px-4 py-3">
                        <CanalIcon canal={p.canal_entrada} />
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-mono text-xs text-slate-600">{p.radicado}</span>
                      </td>
                      <td className="px-4 py-3 max-w-xs">
                        <p className="font-medium text-slate-800 truncate">{p.asunto}</p>
                        <p className="text-xs text-slate-500 truncate">
                          {p.anonimo ? 'Anónimo' : p.nombre_ciudadano}
                          {p.comuna && ` · ${p.comuna}`}
                        </p>
                      </td>
                      <td className="px-4 py-3">
                        <EstadoBadge estado={p.estado} />
                        {!p.clasificacion_validada && p.estado !== 'radicada' && (
                          <span className="block text-xs text-amber-500 mt-0.5">Sin validar</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <PriorityBadge prioridad={p.prioridad} />
                      </td>
                      <td className="px-4 py-3">
                        {p.vencida ? (
                          <span className="flex items-center gap-1 text-xs text-red-600 font-medium">
                            <AlertTriangle className="h-3 w-3" />
                            Vencida
                          </span>
                        ) : p.en_alerta ? (
                          <span className="flex items-center gap-1 text-xs text-amber-600 font-medium">
                            <AlertTriangle className="h-3 w-3" />
                            {p.dias_restantes}d
                          </span>
                        ) : p.dias_restantes !== null ? (
                          <span className="text-xs text-slate-500">{p.dias_restantes}d</span>
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs text-slate-500">
                          {p.dependencia_asignada_nombre || (
                            <span className="text-amber-500">Pendiente</span>
                          )}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div>
                          <p className="text-xs text-slate-500">{formatDate(p.fecha_radicacion)}</p>
                          <p className="text-xs text-slate-400">{formatRelativeTime(p.fecha_radicacion)}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Link
                          to={`/staff/pqrsd/${p.id}`}
                          className="flex items-center gap-1 text-xs text-[#00a859] hover:text-[#008f4c] font-medium"
                        >
                          Ver <ArrowRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
