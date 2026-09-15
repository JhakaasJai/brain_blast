import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getCaregiverLinks, updateCaregiverLink } from '../services/api'
import { getVoicePack, isTTSSupported, speak } from '../services/voice'

const LANGUAGES = [
  { code: 'en',  label: 'English' },
  { code: 'hi',  label: 'हिंदी' },
  { code: 'as',  label: 'অসমীয়া' },
  { code: 'kha', label: 'Khasi' },
  { code: 'mni', label: 'মণিপুরী' },
]

const FONT_SIZES = [
  { label: 'Normal',  px: '18px' },
  { label: 'Large',   px: '22px' },
  { label: 'X-Large', px: '26px' },
]

export default function SettingsPage() {
  const { t, i18n } = useTranslation()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [fontSize, setFontSize] = useState(
    document.documentElement.style.getPropertyValue('--font-size-base') || '20px'
  )
  const [links, setLinks] = useState([])
  const [consentError, setConsentError] = useState('')
  const [voiceStatus, setVoiceStatus] = useState('')

  React.useEffect(() => {
    getCaregiverLinks().then(setLinks).catch(() => setConsentError('Unable to load access grants.'))
  }, [])

  const revokeLink = async (linkId) => {
    setConsentError('')
    try {
      const updated = await updateCaregiverLink(linkId, 'revoked')
      setLinks((current) => current.map((link) => link.id === updated.id ? updated : link))
    } catch {
      setConsentError('Unable to revoke this access grant.')
    }
  }

  const setLang = (code) => {
    i18n.changeLanguage(code)
    localStorage.setItem('lang', code)
    setVoiceStatus('')
  }

  const selectedVoice = getVoicePack(i18n.language)

  const testVoice = () => {
    if (!isTTSSupported) {
      setVoiceStatus('Speech is not available in this browser.')
      return
    }
    speak('This is a voice test. Take your time.', selectedVoice.lang)
    setVoiceStatus(`Testing ${selectedVoice.label} voice (${selectedVoice.lang}). ${selectedVoice.source}.`)
  }

  const applyFontSize = (px) => {
    document.documentElement.style.setProperty('--font-size-base', px)
    setFontSize(px)
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate(-1)}>← {t('back')}</button>
        <h1>⚙️ {t('settings')}</h1>
        <span />
      </header>

      <div className="page">
        <div className="card mb-2">
          <h3 style={{ marginTop: 0 }}>🌐 {t('language')}</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {LANGUAGES.map((l) => (
              <button key={l.code}
                className={`btn ${i18n.language === l.code ? 'btn-primary' : 'btn-outline'} btn-block`}
                onClick={() => setLang(l.code)}>
                {l.label} {i18n.language === l.code ? '✓' : ''}
              </button>
            ))}
          </div>
        </div>

        <div className="card mb-2">
          <h3 style={{ marginTop: 0 }}>🔊 Voice pack</h3>
          <p style={{ marginTop: 0 }}>
            {selectedVoice.label} · {selectedVoice.lang}
          </p>
          <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>
            {selectedVoice.source}. The available voice depends on this device/browser.
          </p>
          <button className="btn btn-outline btn-block" onClick={testVoice}>
            🔊 Test voice
          </button>
          {voiceStatus && <p role="status" style={{ fontSize: '0.9rem' }}>{voiceStatus}</p>}
        </div>

        <div className="card mb-2">
          <h3 style={{ marginTop: 0 }}>🔤 Font Size</h3>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {FONT_SIZES.map((f) => (
              <button key={f.px}
                className={`btn ${fontSize === f.px ? 'btn-primary' : 'btn-outline'}`}
                style={{ flex: 1 }}
                onClick={() => applyFontSize(f.px)}>
                {f.label}
              </button>
            ))}
          </div>
        </div>

        <div className="card mb-2">
          <h3 style={{ marginTop: 0 }}>📋 Data Consent and Access</h3>
          <p>{t('consent_body')}</p>
          {consentError && <p role="alert" className="error-text">{consentError}</p>}
          {links.length === 0 && <p>No caregiver access grants are currently listed.</p>}
          {links.map((link) => (
            <div key={link.id} className="card" style={{ marginBottom: '0.75rem' }}>
              <p><strong>{link.relationship}</strong> · {link.status}</p>
              <p style={{ fontSize: '0.9rem' }}>Caregiver account: {link.caregiver_id}</p>
              {link.status === 'active' && (
                <button className="btn btn-danger btn-outline" onClick={() => revokeLink(link.id)}>
                  {t('consent_revoke')}
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="grid-2 mb-2">
          <button className="btn btn-outline btn-block" onClick={() => navigate('/audit-log')}>
            View access history
          </button>
          <button className="btn btn-outline btn-block" onClick={() => navigate('/caregiver-access')}>
            View care team
          </button>
          <button className="btn btn-outline btn-block" onClick={() => navigate('/backup')}>
            Backup and restore
          </button>
        </div>

        <div className="card">
          <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
            ℹ️ {t('not_a_medical_device')}
          </p>
          <button className="btn btn-danger btn-block mt-2" onClick={signOut}>
            {t('logout')}
          </button>
        </div>
      </div>
    </div>
  )
}
