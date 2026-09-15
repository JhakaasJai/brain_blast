import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getTransportNotes,
  createTransportNote,
  updateTransportNote,
  deleteTransportNote,
} from '../services/api'
import { useAuth } from '../components/AuthContext'

const PATIENTS = [
  { id: 'user-patient-1', name: 'Rina Borah (Assam)' },
  { id: 'user-patient-2', name: 'Banshan Lyngdoh (Meghalaya)' },
  { id: 'user-patient-3', name: 'Thoibi Haobijam (Manipur)' },
]

const MODE_LABELS = {
  walk: '🚶 Walk',
  auto: '🛺 Auto-rickshaw',
  taxi: '🚕 Taxi',
  bus: '🚌 Bus / jeep',
  family_vehicle: '🚗 Family vehicle',
  ambulance: '🚑 Ambulance',
  other: '🔀 Other',
}

const BLANK = {
  patientId: PATIENTS[0].id,
  appointmentRef: '',
  appointmentAt: '',
  mode: 'auto',
  pickupPoint: '',
  pickupTime: '',
  driverName: '',
  driverPhone: '',
  destination: '',
  travelMinutes: '',
  returnNotes: '',
  extraNotes: '',
}

export default function TransportNotesPage() {
  const navigate = useNavigate()
  const { user, signOut } = useAuth()

  const isCareTeam =
    user && ['caregiver', 'health_worker', 'admin'].includes(user.role)

  const defaultPatientId = isCareTeam ? PATIENTS[0].id : user?.id ?? PATIENTS[0].id
  const [viewPatientId, setViewPatientId] = useState(defaultPatientId)
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ ...BLANK, patientId: defaultPatientId })
  const [editingId, setEditingId] = useState(null)
  const [editPickup, setEditPickup] = useState('')

  const load = () => {
    setLoading(true)
    setError('')
    getTransportNotes(viewPatientId)
      .then(setNotes)
      .catch(() => setError('Could not load transport notes.'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [viewPatientId])

  const field = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    if (!form.pickupPoint.trim() || !form.destination.trim() || !form.pickupTime.trim() || !form.appointmentAt) return
    try {
      const note = await createTransportNote(form.patientId, {
        patient_id: form.patientId,
        appointment_ref: form.appointmentRef.trim() || null,
        appointment_at: new Date(form.appointmentAt).toISOString(),
        mode: form.mode,
        pickup_point: form.pickupPoint.trim(),
        pickup_time: form.pickupTime.trim(),
        driver_or_contact_name: form.driverName.trim() || null,
        driver_or_contact_phone: form.driverPhone.trim() || null,
        destination: form.destination.trim(),
        estimated_travel_minutes: form.travelMinutes ? parseInt(form.travelMinutes, 10) : null,
        return_notes: form.returnNotes.trim() || null,
        extra_notes: form.extraNotes.trim() || null,
      })
      setNotes((prev) => [note, ...prev])
      setForm({ ...BLANK, patientId: form.patientId })
      setShowForm(false)
      setMessage('Transport note saved.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save transport note.')
    }
  }

  const savePickup = async (note) => {
    setError('')
    try {
      const updated = await updateTransportNote(note.patient_id, note.id, { pickup_point: editPickup })
      setNotes((prev) => prev.map((n) => (n.id === updated.id ? updated : n)))
      setEditingId(null)
    } catch {
      setError('Could not update transport note.')
    }
  }

  const remove = async (note) => {
    setError('')
    try {
      await deleteTransportNote(note.patient_id, note.id)
      setNotes((prev) => prev.filter((n) => n.id !== note.id))
    } catch {
      setError('Could not delete transport note.')
    }
  }

  const backPath = user?.role === 'patient' ? '/home' : '/dashboard'

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(backPath)}>
          ← {user?.role === 'patient' ? 'Home' : 'Dashboard'}
        </button>
        <h1>🚗 Transport notes</h1>
        <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={signOut}>
          Logout
        </button>
      </header>

      <main className="page" style={{ maxWidth: 800 }}>
        {/* Patient selector */}
        {isCareTeam && (
          <div className="card">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <strong>Viewing:</strong>
              <select
                className="input"
                value={viewPatientId}
                onChange={(e) => {
                  setViewPatientId(e.target.value)
                  setForm((f) => ({ ...f, patientId: e.target.value }))
                }}
                style={{ maxWidth: 320 }}
              >
                {PATIENTS.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </label>
          </div>
        )}

        {/* Create form (care team only) */}
        {isCareTeam && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0 }}>Add transport note</h2>
              <button className="btn btn-outline" onClick={() => setShowForm((v) => !v)} aria-expanded={showForm}>
                {showForm ? 'Cancel' : '+ New'}
              </button>
            </div>

            {showForm && (
              <form onSubmit={submit} style={{ marginTop: '1rem' }}>
                <label>
                  Patient
                  <select className="input" value={form.patientId} onChange={field('patientId')}>
                    {PATIENTS.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </select>
                </label>
                <label>
                  Appointment date and time
                  <input className="input" type="datetime-local" value={form.appointmentAt} onChange={field('appointmentAt')} required />
                </label>
                <label>
                  Appointment reference (optional — prep note id or description)
                  <input className="input" placeholder="e.g. appt-prep-1 or Neurology OPD" value={form.appointmentRef} onChange={field('appointmentRef')} />
                </label>
                <label>
                  Travel mode
                  <select className="input" value={form.mode} onChange={field('mode')}>
                    {Object.entries(MODE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                  </select>
                </label>
                <label>
                  Pickup point
                  <input className="input" placeholder="e.g. Main road stand near the tea stall" value={form.pickupPoint} onChange={field('pickupPoint')} required />
                </label>
                <label>
                  Pickup time
                  <input className="input" placeholder="e.g. 09:30" value={form.pickupTime} onChange={field('pickupTime')} required />
                </label>
                <label>
                  Driver / escort name
                  <input className="input" placeholder="e.g. Raju Bora (auto driver)" value={form.driverName} onChange={field('driverName')} />
                </label>
                <label>
                  Driver / escort phone
                  <input className="input" type="tel" placeholder="+91 XXXXX XXXXX" value={form.driverPhone} onChange={field('driverPhone')} />
                </label>
                <label>
                  Destination
                  <input className="input" placeholder="e.g. Gauhati Medical College, Neurology OPD, Gate 2" value={form.destination} onChange={field('destination')} required />
                </label>
                <label>
                  Estimated travel time (minutes)
                  <input className="input" type="number" min="1" max="300" placeholder="e.g. 40" value={form.travelMinutes} onChange={field('travelMinutes')} />
                </label>
                <label>
                  Return journey notes
                  <textarea className="input" rows={2} placeholder="e.g. Call same driver. He waits near Gate 2." value={form.returnNotes} onChange={field('returnNotes')} />
                </label>
                <label>
                  Extra notes
                  <textarea className="input" rows={2} placeholder="Any comfort or safety notes for the journey" value={form.extraNotes} onChange={field('extraNotes')} />
                </label>
                {error && <p className="error-text" role="alert">{error}</p>}
                <button className="btn btn-primary btn-block" type="submit">Save transport note</button>
              </form>
            )}
          </div>
        )}

        {message && <p role="status" style={{ color: 'var(--color-success, #2e7d32)', padding: '0 1rem' }}>{message}</p>}
        {error && !showForm && <p className="error-text" role="alert" style={{ padding: '0 1rem' }}>{error}</p>}

        <h2>Transport notes</h2>
        {loading && <p>Loading…</p>}
        {!loading && notes.length === 0 && (
          <p style={{ color: 'var(--color-text-muted, #666)' }}>
            No transport notes yet.{isCareTeam ? ' Use the form above to add one.' : ''}
          </p>
        )}

        {notes.map((note) => (
          <article key={note.id} className="card" aria-label={`Transport to ${note.destination}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
              <div>
                <h3 style={{ margin: '0 0 0.2rem' }}>
                  {MODE_LABELS[note.mode] ?? note.mode} → {note.destination}
                </h3>
                <p style={{ margin: 0, color: 'var(--color-text-muted, #555)', fontSize: '0.9rem' }}>
                  Appointment: {new Date(note.appointment_at).toLocaleString(undefined, {
                    weekday: 'short', month: 'short', day: 'numeric',
                    hour: '2-digit', minute: '2-digit',
                  })}
                </p>
              </div>
              <strong style={{ whiteSpace: 'nowrap' }}>Pickup {note.pickup_time}</strong>
            </div>

            <section style={{ marginTop: '1rem' }}>
              <p style={{ margin: '0 0 0.25rem' }}>
                <strong>Pickup point:</strong>{' '}
                {editingId === note.id ? (
                  <span style={{ display: 'inline-flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                    <input
                      className="input"
                      style={{ maxWidth: 320, display: 'inline-block' }}
                      value={editPickup}
                      onChange={(e) => setEditPickup(e.target.value)}
                    />
                    <button className="btn btn-outline" style={{ fontSize: '0.8rem' }} onClick={() => savePickup(note)}>Save</button>
                    <button className="btn btn-ghost" style={{ fontSize: '0.8rem' }} onClick={() => setEditingId(null)}>Cancel</button>
                  </span>
                ) : (
                  <span>
                    {note.pickup_point}
                    {isCareTeam && (
                      <button
                        className="btn btn-ghost"
                        style={{ fontSize: '0.75rem', marginLeft: '0.5rem' }}
                        onClick={() => { setEditingId(note.id); setEditPickup(note.pickup_point) }}
                      >
                        Edit
                      </button>
                    )}
                  </span>
                )}
              </p>
              {note.driver_or_contact_name && (
                <p style={{ margin: '0.25rem 0' }}>
                  <strong>Driver / escort:</strong> {note.driver_or_contact_name}
                  {note.driver_or_contact_phone && (
                    <> — <a href={`tel:${note.driver_or_contact_phone}`}>{note.driver_or_contact_phone}</a></>
                  )}
                </p>
              )}
              {note.estimated_travel_minutes && (
                <p style={{ margin: '0.25rem 0' }}>
                  <strong>Estimated travel:</strong> {note.estimated_travel_minutes} min
                </p>
              )}
            </section>

            {note.return_notes && (
              <section style={{ marginTop: '0.75rem' }}>
                <h4 style={{ margin: '0 0 0.2rem' }}>Return journey</h4>
                <p style={{ margin: 0 }}>{note.return_notes}</p>
              </section>
            )}

            {note.extra_notes && (
              <section style={{ marginTop: '0.75rem' }}>
                <h4 style={{ margin: '0 0 0.2rem' }}>Notes</h4>
                <p style={{ margin: 0 }}>{note.extra_notes}</p>
              </section>
            )}

            {isCareTeam && (
              <div style={{ marginTop: '1rem' }}>
                <button className="btn btn-outline" style={{ fontSize: '0.85rem' }} onClick={() => remove(note)}>Delete</button>
              </div>
            )}
          </article>
        ))}
      </main>
    </div>
  )
}
