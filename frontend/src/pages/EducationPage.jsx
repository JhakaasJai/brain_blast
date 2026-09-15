import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { getEducationArticles, updateEducationProgress } from '../services/api'
import { useAuth } from '../components/AuthContext'
import MedicalDisclaimer from '../components/MedicalDisclaimer'

export default function EducationPage() {
  const { t } = useTranslation()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [articles, setArticles] = useState([])
  const [progress, setProgress] = useState({})
  const [selected, setSelected] = useState(null)
  const [disclaimer, setDisclaimer] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getEducationArticles()
      .then((data) => {
        setArticles(data.articles || [])
        setProgress(data.progress || {})
        setDisclaimer(data.disclaimer || '')
      })
      .catch((err) => setError(err.response?.data?.detail || 'Unable to load education articles.'))
      .finally(() => setLoading(false))
  }, [])

  const toggleProgress = async (article) => {
    const completed = !progress[article.id]
    try {
      await updateEducationProgress(article.id, completed)
      setProgress((current) => ({ ...current, [article.id]: completed }))
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to save reading progress.')
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }} onClick={() => navigate('/dashboard')}>
          ← {t('back')}
        </button>
        <h1>📚 {t('education_title')}</h1>
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }} onClick={signOut}>
          {t('logout')}
        </button>
      </header>
      <main className="page" style={{ maxWidth: 800 }}>
        <MedicalDisclaimer />
        <p>{t('education_body')}</p>
        {disclaimer && <p className="disclaimer" role="note">{disclaimer}</p>}
        {loading && <p>{t('loading')}</p>}
        {error && <p className="error-text" role="alert">{error}</p>}
        <div style={{ display: 'grid', gap: '1rem' }}>
          {articles.map((article) => {
            const done = Boolean(progress[article.id])
            const open = selected === article.id
            return (
              <article key={article.id} className="card" aria-labelledby={`${article.id}-title`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'flex-start' }}>
                  <div>
                    <p style={{ margin: 0, color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>{article.category} · {article.read_time_minutes} min</p>
                    <h2 id={`${article.id}-title`} style={{ margin: '0.35rem 0' }}>{article.title}</h2>
                    <p>{article.summary}</p>
                  </div>
                  <span aria-label={done ? 'Read' : 'Unread'}>{done ? '✅' : '○'}</span>
                </div>
                {open && <p style={{ lineHeight: 1.6 }}>{article.body}</p>}
                <div className="grid-2">
                  <button className="btn btn-primary btn-block" onClick={() => setSelected(open ? null : article.id)}>
                    {open ? 'Hide article' : t('education_read')}
                  </button>
                  <button className="btn btn-outline btn-block" onClick={() => toggleProgress(article)}>
                    {done ? t('education_uncompleted') : t('education_completed')}
                  </button>
                </div>
              </article>
            )
          })}
        </div>
      </main>
    </div>
  )
}
