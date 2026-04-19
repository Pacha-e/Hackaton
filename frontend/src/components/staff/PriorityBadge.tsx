import { Badge } from '@/components/ui/badge'

const config = {
  urgente: { variant: 'danger' as const, label: 'Urgente' },
  alta: { variant: 'warning' as const, label: 'Alta' },
  media: { variant: 'info' as const, label: 'Media' },
  baja: { variant: 'secondary' as const, label: 'Baja' },
}

export function PriorityBadge({ prioridad }: { prioridad: string }) {
  const cfg = config[prioridad as keyof typeof config] || { variant: 'default' as const, label: prioridad }
  return <Badge variant={cfg.variant}>{cfg.label}</Badge>
}
