import 'leaflet/dist/leaflet.css'
import { useQuery } from '@tanstack/react-query'
import { useMemo, useCallback } from 'react'
import { MapContainer, TileLayer, GeoJSON, Tooltip } from 'react-leaflet'
import type { Layer, PathOptions } from 'leaflet'
import type { Feature, FeatureCollection, Geometry } from 'geojson'
import { staffApi } from '@/lib/api'
import { StaffSidebar } from '@/components/layout/StaffSidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MapPin, Flame, TrendingUp, BarChart2 } from 'lucide-react'
import comunasRaw from '@/data/medellin-comunas.json'

const comunasGeoJSON = comunasRaw as FeatureCollection

interface ComunaCount { nombre: string; count: number }
interface BarrioCount { nombre: string; count: number; comuna: string }
interface MapaCalorData {
  por_comuna: ComunaCount[]
  por_barrio: BarrioCount[]
  total: number
}

function normalize(s: string) {
  return s.toLowerCase().replace(/[-\s]+/g, ' ').trim()
}

function getColor(count: number): string {
  if (count === 0) return '#f1f5f9'
  if (count <= 2) return '#fef9c3'
  if (count <= 5) return '#fde68a'
  if (count <= 10) return '#fb923c'
  if (count <= 20) return '#ef4444'
  if (count <= 40) return '#b91c1c'
  return '#7f1d1d'
}

function getIntensityLabel(count: number): string {
  if (count === 0) return 'Sin datos'
  if (count <= 2) return 'Baja'
  if (count <= 5) return 'Moderada'
  if (count <= 10) return 'Media'
  if (count <= 20) return 'Alta'
  if (count <= 40) return 'Muy alta'
  return 'Crítica'
}

