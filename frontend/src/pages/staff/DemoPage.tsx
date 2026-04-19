import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { staffApi } from '@/lib/api'
import { StaffSidebar } from '@/components/layout/StaffSidebar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CanalIcon } from '@/components/staff/CanalIcon'
import {
  Zap, CheckCircle, ArrowRight, Play, Info, MessageCircle,
  Mail, Globe, Hash, Users, RefreshCw
} from 'lucide-react'

interface DemoScenario {
  canal: string
  scenario: string
  label: string
  icon: typeof Globe
  description: string
  preview: string
  iconBg: string
  iconColor: string
}

const scenarios: DemoScenario[] = [
  {
    canal: 'whatsapp',
    scenario: 'whatsapp',
    label: 'WhatsApp',
    icon: MessageCircle,
    description: 'Simula un mensaje de ciudadano reportando huecos en la vía pública desde WhatsApp.',
    preview: '"Hola, quiero reportar que hay varios huecos muy peligrosos en la Carrera 76..."',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
  },
  {
    canal: 'email',
    scenario: 'email',
    label: 'Correo Electrónico',
    icon: Mail,
    description: 'Simula un correo formal solicitando información sobre un proceso licitatorio.',
    preview: '"Estimados señores de la Alcaldía de Medellín, Por medio de la presente me permito solicitar..."',
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600',
  },
  {
    canal: 'instagram',
    scenario: 'instagram',
    label: 'Instagram / Redes',
    icon: Hash,
    description: 'Simula una queja ciudadana publicada en redes sociales sobre alumbrado público.',
    preview: '"@AlcaldíaMedellín hace 2 semanas que se dañó el alumbrado en toda la Cra 45..."',
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600',
  },
  {
    canal: 'presencial',
    scenario: 'presencial',
    label: 'Presencial / Teléfono',
    icon: Users,
    description: 'Simula una queja registrada manualmente por un funcionario de atención.',
    preview: '"La ciudadana Rosa Elena Cardona Ríos se presentó en persona a las instalaciones..."',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600',
  },
  {
    canal: 'web',
    scenario: 'default',
    label: 'Portal Web',
    icon: Globe,
    description: 'Simula una solicitud enviada desde el portal web ciudadano.',
    preview: '"Sugerencia de prueba inyectada para demostrar el sistema multicanal."',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
  },
]

interface InjectedResult {
  radicado: string
  id: number
  canal: string
  message: string
}

export default function DemoPage() {
  const qc = useQueryClient()
  const [loading, setLoading] = useState<string | null>(null)
  const [results, setResults] = useState<InjectedResult[]>([])
  const [error, setError] = useState('')

  const inject = async (scenario: DemoScenario) => {
    setLoading(scenario.canal)
    setError('')
    try {
      const { data } = await staffApi.demoInject(scenario.canal, scenario.scenario)
      setResults(prev => [data, ...prev])
      qc.invalidateQueries({ queryKey: ['pqrsd'] })
      qc.invalidateQueries({ queryKey: ['inbox'] })
      qc.invalidateQueries({ queryKey: ['stats'] })
    } catch {
      setError('Error al inyectar el mensaje de demo.')
    } finally {
      setLoading(null)
    }
  }

  const clearResults = () => setResults([])

  return (
    <div className="flex h-screen bg-slate-50">
      <StaffSidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-8 py-5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-amber-100 rounded-xl flex items-center justify-center">
              <Zap className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-800">Demo Multicanal</h1>
              <p className="text-sm text-slate-500">Simula la recepción de PQRSD desde distintos canales</p>
            </div>
          </div>
        </div>

        <div className="p-8 space-y-6 max-w-4xl">
          {/* Explainer */}
          <div className="flex items-start gap-3 bg-blue-50 border border-blue-100 rounded-xl p-4">
            <Info className="h-5 w-5 text-blue-500 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold text-blue-800 mb-1">¿Cómo funciona este demo?</p>
              <p className="text-sm text-blue-700">
                Cada botón inyecta un PQRSD realista simulando la llegada de un mensaje desde ese canal.
                En producción, esto sería reemplazado por integraciones reales con WhatsApp Business API,
                Gmail, Meta Graph API y otros. El PQRSD creado aparecerá inmediatamente en la bandeja
                multicanal y podrá ser clasificado con IA.
              </p>
            </div>
          </div>

          {/* Scenario cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {scenarios.map((s) => (
              <Card key={s.canal} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-5 pb-5">
                  <div className="flex items-start gap-3 mb-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${s.iconBg}`}>
                      <s.icon className={`h-5 w-5 ${s.iconColor}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">{s.label}</h3>
                      <p className="text-xs text-slate-500">{s.description}</p>
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2.5 mb-3">
                    <p className="text-xs text-slate-500 italic line-clamp-2">{s.preview}</p>
                  </div>
                  <Button
                    onClick={() => inject(s)}
                    loading={loading === s.canal}
                    className="w-full"
                    size="sm"
                  >
                    <Play className="h-3.5 w-3.5" />
                    Simular mensaje de {s.label}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Results */}
          {results.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-slate-800 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-[#00a859]" />
                  Mensajes inyectados ({results.length})
                </h2>
                <button
                  onClick={clearResults}
                  className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600"
                >
                  <RefreshCw className="h-3 w-3" />
                  Limpiar
                </button>
              </div>
              <div className="space-y-2">
                {results.map((r, i) => (
                  <div key={i} className="bg-white border border-emerald-200 rounded-xl p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CanalIcon canal={r.canal} />
                      <div>
                        <p className="font-mono text-sm font-semibold text-slate-800">{r.radicado}</p>
                        <p className="text-xs text-slate-500">{r.message}</p>
                      </div>
                    </div>
                    <Link
                      to={`/staff/pqrsd/${r.id}`}
                      className="flex items-center gap-1 text-sm text-[#00a859] hover:text-[#008f4c] font-medium"
                    >
                      Ver PQRSD <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Flow description */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Flujo de extremo a extremo (demo pitch)</CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="space-y-3">
                {[
                  { n: '1', label: 'Mensaje entra por un canal', desc: 'WhatsApp, email, Instagram, web o presencial.' },
                  { n: '2', label: 'Normalización automática', desc: 'El sistema convierte el mensaje al modelo PQRSD unificado.' },
                  { n: '3', label: 'Clasificación IA (Gemini)', desc: 'Se sugiere tipo, dependencia y prioridad con % de confianza.' },
                  { n: '4', label: 'Validación humana obligatoria', desc: 'El funcionario acepta o corrige la sugerencia (Ley 1755/2015).' },
                  { n: '5', label: 'Enrutamiento a dependencia', desc: 'Se asigna a la secretaría o entidad competente.' },
                  { n: '6', label: 'Control SLA', desc: 'El sistema alerta si el plazo de respuesta está en riesgo.' },
                  { n: '7', label: 'Respuesta y cierre', desc: 'El ciudadano puede consultar el estado en cualquier momento.' },
                ].map((step) => (
                  <li key={step.n} className="flex items-start gap-3">
                    <span className="w-6 h-6 bg-[#00a859] text-white rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                      {step.n}
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{step.label}</p>
                      <p className="text-xs text-slate-500">{step.desc}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
