// API service — all REST calls go here.
// The frontend never hardcodes mock data; it always fetches from the backend.
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE_URL })

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const res = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token: refresh })
          localStorage.setItem('access_token', res.data.access_token)
          localStorage.setItem('refresh_token', res.data.refresh_token)
          error.config.headers.Authorization = `Bearer ${res.data.access_token}`
          return api(error.config)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// Auth
export const login = (email, password) =>
  api.post('/auth/login', { email, password }).then((r) => r.data)

export const register = (data) =>
  api.post('/auth/register', data).then((r) => r.data)

export const adminGetUsers = () =>
  api.get('/auth/admin/users').then((r) => r.data)

export const adminAssignCaregiver = (data) =>
  api.post('/auth/admin/assign-caregiver', data).then((r) => r.data)

// Profile
export const getProfile = (patientId) =>
  api.get(`/patients/${patientId}/profile`).then((r) => r.data)

export const updateProfile = (patientId, data) =>
  api.put(`/patients/${patientId}/profile`, data).then((r) => r.data)

export const getMe = () =>
  api.get('/auth/me').then((r) => r.data)

export const updateMe = (data) =>
  api.patch('/auth/me', data).then((r) => r.data)

export const getRegionalThemes = () =>
  api.get('/regional-themes').then((r) => r.data)

export const getMedications = (patientId) =>
  api.get(`/patients/${patientId}/medications`).then((r) => r.data)

export const createMedication = (patientId, data) =>
  api.post(`/patients/${patientId}/medications`, { ...data, patient_id: patientId }).then((r) => r.data)

export const getSafetyCheckIn = (patientId) =>
  api.get(`/patients/${patientId}/safety-check-in`).then((r) => r.data)

export const createSafetyCheckIn = (patientId, data) =>
  api.post(`/patients/${patientId}/safety-check-in`, { ...data, patient_id: patientId }).then((r) => r.data)

export const getEmergencyContacts = (patientId) =>
  api.get(`/patients/${patientId}/emergency-contacts`).then((r) => r.data)

export const getEmergencyCallPreview = (patientId, contactId) =>
  api.get(`/patients/${patientId}/emergency-call/${contactId}`).then((r) => r.data)

export const createEmergencyContact = (patientId, data) =>
  api.post(`/patients/${patientId}/emergency-contacts`, { ...data, patient_id: patientId }).then((r) => r.data)

// Consent and caregiver access
export const getCaregiverLinks = () =>
  api.get('/caregiver-links').then((r) => r.data)

export const createCaregiverLink = (data) =>
  api.post('/caregiver-links', data).then((r) => r.data)

export const updateCaregiverLink = (linkId, status) =>
  api.patch(`/caregiver-links/${linkId}`, { status }).then((r) => r.data)

export const getAuditLog = (patientId) =>
  api.get('/audit-log', { params: patientId ? { patient_id: patientId } : {} }).then((r) => r.data)

export const getCaregiverNotes = (patientId) =>
  api.get('/caregiver-notes', { params: { patient_id: patientId } }).then((r) => r.data)

export const createCaregiverNote = (data) =>
  api.post('/caregiver-notes', data).then((r) => r.data)

// Reminders
export const getReminders = (patientId) =>
  api.get('/reminders', { params: { patient_id: patientId } }).then((r) => r.data)

export const createReminder = (data) =>
  api.post('/reminders', data).then((r) => r.data)

export const updateReminder = (id, data) =>
  api.patch(`/reminders/${id}`, data).then((r) => r.data)

export const deleteReminder = (id) =>
  api.delete(`/reminders/${id}`)

// Sync
export const syncGameSessions = (sessions) =>
  api.post('/sync/game-sessions', { sessions }).then((r) => r.data)

export const syncReminderEvents = (events) =>
  api.post('/sync/reminder-events', { events }).then((r) => r.data)

// Difficulty
export const getNextDifficulty = (patientId, gameType) =>
  api.get('/difficulty/next', { params: { patient_id: patientId, game_type: gameType } }).then((r) => r.data)

// Dashboard
export const getDashboardSummary = (patientId) =>
  api.get(`/dashboard/${patientId}/summary`).then((r) => r.data)

export const getCareSummary = (patientId, periodDays = 30) =>
  api.get(`/dashboard/${patientId}/care-summary`, { params: { period_days: periodDays } }).then((r) => r.data)

export const exportCareSummary = (patientId, periodDays = 30) =>
  api.get(`/dashboard/${patientId}/care-summary.csv`, { params: { period_days: periodDays } }).then((r) => r.data)

export const getDashboardTrends = (patientId, gameType = 'memory', range = 30) =>
  api.get(`/dashboard/${patientId}/trends`, { params: { game_type: gameType, range } }).then((r) => r.data)

