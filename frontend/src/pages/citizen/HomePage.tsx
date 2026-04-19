import { Link } from 'react-router-dom'
import { PublicNavbar } from '@/components/layout/PublicNavbar'
import {
  MessageSquare, AlertTriangle, HelpCircle, Lightbulb,
  Shield, Mail, ArrowRight, Clock, CheckCircle, Search,
  Smartphone, Globe, MapPin, Users
} from 'lucide-react'

const pqrsdTypes = [
  {
    key: 'peticion',
    label: 'Petición',
    icon: MessageSquare,
    color: 'blue',
    bg: 'bg-blue-50',
    iconColor: 'text-blue-500',
    border: 'border-blue-100',
    desc: 'Solicita información, documentos o la intervención de la entidad.',
    plazo: '15 días hábiles',
  },
  {
    key: 'queja',
    label: 'Queja',
    icon: AlertTriangle,
    color: 'amber',
    bg: 'bg-amber-50',
    iconColor: 'text-amber-500',
    border: 'border-amber-100',
    desc: 'Manifiesta inconformidad con la conducta de un servidor público.',
    plazo: '15 días hábiles',
  },
  {
    key: 'reclamo',
    label: 'Reclamo',
    icon: Shield,
    color: 'red',
    bg: 'bg-red-50',
    iconColor: 'text-red-500',
    border: 'border-red-100',
    desc: 'Exige el reconocimiento o pago de un derecho o servicio.',
    plazo: '15 días hábiles',
  },
  {
    key: 'sugerencia',
    label: 'Sugerencia',
    icon: Lightbulb,
    color: 'emerald',
    bg: 'bg-blue-50',
    iconColor: 'text-blue-500',
    border: 'border-blue-100',
    desc: 'Propone mejoras para optimizar la gestión de la Alcaldía.',
    plazo: 'Sin plazo obligatorio',
  },
  {
    key: 'denuncia',
    label: 'Denuncia',
    icon: HelpCircle,
    color: 'purple',
    bg: 'bg-purple-50',
    iconColor: 'text-purple-500',
    border: 'border-purple-100',
    desc: 'Reporta irregularidades o actos de corrupción.',
    plazo: 'Varía según caso',
  },
  {
    key: 'correspondencia',
    label: 'Correspondencia',
    icon: Mail,
    color: 'slate',
    bg: 'bg-slate-50',
    iconColor: 'text-slate-500',
    border: 'border-slate-100',
    desc: 'Comunicaciones generales que no encajan en las categorías anteriores.',
    plazo: '15 días hábiles',
  },
]

const channels = [
  { icon: Smartphone, label: 'WhatsApp', desc: 'Mensaje directo al número oficial' },
  { icon: Mail, label: 'Correo Electrónico', desc: 'Envío a pqrsd@medellin.gov.co' },
  { icon: Globe, label: 'Portal Web', desc: 'Formulario en línea 24/7' },
  { icon: Users, label: 'Instagram', desc: 'Comentario en redes sociales' },
  { icon: MapPin, label: 'Presencial', desc: 'Centros de Atención Ciudadana' },
]

