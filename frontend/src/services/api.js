import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Frontend luôn gọi qua Vite proxy /api -> backend để demo local không phải đổi base URL.
// Attach JWT token to all requests if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// Auth
export const loginAdmin = (username, password) =>
  api.post('/auth/login', { username, password })

export const verifyToken = () => api.get('/auth/verify')

// Public
export const getCategories = () => api.get('/categories')

export const getProcedures = (params) => api.get('/procedures', { params })

export const getProcedureById = (id) => api.get(`/procedures/${id}`)

export const searchProcedures = (params) => api.get('/search', { params })

export const sendChat = (question, session_id, history = []) =>
  api.post('/chat', { question, session_id, history })

export const sendFeedback = (log_id, rating) =>
  api.post('/chat/feedback', { log_id, rating })

// Admin (requires JWT)
export const getAdminStats = () => api.get('/admin/stats')

export const getAdminChatHistory = (params) =>
  api.get('/admin/chat-history', { params })

export const getSystemHealth = () => api.get('/admin/system-health')