export const getAlerts = (patientId) =>
  api.get('/alerts', { params: { patient_id: patientId } }).then((r) => r.data)

// Notifications (simulated push/SMS)
export const getNotifications = () =>
  api.get('/notifications/').then((r) => r.data)

// Reminiscence therapy
export const getReminiscencePrompts = (patientId) =>
  api.get(`/patients/${patientId}/reminiscence/prompts`).then((r) => r.data)

export const getReminiscenceNotes = (patientId) =>
  api.get(`/patients/${patientId}/reminiscence/notes`).then((r) => r.data)

export const createReminiscenceNote = (patientId, data) =>
  api.post(`/patients/${patientId}/reminiscence/notes`, data).then((r) => r.data)

export const createReminiscencePrompt = (patientId, data) =>
  api.post(`/patients/${patientId}/reminiscence/prompts`, data).then((r) => r.data)

// Social connection messages
export const getSocialMessages = (patientId) =>
  api.get(`/patients/${patientId}/messages`).then((r) => r.data)

export const sendSocialMessage = (patientId, data) =>
  api.post(`/patients/${patientId}/messages`, data).then((r) => r.data)

// Daily living assistance
export const getDailyTasks = (patientId) =>
  api.get(`/patients/${patientId}/daily-tasks`).then((r) => r.data)

export const toggleDailyTask = (patientId, taskId, done) =>
  api.patch(`/patients/${patientId}/daily-tasks/${taskId}`, { done }).then((r) => r.data)

// Sleep and mood check-ins
export const getMoodCheckins = (patientId) =>
  api.get(`/patients/${patientId}/mood-checkins`).then((r) => r.data)

export const createMoodCheckin = (patientId, data) =>
  api.post(`/patients/${patientId}/mood-checkins`, data).then((r) => r.data)

// Physical activity
export const getActivities = (patientId) =>
  api.get(`/patients/${patientId}/activities`).then((r) => r.data)

export const createActivity = (patientId, data) =>
  api.post(`/patients/${patientId}/activities`, data).then((r) => r.data)

// Caregiver education library
export const getEducationArticles = () =>
  api.get('/education/articles').then((r) => r.data)

export const getEducationArticle = (articleId) =>
  api.get(`/education/articles/${articleId}`).then((r) => r.data)

export const updateEducationProgress = (articleId, completed) =>
  api.patch(`/education/articles/${articleId}/progress`, { completed }).then((r) => r.data)

// Caregiver wellbeing check-ins
export const getCaregiverWellbeing = () =>
  api.get('/caregiver-wellbeing').then((r) => r.data)

export const createCaregiverWellbeing = (data) =>
  api.post('/caregiver-wellbeing', data).then((r) => r.data)

// Health-worker route and visit planning
export const getVisitPlans = (patientId) =>
  api.get('/health-worker/visits', { params: patientId ? { patient_id: patientId } : {} }).then((r) => r.data)

export const createVisitPlan = (data) =>
  api.post('/health-worker/visits', data).then((r) => r.data)

export const updateVisitPlan = (visitId, data) =>
  api.patch(`/health-worker/visits/${visitId}`, data).then((r) => r.data)

export const deleteVisitPlan = (visitId) =>
  api.delete(`/health-worker/visits/${visitId}`)

// Appointment preparation (R16)
export const getAppointmentPreps = (patientId) =>
  api.get(`/patients/${patientId}/appointment-prep`).then((r) => r.data)

export const getNextAppointmentPrep = (patientId) =>
  api.get(`/patients/${patientId}/appointment-prep/next`).then((r) => r.data)

export const createAppointmentPrep = (patientId, data) =>
  api.post(`/patients/${patientId}/appointment-prep`, data).then((r) => r.data)

export const updateAppointmentPrep = (patientId, prepId, data) =>
  api.patch(`/patients/${patientId}/appointment-prep/${prepId}`, data).then((r) => r.data)

export const deleteAppointmentPrep = (patientId, prepId) =>
  api.delete(`/patients/${patientId}/appointment-prep/${prepId}`)

// Appointment transport / location notes (R17)
export const getTransportNotes = (patientId) =>
  api.get(`/patients/${patientId}/transport-notes`).then((r) => r.data)

export const getTransportNote = (patientId, noteId) =>
  api.get(`/patients/${patientId}/transport-notes/${noteId}`).then((r) => r.data)

export const createTransportNote = (patientId, data) =>
  api.post(`/patients/${patientId}/transport-notes`, data).then((r) => r.data)

export const updateTransportNote = (patientId, noteId, data) =>
  api.patch(`/patients/${patientId}/transport-notes/${noteId}`, data).then((r) => r.data)

export const deleteTransportNote = (patientId, noteId) =>
  api.delete(`/patients/${patientId}/transport-notes/${noteId}`)

export default api
