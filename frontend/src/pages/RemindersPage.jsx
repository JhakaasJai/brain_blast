import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getReminders } from '../services/api'
import { db } from '../services/db'
import { flushSyncQueue, queueWrite } from '../services/syncManager'
import { startReminderScheduler, stopReminderScheduler, requestNotificationPermission } from '../services/reminderScheduler'
import ReminderCard from '../components/ReminderCard'

export default function RemindersPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [reminders, setReminders] = useState([])
  const [activeReminder, setActiveReminder] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user?.id) return
    const patientId = user.role === 'patient' ? user.id : null
    if (!patientId) { setLoading(false); return }

    getReminders(patientId)
      .then((rems) => {
        setReminders(rems)
        // Cache in IndexedDB
        rems.forEach((r) => db.reminders.put(r))
      })
      .catch(() => {
        // Offline: load from IndexedDB
        db.reminders.where('patient_id').equals(patientId).toArray()
          .then(setReminders)
      })
      .finally(() => setLoading(false))

    // Load events from local DB for display
    db.reminder_events.where('patient_id').equals(patientId).toArray()
      .then(setEvents)

    // Request OS notifications once, then schedule against the cached list.
    requestNotificationPermission().catch(() => {})
    return () => stopReminderScheduler()
  }, [user])

  useEffect(() => {
    if (!reminders.length || user?.role !== 'patient') return undefined
    return startReminderScheduler(reminders, setActiveReminder)
  }, [reminders, user?.role])

  const handleAction = async (reminder, action) => {
    setActiveReminder(null)
    const event = {
      reminder_id: reminder.id,
      patient_id: user.id,
      fired_at: new Date().toISOString(),
      action,
      client_uuid: globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      client_timestamp: new Date().toISOString(),
      sync_status: 'pending',
    }
    await queueWrite('reminder_events', event)
    setEvents((prev) => [...prev, event])
    flushSyncQueue().catch(() => {})
  }

  const getLastAction = (remId) => {
    const ev = [...events].filter((e) => e.reminder_id === remId).pop()
    return ev?.action
  }

  if (loading) return <div className="page"><p>{t('loading')}</p></div>

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      {activeReminder && (
        <ReminderCard
          reminder={activeReminder}
          onDone={() => handleAction(activeReminder, 'done')}
          onSnooze={() => handleAction(activeReminder, 'snoozed')}
          onMiss={() => handleAction(activeReminder, 'missed')}
        />
      )}

      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate(-1)}>← {t('back')}</button>
        <h1>🔔 {t('reminders')}</h1>
        <span />
      </header>

      <div className="page">
        {reminders.length === 0 && (
          <div className="card text-center">
            <p>No reminders set yet.</p>
          </div>
        )}
        {reminders.map((rem) => {
          const lastAction = getLastAction(rem.id)
          return (
            <div key={rem.id} className="card" style={{ marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontSize: '2rem' }}>
                  {{ medicine: '💊', hydration: '💧', activity: '🏃', appointment: '🏥' }[rem.category] || '🔔'}
                </span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 'var(--font-size-lg)' }}>
                    {t(`reminder_${rem.category}`, rem.category)}
                  </div>
                  <div style={{ color: 'var(--color-text-secondary)' }}>{rem.message}</div>
                  {lastAction && (
                    <div style={{ fontSize: '0.85rem', marginTop: '0.25rem',
                                  color: lastAction === 'done' ? '#2e7d32' : lastAction === 'snoozed' ? '#e65100' : '#c62828' }}>
                      Last: {lastAction}
                    </div>
                  )}
                </div>
                <button className="btn btn-primary"
                  style={{ minHeight: '52px', padding: '0.5rem 1rem' }}
                  onClick={() => setActiveReminder(rem)}>
                  View
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