const steps = [
  { n: '1', title: 'Ingresa tu solicitud', desc: 'Completa el formulario con tu información y describe tu necesidad.' },
  { n: '2', title: 'Recibe tu radicado', desc: 'Obtienes un número único para consultar el estado en cualquier momento.' },
  { n: '3', title: 'Clasificación IA', desc: 'El sistema identifica la dependencia competente con ayuda de inteligencia artificial.' },
  { n: '4', title: 'Validación y respuesta', desc: 'Un funcionario valida la clasificación y tramita tu solicitud dentro del plazo legal.' },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <PublicNavbar />

      {/* Hero */}
      <section className="bg-gradient-to-br from-[#0d1b6e] via-[#0d2380] to-[#08155a] text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-[#0693E3]/20 border border-[#0693E3]/30 rounded-full px-4 py-1.5 mb-6">
            <div className="w-2 h-2 bg-[#0693E3] rounded-full animate-pulse" />
            <span className="text-sm text-blue-300 font-medium">Sistema inteligente de atención ciudadana</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
            Tus peticiones, quejas y reclamos{' '}
            <span className="text-[#0693E3]">atendidos con IA</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto mb-8">
            La Alcaldía de Medellín moderniza su sistema PQRSD con inteligencia artificial
            para clasificar, enrutar y responder tus solicitudes de manera eficiente y transparente.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/radicar"
              className="inline-flex items-center gap-2 bg-[#0693E3] hover:bg-[#0578C5] text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors shadow-lg shadow-blue-900/30"
            >
              Radicar PQRSD
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              to="/consultar"
              className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white border border-white/20 px-8 py-4 rounded-xl font-semibold text-lg transition-colors"
            >
              <Search className="h-5 w-5" />
              Consultar Estado
            </Link>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <div className="bg-white border-b border-slate-200 py-4">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-3 gap-4 text-center">
          {[
            { value: '26', label: 'Dependencias conectadas' },
            { value: '15 días', label: 'Plazo máximo de respuesta' },
            { value: 'IA + Humano', label: 'Clasificación inteligente' },
          ].map((s) => (
            <div key={s.label}>
              <p className="text-xl font-bold text-[#0693E3]">{s.value}</p>
              <p className="text-xs text-slate-500 mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* PQRSD Types */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <div className="text-center mb-10">
          <h2 className="text-2xl font-bold text-slate-800 mb-2">¿Qué tipo de solicitud quieres realizar?</h2>
          <p className="text-slate-500">Selecciona el tipo de PQRSD según tu situación</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {pqrsdTypes.map((t) => (
            <Link
              key={t.key}
              to={`/radicar?tipo=${t.key}`}
              className={`group p-5 rounded-xl border ${t.border} ${t.bg} hover:shadow-md transition-all hover:-translate-y-0.5`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg bg-white shadow-sm`}>
                  <t.icon className={`h-5 w-5 ${t.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-slate-800">{t.label}</h3>
                    <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-[#0693E3] transition-colors" />
                  </div>
                  <p className="text-sm text-slate-600 mb-2">{t.desc}</p>
                  <div className="flex items-center gap-1 text-xs text-slate-500">
                    <Clock className="h-3 w-3" />
                    {t.plazo}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
        <div className="text-center mt-6">
          <Link
            to="/radicar"
            className="inline-flex items-center gap-2 bg-[#0693E3] hover:bg-[#0578C5] text-white px-8 py-3 rounded-xl font-semibold transition-colors shadow-sm"
          >
            Iniciar mi PQRSD
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section className="bg-white border-y border-slate-200 py-16">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-800 mb-2">¿Cómo funciona?</h2>
            <p className="text-slate-500">Proceso simple y transparente</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((s, i) => (
              <div key={i} className="text-center">
                <div className="w-12 h-12 bg-[#0693E3] rounded-full flex items-center justify-center text-white font-bold text-lg mx-auto mb-3">
                  {s.n}
                </div>
                <h3 className="font-semibold text-slate-800 mb-1">{s.title}</h3>
                <p className="text-sm text-slate-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Channels */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <div className="text-center mb-10">
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Múltiples canales de atención</h2>
          <p className="text-slate-500">Elige el canal que más te convenga</p>
        </div>
        <div className="flex flex-wrap justify-center gap-4">
          {channels.map((ch) => (
            <div key={ch.label} className="flex flex-col items-center gap-2 p-4 bg-white rounded-xl border border-slate-200 w-36 hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                <ch.icon className="h-5 w-5 text-[#0693E3]" />
              </div>
              <p className="font-medium text-sm text-slate-700">{ch.label}</p>
              <p className="text-xs text-slate-500 text-center">{ch.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Legal note */}
      <section className="bg-[#0d1b6e] text-white py-8">
        <div className="max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center gap-4 justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-[#0693E3] shrink-0" />
            <p className="text-sm text-slate-300">
              Ley 1755 de 2015 — Derecho de Petición | Decreto 883 de 2015 — Alcaldía de Medellín
            </p>
          </div>
          <Link to="/radicar" className="shrink-0 bg-[#0693E3] hover:bg-[#0578C5] text-white px-6 py-2.5 rounded-lg font-medium text-sm transition-colors">
            Radicar ahora
          </Link>
        </div>
      </section>
    </div>
  )
}