export default function MapaCalorPage() {
  const { data, isLoading } = useQuery<MapaCalorData>({
    queryKey: ['mapa-calor'],
    queryFn: async () => {
      const { data } = await staffApi.getMapaCalor()
      return data
    },
    refetchInterval: 60000,
  })

  const countMap = useMemo<Record<string, number>>(() => {
    if (!data) return {}
    const map: Record<string, number> = {}
    for (const item of data.por_comuna) {
      map[normalize(item.nombre)] = item.count
    }
    return map
  }, [data])

  const maxCount = useMemo(() => {
    if (!data?.por_comuna.length) return 1
    return Math.max(...data.por_comuna.map(c => c.count), 1)
  }, [data])

  const getCountForFeature = useCallback((feature: Feature<Geometry, { nombre: string; aliases: string[] }>) => {
    const nameNorm = normalize(feature.properties.nombre)
    if (countMap[nameNorm] !== undefined) return countMap[nameNorm]
    for (const alias of (feature.properties.aliases || [])) {
      const aliasNorm = normalize(alias)
      if (countMap[aliasNorm] !== undefined) return countMap[aliasNorm]
    }
    // partial match fallback
    for (const [key, val] of Object.entries(countMap)) {
      if (key.includes(nameNorm) || nameNorm.includes(key)) return val
    }
    return 0
  }, [countMap])

  const styleFeature = useCallback((feature?: Feature<Geometry, { nombre: string; aliases: string[] }>): PathOptions => {
    if (!feature) return {}
    const count = getCountForFeature(feature)
    return {
      fillColor: getColor(count),
      fillOpacity: count === 0 ? 0.3 : 0.75,
      color: '#475569',
      weight: 1.5,
    }
  }, [getCountForFeature])

  const onEachFeature = useCallback((
    feature: Feature<Geometry, { nombre: string; aliases: string[] }>,
    layer: Layer
  ) => {
    const count = getCountForFeature(feature)
    const intensity = getIntensityLabel(count)
    layer.bindTooltip(
      `<div style="font-family:sans-serif;min-width:140px">
        <strong style="font-size:13px">${feature.properties.nombre}</strong>
        <hr style="margin:4px 0;border-color:#e2e8f0"/>
        <div style="font-size:12px">PQRSD: <strong>${count}</strong></div>
        <div style="font-size:11px;color:#64748b">Intensidad: ${intensity}</div>
      </div>`,
      { sticky: true, opacity: 0.95 }
    )
  }, [getCountForFeature])

  const top5 = data?.por_comuna.slice(0, 5) ?? []
  const top5Barrios = data?.por_barrio.slice(0, 5) ?? []

  return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center">
                <Flame className="h-5 w-5 text-red-500" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">Mapa de Calor PQRSD</h1>
                <p className="text-sm text-slate-500">Zonas con mayor concentración de solicitudes ciudadanas</p>
              </div>
            </div>
            {data && (
              <div className="flex items-center gap-2 text-xs text-slate-500 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                {data.total} PQRSD totales · actualización cada 60s
              </div>
            )}
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Map */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                <MapPin className="h-4 w-4 text-red-500" />
                Medellín — Distribución por Comunas
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="h-[480px] flex items-center justify-center bg-slate-100 animate-pulse">
                  <p className="text-slate-400 text-sm">Cargando mapa…</p>
                </div>
              ) : (
                <MapContainer
                  center={[6.265, -75.575]}
                  zoom={12}
                  style={{ height: 480, width: '100%' }}
                  scrollWheelZoom
                >
                  <TileLayer
                    attribution='&copy; <a href="https://carto.com">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                  />
                  <GeoJSON
                    key={JSON.stringify(countMap)}
                    data={comunasGeoJSON}
                    style={styleFeature as (f?: Feature) => PathOptions}
                    onEachFeature={onEachFeature as (f: Feature, l: Layer) => void}
                  />
                </MapContainer>
              )}

              {/* Legend */}
              <div className="px-4 py-3 border-t border-slate-100 flex flex-wrap items-center gap-4">
                <span className="text-xs font-medium text-slate-500">Intensidad:</span>
                {[
                  { color: '#f1f5f9', label: 'Sin datos' },
                  { color: '#fef9c3', label: 'Baja (1–2)' },
                  { color: '#fde68a', label: 'Moderada (3–5)' },
                  { color: '#fb923c', label: 'Media (6–10)' },
                  { color: '#ef4444', label: 'Alta (11–20)' },
                  { color: '#b91c1c', label: 'Muy alta (21–40)' },
                  { color: '#7f1d1d', label: 'Crítica (41+)' },
                ].map(({ color, label }) => (
                  <div key={label} className="flex items-center gap-1.5">
                    <div
                      className="w-4 h-4 rounded border border-slate-300"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-xs text-slate-600">{label}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Rankings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top comunas */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-red-500" />
                  Top Comunas con más PQRSD
                </CardTitle>
              </CardHeader>
              <CardContent>
                {top5.length === 0 ? (
                  <p className="text-sm text-slate-400 text-center py-6">Sin datos disponibles</p>
                ) : (
                  <div className="space-y-3">
                    {top5.map((item, i) => (
                      <div key={item.nombre} className="flex items-center gap-3">
                        <span className="w-6 text-center text-xs font-bold text-slate-400">#{i + 1}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-slate-700 truncate">{item.nombre}</span>
                            <span className="text-sm font-bold text-slate-800 ml-2 shrink-0">{item.count}</span>
                          </div>
                          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{
                                width: `${(item.count / maxCount) * 100}%`,
                                backgroundColor: getColor(item.count),
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Top barrios */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <BarChart2 className="h-4 w-4 text-orange-500" />
                  Top Barrios con más PQRSD
                </CardTitle>
              </CardHeader>
              <CardContent>
                {top5Barrios.length === 0 ? (
                  <p className="text-sm text-slate-400 text-center py-6">Sin datos disponibles</p>
                ) : (
                  <div className="space-y-3">
                    {top5Barrios.map((item, i) => (
                      <div key={item.nombre} className="flex items-center gap-3">
                        <span className="w-6 text-center text-xs font-bold text-slate-400">#{i + 1}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <div className="min-w-0">
                              <span className="text-sm font-medium text-slate-700 truncate block">{item.nombre}</span>
                              <span className="text-xs text-slate-400">{item.comuna}</span>
                            </div>
                            <span className="text-sm font-bold text-slate-800 ml-2 shrink-0">{item.count}</span>
                          </div>
                          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{
                                width: `${(item.count / (data?.por_barrio[0]?.count ?? 1)) * 100}%`,
                                backgroundColor: '#f97316',
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Full commune table */}
          {data && data.por_comuna.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-700">Detalle por Comuna</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-100">
                        <th className="text-left py-2 px-3 text-xs font-semibold text-slate-500">Pos.</th>
                        <th className="text-left py-2 px-3 text-xs font-semibold text-slate-500">Comuna</th>
                        <th className="text-right py-2 px-3 text-xs font-semibold text-slate-500">PQRSD</th>
                        <th className="text-right py-2 px-3 text-xs font-semibold text-slate-500">% del total</th>
                        <th className="text-left py-2 px-3 text-xs font-semibold text-slate-500">Intensidad</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.por_comuna.map((item, i) => (
                        <tr key={item.nombre} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                          <td className="py-2 px-3 text-slate-400 font-medium">#{i + 1}</td>
                          <td className="py-2 px-3 font-medium text-slate-700">{item.nombre}</td>
                          <td className="py-2 px-3 text-right font-bold text-slate-800">{item.count}</td>
                          <td className="py-2 px-3 text-right text-slate-500">
                            {data.total > 0 ? ((item.count / data.total) * 100).toFixed(1) : '0.0'}%
                          </td>
                          <td className="py-2 px-3">
                            <span
                              className="inline-block px-2 py-0.5 rounded-full text-xs font-medium"
                              style={{
                                backgroundColor: getColor(item.count) + '33',
                                color: item.count > 5 ? getColor(item.count) : '#64748b',
                                border: `1px solid ${getColor(item.count)}66`,
                              }}
                            >
                              {getIntensityLabel(item.count)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}
