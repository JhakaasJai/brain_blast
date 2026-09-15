import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getSafetyCheckIn, createSafetyCheckIn, updateProfile } from '../services/api'

export default function SafetyCheckInPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [status, setStatus] = useState('home')
  const [note, setNote] = useState('')
  const [shareLocation, setShareLocation] = useState(false)
  const [area, setArea] = useState('')
  const [saved, setSaved] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user?.id) return
    getSafetyCheckIn(user.id).then((value) => {
      if (!value) return
      setSaved(value)
      setStatus(value.status)
      setNote(value.note || '')
      setShareLocation(value.share_location)
      setArea(value.approximate_area || '')
    }).catch(() => {})
  }, [user])

  async function save(event) {
    event.preventDefault()
    setError('')
    try {
      if (shareLocation) await updateProfile(user.id, { location_sharing_consent: true })
      setSaved(await createSafetyCheckIn(user.id, {
        status, note, share_location: shareLocation, approximate_area: area || null,
      }))
    } catch (e) {
      setError(e.response?.data?.detail || 'Unable to save check-in.')
    }
  }

  return (
    <main className="page" aria-labelledby="safety-title">
      <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}>
        <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(-1)}>← Back</button>
        <h1 id="safety-title">Safety check-in</h1><span />
      </header>
      <div className="card">
        <p>Share only what you choose. This prototype stores only your latest check-in, not continuous location history.</p>
        {error && <p role="alert" className="error-text">{error}</p>}
        <form onSubmit={save}>
          <label htmlFor="safety-status">I am currently</label>
          <select id="safety-status" className="input" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="home">At home</option><option value="with_caregiver">With my caregiver</option>
            <option value="out">Out</option><option value="needs_help">I need help</option>
          </select>
          <label htmlFor="safety-note">Note</label>
          <textarea id="safety-note" className="input textarea" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note for your caregiver" />
          <label><input type="checkbox" checked={shareLocation} onChange={(e) => setShareLocation(e.target.checked)} /> Share an approximate area</label>
          {shareLocation && <>
            <label htmlFor="area">Approximate area</label>
            <input id="area" className="input" value={area} onChange={(e) => setArea(e.target.value)} placeholder="Village or neighbourhood" />
          </>}
          <button className="btn btn-primary btn-block mt-2">Save check-in</button>
        </form>
        {saved && <p role="status" className="mt-2">Last saved: {saved.checked_in_at}</p>}
      </div>
    </main>
  )
}

export { SafetyCheckInPage }
