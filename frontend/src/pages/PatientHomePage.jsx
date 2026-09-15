import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getNextDifficulty, getProfile } from '../services/api'
import MedicalDisclaimer from '../components/MedicalDisclaimer'
import { getVoicePack, isTTSSupported, speak, stopSpeaking } from '../services/voice' 

function getSpokenHomeSummary(name, isOnline) {
  return `Welcome ${name}. ${isOnline ? 'Your progress is connected.' : 'You are offline; your progress is saved on this device.'} Choose an activity, reminders, messages, or settings.`
} 

function getNavigationAnnouncement(label) {
  return `${label}. Opening now.`
} 

const GAMES = [
  { key: 'memory',      icon: '🃏', color: '#1a73e8' },
  { key: 'attention',   icon: '👁️',  color: '#2e7d32' },
  { key: 'routine',     icon: '📅', color: '#e65100' },
  { key: 'recognition', icon: '🎨', color: '#6a1b9a' },
]

export default function PatientHomePage() {
  const { t } = useTranslation()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [difficulties, setDifficulties] = useState({})
  const [profile, setProfile] = useState(null)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [audioStatus, setAudioStatus] = useState('')

  const patientName = profile?.preferred_name || user?.email?.split('@')[0] || 'Friend'
  const voicePack = getVoicePack(localStorage.getItem('lang') || 'en')

  useEffect(() => () => stopSpeaking(), [])

  const readPage = () => {
    if (!isTTSSupported) {
      setAudioStatus('Audio guidance is not available in this browser.')
      return
    }
    speak(getSpokenHomeSummary(patientName, isOnline), voicePack.lang)
    setAudioStatus(`Reading this page in ${voicePack.label}.`)
  }

  const navigateWithAudio = (path, label) => {
    if (isTTSSupported) speak(getNavigationAnnouncement(label), voicePack.lang)
    navigate(path)
  }

  useEffect(() => {
    const onOnline  = () => setIsOnline(true)
    const onOffline = () => setIsOnline(false)
    window.addEventListener('online',  onOnline)
    window.addEventListener('offline', onOffline)
    return () => { window.removeEventListener('online', onOnline); window.removeEventListener('offline', onOffline) }
  }, [])

  useEffect(() => {
    if (!user?.id) return
    getProfile(user.id).then((nextProfile) => {
      setProfile(nextProfile)
      if (!nextProfile.onboarding_complete) navigate('/onboarding', { replace: true })
    }).catch(() => {})
  }, [user, navigate])

  useEffect(() => {
    if (!user?.id || !navigator.onLine) return
    Promise.all(
      GAMES.map((g) =>
        getNextDifficulty(user.id, g.key)
          .then((d) => ({ key: g.key, tier: d.next_tier }))
          .catch(() => ({ key: g.key, tier: 'easy' }))
      )
    ).then((results) => {
      const map = {}
      results.forEach(({ key, tier }) => { map[key] = tier })
      setDifficulties(map)
    })
  }, [user])

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      {/* Header */}
      <header className="app-header">
        <h1>🧠 {t('app_name')}</h1>
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={signOut}>
          {t('logout')}
        </button>
      </header>

      {!isOnline && (
        <div className="sync-bar" style={{ background: '#fff3cd', color: '#856404' }}>
          📴 {t('offline_mode')}
        </div>
      )}

      <div className="page">
        <h2 style={{ fontSize: 'var(--font-size-xl)', marginTop: '1rem' }}>
          {t('welcome', { name: profile?.preferred_name || user?.email?.split('@')[0] || 'Friend' })}
        </h2>

        <p style={{ fontSize: 'var(--font-size-lg)', color: 'var(--color-text-secondary)', marginBottom: '1.5rem' }}>
          {t('tagline')}
        </p>
        <MedicalDisclaimer />

        <section className="card" aria-labelledby="audio-guide-title">
          <h3 id="audio-guide-title" style={{ marginTop: 0 }}>🔊 Audio guide</h3>
          <p style={{ marginTop: 0 }}>Listen to this page and hear where each choice will take you.</p>
          <div className="grid-2">
            <button className="btn btn-primary btn-block" onClick={readPage}>
              ▶ Read this page
            </button>
            <button className="btn btn-outline btn-block" onClick={() => { stopSpeaking(); setAudioStatus('Audio stopped.') }}>
              ■ Stop audio
            </button>
          </div>
          {audioStatus && <p role="status" style={{ marginBottom: 0 }}>{audioStatus}</p>}
        </section>

        <section aria-labelledby="today-title" className="patient-priority-card">
          <h3 id="today-title">Today</h3>
          <p className="plain-status">{isOnline ? 'Your progress is connected.' : 'You are offline. Your progress is saved on this device.'}</p>
          <button className="btn btn-primary btn-block" onClick={() => navigateWithAudio('/game/memory', 'Today’s activity')}>
            ▶ Start today’s activity
          </button>
        </section>

        <h3 style={{ marginBottom: '0.75rem' }}>{t('play')}</h3>
        <div className="grid-2" aria-label="Activities">
          {GAMES.map((g) => (
            <button key={g.key} className="game-tile"
              aria-label={t(`${g.key}_game`)}
              onClick={() => navigateWithAudio(`/game/${g.key}`, t(`${g.key}_game`))}>
              <span className="tile-icon" aria-hidden="true">{g.icon}</span>
              <span className="tile-name">{t(`${g.key}_game`)}</span>
              <span className="tile-diff" style={{ color: g.color }}>
                {t(difficulties[g.key] || 'easy')}
              </span>
            </button>
          ))}
        </div>

        <h3 className="mt-3" style={{ marginBottom: '0.75rem' }}>Help and routine</h3>
        <div className="patient-actions grid-2">
          <button className="btn btn-outline btn-block" onClick={() => navigate('/reminders')}>
            🔔 {t('reminders')}
          </button>
          <button className="btn btn-outline btn-block" onClick={() => navigate('/safety-check-in')}>
            ✅ Safety check-in
          </button>
          <button className="btn btn-outline btn-block" onClick={() => navigate('/medications')}>
            💊 Medications
          </button>
          <button className="btn btn-danger btn-block" onClick={() => navigate('/emergency-contacts')}>
            📞 Emergency help
          </button>
        </div>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/reminiscence')}>
          🧓 Memory Lane
        </button>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/social')}>
          💬 Messages
        </button>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/daily-living')}>
          📋 My Day
        </button>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/appointment-prep')}>
          🏥 Doctor visit prep
        </button>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/transport-notes')}>
          🚗 Transport notes
        </button>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/mood')}>
          🌙 Sleep & Mood
        </button>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/activity')}>
          🏃 Movement
        </button>
        <button className="btn btn-outline btn-block mt-2" onClick={() => navigate('/notifications')}>
          📢 {t('notifications')}
        </button>

        <div className="mt-2">
          <button className="btn btn-ghost btn-block" style={{ fontSize: '1rem', color: 'var(--color-text-secondary)' }}
            onClick={() => navigate('/settings')}>
            ⚙️ {t('settings')}
          </button>
        </div>
      </div>
    </div>
  )
}
