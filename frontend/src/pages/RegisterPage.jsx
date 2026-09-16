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
  const [successMsg, setSuccessMsg] = useState('')
  const [busy, setBusy] = useState(false)

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    setSuccessMsg('')
    try {
      const data = await register(formData)
      setSuccessMsg(data.message || 'Registration successful. Please check your email to verify your account.')
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
                  alignItems: 'center', justifyContent: 'center', padding: '1.5rem',
                  background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%)' }}>

      <div style={{ marginBottom: '2rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        {languages.map((l) => (
          <button key={l.code}
            className="btn btn-ghost"
            style={{ 
              background: i18n.language === l.code ? 'rgba(255,255,255,0.25)' : 'transparent',
              color: '#fff', 
              border: i18n.language === l.code ? '2px solid rgba(255,255,255,0.5)' : '2px solid transparent',
              minHeight: '44px', padding: '0.4rem 1.2rem', fontSize: '1rem',
              borderRadius: '99px'
            }}
            onClick={() => { i18n.changeLanguage(l.code); localStorage.setItem('lang', l.code) }}>
            {l.label}
          </button>
        ))}
      </div>

      <div className="card" style={{ width: '100%', maxWidth: '480px', padding: '2.5rem 2rem', border: 'none', boxShadow: '0 20px 40px rgba(0,0,0,0.2)' }}>
        <h1 style={{ fontSize: '2rem', textAlign: 'center', marginBottom: '0.5rem', letterSpacing: '-0.03em', color: 'var(--color-primary-dark)' }}>
          🧠 Create Account
        </h1>
        <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', marginBottom: '2rem', fontSize: '1.05rem' }}>
          Join the {t('app_name')} platform
        </p>

        {successMsg ? (
          <div style={{ textAlign: 'center' }}>
            <div style={{ background: '#e8f5e9', color: '#2e7d32', borderRadius: 8, padding: '1rem', marginBottom: '1.5rem', fontWeight: 600 }}>
              {successMsg}
            </div>
            <Link to="/login" className="btn btn-primary btn-block">Return to Login</Link>
          </div>
        ) : (
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
        )}

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
            Already have an account? <Link to="/login" style={{ color: 'var(--color-primary)', fontWeight: 600, textDecoration: 'none' }}>Log In</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
