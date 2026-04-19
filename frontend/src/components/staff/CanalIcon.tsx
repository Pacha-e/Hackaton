import { MessageCircle, Mail, Globe, Instagram, Users } from 'lucide-react'
import { cn } from '@/lib/utils'

const config: Record<string, { icon: typeof Globe; color: string; bg: string; label: string }> = {
  whatsapp: { icon: MessageCircle, color: 'text-green-600', bg: 'bg-green-100', label: 'WhatsApp' },
  email: { icon: Mail, color: 'text-purple-600', bg: 'bg-purple-100', label: 'Email' },
  web: { icon: Globe, color: 'text-blue-600', bg: 'bg-blue-100', label: 'Web' },
  instagram: { icon: Instagram, color: 'text-pink-600', bg: 'bg-pink-100', label: 'Instagram' },
  presencial: { icon: Users, color: 'text-orange-600', bg: 'bg-orange-100', label: 'Presencial' },
}

interface CanalIconProps {
  canal: string
  showLabel?: boolean
  size?: 'sm' | 'md'
  className?: string
}

export function CanalIcon({ canal, showLabel = false, size = 'md', className }: CanalIconProps) {
  const cfg = config[canal] || { icon: Globe, color: 'text-slate-600', bg: 'bg-slate-100', label: canal }
  const Icon = cfg.icon

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className={cn('rounded-lg flex items-center justify-center', cfg.bg, size === 'sm' ? 'w-6 h-6' : 'w-8 h-8')}>
        <Icon className={cn(cfg.color, size === 'sm' ? 'h-3 w-3' : 'h-4 w-4')} />
      </div>
      {showLabel && <span className={cn('font-medium', size === 'sm' ? 'text-xs' : 'text-sm', cfg.color)}>{cfg.label}</span>}
    </div>
  )
}
