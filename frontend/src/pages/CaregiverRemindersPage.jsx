import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getReminders, createReminder, updateReminder, deleteReminder, getMyPatients } from '../services/api'

const emptyForm = { category: 'medicine', message: '', schedule_rule: { time: '09:00', frequency: 'daily' }, active: true }

export default function CaregiverRemindersPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [patients, setPatients] = useState([])
  const [patientId, setPatientId] = useState('')
  const [reminders, setReminders] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Load real patients from backend
  useEffect(() => {
    if (user?.role === 'patient') return
    getMyPatients()
      .then(pts => {
        setPatients(pts)
        if (pts.length > 0) setPatientId(pts[0].id)
      })
      .catch(() => setError('Unable to load patients.'))
  }, [user])

  async function load() {
    if (!patientId) return
    setLoading(true); setError('')
    try { setReminders(await getReminders(patientId)) }
    catch (e) { setError(e.response?.data?.detail || 'Unable to load reminders.') }
    finally { setLoading(false) }
  }
  useEffect(() => { if (user?.role !== 'patient' && patientId) load() }, [patientId, user])

  const setField = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }))
  const setSchedule = (field) => (event) => setForm((current) => ({ ...current, schedule_rule: { ...current.schedule_rule, [field]: event.target.value } }))

  function edit(reminder) {
    setEditingId(reminder.id)
    setForm({ category: reminder.category, message: reminder.message, schedule_rule: reminder.schedule_rule || { time: '09:00', frequency: 'daily' }, active: reminder.active })
  }
  function reset() { setEditingId(null); setForm(emptyForm) }

  async function save(event) {
    event.preventDefault(); setError('')
    try {
      const payload = { ...form, patient_id: patientId }
      if (editingId) await updateReminder(editingId, payload)
      else await createReminder(payload)
      reset(); await load()
    } catch (e) { setError(e.response?.data?.detail || 'Unable to save reminder.') }
  }
  async function remove(id) {
    if (!window.confirm('Delete this reminder?')) return
    try { await deleteReminder(id); await load() }
    catch (e) { setError(e.response?.data?.detail || 'Unable to delete reminder.') }
  }

  return (
    <main className="page" style={{ maxWidth: 800 }}>
      <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}>
        <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate('/dashboard')}>← Back</button>
        <h1>Reminder management</h1><span />
      </header>
      <div className="card">
        <label htmlFor="managed-patient">Patient</label>
        {patients.length === 0 ? (
          <p style={{ color: 'var(--color-text-secondary)' }}>No patients assigned to you yet.</p>
        ) : (
          <select id="managed-patient" className="input" value={patientId} onChange={(e) => setPatientId(e.target.value)}>
            {patients.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.email})</option>)}
          </select>
        )}
      </div>
      {patientId && (
        <form className="card" onSubmit={save}>
          <h2>{editingId ? 'Edit reminder' : 'Add reminder'}</h2>
          {error && <p role="alert" className="error-text">{error}</p>}
          <label htmlFor="rem-category">Category</label>
          <select id="rem-category" className="input" value={form.category} onChange={setField('category')}>
            <option value="medicine">Medicine</option><option value="hydration">Hydration</option><option value="activity">Activity</option><option value="appointment">Appointment</option>
          </select>
          <label htmlFor="rem-message">Message</label>
          <input id="rem-message" className="input" value={form.message} onChange={setField('message')} required />
          <label htmlFor="rem-time">Time</label>
          <input id="rem-time" className="input" type="time" value={form.schedule_rule.time} onChange={setSchedule('time')} required />
          <label htmlFor="rem-frequency">Frequency</label>
          <select id="rem-frequency" className="input" value={form.schedule_rule.frequency} onChange={setSchedule('frequency')}>
            <option value="daily">Daily</option><option value="weekly">Weekly</option><option value="once">Once</option>
          </select>
          <label><input type="checkbox" checked={form.active} onChange={(e) => setForm((current) => ({ ...current, active: e.target.checked }))} /> Active</label>
          <button className="btn btn-primary" type="submit">{editingId ? 'Save changes' : 'Create reminder'}</button>
          {editingId && <button className="btn btn-ghost" type="button" onClick={reset}>Cancel</button>}
        </form>
      )}
      {loading && <p>Loading…</p>}
      {reminders.map((reminder) => (
        <article className="card" key={reminder.id}>
          <h3>{reminder.category}: {reminder.message}</h3>
          <p>{reminder.schedule_rule?.frequency || 'daily'} at {reminder.schedule_rule?.time || '—'} · {reminder.active ? 'Active' : 'Paused'}</p>
          <button className="btn btn-outline" onClick={() => edit(reminder)}>Edit</button>{' '}
          <button className="btn btn-danger" onClick={() => remove(reminder.id)}>Delete</button>
        </article>
      ))}
    </main>
  )
}

export { emptyForm }
