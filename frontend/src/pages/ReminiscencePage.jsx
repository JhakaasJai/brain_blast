import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import {
  getReminiscencePrompts,
  getReminiscenceNotes,
  createReminiscenceNote,
} from '../services/api'

const THEME_ICONS = {
  family: '👨\u200d👩\u200d👧',
  festivals: '🎉',
  food: '🍛',
  seasons: '🌿',
  work: '🧑\u200d🌾',
  home: '🏡',
}

export default function ReminiscencePage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [prompts, setPrompts] = useState([])
  const [notes, setNotes] = useState([])
  const [activePrompt, setActivePrompt] = useState(null)
  const [noteText, setNoteText] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const patientId = user?.id

  useEffect(() => {
    if (!patientId) return
    Promise.all([
      getReminiscencePrompts(patientId),
      getReminiscenceNotes(patientId),
    ])
      .then(([ps, ns]) => {
        setPrompts(ps)
        setNotes(ns)
      })
      .catch(() => setError('Could not load reminiscence prompts.'))
      .finally(() => setLoading(false))
  }, [patientId])

  const noteForPrompt = (promptId) =>
    notes.filter((n) => n.prompt_id === promptId)

  const handleSelectPrompt = (prompt) => {
    setActivePrompt(prompt)
    const existing = noteForPrompt(prompt.id)
    setNoteText(existing.length ? existing[existing.length - 1].note_text : '')
    setSaved(false)
    setError(null)
  }

  const handleSave = async () => {
    if (!noteText.trim()) return
    setSaving(true)
    setError(null)
    try {
      const newNote = await createReminiscenceNote(patientId, {
        prompt_id: activePrompt.id,
        patient_id: patientId,
        note_text: noteText.trim(),
      })
      setNotes((prev) => [...prev, newNote])
      setSaved(true)
    } catch {
      setError('Could not save your memory note. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button
          className="btn btn-ghost"
          style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate('/home')}
          aria-label={t('back')}
        >
          ← {t('home')}
        </button>
        <h1 style={{ fontSize: 'var(--font-size-base)' }}>
          🧓 {t('reminiscence_title')}
        </h1>
        <span />
      </header>

      <div className="page">
        <p style={{ color: 'var(--color-text-secondary)', marginBottom: '1rem' }}>
          {t('reminiscence_body')}
        </p>

        {loading && <p aria-live="polite">{t('loading')}</p>}
        {error && !loading && (
          <p style={{ color: 'var(--color-danger)', marginBottom: '1rem' }}>
            {error}
          </p>
        )}

        {!loading && !activePrompt && (
          <>
            <h3 style={{ marginBottom: '0.75rem' }}>{t('reminiscence_pick')}</h3>
            {prompts.length === 0 && (
              <p style={{ color: 'var(--color-text-secondary)' }}>
                {t('reminiscence_none')}
              </p>
            )}
            <div className="grid-2">
              {prompts.map((p) => {
                const hasNote = noteForPrompt(p.id).length > 0
                return (
                  <button
                    key={p.id}
                    className="game-tile"
                    aria-label={p.title}
                    onClick={() => handleSelectPrompt(p)}
                    style={{ position: 'relative' }}
                  >
                    <span className="tile-icon" aria-hidden="true">
                      {THEME_ICONS[p.theme] || '💭'}
                    </span>
                    <span className="tile-name">{p.title}</span>
                    <span
                      className="tile-diff"
                      style={{ color: hasNote ? 'var(--color-success, #2e7d32)' : 'var(--color-text-secondary)' }}
                    >
                      {hasNote ? '✓ Written' : p.theme}
                    </span>
                  </button>
                )
              })}
            </div>
          </>
        )}

        {!loading && activePrompt && (
          <div className="card">
            <button
              className="btn btn-ghost"
              style={{ marginBottom: '1rem', padding: '0.25rem 0' }}
              onClick={() => { setActivePrompt(null); setSaved(false); setError(null) }}
            >
              ← Back to prompts
            </button>

            <div style={{ fontSize: '3rem', textAlign: 'center', marginBottom: '0.5rem' }}>
              {THEME_ICONS[activePrompt.theme] || '💭'}
            </div>
            <h2 style={{ fontSize: 'var(--font-size-xl)', textAlign: 'center', marginBottom: '0.5rem' }}>
              {activePrompt.title}
            </h2>
            <p style={{
              background: 'var(--color-bg)',
              borderRadius: 8,
              padding: '1rem',
              fontSize: 'var(--font-size-lg)',
              marginBottom: '1.5rem',
              color: 'var(--color-text)',
            }}>
              {activePrompt.prompt_text}
            </p>

            <label
              htmlFor="reminiscence-note"
              style={{ fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}
            >
              {t('reminiscence_your_memory')}
            </label>
            <textarea
              id="reminiscence-note"
              value={noteText}
              onChange={(e) => { setNoteText(e.target.value); setSaved(false) }}
              rows={6}
              style={{
                width: '100%',
                fontSize: 'var(--font-size-base)',
                padding: '0.75rem',
                borderRadius: 8,
                border: '1px solid var(--color-border, #ccc)',
                resize: 'vertical',
                marginBottom: '1rem',
                boxSizing: 'border-box',
              }}
              placeholder={t('reminiscence_placeholder')}
              aria-label={t('reminiscence_your_memory')}
            />

            {error && (
              <p style={{ color: 'var(--color-danger)', marginBottom: '0.75rem' }}>
                {error}
              </p>
            )}
            {saved && (
              <p
                style={{ color: 'var(--color-success, #2e7d32)', marginBottom: '0.75rem' }}
                aria-live="polite"
              >
                ✓ {t('reminiscence_saved')}
              </p>
            )}

            <button
              className="btn btn-primary btn-block btn-lg"
              onClick={handleSave}
              disabled={saving || !noteText.trim()}
            >
              {saving ? t('saving') : t('reminiscence_save')}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
