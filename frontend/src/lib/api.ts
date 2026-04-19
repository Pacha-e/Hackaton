import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// Fetch CSRF token and set it on all requests
let csrfFetched = false
api.interceptors.request.use(async (config) => {
  if (!csrfFetched && ['post', 'put', 'patch', 'delete'].includes(config.method || '')) {
    try {
      const { data } = await axios.get('/api/v1/auth/csrf/', { withCredentials: true })
      api.defaults.headers.common['X-CSRFToken'] = data.csrfToken
      config.headers['X-CSRFToken'] = data.csrfToken
      csrfFetched = true
    } catch (_) {}
  }
  // Also read from cookie as fallback
  const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/)
  if (cookieMatch) {
    config.headers['X-CSRFToken'] = cookieMatch[1]
  }
  return config
})

export default api

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),
  logout: () => api.post('/auth/logout/'),
  me: () => api.get('/auth/me/'),
}

// ── Public / Citizen ──────────────────────────────────────────────────────
export const citizenApi = {
  submit: (data: FormData) =>
    api.post('/pqrsd/submit/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getStatus: (radicado: string) => api.get(`/pqrsd/status/${radicado}/`),
  getDependencias: () => api.get('/dependencias/'),
  getChoices: () => api.get('/choices/'),
}

// ── Staff ─────────────────────────────────────────────────────────────────
export const staffApi = {
  listPqrsd: (params?: Record<string, string>) =>
    api.get('/pqrsd/', { params }),
  getPqrsd: (id: number) => api.get(`/pqrsd/${id}/`),
  updateEstado: (id: number, data: { estado: string; observaciones?: string; dependencia_asignada?: number }) =>
    api.patch(`/pqrsd/${id}/estado/`, data),
  classify: (id: number) => api.post(`/pqrsd/${id}/classify/`),
  validateClassification: (id: number, data: { aceptada: boolean; comentario?: string; dependencia_id?: number }) =>
    api.post(`/pqrsd/${id}/validate/`, data),
  getSynthesis: (id: number) => api.get(`/pqrsd/${id}/synthesis/`),
  generateSynthesis: (id: number) => api.post(`/pqrsd/${id}/synthesis/`),
  getStats: () => api.get('/stats/'),
  getMapaCalor: () => api.get('/stats/mapa-calor/'),
  getInbox: (params?: Record<string, string>) => api.get('/inbox/', { params }),
  demoInject: (canal: string, scenario?: string) =>
    api.post('/demo/inject/', { canal, scenario }),
}
