import React, { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { speak, stopSpeaking } from '../services/voice'

/**
 * Full-screen reminder card — high-visibility, elderly-friendly.
 * Auto-reads the message aloud via TTS on mount.
 */
export default function ReminderCard({ reminder, onDone, onSnooze, onMiss }) {
  const { t } = useTranslation()

  useEffect(() => {
    if (reminder?.message) speak(reminder.message)
    return () => stopSpeaking()
  }, [reminder])

  if (!reminder) return null

  const categoryIcon = {
    medicine:    '💊',
    hydration:   '💧',
    activity:    '🏃',
    appointment: '🏥',
  }[reminder.category] || '🔔'

  return (
    <div className="reminder-fullscreen" role="alertdialog" aria-modal="true">
      <div style={{ fontSize: '5rem', marginBottom: '0.5rem' }}>{categoryIcon}</div>
      <h2>{t(`reminder_${reminder.category}`, reminder.category)}</h2>
      <p>{reminder.message}</p>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        <button className="btn btn-success btn-lg" onClick={() => { stopSpeaking(); onDone() }}>
          {t('mark_done')}
        </button>
        <button className="btn btn-outline btn-lg" style={{ background: 'rgba(255,255,255,0.2)', color: '#fff' }}
          onClick={() => { stopSpeaking(); onSnooze() }}>
          {t('snooze')}
        </button>
        <button className="btn btn-ghost btn-lg" style={{ color: '#fff' }}
          onClick={() => { stopSpeaking(); onMiss && onMiss() }}>
          ✕
        </button>
      </div>
      <p style={{ fontSize: '0.75rem', marginTop: '2rem', opacity: 0.7 }}>
        {t('not_a_medical_device')}
      </p>
    </div>
  )
}
