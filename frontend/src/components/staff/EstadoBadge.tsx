import { Badge } from '@/components/ui/badge'

const config: Record<string, { variant: 'default' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'outline'; label: string }> = {
  radicada: { variant: 'secondary', label: 'Radicada' },
  en_clasificacion: { variant: 'warning', label: 'En Clasificación' },
  clasificada: { variant: 'info', label: 'Clasificada' },
  en_tramite: { variant: 'default', label: 'En Trámite' },
  respondida: { variant: 'success', label: 'Respondida' },
  cerrada: { variant: 'outline', label: 'Cerrada' },
}

export function EstadoBadge({ estado }: { estado: string }) {
  const cfg = config[estado] || { variant: 'default' as const, label: estado }
  return <Badge variant={cfg.variant}>{cfg.label}</Badge>
}
