import React, { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getSocialMessages, sendSocialMessage } from '../services/api'

export default function SocialPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [messages, setMessages] = useState([])
  const [newText, setNewText] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const bottomRef = useRef(null)

  const patientId = user?.role === 'patient' ? user.id : null

  useEffect(() => {
    if (!patientId) return
    getSocialMessages(patientId)
      .then(setMessages)
      .catch(() => setError('Could not load messages.'))
      .finally(() => setLoading(false))
  }, [patientId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!newText.trim() || !patientId) return
    setSending(true)
    setError(null)
    try {
      const msg = await sendSocialMessage(patientId, {
        patient_id: patientId,
        sender_id: user.id,
        message_text: newText.trim(),
      })
      setMessages((prev) => [...prev, msg])
      setNewText('')
    } catch {
      setError('Could not send message. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const isMe = (msg) => msg.sender_id === user?.id

  if (!patientId) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
        <header className="app-header">
          <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
            onClick={() => navigate('/dashboard')} aria-label={t('back')}>
            ← {t('back')}
          </button>
          <h1 style={{ fontSize: 'var(--font-size-base)' }}>💬 {t('social_title')}</h1>
          <span />
        </header>
        <div className="page">
          <p style={{ color: 'var(--color-text-secondary)' }}>
            {t('social_not_patient')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', display: 'flex', flexDirection: 'column' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate('/home')} aria-label={t('back')}>
          ← {t('home')}
        </button>
        <h1 style={{ fontSize: 'var(--font-size-base)' }}>💬 {t('social_title')}</h1>
        <span />
      </header>

      <div className="page" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <p style={{ color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
          {t('social_body')}
        </p>

        {loading && <p aria-live="polite">{t('loading')}</p>}
        {error && (
          <p style={{ color: 'var(--color-danger)', marginBottom: '0.75rem' }}>{error}</p>
        )}

        {/* Message thread */}
        <div
          aria-label="Message thread"
          style={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
            marginBottom: '1rem',
            maxHeight: '55vh',
            paddingBottom: '0.5rem',
          }}
        >
          {!loading && messages.length === 0 && (
            <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', marginTop: '2rem' }}>
              {t('social_empty')}
            </p>
          )}
          {messages.map((msg) => {
            const mine = isMe(msg)
            return (
              <div key={msg.id} style={{
                alignSelf: mine ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
              }}>
                {!mine && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', marginBottom: '0.2rem', marginLeft: '0.5rem' }}>
                    {msg.sender_name}
                  </p>
                )}
                <div style={{
                  background: mine ? 'var(--color-primary, #1a73e8)' : 'var(--color-surface, #fff)',
                  color: mine ? '#fff' : 'var(--color-text)',
                  borderRadius: mine ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  padding: '0.75rem 1rem',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  fontSize: 'var(--font-size-base)',
                }}>
                  {msg.message_text}
                </div>
                <p style={{
                  fontSize: '0.75rem',
                  color: 'var(--color-text-secondary)',
                  textAlign: mine ? 'right' : 'left',
                  marginTop: '0.2rem',
                  marginLeft: mine ? 0 : '0.5rem',
                  marginRight: mine ? '0.5rem' : 0,
                }}>
                  {new Date(msg.sent_at).toLocaleString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}
                </p>
              </div>
            )
          })}
          <div ref={bottomRef} />
        </div>

        {/* Compose */}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-end' }}>
          <textarea
            value={newText}
            onChange={(e) => setNewText(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
            rows={2}
            style={{
              flex: 1,
              fontSize: 'var(--font-size-base)',
              padding: '0.75rem',
              borderRadius: 12,
              border: '1px solid var(--color-border, #ccc)',
              resize: 'none',
              boxSizing: 'border-box',
            }}
            placeholder={t('social_placeholder')}
            aria-label={t('social_placeholder')}
          />
          <button
            className="btn btn-primary btn-lg"
            onClick={handleSend}
            disabled={sending || !newText.trim()}
            style={{ minWidth: 72, height: 52 }}
            aria-label={t('social_send')}
          >
            {sending ? '…' : '➤'}
          </button>
        </div>
      </div>
    </div>
  )
}
