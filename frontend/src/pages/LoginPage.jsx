import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { login } from '../services/api'

export default function LoginPage() {
  const { t, i18n } = useTranslation()
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const data = await login(email, password)
      signIn({ id: data.user_id, role: data.role, email }, data.access_token, data.refresh_token)
      navigate(data.role === 'patient' ? '/home' : '/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check credentials.')
    } finally {
      setBusy(false)
    }
  }

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिंदी' },
    { code: 'as', label: 'অসমীয়া' },
    { code: 'kha', label: 'Khasi' },
    { code: 'mni', label: 'মণিপুরী' },
  ]

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column',
                  alignItems: 'center', justifyContent: 'center', padding: '1rem',
                  background: 'linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)' }}>

      {/* Language picker */}
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

      <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
        <h1 style={{ fontSize: 'var(--font-size-xl)', textAlign: 'center', marginBottom: '0.25rem' }}>
          🧠 {t('app_name')}
        </h1>
        <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>
          {t('tagline')}
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-2">
            <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>
              {t('email')}
            </label>
            <input className="input" type="email" required autoComplete="email"
              value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="mb-3">
            <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>
              {t('password')}
            </label>
            <input className="input" type="password" required autoComplete="current-password"
              value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>

          {error && (
            <div style={{ background: '#fdecea', color: '#c62828', borderRadius: 8,
                          padding: '0.75rem', marginBottom: '1rem', fontWeight: 600 }}>
              {error}
            </div>
          )}

          <button className="btn btn-primary btn-block btn-lg" type="submit" disabled={busy}>
            {busy ? t('loading') : t('login')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
            Don't have an account? <Link to="/register" style={{ color: 'var(--color-primary)', fontWeight: 600, textDecoration: 'none' }}>Sign Up</Link>
          </p>
        </div>

        <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginTop: '1.5rem', textAlign: 'center' }}>
          {t('not_a_medical_device')}
        </p>

        {/* Demo credentials helper */}
        <details style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 700 }}>Demo accounts</summary>
          <ul style={{ marginTop: '0.5rem', paddingLeft: '1.2rem' }}>
            <li>patient@ner.in / patpass (Patient)</li>
            <li>caregiver@ner.in / carepass (Caregiver)</li>
            <li>hw@ner.in / hwpass (Health Worker)</li>
            <li>admin@ner.in / adminpass (Admin)</li>
          </ul>
        </details>
      </div>
    </div>
  )
}
