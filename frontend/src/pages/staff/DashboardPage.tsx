import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { staffApi } from '@/lib/api'
import type { Stats } from '@/types'
import { StaffSidebar } from '@/components/layout/StaffSidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatCardSkeleton } from '@/components/ui/skeleton'
import {
  FileText, AlertTriangle, Clock, CheckCircle, TrendingUp,
  Inbox, Users, Zap, ArrowRight, Activity
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
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

interface StatCardProps {
  label: string
  value: number
  icon: typeof FileText
  color: string
  bgColor: string
  link?: string
  alert?: boolean
}

function StatCard({ label, value, icon: Icon, color, bgColor, link, alert }: StatCardProps) {
  const content = (
    <Card className={`hover:shadow-md transition-shadow ${alert && value > 0 ? 'border-red-200' : ''}`}>
      <CardContent className="pt-5 pb-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 mb-1">{label}</p>
            <p className={`text-3xl font-bold ${alert && value > 0 ? 'text-red-600' : 'text-slate-800'}`}>{value}</p>
          </div>
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${bgColor}`}>
            <Icon className={`h-6 w-6 ${color} ${alert && value > 0 ? 'animate-pulse' : ''}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  )

  if (link) return <Link to={link}>{content}</Link>
  return content
}

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery<Stats>({
    queryKey: ['stats'],
    queryFn: async () => {
      const { data } = await staffApi.getStats()
      return data
    },
    refetchInterval: 30000,
  })

  if (isLoading) return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="bg-white border-b border-slate-200 px-8 py-5">
          <div className="h-6 w-48 bg-slate-200 rounded animate-pulse" />
          <div className="h-4 w-32 bg-slate-100 rounded mt-1 animate-pulse" />
        </div>
        <div className="p-8 space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)}
          </div>
        </div>
      </main>
    </div>
  )

  if (!stats) return null

  // Chart data
  const canalData = Object.entries(stats.por_canal).map(([key, value]) => ({
    name: CANAL_LABELS[key] || key,
    value,
    color: CANAL_COLORS[key] || '#94a3b8',
  }))

  const tipoData = Object.entries(stats.por_tipo).map(([key, value]) => ({
    name: TIPO_LABELS[key] || key,
    value,
  }))

  return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-slate-800">Dashboard PQRSD</h1>
                <span className="flex items-center gap-1 text-xs text-blue-600 bg-blue-50 border border-blue-100 px-2 py-0.5 rounded-full">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                  En vivo
                </span>
              </div>
              <p className="text-sm text-slate-500">Actualización automática cada 30s</p>
            </div>
            <div className="flex items-center gap-3">
              <Link
                to="/staff/inbox"
                className="flex items-center gap-2 bg-[#0693E3] hover:bg-[#0578C5] text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                <Inbox className="h-4 w-4" />
                Bandeja de entrada
              </Link>
              <Link
                to="/staff/demo"
                className="flex items-center gap-2 bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                <Zap className="h-4 w-4" />
                Demo
              </Link>
            </div>
          </div>
        </div>

        <div className="p-8 space-y-6">
          {/* Alerts */}
          {(stats.alertas > 0 || stats.vencidas > 0) && (
            <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl p-4">
              <AlertTriangle className="h-5 w-5 text-red-500 shrink-0" />
              <div className="flex-1">
                <p className="font-semibold text-red-700 text-sm">
                  Atención requerida:
                  {stats.vencidas > 0 && ` ${stats.vencidas} PQRSD${stats.vencidas !== 1 ? 's' : ''} vencida${stats.vencidas !== 1 ? 's' : ''}`}
                  {stats.alertas > 0 && ` · ${stats.alertas} en alerta SLA`}
                </p>
                <p className="text-xs text-red-600">Estas solicitudes requieren atención inmediata para cumplir con la Ley 1755/2015.</p>
              </div>
              <Link
                to="/staff/pqrsd?alertas=1"
                className="flex items-center gap-1 text-sm font-medium text-red-600 hover:text-red-700"
              >
                Ver todas <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          )}

          {/* Stats grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total PQRSD" value={stats.total} icon={FileText} color="text-slate-600" bgColor="bg-slate-100" link="/staff/pqrsd" />
            <StatCard label="Sin clasificar" value={stats.sin_clasificar} icon={Clock} color="text-amber-500" bgColor="bg-amber-50" link="/staff/pqrsd?sin_clasificar=1" />
            <StatCard label="Alertas SLA" value={stats.alertas} icon={AlertTriangle} color="text-orange-500" bgColor="bg-orange-50" link="/staff/pqrsd?alertas=1" alert />
            <StatCard label="Vencidas" value={stats.vencidas} icon={AlertTriangle} color="text-red-500" bgColor="bg-red-50" link="/staff/pqrsd?alertas=1" alert />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Radicadas" value={stats.radicadas} icon={FileText} color="text-slate-500" bgColor="bg-slate-50" />
            <StatCard label="En trámite" value={stats.en_tramite} icon={Activity} color="text-blue-500" bgColor="bg-blue-50" />
            <StatCard label="Respondidas" value={stats.respondidas} icon={CheckCircle} color="text-blue-500" bgColor="bg-blue-50" />
            <StatCard label="Cerradas" value={stats.cerradas} icon={CheckCircle} color="text-slate-400" bgColor="bg-slate-50" />
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Canal distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-700">PQRSD por Canal</CardTitle>
              </CardHeader>
              <CardContent>
                {canalData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={canalData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {canalData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v) => [`${v} casos`]} />
                      <Legend
                        formatter={(value) => <span className="text-xs text-slate-600">{value}</span>}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[220px] flex items-center justify-center text-slate-400 text-sm">Sin datos</div>
                )}
              </CardContent>
            </Card>

            {/* Type distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold text-slate-700">PQRSD por Tipo</CardTitle>
              </CardHeader>
              <CardContent>
                {tipoData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={tipoData} barSize={28} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#0693E3" radius={[4, 4, 0, 0]} name="Casos" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[220px] flex items-center justify-center text-slate-400 text-sm">Sin datos</div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick links */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { href: '/staff/inbox', icon: Inbox, title: 'Bandeja multichannel', desc: 'Mensajes de todos los canales', color: 'text-blue-500', bg: 'bg-blue-50' },
              { href: '/staff/pqrsd?sin_clasificar=1', icon: Zap, title: 'Clasificar pendientes', desc: `${stats.sin_clasificar} solicitudes esperan clasificación`, color: 'text-amber-500', bg: 'bg-amber-50' },
              { href: '/staff/metricas', icon: TrendingUp, title: 'Métricas detalladas', desc: 'Análisis completo del sistema', color: 'text-purple-500', bg: 'bg-purple-50' },
            ].map(({ href, icon: Icon, title, desc, color, bg }) => (
              <Link key={href} to={href}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer group">
                  <CardContent className="pt-5 pb-5">
                    <div className="flex items-start gap-3">
                      <div className={`p-2.5 rounded-xl ${bg}`}>
                        <Icon className={`h-5 w-5 ${color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm text-slate-800 group-hover:text-[#0693E3] transition-colors">{title}</p>
                        <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-[#0693E3] transition-colors mt-1" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
