import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAuditLog } from '../services/api'

export default function AuditLogPage() {
  const navigate = useNavigate()
  const [entries, setEntries] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { getAuditLog().then(setEntries).catch(() => setError('Unable to load audit history.')) }, [])
  return <main className="page" aria-labelledby="audit-title">
    <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}>
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(-1)}>← Back</button>
      <h1 id="audit-title">Access history</h1><span />
    </header>
    <div className="disclaimer">This history shows recent access and consent changes for the patients you are allowed to support.</div>
    {error && <p role="alert" className="error-text">{error}</p>}
    {!entries.length && !error && <div className="card"><p>No access events recorded yet.</p></div>}
    {entries.map((entry) => <article className="card" key={entry.id}>
      <strong>{entry.action.replaceAll('_', ' ')}</strong>
      <p>Patient: {entry.patient_id}</p>
      <small>{entry.accessed_at} · Actor: {entry.actor_id}</small>
    </article>)}
  </main>
}

export { AuditLogPage }
