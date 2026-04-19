import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Inbox, FileText, BarChart2,
  LogOut, ChevronRight, AlertTriangle, CheckSquare,
  BookOpen, Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/useAuth'

const navItems = [
  { href: '/staff/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/staff/inbox', label: 'Bandeja de Entrada', icon: Inbox },
  { href: '/staff/pqrsd', label: 'Todos los PQRSD', icon: FileText },
  { href: '/staff/metricas', label: 'Métricas', icon: BarChart2 },
  { href: '/staff/demo', label: 'Demo Multicanal', icon: Zap },
]

interface StaffSidebarProps {
  collapsed?: boolean
}

export function StaffSidebar({ collapsed = false }: StaffSidebarProps) {
  const location = useLocation()
  const { user, logout } = useAuth()

  const isActive = (href: string) => location.pathname.startsWith(href)

  return (
    <aside className={cn(
      'bg-[#1a3a2a] text-white flex flex-col transition-all duration-200',
      collapsed ? 'w-16' : 'w-64'
    )}>
      {/* Logo */}
      <div className="p-4 border-b border-white/10">
        <Link to="/staff/dashboard" className="flex items-center gap-3">
          <div className="w-9 h-9 bg-[#00a859] rounded-lg flex items-center justify-center shrink-0">
            <span className="text-white font-bold text-sm">MDE</span>
          </div>
          {!collapsed && (
            <div>
              <p className="text-sm font-semibold leading-tight">Alcaldía</p>
              <p className="text-xs text-emerald-300">Panel PQRSD</p>
            </div>
          )}
        </Link>
      </div>

      {/* User info */}
      {!collapsed && (
        <div className="px-4 py-3 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-gradient-to-br from-[#00a859] to-[#006b3c] rounded-full flex items-center justify-center text-sm font-bold ring-2 ring-white/20 shrink-0">
              {user?.fullName?.charAt(0)?.toUpperCase() || '?'}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold truncate leading-tight">{user?.fullName || 'Funcionario'}</p>
              <p className="text-xs text-emerald-300 leading-tight">{user?.username || 'Sistema PQRSD'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            to={href}
            className={cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group',
              isActive(href)
                ? 'bg-[#00a859] text-white'
                : 'text-slate-300 hover:bg-white/10 hover:text-white'
            )}
            title={collapsed ? label : undefined}
          >
            <Icon className="h-5 w-5 shrink-0" />
            {!collapsed && (
              <>
                <span className="flex-1">{label}</span>
                {isActive(href) && <ChevronRight className="h-4 w-4" />}
              </>
            )}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-2 border-t border-white/10 space-y-1">
        <Link
          to="/"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          target="_blank"
        >
          <BookOpen className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Portal Ciudadano</span>}
        </Link>
        <button
          onClick={() => logout()}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          {!collapsed && <span>Cerrar Sesión</span>}
        </button>
      </div>
    </aside>
  )
}
