import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useQuery } from '@tanstack/react-query'
import { PublicNavbar } from '@/components/layout/PublicNavbar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { citizenApi } from '@/lib/api'
import type { Choices } from '@/types'
import {
  FileText, User, AlignLeft, CheckCircle, ArrowRight, ArrowLeft,
  AlertCircle, Info, MessageSquare, AlertTriangle, Shield,
  Lightbulb, HelpCircle, Mail, MapPin, Clock, Send, Eye
} from 'lucide-react'

const schema = z.object({
  tipo: z.string().min(1, 'Selecciona el tipo de solicitud'),
  canal_entrada: z.string().min(1, 'Selecciona el canal'),
  anonimo: z.boolean(),
  nombre_ciudadano: z.string().optional(),
  email_ciudadano: z.string().email('Email inválido').optional().or(z.literal('')),
  telefono_ciudadano: z.string().optional(),
  documento_ciudadano: z.string().optional(),
  comuna: z.string().optional(),
  barrio: z.string().optional(),
  asunto: z.string().min(10, 'El asunto debe tener al menos 10 caracteres'),
  descripcion: z.string().min(30, 'La descripción debe tener al menos 30 caracteres'),
  acepta_datos: z.boolean().refine(v => v, 'Debes aceptar el tratamiento de datos'),
}).superRefine((data, ctx) => {
  if (!data.anonimo && !data.nombre_ciudadano?.trim()) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'El nombre es obligatorio si no es anónimo', path: ['nombre_ciudadano'] })
  }
})

type FormData = z.infer<typeof schema>

