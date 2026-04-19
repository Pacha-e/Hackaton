import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuth } from '@/hooks/useAuth'
import { PageLoader } from '@/components/ui/spinner'

// Citizen pages
import HomePage from '@/pages/citizen/HomePage'
import SubmitPage from '@/pages/citizen/SubmitPage'
import ConfirmationPage from '@/pages/citizen/ConfirmationPage'
import StatusPage from '@/pages/citizen/StatusPage'

// Staff pages
import LoginPage from '@/pages/staff/LoginPage'
import DashboardPage from '@/pages/staff/DashboardPage'
import InboxPage from '@/pages/staff/InboxPage'
import PqrsdListPage from '@/pages/staff/PqrsdListPage'
import PqrsdDetailPage from '@/pages/staff/PqrsdDetailPage'
import MetricasPage from '@/pages/staff/MetricasPage'
import DemoPage from '@/pages/staff/DemoPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
    },
  },
})

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) return <PageLoader />
  if (!isAuthenticated) return <Navigate to="/staff/login" replace />
  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      {/* Citizen routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/radicar" element={<SubmitPage />} />
      <Route path="/confirmacion/:radicado" element={<ConfirmationPage />} />
      <Route path="/consultar" element={<StatusPage />} />

      {/* Staff routes */}
      <Route path="/staff/login" element={<LoginPage />} />
      <Route path="/staff/dashboard" element={
        <ProtectedRoute><DashboardPage /></ProtectedRoute>
      } />
      <Route path="/staff/inbox" element={
        <ProtectedRoute><InboxPage /></ProtectedRoute>
      } />
      <Route path="/staff/pqrsd" element={
        <ProtectedRoute><PqrsdListPage /></ProtectedRoute>
      } />
      <Route path="/staff/pqrsd/:id" element={
        <ProtectedRoute><PqrsdDetailPage /></ProtectedRoute>
      } />
      <Route path="/staff/metricas" element={
        <ProtectedRoute><MetricasPage /></ProtectedRoute>
      } />
      <Route path="/staff/demo" element={
        <ProtectedRoute><DemoPage /></ProtectedRoute>
      } />

      {/* Fallbacks */}
      <Route path="/staff" element={<Navigate to="/staff/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
