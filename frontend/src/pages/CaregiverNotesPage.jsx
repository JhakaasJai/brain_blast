import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { createCaregiverNote, getCaregiverNotes } from '../services/api'

export default function CaregiverNotesPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const patientId = params.get('patient_id') || ''
  const [notes, setNotes] = useState([])
  const [note, setNote] = useState('')
  const [category, setCategory] = useState('handover')
  const [error, setError] = useState('')
  const [saved, setSaved] = useState('')

  const load = () => getCaregiverNotes(patientId).then(setNotes).catch(() => setError('Unable to load handover notes.'))
  useEffect(() => { load() }, [patientId])

  async function submit(event) {
    event.preventDefault()
    setError('')
    setSaved('')
    if (!note.trim()) return setError('Write a note before saving.')
    try {
      await createCaregiverNote({ patient_id: patientId, note: note.trim(), category })
      setNote('')
      setSaved('Note added to the handover log.')
      await load()
    } catch (e) { setError(e.response?.data?.detail || 'Unable to save note.') }
  }

  return <main className="page" aria-labelledby="notes-title">
    <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}>
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(-1)}>← Back</button>
      <h1 id="notes-title">Care notes</h1><span />
    </header>
    <div className="card">
      <h2>Add handover note</h2>
      <form onSubmit={submit}>
        <label htmlFor="note-category">Category</label>
        <select id="note-category" className="input" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="handover">Handover</option><option value="observation">Observation</option>
          <option value="appointment">Appointment</option><option value="routine">Routine</option><option value="other">Other</option>
        </select>
        <label htmlFor="care-note">Note</label>
        <textarea id="care-note" className="input textarea" value={note} onChange={(e) => setNote(e.target.value)} placeholder="What should the next caregiver know?" />
        <button className="btn btn-primary btn-block mt-2">Save note</button>
      </form>
    </div>
    {error && <p role="alert" className="error-text">{error}</p>}
    {saved && <p role="status" className="success-text">{saved}</p>}
    {notes.map((entry) => <article className="card" key={entry.id}>
      <h2>{entry.category}</h2><p>{entry.note}</p><small>{entry.created_at} · Author: {entry.author_id}</small>
    </article>)}
  </main>
}

export { CaregiverNotesPage }
