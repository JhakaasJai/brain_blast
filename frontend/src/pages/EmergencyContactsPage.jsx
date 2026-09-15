import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getEmergencyContacts, getEmergencyCallPreview } from '../services/api'

export default function EmergencyContactsPage() {
  const { user } = useAuth(); const navigate = useNavigate()
  const [contacts, setContacts] = useState([]); const [error, setError] = useState('')
  useEffect(() => { if (user?.id) getEmergencyContacts(user.id).then(setContacts).catch(() => setError('Unable to load contacts.')) }, [user])
  async function call(contact) {
    try {
      const preview = await getEmergencyCallPreview(user.id, contact.id)
      if (window.confirm(`Call ${preview.contact_name}?`)) window.location.href = `tel:${preview.phone}`
    } catch { setError('Unable to prepare the call.') }
  }
  return <main className="page" aria-labelledby="emergency-title">
    <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}><button className="btn btn-ghost" style={{color:'#fff'}} onClick={() => navigate(-1)}>← Back</button><h1>Emergency contacts</h1><span /></header>
    <div className="disclaimer">Use only for real safety needs. The app asks for confirmation before calling and never calls automatically from game scores.</div>
    {error && <p role="alert" className="error-text">{error}</p>}
    {contacts.map((contact) => <article className="card" key={contact.id}><h2>{contact.name}</h2><p>{contact.relationship} · {contact.phone}</p><button className="btn btn-danger btn-block" onClick={() => call(contact)}>📞 Call {contact.name}</button></article>)}
    {!contacts.length && !error && <p>No emergency contacts configured.</p>}
  </main>
}

export { EmergencyContactsPage }
