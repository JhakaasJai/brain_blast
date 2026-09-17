import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createVisitPlan, getVisitPlans, updateVisitPlan, getMyPatients } from '../services/api'
import { useAuth } from '../components/AuthContext'

export default function VisitPlanningPage() {
  const navigate = useNavigate()
  const { signOut } = useAuth()
  const [visits, setVisits] = useState([])
  const [patients, setPatients] = useState([])
  const [patientId, setPatientId] = useState('')
  const [scheduledAt, setScheduledAt] = useState('')
  const [purpose, setPurpose] = useState('Routine wellbeing check')
  const [location, setLocation] = useState('Patient home')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    getMyPatients()
      .then(pts => {
        setPatients(pts)
        if (pts.length > 0) setPatientId(pts[0].id)
      })
      .catch(() => {})
  }, [])

  const load = () => getVisitPlans().then(setVisits).catch(() => setError('Could not load visit plans.'))
  useEffect(() => { load() }, [])

  const submit = async (event) => {
    event.preventDefault(); setError(''); setMessage('')
    if (!scheduledAt || !purpose.trim() || !location.trim()) return
    try {
      const visit = await createVisitPlan({ patient_id: patientId, scheduled_at: new Date(scheduledAt).toISOString(), purpose, location, notes: notes.trim() || null })
      setVisits((current) => [...current, visit].sort((a, b) => a.scheduled_at.localeCompare(b.scheduled_at)))
      setScheduledAt(''); setNotes(''); setMessage('Visit added to the route plan.')
    } catch (err) { setError(err.response?.data?.detail || 'Could not create visit.') }
  }

  const changeStatus = async (visit, status) => {
    try {
      const updated = await updateVisitPlan(visit.id, { status })
      setVisits((current) => current.map((item) => item.id === updated.id ? updated : item))
    } catch (err) { setError(err.response?.data?.detail || 'Could not update visit.') }
  }

  return <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
    <header className="app-header">
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate('/dashboard')}>← Dashboard</button>
      <h1>🗓️ Visit planning</h1>
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={signOut}>Logout</button>
    </header>
    <main className="page" style={{ maxWidth: 800 }}>
      <div className="card">
        <h2>Add a planned visit</h2>
        <p>Keep route notes practical. This prototype does not calculate travel time or share live location.</p>
        <form onSubmit={submit}>
          <label>Patient<select className="input" value={patientId} onChange={(e) => setPatientId(e.target.value)}>{patients.map((patient) => <option key={patient.id} value={patient.id}>{patient.name}</option>)}</select></label>
          <label>Date and time<input className="input" type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} required /></label>
          <label>Purpose<input className="input" value={purpose} onChange={(e) => setPurpose(e.target.value)} required /></label>
          <label>Location<input className="input" value={location} onChange={(e) => setLocation(e.target.value)} required /></label>
          <label>Notes<textarea className="input" rows="2" value={notes} onChange={(e) => setNotes(e.target.value)} /></label>
          {error && <p className="error-text" role="alert">{error}</p>}
          {message && <p role="status" style={{ color: 'var(--color-success, #2e7d32)' }}>{message}</p>}
          <button className="btn btn-primary btn-block" type="submit">Add visit</button>
        </form>
      </div>
      <h2>Route plan</h2>
      {visits.length === 0 && <p>No planned visits.</p>}
      {visits.map((visit) => <article className="card" key={visit.id}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>{visit.patient_name}</h3>
          <strong>{visit.status}</strong>
        </div>
        <p><strong>{new Date(visit.scheduled_at).toLocaleString()}</strong> · {visit.location}</p>
        <p>{visit.purpose}</p>
        {visit.notes && <p>{visit.notes}</p>}
        {visit.status === 'planned' && <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-outline" onClick={() => changeStatus(visit, 'completed')}>Mark completed</button>
          <button className="btn btn-outline" onClick={() => changeStatus(visit, 'cancelled')}>Cancel</button>
        </div>}
      </article>)}
    </main>
  </div>
}
