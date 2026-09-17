import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getAppointmentPreps,
  createAppointmentPrep,
  deleteAppointmentPrep,
  getMyPatients,
} from '../services/api'
import { useAuth } from '../components/AuthContext'

const DISCLAIMER =
  'This preparation note is an organisational aid only and does not constitute medical advice. ' +
  "Discuss all clinical decisions with the patient's doctor."

const BLANK_FORM = {
  patientId: '',
  appointmentAt: '',
  doctorName: '',
  clinicOrHospital: '',
  questionsRaw: '',
  itemsRaw: '',
  transportNotes: '',
  extraNotes: '',
}

function parseLines(raw) {
  return raw
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean)
}

export default function AppointmentPrepPage() {
  const navigate = useNavigate()
  const { user, signOut } = useAuth()

  const isCareTeam =
    user && ['caregiver', 'health_worker', 'admin'].includes(user.role)

  const [patients, setPatients] = useState([])
  const [preps, setPreps] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [form, setForm] = useState(BLANK_FORM)
  const [showForm, setShowForm] = useState(false)

  const [viewPatientId, setViewPatientId] = useState(
    isCareTeam ? '' : user?.id ?? ''
  )

  // Load real patients for care team
  useEffect(() => {
    if (!isCareTeam) return
    getMyPatients()
      .then(pts => {
        setPatients(pts)
        if (pts.length > 0) {
          setViewPatientId(pts[0].id)
          setForm(f => ({ ...f, patientId: pts[0].id }))
        }
      })
      .catch(() => setError('Could not load patients.'))
  }, [isCareTeam])

  /* Patients a care-team member might view; patients only see themselves. */
  const patientOptions = isCareTeam ? patients : (user ? [user] : [])

  const load = () => {
    setLoading(true)
    setError('')
    getAppointmentPreps(viewPatientId)
      .then(setPreps)
      .catch(() => setError('Could not load appointment preparation notes.'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [viewPatientId])

  const handleField = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    if (!form.appointmentAt || !form.doctorName.trim() || !form.clinicOrHospital.trim()) return
    try {
      const prep = await createAppointmentPrep(form.patientId, {
        patient_id: form.patientId,
        appointment_at: new Date(form.appointmentAt).toISOString(),
        doctor_name: form.doctorName.trim(),
        clinic_or_hospital: form.clinicOrHospital.trim(),
        questions_to_ask: parseLines(form.questionsRaw),
        items_to_bring: parseLines(form.itemsRaw),
        transport_notes: form.transportNotes.trim() || null,
        extra_notes: form.extraNotes.trim() || null,
      })
      setPreps((prev) => [prep, ...prev])
      setForm(BLANK_FORM)
      setShowForm(false)
      setMessage('Appointment preparation note saved.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save appointment prep.')
    }
  }

  const removePrep = async (prep) => {
    setError('')
    try {
      await deleteAppointmentPrep(prep.patient_id, prep.id)
      setPreps((prev) => prev.filter((p) => p.id !== prep.id))
    } catch {
      setError('Could not delete prep note.')
    }
  }

  const backPath = user?.role === 'patient' ? '/home' : '/dashboard'

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button
          className="btn btn-ghost"
          style={{ color: '#fff' }}
          onClick={() => navigate(backPath)}
        >
          ← {user?.role === 'patient' ? 'Home' : 'Dashboard'}
        </button>
        <h1>🏥 Appointment preparation</h1>
        <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={signOut}>
          Logout
        </button>
      </header>

      <main className="page" style={{ maxWidth: 800 }}>
        <div className="card" style={{ background: 'var(--color-surface, #fff9f0)', borderLeft: '4px solid var(--color-warning, #e65100)' }}>
          <p style={{ margin: 0, fontSize: '0.92rem', color: 'var(--color-text-muted, #555)' }}>
            {DISCLAIMER}
          </p>
        </div>

        {/* Patient selector (care team) */}
        {isCareTeam && (
          <div className="card">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <strong>Viewing:</strong>
              <select
                className="input"
                value={viewPatientId}
                onChange={(e) => setViewPatientId(e.target.value)}
                style={{ maxWidth: 320 }}
              >
                {patientOptions.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
        )}

        {/* Create form (care team only) */}
        {isCareTeam && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0 }}>Add preparation note</h2>
              <button
                className="btn btn-outline"
                onClick={() => setShowForm((v) => !v)}
                aria-expanded={showForm}
              >
                {showForm ? 'Cancel' : '+ New'}
              </button>
            </div>
            {showForm && (
              <form onSubmit={submit} style={{ marginTop: '1rem' }}>
                <label>
                  Patient
                  <select
                    className="input"
                    value={form.patientId}
                    onChange={handleField('patientId')}
                  >
                  {patientOptions.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
                  </select>
                </label>
                <label>
                  Appointment date and time
                  <input
                    className="input"
                    type="datetime-local"
                    value={form.appointmentAt}
                    onChange={handleField('appointmentAt')}
                    required
                  />
                </label>
                <label>
                  Doctor's name
                  <input
                    className="input"
                    placeholder="e.g. Dr. Pranjal Saikia"
                    value={form.doctorName}
                    onChange={handleField('doctorName')}
                    required
                  />
                </label>
                <label>
                  Clinic or hospital
                  <input
                    className="input"
                    placeholder="e.g. Gauhati Medical College, Neurology OPD"
                    value={form.clinicOrHospital}
                    onChange={handleField('clinicOrHospital')}
                    required
                  />
                </label>
                <label>
                  Questions to ask the doctor (one per line)
                  <textarea
                    className="input"
                    rows={3}
                    placeholder={"Is the current dose correct?\nAre there exercises that help?"}
                    value={form.questionsRaw}
                    onChange={handleField('questionsRaw')}
                  />
                </label>
                <label>
                  Items to bring (one per line)
                  <textarea
                    className="input"
                    rows={3}
                    placeholder={"Aadhar card\nPrevious prescription\nMedication list"}
                    value={form.itemsRaw}
                    onChange={handleField('itemsRaw')}
                  />
                </label>
                <label>
                  Transport notes
                  <input
                    className="input"
                    placeholder="e.g. Auto from village stand at 9am; allow 40 minutes"
                    value={form.transportNotes}
                    onChange={handleField('transportNotes')}
                  />
                </label>
                <label>
                  Extra notes
                  <textarea
                    className="input"
                    rows={2}
                    placeholder="Any comfort or support notes for the visit"
                    value={form.extraNotes}
                    onChange={handleField('extraNotes')}
                  />
                </label>
                {error && <p className="error-text" role="alert">{error}</p>}
                <button className="btn btn-primary btn-block" type="submit">
                  Save preparation note
                </button>
              </form>
            )}
          </div>
        )}

        {/* Status messages */}
        {message && (
          <p role="status" style={{ color: 'var(--color-success, #2e7d32)', padding: '0 1rem' }}>
            {message}
          </p>
        )}
        {error && !showForm && (
          <p className="error-text" role="alert" style={{ padding: '0 1rem' }}>
            {error}
          </p>
        )}

        {/* Prep list */}
        <h2>Preparation notes</h2>
        {loading && <p>Loading…</p>}
        {!loading && preps.length === 0 && (
          <p style={{ color: 'var(--color-text-muted, #666)' }}>
            No preparation notes yet.{isCareTeam ? ' Use the form above to add one.' : ''}
          </p>
        )}
        {preps.map((prep) => (
          <article
            key={prep.id}
            className="card"
            aria-label={`Appointment with ${prep.doctor_name}`}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
              <div>
                <h3 style={{ margin: '0 0 0.25rem' }}>
                  {prep.doctor_name}
                </h3>
                <p style={{ margin: 0, color: 'var(--color-text-muted, #555)' }}>
                  {prep.clinic_or_hospital}
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <strong style={{ fontSize: '1.05rem' }}>
                  {new Date(prep.appointment_at).toLocaleString(undefined, {
                    weekday: 'short',
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </strong>
              </div>
            </div>

            {prep.questions_to_ask?.length > 0 && (
              <section style={{ marginTop: '1rem' }}>
                <h4 style={{ margin: '0 0 0.4rem' }}>Questions to ask the doctor</h4>
                <ul style={{ margin: 0, paddingLeft: '1.4rem' }}>
                  {prep.questions_to_ask.map((q, i) => (
                    <li key={i}>{q}</li>
                  ))}
                </ul>
              </section>
            )}

            {prep.items_to_bring?.length > 0 && (
              <section style={{ marginTop: '1rem' }}>
                <h4 style={{ margin: '0 0 0.4rem' }}>Items to bring</h4>
                <ul style={{ margin: 0, paddingLeft: '1.4rem' }}>
                  {prep.items_to_bring.map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </section>
            )}

            {prep.transport_notes && (
              <section style={{ marginTop: '1rem' }}>
                <h4 style={{ margin: '0 0 0.25rem' }}>🚗 Transport</h4>
                <p style={{ margin: 0 }}>{prep.transport_notes}</p>
              </section>
            )}

            {prep.extra_notes && (
              <section style={{ marginTop: '1rem' }}>
                <h4 style={{ margin: '0 0 0.25rem' }}>Notes</h4>
                <p style={{ margin: 0 }}>{prep.extra_notes}</p>
              </section>
            )}

            {isCareTeam && (
              <div style={{ marginTop: '1rem' }}>
                <button
                  className="btn btn-outline"
                  style={{ fontSize: '0.85rem' }}
                  onClick={() => removePrep(prep)}
                >
                  Delete
                </button>
              </div>
            )}
          </article>
        ))}
      </main>
    </div>
  )
}
