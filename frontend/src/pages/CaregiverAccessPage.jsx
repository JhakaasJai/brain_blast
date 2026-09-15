import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCaregiverLinks } from '../services/api'

export default function CaregiverAccessPage() {
  const navigate = useNavigate()
  const [links, setLinks] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { getCaregiverLinks().then(setLinks).catch(() => setError('Unable to load caregiver access.')) }, [])
  return <main className="page" aria-labelledby="caregiver-access-title">
    <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}><button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(-1)}>← Back</button><h1 id="caregiver-access-title">Care team</h1><span /></header>
    <p>These caregivers can support the patient account. Access is controlled by consent and can be revoked.</p>
    {error && <p role="alert" className="error-text">{error}</p>}
    {!links.length && !error && <div className="card"><p>No caregiver links found.</p></div>}
    {links.map((link) => <article className="card" key={link.id}><h2>{link.relationship}</h2><p>Caregiver account: {link.caregiver_id}</p><p>Status: <strong>{link.status}</strong></p></article>)}
  </main>
}

export { CaregiverAccessPage }
