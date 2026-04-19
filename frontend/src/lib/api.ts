import axios from "axios";

const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL ?? ""}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach token from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// On 401 response, clear stored token
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("auth_token");
    }
    return Promise.reject(err);
  },
);

export default api;

// ── Auth ──────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username: string, password: string) =>
    api.post("/auth/login/", { username, password }),
  logout: () => api.post("/auth/logout/"),
  me: () => api.get("/auth/me/"),
};

// ── Public / Citizen ──────────────────────────────────────────────────────
export const citizenApi = {
  submit: (data: FormData) =>
    api.post("/pqrsd/submit/", data, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  getStatus: (radicado: string) => api.get(`/pqrsd/status/${radicado}/`),
  getDependencias: () => api.get("/dependencias/"),
  getChoices: () => api.get("/choices/"),
};

// ── Staff ─────────────────────────────────────────────────────────────────
export const staffApi = {
  listPqrsd: (params?: Record<string, string>) =>
    api.get("/pqrsd/", { params }),
  getPqrsd: (id: number) => api.get(`/pqrsd/${id}/`),
  updateEstado: (
    id: number,
    data: {
      estado: string;
      observaciones?: string;
      dependencia_asignada?: number;
    },
  ) => api.patch(`/pqrsd/${id}/estado/`, data),
  classify: (id: number) => api.post(`/pqrsd/${id}/classify/`),
  validateClassification: (
    id: number,
    data: { aceptada: boolean; comentario?: string; dependencia_id?: number },
  ) => api.post(`/pqrsd/${id}/validate/`, data),
  getSynthesis: (id: number) => api.get(`/pqrsd/${id}/synthesis/`),
  generateSynthesis: (id: number) => api.post(`/pqrsd/${id}/synthesis/`),
  getStats: () => api.get("/stats/"),
  getMapaCalor: () => api.get("/stats/mapa-calor/"),
  getInbox: (params?: Record<string, string>) => api.get("/inbox/", { params }),
  demoInject: (canal: string, scenario?: string) =>
    api.post("/demo/inject/", { canal, scenario }),
};
