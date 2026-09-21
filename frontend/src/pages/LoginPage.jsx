import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { login, getMe } from '../services/api'
import { AppLogo } from '../components/Icons'

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
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1.25rem 1rem',
      backgroundColor: 'var(--color-bg)'
    }}>
      {/* Multilingual Selector Header */}
      <nav aria-label="Language selection" style={{
        marginBottom: '1.5rem',
        display: 'flex',
        gap: '0.4rem',
        flexWrap: 'wrap',
        justifyContent: 'center',
        maxWidth: '420px',
        width: '100%'
      }}>
        {languages.map((l) => {
          const isActive = i18n.language === l.code
          return (
            <button
              key={l.code}
              type="button"
              className="btn"
              style={{
                background: isActive ? 'var(--color-primary)' : 'var(--color-surface)',
                color: isActive ? '#FFFFFF' : 'var(--color-text)',
                border: isActive ? '2px solid var(--color-primary)' : '2px solid var(--color-border)',
                minHeight: '48px',
                padding: '0.4rem 0.9rem',
                fontSize: '0.95rem',
                fontWeight: isActive ? 700 : 500,
                borderRadius: 'var(--radius-pill)',
                boxShadow: 'var(--shadow-sm)'
              }}
              onClick={() => { i18n.changeLanguage(l.code); localStorage.setItem('lang', l.code) }}
              aria-pressed={isActive}
            >
              {l.label}
            </button>
          )
        })}
      </nav>

      {/* Main Login Card */}
      <main className="card" style={{
        width: '100%',
        maxWidth: '420px',
        padding: '2rem 1.5rem',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-hover)'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'var(--color-primary-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '0.75rem'
          }}>
            <AppLogo size={42} />
          </div>
          <h1 style={{
            fontSize: '1.85rem',
            textAlign: 'center',
            margin: '0 0 0.35rem 0',
            color: 'var(--color-primary)',
            fontWeight: 800
          }}>
            {t('app_name')}
          </h1>
          <p style={{
            textAlign: 'center',
            color: 'var(--color-text-secondary)',
            margin: 0,
            fontSize: '1.05rem',
            lineHeight: 1.4
          }}>
            {t('tagline')}
          </p>
        </div>

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ marginBottom: '1.25rem' }}>
            <label htmlFor="login-email" style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>
              {t('email')}
            </label>
            <input
              id="login-email"
              className="input"
              type="email"
              required
              autoComplete="email"
              placeholder="e.g. patient@ner.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="login-password" style={{ display: 'block', fontWeight: 700, marginBottom: '0.4rem' }}>
              {t('password')}
            </label>
            <input
              id="login-password"
              className="input"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && (
            <div
              role="alert"
              style={{
                background: 'var(--color-emergency-light)',
                color: 'var(--color-emergency-dark)',
                border: '1.5px solid var(--color-emergency)',
                borderRadius: '12px',
                padding: '0.85rem 1rem',
                marginBottom: '1.25rem',
                fontWeight: 600,
                fontSize: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <button
            className="btn btn-primary btn-block btn-lg"
            type="submit"
            disabled={busy}
            style={{ fontWeight: 700 }}
          >
            {busy ? t('loading') : t('login')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '1rem', margin: 0 }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: 'var(--color-primary)', fontWeight: 700, textDecoration: 'underline' }}>
              Sign Up
            </Link>
          </p>
        </div>

        <div style={{
          marginTop: '1.5rem',
          padding: '0.75rem',
          background: 'var(--color-surface-subtle)',
          borderRadius: '10px',
          fontSize: '0.9rem',
          color: 'var(--color-text-secondary)',
          textAlign: 'center',
          lineHeight: 1.4
        }}>
          ℹ️ {t('not_a_medical_device')}
        </div>

        {/* Demo Credentials Helper */}
        <details style={{
          marginTop: '1.25rem',
          fontSize: '0.95rem',
          color: 'var(--color-text-secondary)',
          background: 'var(--color-bg)',
          padding: '0.85rem 1rem',
          borderRadius: '12px',
          border: '1px solid var(--color-border)'
        }}>
          <summary style={{ cursor: 'pointer', fontWeight: 700, color: 'var(--color-text)' }}>
            🔑 Demo accounts for testing
          </summary>
          <ul style={{ marginTop: '0.65rem', paddingLeft: '1.2rem', lineHeight: 1.6 }}>
            <li><strong>Patient:</strong> patient@ner.in / patpass</li>
            <li><strong>Caregiver:</strong> caregiver@ner.in / carepass</li>
            <li><strong>Health Worker:</strong> hw@ner.in / hwpass</li>
            <li><strong>Admin:</strong> admin@ner.in / adminpass</li>
          </ul>
        </details>
      </main>
    </div>
  )
}
