import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getNextDifficulty, getProfile } from '../services/api'
import MedicalDisclaimer from '../components/MedicalDisclaimer'
import { getVoicePack, isTTSSupported, speak, stopSpeaking } from '../services/voice' 
import TodayHero from '../components/TodayHero'
import BottomNav from '../components/BottomNav'
import {
  AppLogo,
  EmergencyIcon,
  MemoryIcon,
  AttentionIcon,
  RoutineIcon,
  RecognitionIcon,
  RemindersIcon,
  SafetyIcon,
  MedicationsIcon,
  MemoryLaneIcon,
  MessagesIcon,
  MyDayIcon,
  DoctorPrepIcon,
  TransportIcon,
  SleepMoodIcon,
  MovementIcon,
  NotificationsIcon,
  AudioWaveIcon,
  ArrowRightIcon,
} from '../components/Icons'

function getSpokenHomeSummary(name, isOnline) {
  return `Welcome ${name}. ${isOnline ? 'Your progress is connected.' : 'You are offline; your progress is saved on this device.'} You can start today's activity, practice memory games, or open your health, family, and daily routine assistance.`
} 

function getNavigationAnnouncement(label) {
  return `${label}. Opening now.`
} 

const GAMES = [
  { key: 'memory',      nameKey: 'memory_game',      Icon: MemoryIcon },
  { key: 'attention',   nameKey: 'attention_game',   Icon: AttentionIcon },
  { key: 'routine',     nameKey: 'routine_game',     Icon: RoutineIcon },
  { key: 'recognition', nameKey: 'recognition_game', Icon: RecognitionIcon },
]

// Accessible difficulty formatting with dots + label so color is never alone
function formatDifficulty(tier) {
  switch (tier) {
    case 'hard':
      return { label: 'Hard (Challenging)', dots: '●●●', className: 'diff-hard' }
    case 'medium':
      return { label: 'Medium (Steady)', dots: '●●', className: 'diff-medium' }
    case 'easy':
    default:
      return { label: 'Easy (Gentle)', dots: '●', className: 'diff-easy' }
  }
}

