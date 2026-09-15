import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getMedications } from '../services/api'
import MedicalDisclaimer from '../components/MedicalDisclaimer'

export default function MedicationsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [medications, setMedications] = useState([])
  const [error, setError] = useState('')
  useEffect(() => {
    if (user?.id) getMedications(user.id).then(setMedications).catch(() => setError('Unable to load medication records.'))
  }, [user])
  return <main className="page" aria-labelledby="medications-title">
    <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}>
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(-1)}>← Back</button>
      <h1 id="medications-title">Medications</h1><span />
    </header>
    <MedicalDisclaimer />
    <div className="disclaimer mt-1">Medication records are for reference. Do not change a dose or take an extra dose after a missed dose. Ask the prescribing clinician or pharmacist.</div>
    {error && <p role="alert" className="error-text">{error}</p>}
    {medications.map((medication) => <article className="card" key={medication.id}>
      <h2>{medication.name}</h2><p><strong>{medication.dose}</strong> · {medication.form}</p>
      <p>{medication.instructions}</p>
      {medication.prescribing_clinician && <p>Prescriber: {medication.prescribing_clinician}</p>}
      <p className="disclaimer">If missed: {medication.missed_dose_guidance}</p>
    </article>)}
    {!medications.length && !error && <p>No medication records configured.</p>}
  </main>
}

export { MedicationsPage }
