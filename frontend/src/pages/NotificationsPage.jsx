import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { getNotifications } from '../services/api'

export default function NotificationsPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [notifs, setNotifs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getNotifications()
      .then(setNotifs)
      .catch(() => setNotifs([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate(-1)}>← {t('back')}</button>
        <h1>📢 {t('notifications')}</h1>
        <span />
      </header>

      <div className="page">
        {loading && <p>{t('loading')}</p>}
        {!loading && notifs.length === 0 && (
          <div className="card text-center"><p>No notifications yet.</p></div>
        )}
        {notifs.map((n) => (
          <div key={n.id} className="card" style={{
            marginBottom: '0.75rem',
            borderLeft: `5px solid ${n.channel === 'sms' ? '#e65100' : '#1a73e8'}`,
          }}>
            <div style={{ fontFamily: 'monospace', fontSize: '0.9rem', marginBottom: '0.25rem' }}>
              {n.message}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
              {n.created_at?.slice(0, 16)} · Channel: {n.channel} · {n.read ? 'Read' : 'Unread'}
            </div>
          </div>
        ))}
        <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginTop: '1rem' }}>
          Messages marked [SMS SIMULATION] were logged here instead of being sent via Twilio/MSG91.
        </p>
      </div>
    </div>
  )
}
