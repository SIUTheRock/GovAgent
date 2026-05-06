import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export const getCategories = () => api.get('/categories')

export const getProcedures = (params) => api.get('/procedures', { params })

export const getProcedureById = (id) => api.get(`/procedures/${id}`)

export const searchProcedures = (params) => api.get('/search', { params })

export const sendChat = (question, session_id, history = []) =>
  api.post('/chat', { question, session_id, history })

export const sendFeedback = (log_id, rating) =>
  api.post('/chat/feedback', { log_id, rating })

export const getAdminStats = () => api.get('/admin/stats')