const TIPO_CONFIG: Record<string, { icon: typeof MessageSquare; color: string; bg: string; border: string; plazo: string }> = {
  peticion: { icon: MessageSquare, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', plazo: '15 días hábiles' },
  queja: { icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', plazo: '15 días hábiles' },
  reclamo: { icon: Shield, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', plazo: '15 días hábiles' },
  sugerencia: { icon: Lightbulb, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', plazo: 'Sin plazo obligatorio' },
  denuncia: { icon: HelpCircle, color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200', plazo: 'Varía según caso' },
  correspondencia: { icon: Mail, color: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200', plazo: '15 días hábiles' },
}

const TIPO_OPTIONS = [
  { value: 'peticion', label: 'Petición', desc: 'Solicita información, documentos o la intervención de la entidad.' },
  { value: 'queja', label: 'Queja', desc: 'Manifiesta inconformidad con la conducta de un servidor público.' },
  { value: 'reclamo', label: 'Reclamo', desc: 'Exige el reconocimiento o pago de un derecho o servicio.' },
  { value: 'sugerencia', label: 'Sugerencia', desc: 'Propone mejoras para optimizar la gestión de la Alcaldía.' },
  { value: 'denuncia', label: 'Denuncia', desc: 'Reporta irregularidades o actos de corrupción.' },
  { value: 'correspondencia', label: 'Correspondencia', desc: 'Comunicaciones generales que no encajan en las categorías anteriores.' },
]

const CANAL_OPTIONS = [
  { value: 'web', label: 'Portal Web' },
  { value: 'email', label: 'Correo Electrónico' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'presencial', label: 'Presencial' },
]

const comunas = [
  'Popular', 'Santa Cruz', 'Manrique', 'Aranjuez', 'Castilla', 'Doce de Octubre',
  'Robledo', 'Villa Hermosa', 'Buenos Aires', 'La Candelaria', 'Laureles - Estadio',
  'La América', 'San Javier', 'El Poblado', 'Guayabal', 'Belén',
  'San Sebastián de Palmitas', 'San Cristóbal', 'Altavista', 'San Antonio de Prado',
  'Santa Elena', 'Corregimiento de Palmitas',
]

const STEPS = [
  { id: 1, label: 'Tipo', icon: FileText },
  { id: 2, label: 'Tus datos', icon: User },
  { id: 3, label: 'Descripción', icon: AlignLeft },
  { id: 4, label: 'Revisión', icon: Eye },
]

function StepIndicator({ current }: { current: number }) {
  return (
    <div className="flex items-center justify-center mb-8">
      {STEPS.map((step, i) => {
        const done = step.id < current
        const active = step.id === current
        return (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                done
                  ? 'bg-[#0693E3] border-[#0693E3]'
                  : active
                  ? 'bg-white border-[#0693E3] shadow-md shadow-emerald-100'
                  : 'bg-white border-slate-200'
              }`}>
                {done ? (
                  <CheckCircle className="h-5 w-5 text-white" />
                ) : (
                  <step.icon className={`h-4 w-4 ${active ? 'text-[#0693E3]' : 'text-slate-300'}`} />
                )}
              </div>
              <span className={`text-xs mt-1 font-medium hidden sm:block ${
                active ? 'text-[#0693E3]' : done ? 'text-slate-500' : 'text-slate-300'
              }`}>
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`w-12 sm:w-20 h-0.5 mx-1 mb-4 transition-colors duration-300 ${
                done ? 'bg-[#0693E3]' : 'bg-slate-200'
              }`} />
            )}
          </div>
        )
      })}
    </div>
  )
}

export default function SubmitPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [step, setStep] = useState(1)
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { data: choices } = useQuery<Choices>({
    queryKey: ['choices'],
    queryFn: async () => {
      const { data } = await citizenApi.getChoices()
      return data
    },
  })

  const {
    register,
    handleSubmit,
    watch,
    trigger,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      tipo: searchParams.get('tipo') || '',
      canal_entrada: 'web',
      anonimo: false,
      acepta_datos: false,
    },
  })

  const values = watch()
  const anonimo = watch('anonimo')
  const tipoSelected = watch('tipo')
  const tipoCfg = TIPO_CONFIG[tipoSelected]

  const nextStep = async () => {
    let fields: (keyof FormData)[] = []
    if (step === 1) fields = ['tipo', 'canal_entrada']
    if (step === 2) fields = ['nombre_ciudadano']
    if (step === 3) fields = ['asunto', 'descripcion']

    const ok = await trigger(fields)
    if (ok) setStep(s => s + 1)
  }

  const onSubmit = async (formData: FormData) => {
    setIsSubmitting(true)
    setSubmitError('')
    try {
      const fd = new FormData()
      Object.entries(formData).forEach(([k, v]) => {
        if (k !== 'acepta_datos' && v !== undefined && v !== '') {
          fd.append(k, String(v))
        }
      })
      const { data } = await citizenApi.submit(fd)
      navigate(`/confirmacion/${data.radicado}`, { state: data })
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, string[]> } }
      if (axiosErr?.response?.data) {
        const msgs = Object.entries(axiosErr.response.data)
          .map(([f, e]) => `${f}: ${Array.isArray(e) ? e.join(', ') : e}`)
          .join(' | ')
        setSubmitError(msgs)
      } else {
        setSubmitError('Error al enviar la solicitud. Por favor, intenta de nuevo.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const TIPO_LABELS: Record<string, string> = {
    peticion: 'Petición', queja: 'Queja', reclamo: 'Reclamo',
    sugerencia: 'Sugerencia', denuncia: 'Denuncia', correspondencia: 'Correspondencia',
  }
  const CANAL_LABELS: Record<string, string> = {
    web: 'Portal Web', email: 'Correo Electrónico', whatsapp: 'WhatsApp',
    instagram: 'Instagram', presencial: 'Presencial',
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <PublicNavbar />

      <div className="max-w-2xl mx-auto px-4 py-10">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 bg-[#0693E3]/10 border border-[#0693E3]/20 rounded-full px-4 py-1.5 mb-3">
            <span className="text-sm text-[#0693E3] font-medium">Paso {step} de {STEPS.length}</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-800">
            {step === 1 && 'Tipo de solicitud'}
            {step === 2 && 'Tus datos personales'}
            {step === 3 && 'Describe tu solicitud'}
            {step === 4 && 'Revisa y envía'}
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            {step === 1 && 'Selecciona el tipo de PQRSD que mejor describe tu solicitud'}
            {step === 2 && 'Esta información nos permite contactarte y dar seguimiento'}
            {step === 3 && 'Sé lo más específico posible para una atención más eficiente'}
            {step === 4 && 'Verifica los datos antes de enviar tu solicitud'}
          </p>
        </div>

        <StepIndicator current={step} />

        <form onSubmit={handleSubmit(onSubmit)}>

          {/* STEP 1: Tipo */}
          {step === 1 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {TIPO_OPTIONS.map((opt) => {
                  const cfg = TIPO_CONFIG[opt.value]
                  const Icon = cfg.icon
                  const selected = tipoSelected === opt.value
                  return (
                    <label
                      key={opt.value}
                      className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all duration-150 hover:shadow-md ${
                        selected
                          ? `${cfg.border} ${cfg.bg} shadow-sm`
                          : 'border-slate-200 bg-white hover:border-slate-300'
                      }`}
                    >
                      <input type="radio" value={opt.value} {...register('tipo')} className="sr-only" />
                      <div className={`p-2 rounded-lg ${selected ? cfg.bg : 'bg-slate-100'} shrink-0`}>
                        <Icon className={`h-4 w-4 ${selected ? cfg.color : 'text-slate-400'}`} />
                      </div>
                      <div className="min-w-0">
                        <p className={`font-semibold text-sm ${selected ? 'text-slate-800' : 'text-slate-700'}`}>
                          {opt.label}
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5 leading-snug">{opt.desc}</p>
                        {selected && (
                          <div className="flex items-center gap-1 mt-1.5">
                            <Clock className={`h-3 w-3 ${cfg.color}`} />
                            <span className={`text-xs font-medium ${cfg.color}`}>{cfg.plazo}</span>
                          </div>
                        )}
                      </div>
                      {selected && (
                        <CheckCircle className={`h-4 w-4 ${cfg.color} shrink-0 mt-0.5`} />
                      )}
                    </label>
                  )
                })}
              </div>
              {errors.tipo && (
                <p role="alert" className="text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />{errors.tipo.message}
                </p>
              )}

              <div className="pt-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">Canal de entrada</label>
                <div className="flex flex-wrap gap-2">
                  {(choices?.canal || CANAL_OPTIONS).map((opt) => {
                    const selected = watch('canal_entrada') === opt.value
                    return (
                      <label key={opt.value} className={`flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-all text-sm font-medium ${
                        selected
                          ? 'bg-[#0d1b6e] border-[#0d1b6e] text-white'
                          : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                      }`}>
                        <input type="radio" value={opt.value} {...register('canal_entrada')} className="sr-only" />
                        {opt.label}
                      </label>
                    )
                  })}
                </div>
              </div>

              <div className="flex items-start gap-2 bg-blue-50 border border-blue-100 rounded-lg p-3 mt-2">
                <Info className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                <p className="text-sm text-blue-700">
                  Tu solicitud será atendida según la <strong>Ley 1755 de 2015</strong>.
                  Recibirás un número de radicado único para hacer seguimiento.
                </p>
              </div>
            </div>
          )}

          {/* STEP 2: Ciudadano */}
          {step === 2 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-slate-700 flex items-center gap-2 text-sm">
                    <User className="h-4 w-4 text-[#0693E3]" />
                    Información de contacto
                  </h3>
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <div className={`relative w-10 h-5 rounded-full transition-colors ${anonimo ? 'bg-[#0693E3]' : 'bg-slate-300'}`}>
                      <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${anonimo ? 'translate-x-5' : ''}`} />
                      <input type="checkbox" {...register('anonimo')} className="sr-only" />
                    </div>
                    <span className="text-sm text-slate-600">Anónimo</span>
                  </label>
                </div>

                {anonimo ? (
                  <div className="bg-amber-50 border border-amber-100 rounded-lg p-3 flex items-start gap-2">
                    <Info className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                    <p className="text-sm text-amber-700">
                      Tu solicitud será procesada de forma anónima. No podremos enviarte actualizaciones por correo.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <Input
                      label="Nombre completo"
                      required
                      placeholder="Ej: María García Pérez"
                      error={errors.nombre_ciudadano?.message}
                      {...register('nombre_ciudadano')}
                    />
                    <Input
                      label="Número de documento"
                      placeholder="CC, NIT, etc."
                      {...register('documento_ciudadano')}
                    />
                    <Input
                      label="Correo electrónico"
                      type="email"
                      placeholder="correo@ejemplo.com"
                      error={errors.email_ciudadano?.message}
                      {...register('email_ciudadano')}
                    />
                    <Input
                      label="Teléfono"
                      type="tel"
                      placeholder="+57 300 000 0000"
                      {...register('telefono_ciudadano')}
                    />
                  </div>
                )}
              </div>

              <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                <h3 className="font-semibold text-slate-700 flex items-center gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-[#0693E3]" />
                  Ubicación <span className="text-slate-400 font-normal">(opcional)</span>
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Select
                    label="Comuna / Corregimiento"
                    options={comunas.map(c => ({ value: c, label: c }))}
                    placeholder="Selecciona tu comuna..."
                    {...register('comuna')}
                  />
                  <Input
                    label="Barrio"
                    placeholder="Ej: Laureles, Envigado..."
                    {...register('barrio')}
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: Descripción */}
          {step === 3 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              {tipoSelected && tipoCfg && (
                <div className={`flex items-center gap-3 p-3 rounded-xl ${tipoCfg.bg} border ${tipoCfg.border}`}>
                  <tipoCfg.icon className={`h-5 w-5 ${tipoCfg.color} shrink-0`} />
                  <div>
                    <p className={`text-sm font-semibold ${tipoCfg.color}`}>{TIPO_LABELS[tipoSelected]}</p>
                    <p className="text-xs text-slate-500">Plazo de respuesta: {tipoCfg.plazo}</p>
                  </div>
                </div>
              )}

              <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
                <Input
                  label="Asunto"
                  required
                  placeholder="Resumen breve de tu solicitud"
                  error={errors.asunto?.message}
                  maxLength={300}
                  {...register('asunto')}
                />
                <div>
                  <Textarea
                    label="Descripción detallada"
                    required
                    placeholder="Describe tu solicitud con el mayor detalle posible. Incluye fechas, lugares y cualquier información relevante..."
                    rows={7}
                    error={errors.descripcion?.message}
                    {...register('descripcion')}
                  />
                  <p className="text-xs text-slate-400 mt-1">
                    {watch('descripcion')?.length || 0} caracteres · mínimo 30
                  </p>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 flex items-start gap-2">
                <Info className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                <p className="text-sm text-blue-700">
                  El sistema utilizará <strong>Inteligencia Artificial</strong> para clasificar tu solicitud
                  automáticamente. Un funcionario revisará y validará la asignación.
                </p>
              </div>
            </div>
          )}

          {/* STEP 4: Review */}
          {step === 4 && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                <div className="bg-slate-50 border-b border-slate-100 px-5 py-3">
                  <p className="text-sm font-semibold text-slate-700">Resumen de tu solicitud</p>
                </div>
                <div className="p-5 space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-xs text-slate-400 mb-0.5">Tipo</p>
                      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg ${tipoCfg?.bg || 'bg-slate-50'} border ${tipoCfg?.border || 'border-slate-200'}`}>
                        {tipoCfg && <tipoCfg.icon className={`h-3.5 w-3.5 ${tipoCfg.color}`} />}
                        <span className={`font-medium text-xs ${tipoCfg?.color || 'text-slate-600'}`}>
                          {TIPO_LABELS[values.tipo] || values.tipo}
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-0.5">Canal</p>
                      <p className="font-medium text-slate-700">{CANAL_LABELS[values.canal_entrada] || values.canal_entrada}</p>
                    </div>
                    {!values.anonimo && values.nombre_ciudadano && (
                      <div>
                        <p className="text-xs text-slate-400 mb-0.5">Nombre</p>
                        <p className="font-medium text-slate-700">{values.nombre_ciudadano}</p>
                      </div>
                    )}
                    {values.anonimo && (
                      <div>
                        <p className="text-xs text-slate-400 mb-0.5">Identidad</p>
                        <p className="font-medium text-slate-500 italic">Anónimo</p>
                      </div>
                    )}
                    {values.email_ciudadano && (
                      <div>
                        <p className="text-xs text-slate-400 mb-0.5">Email</p>
                        <p className="font-medium text-slate-700">{values.email_ciudadano}</p>
                      </div>
                    )}
                    {values.comuna && (
                      <div>
                        <p className="text-xs text-slate-400 mb-0.5">Ubicación</p>
                        <p className="font-medium text-slate-700">
                          {values.comuna}{values.barrio ? ` — ${values.barrio}` : ''}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="border-t border-slate-100 pt-4">
                    <p className="text-xs text-slate-400 mb-1">Asunto</p>
                    <p className="text-sm font-medium text-slate-800">{values.asunto}</p>
                  </div>

                  <div>
                    <p className="text-xs text-slate-400 mb-1">Descripción</p>
                    <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap bg-slate-50 rounded-lg p-3">
                      {values.descripcion}
                    </p>
                  </div>
                </div>
              </div>

              {/* Datos consent */}
              <label className="flex items-start gap-3 p-4 bg-white rounded-xl border border-slate-200 cursor-pointer hover:border-[#0693E3]/40 transition-colors group">
                <div className={`mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 transition-colors ${
                  values.acepta_datos ? 'bg-[#0693E3] border-[#0693E3]' : 'border-slate-300 bg-white group-hover:border-[#0693E3]'
                }`}>
                  {values.acepta_datos && <CheckCircle className="h-3.5 w-3.5 text-white" />}
                  <input type="checkbox" id="acepta_datos" className="sr-only" {...register('acepta_datos')} />
                </div>
                <span className="text-sm text-slate-600">
                  Autorizo el tratamiento de mis datos personales según la{' '}
                  <strong className="text-slate-800">Ley 1581 de 2012</strong> y la política de privacidad de la
                  Alcaldía de Medellín.
                </span>
              </label>
              {errors.acepta_datos && (
                <p role="alert" className="text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />{errors.acepta_datos.message}
                </p>
              )}

              {submitError && (
                <div role="alert" className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg p-3">
                  <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 shrink-0" />
                  <p className="text-sm text-red-700">{submitError}</p>
                </div>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className={`flex gap-3 mt-8 ${step === 1 ? 'justify-end' : 'justify-between'}`}>
            {step > 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={() => setStep(s => s - 1)}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Atrás
              </Button>
            )}
            {step < 4 ? (
              <Button
                type="button"
                onClick={nextStep}
                className="flex items-center gap-2"
              >
                Continuar
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                type="submit"
                size="lg"
                loading={isSubmitting}
                className="flex items-center gap-2 px-8"
              >
                <Send className="h-4 w-4" />
                Enviar solicitud
              </Button>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}
