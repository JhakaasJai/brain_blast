import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getDailyTasks, toggleDailyTask } from '../services/api'

const CATEGORY_ICONS = {
  morning: '🌅',
  hygiene: '🧼',
  meals: '🍽️',
  exercise: '🏃',
  evening: '🌙',
}

export default function DailyLivingPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toggling, setToggling] = useState(null)

  const patientId = user?.id

  useEffect(() => {
    if (!patientId) return
    getDailyTasks(patientId)
      .then(setTasks)
      .catch(() => setError('Could not load your daily tasks.'))
      .finally(() => setLoading(false))
  }, [patientId])

  const handleToggle = async (task) => {
    setToggling(task.id)
    try {
      const updated = await toggleDailyTask(patientId, task.id, !task.done)
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
    } catch {
      setError('Could not update task. Please try again.')
    } finally {
      setToggling(null)
    }
  }

  const done = tasks.filter((t) => t.done).length
  const total = tasks.length

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate('/home')} aria-label={t('back')}>
          ← {t('home')}
        </button>
        <h1 style={{ fontSize: 'var(--font-size-base)' }}>
          📋 {t('daily_living_title')}
        </h1>
        <span />
      </header>

      <div className="page">
        <p style={{ color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>
          {t('daily_living_body')}
        </p>

        {/* Progress bar */}
        {!loading && total > 0 && (
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
              <span style={{ fontWeight: 600 }}>{t('daily_living_progress', { done, total })}</span>
              <span style={{ color: done === total ? 'var(--color-success, #2e7d32)' : 'var(--color-text-secondary)' }}>
                {done === total ? '🎉 All done!' : `${total - done} remaining`}
              </span>
            </div>
            <div style={{ background: '#e8eaed', borderRadius: 8, height: 12 }}>
              <div style={{
                background: done === total ? 'var(--color-success, #2e7d32)' : 'var(--color-primary, #1a73e8)',
                borderRadius: 8,
                height: 12,
                width: `${total > 0 ? (done / total) * 100 : 0}%`,
                transition: 'width 0.3s ease',
              }} />
            </div>
          </div>
        )}

        {loading && <p aria-live="polite">{t('loading')}</p>}
        {error && (
          <p style={{ color: 'var(--color-danger)', marginBottom: '0.75rem' }}>{error}</p>
        )}

        {!loading && (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {tasks.map((task) => (
              <li key={task.id}>
                <button
                  className={`card ${task.done ? 'task-done' : ''}`}
                  onClick={() => handleToggle(task)}
                  disabled={toggling === task.id}
                  aria-pressed={task.done}
                  aria-label={`${task.done ? 'Mark undone' : 'Mark done'}: ${task.label}`}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    textAlign: 'left',
                    cursor: 'pointer',
                    background: task.done ? 'var(--color-surface-done, #f0f9f0)' : 'var(--color-surface, #fff)',
                    border: task.done ? '1.5px solid var(--color-success, #2e7d32)' : '1.5px solid transparent',
                    transition: 'all 0.2s ease',
                    padding: '0.85rem 1rem',
                  }}
                >
                  <span style={{ fontSize: '1.8rem', lineHeight: 1 }} aria-hidden="true">
                    {CATEGORY_ICONS[task.category] || '📌'}
                  </span>
                  <span style={{
                    flex: 1,
                    fontSize: 'var(--font-size-base)',
                    fontWeight: 500,
                    textDecoration: task.done ? 'line-through' : 'none',
                    color: task.done ? 'var(--color-text-secondary)' : 'var(--color-text)',
                  }}>
                    {task.label}
                  </span>
                  <span style={{
                    fontSize: '1.5rem',
                    color: task.done ? 'var(--color-success, #2e7d32)' : '#ccc',
                  }} aria-hidden="true">
                    {toggling === task.id ? '⏳' : task.done ? '✅' : '⭕'}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
