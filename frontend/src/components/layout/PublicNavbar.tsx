import { Link, useLocation } from 'react-router-dom'
import { FileText, Search, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

export function PublicNavbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="bg-[#0d1b6e] text-white shadow-lg sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div className="w-9 h-9 bg-[#0693E3] rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">MDE</span>
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold leading-tight">Alcaldía de Medellín</p>
              <p className="text-xs text-blue-300 leading-tight">Sistema PQRSD</p>
            </div>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            <Link
              to="/"
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive('/') ? 'bg-[#0693E3] text-white' : 'text-slate-300 hover:bg-white/10'
              )}
            >
              Inicio
            </Link>
            <Link
              to="/radicar"
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive('/radicar') ? 'bg-[#0693E3] text-white' : 'text-slate-300 hover:bg-white/10'
              )}
            >
              <FileText className="h-4 w-4" />
              Radicar PQRSD
            </Link>
            <Link
              to="/consultar"
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive('/consultar') ? 'bg-[#0693E3] text-white' : 'text-slate-300 hover:bg-white/10'
              )}
            >
              <Search className="h-4 w-4" />
              Consultar Estado
            </Link>
            <Link
              to="/staff/login"
              className="ml-2 px-4 py-2 rounded-lg text-sm font-medium bg-white/10 hover:bg-white/20 text-white transition-colors"
            >
              Acceso Funcionarios
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-white/10"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden pb-3 border-t border-white/10 pt-2 space-y-1">
            <Link to="/" className="block px-3 py-2 rounded-lg text-sm hover:bg-white/10" onClick={() => setMenuOpen(false)}>Inicio</Link>
            <Link to="/radicar" className="block px-3 py-2 rounded-lg text-sm hover:bg-white/10" onClick={() => setMenuOpen(false)}>Radicar PQRSD</Link>
            <Link to="/consultar" className="block px-3 py-2 rounded-lg text-sm hover:bg-white/10" onClick={() => setMenuOpen(false)}>Consultar Estado</Link>
            <Link to="/staff/login" className="block px-3 py-2 rounded-lg text-sm hover:bg-white/10" onClick={() => setMenuOpen(false)}>Acceso Funcionarios</Link>
          </div>
        )}
      </div>
    </nav>
  )
}
