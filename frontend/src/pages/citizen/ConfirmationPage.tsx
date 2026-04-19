import { useParams, useLocation, Link } from 'react-router-dom'
import { PublicNavbar } from '@/components/layout/PublicNavbar'
import { CheckCircle, Copy, Search, FileText, Clock, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/lib/utils'
import { useState } from 'react'

interface ConfirmationState {
  radicado: string
  fecha_radicacion: string
  fecha_limite: string
  estado: string
}

export default function ConfirmationPage() {
  const { radicado } = useParams<{ radicado: string }>()
  const location = useLocation()
  const state = location.state as ConfirmationState | null
  const [copied, setCopied] = useState(false)

  const actualRadicado = radicado || state?.radicado || ''

  const copyRadicado = () => {
    navigator.clipboard.writeText(actualRadicado)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <PublicNavbar />

      <div className="max-w-xl mx-auto px-4 py-16">
        {/* Success card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-lg overflow-hidden">
          {/* Green header */}
          <div className="bg-gradient-to-br from-[#0693E3] to-[#0578C5] p-8 text-white text-center">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="h-9 w-9 text-white" />
            </div>
            <h1 className="text-2xl font-bold mb-1">¡PQRSD Radicada!</h1>
            <p className="text-blue-100 text-sm">Tu solicitud fue registrada exitosamente</p>
          </div>

          <div className="p-6 space-y-6">
            {/* Radicado number */}
            <div className="text-center">
              <p className="text-sm text-slate-500 mb-2">Número de radicado</p>
              <div className="flex items-center justify-center gap-2">
                <span className="text-2xl font-mono font-bold text-slate-800">{actualRadicado}</span>
                <button
                  onClick={copyRadicado}
                  className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-[#0693E3] transition-colors"
                  title="Copiar número"
                >
                  {copied ? <CheckCircle className="h-4 w-4 text-[#0693E3]" /> : <Copy className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Info grid */}
            {state && (
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 mb-1">Fecha de radicación</p>
                  <p className="text-sm font-medium text-slate-800">{formatDate(state.fecha_radicacion)}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 mb-1">Fecha límite de respuesta</p>
                  <p className="text-sm font-medium text-slate-800">{formatDate(state.fecha_limite)}</p>
                </div>
                <div className="col-span-2 bg-blue-50 border border-blue-100 rounded-lg p-3">
                  <p className="text-xs text-blue-600 mb-1">Estado actual</p>
                  <p className="text-sm font-semibold text-blue-700">Radicada — en proceso de clasificación</p>
                </div>
              </div>
            )}

            {/* Instructions */}
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                <Clock className="h-4 w-4 text-[#0693E3]" />
                Próximos pasos
              </h3>
              <ol className="space-y-2 text-sm text-slate-600">
                {[
                  'El sistema clasificará automáticamente tu solicitud con IA.',
                  'Un funcionario validará la clasificación y la asignará a la dependencia competente.',
                  'Recibirás respuesta dentro del plazo legal establecido.',
                  'Puedes consultar el estado en cualquier momento con tu número de radicado.',
                ].map((s, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="w-5 h-5 bg-[#0693E3] text-white rounded-full flex items-center justify-center text-xs shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {s}
                  </li>
                ))}
              </ol>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Link to={`/consultar?radicado=${actualRadicado}`} className="flex-1">
                <Button variant="primary" className="w-full gap-2">
                  <Search className="h-4 w-4" />
                  Consultar estado
                </Button>
              </Link>
              <Link to="/radicar" className="flex-1">
                <Button variant="outline" className="w-full gap-2">
                  <FileText className="h-4 w-4" />
                  Nueva solicitud
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Legal note */}
        <div className="mt-6 text-center">
          <p className="text-xs text-slate-500">
            De acuerdo con la <strong>Ley 1755 de 2015</strong>, la Alcaldía de Medellín
            tiene <strong>15 días hábiles</strong> para dar respuesta a tu solicitud.
          </p>
        </div>

        <div className="mt-6 text-center">
          <Link to="/" className="text-sm text-[#0693E3] hover:underline inline-flex items-center gap-1">
            Volver al inicio
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  )
}
