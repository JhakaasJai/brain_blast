import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { register } from '../services/api'

export default function RegisterPage() {
  const { t, i18n } = useTranslation()
  const { signIn } = useAuth()
  const navigate = useNavigate()
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    role: 'patient',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const data = await register(formData)
      signIn({ id: data.user_id, role: data.role, email: formData.email }, data.access_token, data.refresh_token)
      navigate(data.role === 'patient' ? '/onboarding' : '/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Check details.')
    } finally {
      setBusy(false)
    }
  }

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिंदी' },
    { code: 'as', label: 'অসমীয়া' },
  ]

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center', padding: '1rem',
                  background: 'linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)' }}>

      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        {languages.map((l) => (
          <button key={l.code}
            className="btn btn-ghost"
            style={{ background: i18n.language === l.code ? 'rgba(255,255,255,0.3)' : 'rgba(255,255,255,0.1)',
                     color: '#fff', minHeight: '48px', padding: '0.4rem 0.9rem', fontSize: '1rem' }}
            onClick={() => { i18n.changeLanguage(l.code); localStorage.setItem('lang', l.code) }}>
            {l.label}
          </button>
        ))}
      </div>

      <div className="card" style={{ width: '100%', maxWidth: '450px' }}>
        <h1 style={{ fontSize: 'var(--font-size-xl)', textAlign: 'center', marginBottom: '0.25rem' }}>
          🧠 Create Account
        </h1>
        <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>
          Join the {t('app_name')} platform
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-2">
            <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>Role</label>
            <select name="role" value={formData.role} onChange={handleChange} className="input" style={{ appearance: 'auto' }}>
              <option value="patient">Patient (Senior)</option>
              <option value="caregiver">Caregiver / Family Member</option>
              <option value="health_worker">Health Worker (ASHA)</option>
            </select>
          </div>
          <div className="mb-2">
            <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>Full Name</label>
            <input className="input" type="text" name="name" required value={formData.name} onChange={handleChange} />
          </div>
          <div className="mb-2">
            <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>{t('email')}</label>
            <input className="input" type="email" name="email" required value={formData.email} onChange={handleChange} />
          </div>
          <div className="mb-2">
            <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>Phone Number (Optional)</label>
            <input className="input" type="tel" name="phone" value={formData.phone} onChange={handleChange} />
          </div>
          <div className="mb-3">
            <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>{t('password')}</label>
            <input className="input" type="password" name="password" required value={formData.password} onChange={handleChange} />
            <small style={{ display: 'block', marginTop: '0.25rem', color: 'var(--color-text-secondary)' }}>
              Must be at least 8 characters, with 1 uppercase, 1 lowercase, and 1 number.
            </small>
          </div>

          {error && (
            <div style={{ background: '#fdecea', color: '#c62828', borderRadius: 8,
                          padding: '0.75rem', marginBottom: '1rem', fontWeight: 600 }}>
              {error}
            </div>
          )}

          <button className="btn btn-primary btn-block btn-lg" type="submit" disabled={busy}>
            {busy ? 'Creating Account...' : 'Sign Up'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
            Already have an account? <Link to="/login" style={{ color: 'var(--color-primary)', fontWeight: 600, textDecoration: 'none' }}>Log In</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
