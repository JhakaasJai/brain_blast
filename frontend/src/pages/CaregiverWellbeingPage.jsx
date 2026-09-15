import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCaregiverWellbeing, getCaregiverWellbeing } from '../services/api'
import { useAuth } from '../components/AuthContext'
import MedicalDisclaimer from '../components/MedicalDisclaimer'

const labels = { 1: 'Very low', 2: 'Low', 3: 'Okay', 4: 'Good', 5: 'Very good' }

export default function CaregiverWellbeingPage() {
  const navigate = useNavigate()
  const { signOut } = useAuth()
  const [history, setHistory] = useState([])
  const [energy, setEnergy] = useState(null)
  const [stress, setStress] = useState(null)
  const [support, setSupport] = useState('')
  const [notes, setNotes] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    getCaregiverWellbeing().then(setHistory).catch(() => setError('Could not load wellbeing history.'))
  }, [])

  const submit = async (event) => {
    event.preventDefault()
    if (!energy || !stress) return
    setSaving(true); setError(''); setMessage('')
    try {
      const entry = await createCaregiverWellbeing({
        energy_score: energy, stress_score: stress,
        support_needed: support.trim() || null, notes: notes.trim() || null,
      })
      setHistory((current) => [...current, entry])
      setEnergy(null); setStress(null); setSupport(''); setNotes('')
      setMessage('Check-in saved. Please take a small break if you can.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save check-in.')
    } finally { setSaving(false) }
  }

  const scale = (selected, setSelected, name) => (
    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }} role="group" aria-label={name}>
      {[1, 2, 3, 4, 5].map((score) => (
        <button type="button" key={score} className={`btn ${selected === score ? 'btn-primary' : 'btn-outline'}`}
          aria-pressed={selected === score} onClick={() => setSelected(score)}>
          {score} — {labels[score]}
        </button>
      ))}
    </div>
  )

  return <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
    <header className="app-header">
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate('/dashboard')}>← Dashboard</button>
      <h1>💚 Caregiver wellbeing</h1>
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={signOut}>Logout</button>
    </header>
    <main className="page" style={{ maxWidth: 720 }}>
      <MedicalDisclaimer />
      <div className="card">
        <h2>How are you doing?</h2>
        <p>These private check-ins help you notice when you may need support. They are not a medical assessment.</p>
        <form onSubmit={submit}>
          <label style={{ fontWeight: 700 }}>Energy today</label>
          {scale(energy, setEnergy, 'Energy today')}
          <label style={{ fontWeight: 700, display: 'block', marginTop: '1rem' }}>Stress today</label>
          {scale(stress, setStress, 'Stress today')}
          <label style={{ fontWeight: 700, display: 'block', marginTop: '1rem' }}>Support I may need</label>
          <input className="input" value={support} onChange={(e) => setSupport(e.target.value)} placeholder="A break, a conversation, practical help…" />
          <label style={{ fontWeight: 700, display: 'block', marginTop: '1rem' }}>Optional note</label>
          <textarea className="input" rows="3" value={notes} onChange={(e) => setNotes(e.target.value)} />
          {error && <p role="alert" className="error-text">{error}</p>}
          {message && <p role="status" style={{ color: 'var(--color-success, #2e7d32)' }}>{message}</p>}
          <button className="btn btn-primary btn-block" type="submit" disabled={saving || !energy || !stress}>
            {saving ? 'Saving…' : 'Save check-in'}
          </button>
        </form>
      </div>
      <h2>Previous check-ins</h2>
      {history.length === 0 && <p>No check-ins yet.</p>}
      {[...history].reverse().map((entry) => <div className="card" key={entry.id}>
        <strong>{new Date(entry.recorded_at).toLocaleDateString()}</strong>
        <p>Energy: {entry.energy_score}/5 · Stress: {entry.stress_score}/5</p>
        {entry.support_needed && <p>Support: {entry.support_needed}</p>}
        {entry.notes && <p>{entry.notes}</p>}
      </div>)}
    </main>
  </div>
}
