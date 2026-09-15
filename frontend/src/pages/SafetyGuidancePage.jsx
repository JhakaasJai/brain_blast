import React from 'react'
import { useNavigate } from 'react-router-dom'
import MedicalDisclaimer from '../components/MedicalDisclaimer'

const RED_FLAGS = [
  ['Sudden confusion', 'A sudden change needs prompt medical attention.'],
  ['Fall or head injury', 'Keep the person still if seriously injured and contact emergency help.'],
  ['Breathing difficulty or chest pain', 'Call local emergency services immediately.'],
  ['New weakness or speech difficulty', 'Treat as urgent and seek emergency medical help.'],
  ['Fever, dehydration, or severe pain', 'Contact a clinician promptly.'],
  ['Suspected medication error', 'Do not give an extra dose. Contact the pharmacist or clinician.'],
  ['Missing or lost person', 'Call trusted contacts and local emergency services; share the last known check-in.'],
]

export default function SafetyGuidancePage() {
  const navigate = useNavigate()
  return <main className="page" aria-labelledby="safety-guidance-title">
    <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}>
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(-1)}>← Back</button>
      <h1 id="safety-guidance-title">When to seek help</h1><span />
    </header>
    <MedicalDisclaimer />
    <div className="disclaimer mt-1">This is general safety information, not a diagnosis. In an emergency, contact local emergency services or a clinician.</div>
    {RED_FLAGS.map(([title, advice]) => <article className="card" key={title}><h2>⚠️ {title}</h2><p>{advice}</p></article>)}
    <button className="btn btn-danger btn-block" onClick={() => navigate('/emergency-contacts')}>Open emergency contacts</button>
  </main>
}

export { RED_FLAGS }