export default function PatientHomePage() {
  const { t } = useTranslation()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [difficulties, setDifficulties] = useState({})
  const [profile, setProfile] = useState(null)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [audioStatus, setAudioStatus] = useState('')
  const [textSize, setTextSize] = useState(
    document.documentElement.style.getPropertyValue('--font-size-base') || '19px'
  )

  const patientName = profile?.preferred_name || user?.email?.split('@')[0] || 'Friend'
  const voicePack = getVoicePack(localStorage.getItem('lang') || 'en')

  useEffect(() => () => stopSpeaking(), [])

  const toggleTextSize = () => {
    const next = textSize === '19px' ? '22px' : textSize === '22px' ? '25px' : '19px'
    document.documentElement.style.setProperty('--font-size-base', next)
    setTextSize(next)
  }

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
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }} id="top-section">
      {/* Persistent App Header with Emergency Quick Access & Text Size Toggle */}
      <header className="app-header">
        <h1>
          <AppLogo size={32} />
          <span>{t('app_name')}</span>
        </h1>

        <div className="app-header-actions">
          {/* Quick Text Size Toggle */}
          <button
            type="button"
            className="btn btn-ghost"
            style={{
              color: '#FFFFFF',
              minHeight: '44px',
              minWidth: '44px',
              padding: '0.3rem 0.65rem',
              border: '1.5px solid rgba(255,255,255,0.4)',
              borderRadius: 'var(--radius-pill)',
              fontSize: '0.95rem',
              fontWeight: 700
            }}
            onClick={toggleTextSize}
            aria-label={`Change text size. Currently ${textSize === '19px' ? 'Standard' : textSize === '22px' ? 'Large' : 'Extra Large'}`}
          >
            A{textSize !== '19px' ? '+' : ''}
          </button>

          {/* Persistent Emergency Action Affordance (Never hidden behind scroll) */}
          <button
            type="button"
            className="btn btn-danger"
            style={{
              minHeight: '44px',
              padding: '0.4rem 0.85rem',
              fontSize: '0.95rem',
              fontWeight: 700,
              borderRadius: 'var(--radius-pill)',
              gap: '0.4rem'
            }}
            onClick={() => navigateWithAudio('/emergency-contacts', 'Emergency Help')}
            aria-label="Emergency Help"
          >
            <EmergencyIcon size={18} color="#FFFFFF" />
            <span>SOS</span>
          </button>
        </div>
      </header>

      {!isOnline && (
        <div className="offline-banner" role="status">
          <span>📴</span>
          <span>{t('offline_mode')}</span>
        </div>
      )}

      <main className="page">
        {/* Welcome Greeting */}
        <section aria-labelledby="welcome-heading" style={{ marginTop: '0.5rem', marginBottom: '1.25rem' }}>
          <h1 id="welcome-heading" style={{ fontSize: 'var(--font-size-xxl)', marginBottom: '0.35rem' }}>
            {t('welcome', { name: patientName })}
          </h1>
          <p style={{ fontSize: 'var(--font-size-lg)', color: 'var(--color-text-secondary)', margin: 0 }}>
            {t('tagline')}
          </p>
        </section>

        {/* Medical Disclaimer */}
        <MedicalDisclaimer />

        {/* Audio Guide Card */}
        <section className="card" aria-labelledby="audio-guide-title" style={{
          borderLeft: '4px solid var(--color-primary)',
          marginBottom: '1.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
            <div style={{
              width: '38px',
              height: '38px',
              borderRadius: '50%',
              background: 'var(--color-primary-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-primary)'
            }}>
              <AudioWaveIcon size={22} />
            </div>
            <h2 id="audio-guide-title" style={{ fontSize: '1.25rem', margin: 0 }}>
              Audio Guide
            </h2>
          </div>
          <p style={{ fontSize: '1.05rem', color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
            Listen to this page spoken aloud to help guide your choices.
          </p>
          <div className="grid-2">
            <button className="btn btn-primary" onClick={readPage}>
              <span aria-hidden="true">▶</span>
              <span>Read Aloud</span>
            </button>
            <button
              className="btn btn-outline"
              onClick={() => { stopSpeaking(); setAudioStatus('Audio stopped.') }}
            >
              <span aria-hidden="true">■</span>
              <span>Stop Audio</span>
            </button>
          </div>
          {audioStatus && (
            <p role="status" style={{ marginTop: '0.75rem', marginBottom: 0, fontWeight: 600, fontSize: '0.95rem' }}>
              {audioStatus}
            </p>
          )}
        </section>

        {/* Today's Recommended Activity Hero (Replaces broken placeholder box) */}
        <TodayHero
          isOnline={isOnline}
          onStartActivity={() => navigateWithAudio('/game/memory', 'Today’s recommended activity')}
        />

        {/* Play & Practice Section */}
        <section id="play-section" aria-labelledby="play-title" style={{ marginBottom: '2rem', scrollMarginTop: '70px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2 id="play-title" style={{ fontSize: '1.5rem', margin: 0 }}>
              {t('play')} & Practice
            </h2>
            <span style={{ fontSize: '0.95rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>
              4 activities
            </span>
          </div>

          <div className="grid-2" aria-label="Cognitive Games">
            {GAMES.map((g) => {
              const currentTier = difficulties[g.key] || 'easy'
              const diffInfo = formatDifficulty(currentTier)
              const GameIcon = g.Icon

              return (
                <button
                  key={g.key}
                  className="game-tile"
                  onClick={() => navigateWithAudio(`/game/${g.key}`, t(g.nameKey))}
                  aria-label={`${t(g.nameKey)}, difficulty: ${diffInfo.label}`}
                >
                  <div className="tile-icon-wrap">
                    <GameIcon size={32} color="var(--color-primary)" />
                  </div>
                  <span className="tile-name">{t(g.nameKey)}</span>
                  <span className={`diff-badge ${diffInfo.className}`}>
                    <span aria-hidden="true">{diffInfo.dots}</span>
                    <span>{diffInfo.label.split(' ')[0]}</span>
                  </span>
                </button>
              )
            })}
          </div>
        </section>

        {/* Restructured Help & Routine Section — 3 Scannable Categories + Dedicated Emergency */}
        <section id="routine-section" aria-labelledby="routine-title" style={{ marginBottom: '2.5rem', scrollMarginTop: '70px' }}>
          <div style={{ marginBottom: '1rem' }}>
            <h2 id="routine-title" style={{ fontSize: '1.5rem', margin: '0 0 0.25rem 0' }}>
              Help & Routine
            </h2>
            <p style={{ color: 'var(--color-text-secondary)', margin: 0, fontSize: '1.05rem' }}>
              Your essential health, family connection, and daily living support.
            </p>
          </div>

          {/* 1. Dedicated Emergency Call Action (Distinct & Prominent) */}
          <div className="emergency-card">
            <div className="emergency-header">
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-emergency)'
              }}>
                <EmergencyIcon size={26} />
              </div>
              <div>
                <h3 className="emergency-title">Emergency Help</h3>
                <p className="emergency-desc">
                  One-tap call to your emergency contact or family member.
                </p>
              </div>
            </div>
            <button
              className="btn btn-danger btn-block"
              style={{ minHeight: '56px', fontSize: '1.15rem', fontWeight: 700 }}
              onClick={() => navigateWithAudio('/emergency-contacts', 'Emergency Contacts')}
            >
              <EmergencyIcon size={22} color="#FFFFFF" />
              <span>Call Emergency Help</span>
            </button>
          </div>

          {/* 2. Category: Health & Safety */}
          <div className="category-card">
            <div className="category-header">
              <div className="category-icon-wrap" style={{ background: '#E8F5E9', color: 'var(--color-primary)' }}>
                <SafetyIcon size={26} />
              </div>
              <div>
                <h3 className="category-title">Health & Safety</h3>
                <p className="category-subtitle">Medications, daily check-in, and doctor visits</p>
              </div>
            </div>
            <div className="category-actions">
              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/medications', 'Medications')}
              >
                <div className="routine-action-left">
                  <MedicationsIcon size={24} color="var(--color-primary)" />
                  <span>Medications</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/safety-check-in', 'Safety check-in')}
              >
                <div className="routine-action-left">
                  <SafetyIcon size={24} color="var(--color-primary)" />
                  <span>Safety Check-In</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/appointment-prep', 'Doctor visit prep')}
              >
                <div className="routine-action-left">
                  <DoctorPrepIcon size={24} color="var(--color-primary)" />
                  <span>Doctor Visit Prep</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>
            </div>
          </div>

          {/* 3. Category: Memory & Connection */}
          <div className="category-card">
            <div className="category-header">
              <div className="category-icon-wrap" style={{ background: '#FEF3C7', color: 'var(--color-secondary)' }}>
                <MemoryLaneIcon size={26} />
              </div>
              <div>
                <h3 className="category-title">Memory & Family</h3>
                <p className="category-subtitle">Reminders, personal photos, and loved ones</p>
              </div>
            </div>
            <div className="category-actions">
              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/reminders', 'Reminders')}
              >
                <div className="routine-action-left">
                  <RemindersIcon size={24} color="var(--color-secondary)" />
                  <span>Daily Reminders</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/reminiscence', 'Memory Lane')}
              >
                <div className="routine-action-left">
                  <MemoryLaneIcon size={24} color="var(--color-secondary)" />
                  <span>Memory Lane</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/social', 'Messages')}
              >
                <div className="routine-action-left">
                  <MessagesIcon size={24} color="var(--color-secondary)" />
                  <span>Family Messages</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>
            </div>
          </div>

          {/* 4. Category: Daily Life & Wellness */}
          <div className="category-card">
            <div className="category-header">
              <div className="category-icon-wrap" style={{ background: '#EAF2EC', color: 'var(--color-primary)' }}>
                <MyDayIcon size={26} />
              </div>
              <div>
                <h3 className="category-title">Daily Life & Wellness</h3>
                <p className="category-subtitle">Daily activities, movement, sleep, and travel</p>
              </div>
            </div>
            <div className="category-actions">
              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/daily-living', 'My Day')}
              >
                <div className="routine-action-left">
                  <MyDayIcon size={24} color="var(--color-primary)" />
                  <span>My Day Tasks</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/mood', 'Sleep and Mood')}
              >
                <div className="routine-action-left">
                  <SleepMoodIcon size={24} color="var(--color-primary)" />
                  <span>Sleep & Mood</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/activity', 'Movement')}
              >
                <div className="routine-action-left">
                  <MovementIcon size={24} color="var(--color-primary)" />
                  <span>Movement & Walking</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/transport-notes', 'Transport notes')}
              >
                <div className="routine-action-left">
                  <TransportIcon size={24} color="var(--color-primary)" />
                  <span>Transport Notes</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>

              <button
                className="routine-action-btn"
                onClick={() => navigateWithAudio('/notifications', 'Notifications')}
              >
                <div className="routine-action-left">
                  <NotificationsIcon size={24} color="var(--color-primary)" />
                  <span>Notifications</span>
                </div>
                <ArrowRightIcon size={20} color="var(--color-text-secondary)" />
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Persistent Bottom Navigation Bar */}
      <BottomNav />
    </div>
  )
}
