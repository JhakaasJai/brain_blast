import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../components/AuthContext'
import { getProfile, updateProfile } from '../services/api'

const splitList = (value) => value.split(',').map((item) => item.trim()).filter(Boolean)

export default function OnboardingPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    preferred_name: '', theme_preference: 'assam_village', likes: '', dislikes: '',
    routine_notes: '', mobility_notes: '', vision_notes: '', hearing_notes: '', identification_notes: ''
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user?.id) return
    getProfile(user.id).then((profile) => setForm({
      preferred_name: profile.preferred_name || '',
      theme_preference: profile.theme_preference || 'assam_village',
      likes: (profile.likes || []).join(', '),
      dislikes: (profile.dislikes || []).join(', '),
      routine_notes: profile.routine_notes || '',
      mobility_notes: profile.mobility_notes || '',
      vision_notes: profile.vision_notes || '',
      hearing_notes: profile.hearing_notes || '',
      identification_notes: profile.identification_notes || '',
    })).catch(() => setError('We could not load the profile. Please try again.'))
      .finally(() => setLoading(false))
  }, [user])

  const set = (key) => (event) => setForm((current) => ({ ...current, [key]: event.target.value }))

  async function save(event) {
    event.preventDefault()
    setSaving(true); setError('')
    try {
      await updateProfile(user.id, {
        ...form,
        likes: splitList(form.likes),
        dislikes: splitList(form.dislikes),
        onboarding_complete: true,
      })
      navigate('/home', { replace: true })
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'We could not save these details. Your information is still safe; please try again.')
    } finally { setSaving(false) }
  }

  if (loading) return <div className="page"><p>{t('loading')}</p></div>
  return (
    <main className="page" aria-labelledby="onboarding-title">
      <div className="card">
        <h1 id="onboarding-title">{t('onboarding_title')}</h1>
        <p className="text-muted">{t('onboarding_body')}</p>
        <p className="disclaimer">{t('not_a_medical_device')}</p>
        {error && <p role="alert" className="error-text">{error}</p>}
        <form onSubmit={save}>
          <label htmlFor="preferred_name">{t('preferred_name')}</label>
          <input id="preferred_name" className="input" value={form.preferred_name} onChange={set('preferred_name')} required />
          <label htmlFor="theme_preference">{t('regional_theme')}</label>
          <select id="theme_preference" className="input" value={form.theme_preference} onChange={set('theme_preference')}>
            <option value="assam_village">Assam</option><option value="meghalaya_highlands">Meghalaya</option><option value="manipur_festival">Manipur</option>
          </select>
          <label htmlFor="likes">{t('likes')}</label>
          <input id="likes" className="input" placeholder="tea, music, family photos" value={form.likes} onChange={set('likes')} />
          <label htmlFor="dislikes">{t('dislikes')}</label>
          <input id="dislikes" className="input" value={form.dislikes} onChange={set('dislikes')} />
          <label htmlFor="routine_notes">{t('routine_notes')}</label>
          <textarea id="routine_notes" className="input textarea" value={form.routine_notes} onChange={set('routine_notes')} />
          <label htmlFor="mobility_notes">{t('mobility_notes')}</label>
          <textarea id="mobility_notes" className="input textarea" value={form.mobility_notes} onChange={set('mobility_notes')} />
          <label htmlFor="vision_notes">{t('vision_notes')}</label>
          <input id="vision_notes" className="input" value={form.vision_notes} onChange={set('vision_notes')} />
          <label htmlFor="hearing_notes">{t('hearing_notes')}</label>
          <input id="hearing_notes" className="input" value={form.hearing_notes} onChange={set('hearing_notes')} />

          <label htmlFor="identification_notes">Identification markers (for safe wandering)</label>
          <p style={{ margin: '0 0 0.5rem', fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>e.g. ID bracelet, usual clothing, distinct features to help others assist them.</p>
          <textarea id="identification_notes" className="input textarea" value={form.identification_notes} onChange={set('identification_notes')} />

          <button className="btn btn-primary btn-block mt-2" disabled={saving}>{saving ? t('saving') : t('save_continue')}</button>
        </form>
      </div>
    </main>
  )
}

export { splitList }
