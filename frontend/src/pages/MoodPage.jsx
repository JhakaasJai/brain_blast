import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getMoodCheckins, createMoodCheckin } from '../services/api'

const MOOD_LABELS = ['', 'Very low 😢', 'Low 😟', 'Okay 😐', 'Good 😊', 'Great 😄']
const SLEEP_LABELS = { poor: '😴 Poor', fair: '🌙 Fair', good: '⭐ Good' }

export default function MoodPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  // Form state
  const [mood, setMood] = useState(null)
  const [sleepHours, setSleepHours] = useState('')
  const [sleepQuality, setSleepQuality] = useState('')
  const [notes, setNotes] = useState('')

  const patientId = user?.id

  useEffect(() => {
    if (!patientId) return
    getMoodCheckins(patientId)
      .then(setHistory)
      .catch(() => setError('Could not load check-in history.'))
      .finally(() => setLoading(false))
  }, [patientId])

  const handleSubmit = async () => {
    if (!mood) return
    setSaving(true)
    setError(null)
    try {
      const entry = await createMoodCheckin(patientId, {
        patient_id: patientId,
        mood_score: mood,
        sleep_hours: sleepHours ? parseFloat(sleepHours) : null,
        sleep_quality: sleepQuality || null,
        notes: notes.trim() || null,
      })
      setHistory((prev) => [...prev, entry])
      setSaved(true)
      setMood(null)
      setSleepHours('')
      setSleepQuality('')
      setNotes('')
    } catch {
      setError('Could not save check-in. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate('/home')} aria-label={t('back')}>
          ← {t('home')}
        </button>
        <h1 style={{ fontSize: 'var(--font-size-base)' }}>🌙 {t('mood_title')}</h1>
        <span />
      </header>

      <div className="page">
        {/* Today's check-in form */}
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.75rem' }}>{t('mood_today')}</h3>

          <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{t('mood_how_feeling')}</p>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            {[1, 2, 3, 4, 5].map((score) => (
              <button key={score}
                onClick={() => { setMood(score); setSaved(false) }}
                aria-pressed={mood === score}
                style={{
                  flex: '1 0 48px',
                  padding: '0.6rem 0.3rem',
                  borderRadius: 12,
                  border: mood === score ? '2.5px solid var(--color-primary, #1a73e8)' : '1.5px solid #ccc',
                  background: mood === score ? '#e8f0fe' : 'var(--color-surface, #fff)',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  fontWeight: 600,
                  transition: 'all 0.15s',
                }}
                title={MOOD_LABELS[score]}
              >
                {MOOD_LABELS[score].split(' ')[1]}
              </button>
            ))}
          </div>
          {mood && (
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '0.75rem', fontStyle: 'italic' }}>
              {MOOD_LABELS[mood]}
            </p>
          )}

          <p style={{ fontWeight: 600, marginBottom: '0.4rem' }}>{t('mood_sleep_hours')}</p>
          <input
            type="number" min="0" max="24" step="0.5"
            value={sleepHours}
            onChange={(e) => setSleepHours(e.target.value)}
            placeholder="e.g. 7"
            style={{
              width: '100%', padding: '0.6rem', borderRadius: 8, border: '1px solid #ccc',
              fontSize: 'var(--font-size-base)', marginBottom: '0.75rem', boxSizing: 'border-box',
            }}
            aria-label={t('mood_sleep_hours')}
          />

          <p style={{ fontWeight: 600, marginBottom: '0.4rem' }}>{t('mood_sleep_quality')}</p>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
            {Object.entries(SLEEP_LABELS).map(([val, label]) => (
              <button key={val}
                onClick={() => setSleepQuality(sleepQuality === val ? '' : val)}
                aria-pressed={sleepQuality === val}
                style={{
                  flex: 1,
                  padding: '0.5rem 0.25rem',
                  borderRadius: 10,
                  border: sleepQuality === val ? '2px solid var(--color-primary, #1a73e8)' : '1px solid #ccc',
                  background: sleepQuality === val ? '#e8f0fe' : 'var(--color-surface, #fff)',
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  fontWeight: sleepQuality === val ? 600 : 400,
                }}
              >
                {label}
              </button>
            ))}
          </div>

          <label style={{ fontWeight: 600, display: 'block', marginBottom: '0.4rem' }}>
            {t('mood_notes')}
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            placeholder={t('mood_notes_placeholder')}
            style={{
              width: '100%', padding: '0.6rem', borderRadius: 8, border: '1px solid #ccc',
              fontSize: 'var(--font-size-base)', resize: 'vertical', marginBottom: '1rem',
              boxSizing: 'border-box',
            }}
          />

          {error && <p style={{ color: 'var(--color-danger)', marginBottom: '0.5rem' }}>{error}</p>}
          {saved && (
            <p style={{ color: 'var(--color-success, #2e7d32)', marginBottom: '0.5rem' }} aria-live="polite">
              ✓ {t('mood_saved')}
            </p>
          )}

          <button className="btn btn-primary btn-block btn-lg"
            onClick={handleSubmit}
            disabled={saving || !mood}
          >
            {saving ? t('saving') : t('mood_save')}
          </button>
        </div>

        {/* History */}
        <h3 style={{ marginBottom: '0.75rem' }}>{t('mood_history')}</h3>
        {loading && <p aria-live="polite">{t('loading')}</p>}
        {!loading && history.length === 0 && (
          <p style={{ color: 'var(--color-text-secondary)' }}>{t('mood_none')}</p>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          {[...history].reverse().map((c) => (
            <div key={c.id} className="card" style={{ padding: '0.75rem 1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '1.5rem' }}>{MOOD_LABELS[c.mood_score]?.split(' ')[1] || '❓'}</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
                  {new Date(c.recorded_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                </span>
              </div>
              <p style={{ margin: '0.3rem 0 0', color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>
                {MOOD_LABELS[c.mood_score]}
                {c.sleep_hours ? ` · ${c.sleep_hours}h sleep` : ''}
                {c.sleep_quality ? ` · ${SLEEP_LABELS[c.sleep_quality]}` : ''}
              </p>
              {c.notes && <p style={{ margin: '0.2rem 0 0', fontSize: '0.9rem' }}>{c.notes}</p>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
