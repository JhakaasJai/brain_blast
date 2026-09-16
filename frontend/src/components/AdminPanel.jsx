import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { adminGetUsers, adminAssignCaregiver } from '../services/api'
import { useAuth } from '../components/AuthContext'

export default function AdminPanel() {
  const { t } = useTranslation()
  const { user } = useAuth()
  
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const [formData, setFormData] = useState({
    caregiver_id: '',
    patient_id: '',
    relationship: 'Family Member'
  })

  useEffect(() => {
    if (user?.role !== 'admin') return
    adminGetUsers()
      .then(data => {
        setUsers(data)
        setLoading(false)
      })
      .catch(err => {
        setError('Failed to load users: ' + (err.response?.data?.detail || err.message))
        setLoading(false)
      })
  }, [user])

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value })

  const handleAssign = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    try {
      await adminAssignCaregiver(formData)
      setSuccess('Caregiver successfully assigned to patient!')
      setFormData({ caregiver_id: '', patient_id: '', relationship: 'Family Member' })
    } catch (err) {
      setError('Assignment failed: ' + (err.response?.data?.detail || err.message))
    }
  }

  if (user?.role !== 'admin') {
    return <div className="card">Admin access required.</div>
  }

  const patients = users.filter(u => u.role === 'patient')
  const caregivers = users.filter(u => u.role === 'caregiver')

  return (
    <div className="card" style={{ marginTop: '1.5rem' }}>
      <h2>Admin Control Panel</h2>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>
        Assign caregivers to newly registered patients.
      </p>

      {loading ? (
        <p>Loading users...</p>
      ) : (
        <form onSubmit={handleAssign}>
          <div className="mb-2">
            <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem' }}>Select Caregiver</label>
            <select name="caregiver_id" className="input" style={{ appearance: 'auto' }} required value={formData.caregiver_id} onChange={handleChange}>
              <option value="">-- Choose Caregiver --</option>
              {caregivers.map(c => (
                <option key={c.id} value={c.id}>{c.name} ({c.email})</option>
              ))}
            </select>
          </div>

          <div className="mb-2">
            <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem' }}>Select Patient</label>
            <select name="patient_id" className="input" style={{ appearance: 'auto' }} required value={formData.patient_id} onChange={handleChange}>
              <option value="">-- Choose Patient --</option>
              {patients.map(p => (
                <option key={p.id} value={p.id}>{p.name} ({p.email})</option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.4rem' }}>Relationship</label>
            <input type="text" name="relationship" className="input" required value={formData.relationship} onChange={handleChange} placeholder="e.g., Son, Daughter, Professional Caregiver" />
          </div>

          {error && <div style={{ color: '#c62828', marginBottom: '1rem', fontWeight: 600 }}>{error}</div>}
          {success && <div style={{ color: '#2e7d32', marginBottom: '1rem', fontWeight: 600 }}>{success}</div>}

          <button type="submit" className="btn btn-primary" disabled={!formData.caregiver_id || !formData.patient_id}>
            Assign Caregiver
          </button>
        </form>
      )}

      <hr style={{ margin: '2rem 0', borderColor: 'var(--color-border)' }} />
      <h3>Registered Users ({users.length})</h3>
      <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--color-border)', textAlign: 'left' }}>
              <th style={{ padding: '0.5rem' }}>Name</th>
              <th style={{ padding: '0.5rem' }}>Email</th>
              <th style={{ padding: '0.5rem' }}>Role</th>
              <th style={{ padding: '0.5rem' }}>Registered</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '0.5rem' }}>{u.name}</td>
                <td style={{ padding: '0.5rem' }}>{u.email}</td>
                <td style={{ padding: '0.5rem' }}>
                  <span style={{ 
                    background: u.role === 'admin' ? '#ffe0b2' : u.role === 'patient' ? '#e1bee7' : '#c8e6c9', 
                    padding: '0.2rem 0.5rem', 
                    borderRadius: '4px',
                    fontSize: '0.8rem'
                  }}>
                    {u.role}
                  </span>
                </td>
                <td style={{ padding: '0.5rem' }}>{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
