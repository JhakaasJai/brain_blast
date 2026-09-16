import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getDashboardSummary, getDashboardTrends, getAlerts, getNotifications, getProfile } from '../services/api'
import MedicalDisclaimer from '../components/MedicalDisclaimer'
import AdminPanel from '../components/AdminPanel'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const GAME_TYPES = ['memory', 'attention', 'routine', 'recognition']

const PATIENTS = [
  { id: 'user-patient-1', name: 'Rina Borah (Assam)', region: 'Assam' },
  { id: 'user-patient-2', name: 'Banshan Lyngdoh (Meghalaya)', region: 'Meghalaya' },
  { id: 'user-patient-3', name: 'Thoibi Haobijam (Manipur)', region: 'Manipur' },
]

export default function CaregiverDashboard() {
  const { t } = useTranslation()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [patientId, setPatientId] = useState('user-patient-1')
  const [summary, setSummary] = useState(null)
  const [trends, setTrends] = useState({})
  const [trendExplanations, setTrendExplanations] = useState({})
  const [alerts, setAlerts] = useState([])
  const [notifications, setNotifications] = useState([])
  const [profile, setProfile] = useState(null)
  const [activeGame, setActiveGame] = useState('memory')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [searchQuery, setSearchQuery] = useState('')
  const [regionFilter, setRegionFilter] = useState('')

  const filteredPatients = PATIENTS.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRegion = regionFilter === '' || p.region === regionFilter
    return matchesSearch && matchesRegion
  })

  // Ensure selected patient is always valid if they get filtered out, though not strictly necessary for a <select>
  // since the dropdown value will just show empty if not in list. We let it be.

  useEffect(() => {
    loadData()
  }, [patientId])

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [sum, al, notifs, prof] = await Promise.all([
        getDashboardSummary(patientId),
        getAlerts(patientId),
        getNotifications(),
        getProfile(patientId),
      ])
      setSummary(sum)
      setAlerts(al)
      setNotifications(notifs)
      setProfile(prof)

      // Load trends for all game types
      const trendData = {}
      const trendSummaries = {}
      await Promise.all(
      GAME_TYPES.map(async (gt) => {
      const t = await getDashboardTrends(patientId, gt, 30)
      trendData[gt] = t.points
      trendSummaries[gt] = t.plain_language_summary
      })
      )
      setTrends(trendData)
      setTrendExplanations(trendSummaries)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <h1 style={{ fontSize: 'var(--font-size-base)' }}>
          📊 {user?.role === 'health_worker' ? 'Health Worker' : 'Caregiver'} Dashboard
        </h1>
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }} onClick={signOut}>
          {t('logout')}
        </button>
      </header>

      <div className="page" style={{ maxWidth: '800px' }}>
        <MedicalDisclaimer />
        {/* Patient selector */}
        <div className="card mb-2">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <label style={{ fontWeight: 700, display: 'block', marginBottom: '0.5rem' }}>
              Select Patient
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button className="btn btn-outline" onClick={() => navigate('/dashboard/reminders')}>Manage reminders</button>
              <button className="btn btn-outline" onClick={() => navigate('/education')}>📚 Caregiver learning</button>
              <button className="btn btn-outline" onClick={() => navigate('/caregiver-wellbeing')}>💚 My wellbeing</button>
              {user?.role === 'health_worker' && <button className="btn btn-outline" onClick={() => navigate('/visit-planning')}>🗓️ Plan visits</button>}
              <button className="btn btn-outline" onClick={() => navigate(`/caregiver-notes?patient_id=${patientId}`)}>Care notes</button>
              <button className="btn btn-outline" onClick={() => navigate('/appointment-prep')}>🏥 Appointment prep</button>
              <button className="btn btn-outline" onClick={() => navigate('/transport-notes')}>🚗 Transport notes</button>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem', marginTop: '0.5rem' }}>
            <input
              className="input"
              type="search"
              placeholder="🔍 Search patients by name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ flex: '1 1 200px' }}
            />
            <select
              className="input"
              value={regionFilter}
              onChange={(e) => setRegionFilter(e.target.value)}
              style={{ flex: '0 0 auto' }}
            >
              <option value="">All Regions</option>
              <option value="Assam">Assam</option>
              <option value="Meghalaya">Meghalaya</option>
              <option value="Manipur">Manipur</option>
            </select>
          </div>

          <select className="input" value={patientId}
            onChange={(e) => setPatientId(e.target.value)}>
            {filteredPatients.length === 0 && <option value="" disabled>No patients match the search criteria</option>}
            {filteredPatients.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        {loading && <p>{t('loading')}</p>}
        {error && <div className="card" style={{ background: '#fdecea', color: '#c62828' }}>{error}</div>}

        {/* Summary cards */}
        {summary && (
          <div className="mt-3 grid-2">
            {profile && (
              <div className="card grid-span-full" style={{ background: '#e3f2fd', marginBottom: '1rem', textAlign: 'left' }}>
                <h4 style={{ marginTop: 0 }}>Information & Constraints</h4>
                <div style={{ fontSize: '0.9rem', lineHeight: '1.4' }}>
                  <p><strong>DOB/Age:</strong> {profile.dob_or_age}</p>
                  <p><strong>Dementia stage:</strong> {profile.dementia_stage_note}</p>
                  <p><strong>Routines:</strong> {profile.routine_notes || 'None'}</p>
                  <p><strong>Mobility:</strong> {profile.mobility_notes || 'None'}</p>
                  <p><strong>Vision:</strong> {profile.vision_notes || 'None'} | <strong>Hearing:</strong> {profile.hearing_notes || 'None'}</p>
                  <p><strong>Identification markers:</strong> {profile.identification_notes || 'None recorded'}</p>
                </div>
              </div>
            )}
            <button className="btn btn-outline btn-block" onClick={() => navigate('/safety-guidance')}>
              ⚠️ Safety guidance
            </button>
            {[
              { label: 'Total Sessions',    value: summary.total_sessions },
              { label: 'This Week',         value: summary.sessions_last_7_days },
              { label: 'Day Streak 🔥',     value: summary.streak_days },
              { label: 'Avg Accuracy (7d)', value: `${summary.avg_accuracy_last_7_days}%` },
              { label: 'Reminder Adherence',value: `${summary.reminder_adherence_pct}%` },
              { label: 'Inactivity',        value: `${summary.inactivity_hours}h ago` },
            ].map(({ label, value }) => (
              <div key={label} className="card" style={{ textAlign: 'center', margin: 0 }}>
                <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 900 }}>{value}</div>
                <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>{label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Score trends */}
        <div className="card mb-2">
          <h3 style={{ marginTop: 0 }}>Score Trends (last 30 days)</h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            {GAME_TYPES.map((g) => (
              <button key={g}
                className={`btn ${activeGame === g ? 'btn-primary' : 'btn-outline'}`}
                style={{ fontSize: '0.9rem', minHeight: '40px', padding: '0.3rem 0.8rem' }}
                onClick={() => setActiveGame(g)}>
                {g}
              </button>
            ))}
          </div>
          {trends[activeGame]?.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={trends[activeGame]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="accuracy" stroke="#1a73e8" name="Accuracy %" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
              {trendExplanations[activeGame] && (
                <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#f5f5f5', borderRadius: '4px', fontSize: '0.9rem', color: '#333' }}>
                  <p style={{ margin: 0 }}><strong>Explanation:</strong> {trendExplanations[activeGame]}</p>
                </div>
              )}
            </>
          ) : (
            <p style={{ color: 'var(--color-text-secondary)' }}>No data for this game type yet.</p>
          )}
        </div>

        {/* Alerts */}
        <div className="card mb-2">
          <h3 style={{ marginTop: 0 }}>⚠️ Alerts</h3>
          {alerts.length === 0 && <p style={{ color: 'var(--color-text-secondary)' }}>No active alerts.</p>}
          {alerts.map((a) => (
            <div key={a.id} style={{ background: '#fff3cd', borderRadius: 8, padding: '0.75rem',
                                     marginBottom: '0.5rem', fontSize: '0.95rem' }}>
              <strong>{a.type.replace('_', ' ')}</strong> — {a.triggered_at?.slice(0, 10)} — {a.channel}
              {a.explanation && <p style={{ margin: '0.35rem 0' }}>{a.explanation}</p>}
              {a.observed_threshold && <p style={{ margin: '0.35rem 0', fontSize: '0.85rem' }}>Observed threshold: {a.observed_threshold}</p>}
              {a.next_step && <p style={{ margin: '0.35rem 0', fontSize: '0.85rem' }}>Suggested next step: {a.next_step}</p>}
              {a.simulation_label && (
                <div style={{ marginTop: '0.25rem', color: '#856404', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                  {a.simulation_label}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Notifications log */}
        <div className="card">
          <h3 style={{ marginTop: 0 }}>📢 Notifications Log (simulated)</h3>
          {notifications.length === 0 && <p style={{ color: 'var(--color-text-secondary)' }}>No notifications.</p>}
          {notifications.map((n) => (
            <div key={n.id} style={{ background: n.read ? '#f5f5f5' : '#e3f2fd',
                                     borderRadius: 8, padding: '0.75rem', marginBottom: '0.5rem' }}>
              <div style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{n.message}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                {n.created_at?.slice(0, 16)} · {n.channel}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
