import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { login, getMe } from '../services/api'

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
      // Store tokens first so getMe() can attach the Authorization header
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      let userData = { id: data.user_id, role: data.role, email }
      try {
        // Fetch full user profile to get name, state_region, etc.
        const me = await getMe()
        userData = { ...userData, ...me }
      } catch {
        // Non-fatal: keep minimal userData if /auth/me fails
      }
      signIn(userData, data.access_token, data.refresh_token)
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

      <div className="card" style={{ width: '100%', maxWidth: '420px', padding: '2.5rem 2rem', border: 'none', boxShadow: '0 20px 40px rgba(0,0,0,0.2)' }}>
        <h1 style={{ fontSize: '2rem', textAlign: 'center', marginBottom: '0.5rem', letterSpacing: '-0.03em', color: 'var(--color-primary-dark)' }}>
          🧠 {t('app_name')}
        </h1>
        <p style={{ textAlign: 'center', color: 'var(--color-text-secondary)', marginBottom: '2rem', fontSize: '1.05rem' }}>
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
            <li>patient@ner.in / patpass <em>(Patient — games, reminders, daily tasks)</em></li>
            <li>caregiver@ner.in / carepass <em>(Caregiver — view patient data, care notes)</em></li>
            <li>hw@ner.in / hwpass <em>(Health Worker — visit planning + caregiver features)</em></li>
            <li>admin@ner.in / adminpass <em>(Admin — user management, assign caregivers)</em></li>
          </ul>
        </details>
      </div>
    </div>
  )
}
