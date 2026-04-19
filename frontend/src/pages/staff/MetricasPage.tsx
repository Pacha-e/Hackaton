import { useQuery } from '@tanstack/react-query'
import { staffApi } from '@/lib/api'
import type { Stats } from '@/types'
import { StaffSidebar } from '@/components/layout/StaffSidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageLoader } from '@/components/ui/spinner'
import { BarChart2, TrendingUp, Clock, CheckCircle } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, RadialBarChart, RadialBar
} from 'recharts'

const CANAL_COLORS: Record<string, string> = {
  web: '#3b82f6',
  email: '#8b5cf6',
  whatsapp: '#22c55e',
  instagram: '#ec4899',
  presencial: '#f97316',
}

const CANAL_LABELS: Record<string, string> = {
  web: 'Web',
  email: 'Email',
  whatsapp: 'WhatsApp',
  instagram: 'Instagram',
  presencial: 'Presencial',
}

const TIPO_LABELS: Record<string, string> = {
  peticion: 'Petición',
  queja: 'Queja',
  reclamo: 'Reclamo',
  sugerencia: 'Sugerencia',
  denuncia: 'Denuncia',
  correspondencia: 'Correspondencia',
}

const TIPO_COLORS = ['#00a859', '#3b82f6', '#f97316', '#8b5cf6', '#ec4899', '#64748b']

export default function MetricasPage() {
  const { data: stats, isLoading } = useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: async () => {
      const { data } = await staffApi.getStats()
      return data
    },
    refetchInterval: 30000,
  })

  if (isLoading) return (
    <div className="flex h-screen">
      <StaffSidebar />
      <div className="flex-1"><PageLoader /></div>
    </div>
  )

  if (!stats) return null

  const canalData = Object.entries(stats.por_canal).map(([key, value]) => ({
    name: CANAL_LABELS[key] || key,
    value,
    color: CANAL_COLORS[key] || '#94a3b8',
  }))

  const tipoData = Object.entries(stats.por_tipo).map(([key, value], i) => ({
    name: TIPO_LABELS[key] || key,
    value,
    fill: TIPO_COLORS[i % TIPO_COLORS.length],
  }))

  const estadoData = [
    { name: 'Radicadas', value: stats.radicadas, fill: '#94a3b8' },
    { name: 'En Clasificación', value: stats.en_clasificacion, fill: '#f59e0b' },
    { name: 'Clasificadas', value: stats.clasificadas, fill: '#3b82f6' },
    { name: 'En Trámite', value: stats.en_tramite, fill: '#6366f1' },
    { name: 'Respondidas', value: stats.respondidas, fill: '#00a859' },
    { name: 'Cerradas', value: stats.cerradas, fill: '#374151' },
  ].filter(d => d.value > 0)

  const resolutionRate = stats.total > 0
    ? Math.round(((stats.respondidas + stats.cerradas) / stats.total) * 100)
    : 0

  const slaCompliance = stats.total > 0
    ? Math.round(((stats.total - stats.vencidas) / stats.total) * 100)
    : 100

  return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-5">
          <div className="flex items-center gap-3">
            <BarChart2 className="h-5 w-5 text-[#00a859]" />
            <div>
              <h1 className="text-xl font-bold text-slate-800">Métricas del Sistema</h1>
              <p className="text-sm text-slate-500">Análisis de desempeño PQRSD</p>
            </div>
          </div>
        </div>

        <div className="p-8 space-y-6">
          {/* KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total PQRSD', value: stats.total, icon: BarChart2, color: 'text-slate-600', bg: 'bg-slate-100' },
              { label: 'Tasa de resolución', value: `${resolutionRate}%`, icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50' },
              { label: 'Cumplimiento SLA', value: `${slaCompliance}%`, icon: Clock, color: 'text-blue-600', bg: 'bg-blue-50' },
              { label: 'Respondidas', value: stats.respondidas, icon: CheckCircle, color: 'text-purple-600', bg: 'bg-purple-50' },
            ].map((kpi) => (
              <Card key={kpi.label}>
                <CardContent className="pt-5 pb-5">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${kpi.bg}`}>
                      <kpi.icon className={`h-5 w-5 ${kpi.color}`} />
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">{kpi.label}</p>
                      <p className="text-2xl font-bold text-slate-800">{kpi.value}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Charts row 1 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Distribución por Canal</CardTitle>
              </CardHeader>
              <CardContent>
                {canalData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie
                        data={canalData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {canalData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v) => [`${v} casos`]} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[260px] flex items-center justify-center text-slate-400">Sin datos</div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">PQRSD por Tipo</CardTitle>
              </CardHeader>
              <CardContent>
                {tipoData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={tipoData} barSize={32} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]} name="Casos">
                        {tipoData.map((entry, index) => (
                          <Cell key={index} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[260px] flex items-center justify-center text-slate-400">Sin datos</div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Charts row 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Estado actual del portafolio</CardTitle>
              </CardHeader>
              <CardContent>
                {estadoData.length > 0 ? (
                  <div className="space-y-2">
                    {estadoData.map((item) => (
                      <div key={item.name} className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: item.fill }} />
                        <div className="flex-1">
                          <div className="flex justify-between text-sm mb-0.5">
                            <span className="text-slate-600">{item.name}</span>
                            <span className="font-semibold text-slate-800">{item.value}</span>
                          </div>
                          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{
                                width: `${stats.total > 0 ? (item.value / stats.total) * 100 : 0}%`,
                                backgroundColor: item.fill,
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 text-sm">Sin datos</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Alertas SLA</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { label: 'PQRSD vencidas', value: stats.vencidas, color: 'text-red-600', bg: 'bg-red-50', bar: '#ef4444' },
                    { label: 'En alerta (≤3 días)', value: stats.alertas, color: 'text-amber-600', bg: 'bg-amber-50', bar: '#f59e0b' },
                    { label: 'Sin clasificar', value: stats.sin_clasificar, color: 'text-orange-600', bg: 'bg-orange-50', bar: '#f97316' },
                    { label: 'Al día', value: Math.max(0, stats.total - stats.vencidas - stats.alertas), color: 'text-emerald-600', bg: 'bg-emerald-50', bar: '#00a859' },
                  ].map((item) => (
                    <div key={item.label} className={`flex items-center justify-between p-3 rounded-lg ${item.bg}`}>
                      <span className={`text-sm font-medium ${item.color}`}>{item.label}</span>
                      <span className={`text-2xl font-bold ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
