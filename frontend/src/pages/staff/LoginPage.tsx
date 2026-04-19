import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/hooks/useAuth'
import { Lock, AlertCircle, Building2, Zap } from 'lucide-react'

const schema = z.object({
  username: z.string().min(1, 'Usuario requerido'),
  password: z.string().min(1, 'Contraseña requerida'),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const { login, isAuthenticated, loginLoading } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  if (isAuthenticated) {
    return <Navigate to="/staff/dashboard" replace />
  }

  const onSubmit = async (data: FormData) => {
    setError('')
    try {
      await login(data)
      navigate('/staff/dashboard')
    } catch {
      setError('Credenciales incorrectas. Verifica tu usuario y contraseña.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a3a2a] to-[#0f2a1c] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#00a859] rounded-2xl mb-4 shadow-lg shadow-emerald-900/30">
            <Building2 className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-1">Alcaldía de Medellín</h1>
          <p className="text-emerald-300 text-sm">Sistema Inteligente PQRSD</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-2xl shadow-black/30 overflow-hidden">
          <div className="bg-slate-50 border-b border-slate-200 px-6 py-4">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-slate-500" />
              <h2 className="text-sm font-semibold text-slate-700">Acceso funcionarios</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
            <Input
              label="Usuario"
              placeholder="Ingresa tu usuario"
              autoComplete="username"
              error={errors.username?.message}
              {...register('username')}
            />
            <Input
              label="Contraseña"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              error={errors.password?.message}
              {...register('password')}
            />

            {error && (
              <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-3">
                <AlertCircle className="h-4 w-4 text-red-500 shrink-0" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <Button type="submit" loading={loginLoading} className="w-full" size="lg">
              Ingresar al sistema
            </Button>
          </form>

          {/* Demo credentials */}
          <div className="px-6 pb-6">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-3.5 w-3.5 text-amber-500" />
                <p className="text-xs font-semibold text-amber-700">Demo — credenciales de prueba</p>
              </div>
              <div className="space-y-1 text-xs text-amber-700 font-mono">
                <p><strong>Admin:</strong> admin / admin1234</p>
                <p><strong>Enlace:</strong> enlace1 / pqrsd2026</p>
                <p><strong>Jurídico:</strong> juridico1 / pqrsd2026</p>
              </div>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500 mt-6">
          Portal ciudadano:{' '}
          <a href="/" className="text-emerald-300 hover:underline">Ir al inicio</a>
        </p>
      </div>
    </div>
  )
}
