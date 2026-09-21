import React from 'react'
import { useTranslation } from 'react-i18next'

export default function TodayHero({ isOnline, onStartActivity }) {
  const { t } = useTranslation()

  // Format today's date in a reassuring, legible way
  const today = new Date()
  const dateFormatted = today.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  })

  return (
    <section className="card" aria-labelledby="today-title" style={{
      background: 'linear-gradient(180deg, #FFFFFF 0%, #F9F7F1 100%)',
      border: '2px solid var(--color-primary-light)',
      borderRadius: 'var(--radius-lg)',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      boxShadow: 'var(--shadow)'
    }}>
      {/* Warm Morning North Eastern Hills & Sun SVG Illustration */}
      <div style={{
        width: '100%',
        height: '140px',
        borderRadius: '14px',
        overflow: 'hidden',
        background: 'linear-gradient(180deg, #FFF9EB 0%, #E8F5E9 100%)',
        marginBottom: '1.25rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative'
      }} aria-hidden="true">
        <svg width="100%" height="100%" viewBox="0 0 360 140" fill="none" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
          {/* Sky background */}
          <rect width="360" height="140" fill="url(#skyGrad)" />
          
          {/* Gentle Morning Sun */}
          <circle cx="180" cy="55" r="32" fill="#FEF08A" fillOpacity="0.8" />
          <circle cx="180" cy="55" r="22" fill="#FDE047" />

          {/* Distant Hills (North Eastern mountain ridges) */}
          <path d="M-20 140 L-20 90 Q60 50 140 85 T300 70 Q340 80 380 95 L380 140 Z" fill="#A7D7B5" fillOpacity="0.6" />
          
          {/* Forefront Rolling Tea Hills */}
          <path d="M-10 140 L-10 105 Q70 75 160 100 T370 85 L370 140 Z" fill="#68A67D" />
          <path d="M60 140 L60 115 Q150 95 240 115 T380 105 L380 140 Z" fill="#3D7B54" />

          {/* Calming Morning Tea Cup on side */}
          <g transform="translate(30, 75)">
            <rect x="0" y="8" width="34" height="24" rx="6" fill="#FFFFFF" stroke="#8C5311" strokeWidth="2" />
            <path d="M34 14 C39 14 41 22 34 26" stroke="#8C5311" strokeWidth="2" fill="none" strokeLinecap="round" />
            {/* Gentle steam */}
            <path d="M10 4 Q12 1 10 -2" stroke="#8C5311" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
            <path d="M22 4 Q24 1 22 -2" stroke="#8C5311" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
          </g>

          <defs>
            <linearGradient id="skyGrad" x1="180" y1="0" x2="180" y2="140" gradientUnits="userSpaceOnUse">
              <stop stopColor="#FEF9E7" />
              <stop offset="1" stopColor="#EAF5EC" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-secondary)' }}>
          🗓️ {dateFormatted}
        </span>
        <span style={{
          fontSize: '0.85rem',
          fontWeight: 600,
          padding: '0.2rem 0.6rem',
          borderRadius: '999px',
          background: isOnline ? '#E6F4EA' : '#FEF3C7',
          color: isOnline ? '#137333' : '#92400E',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: isOnline ? '#1B7340' : '#B45309' }} />
          {isOnline ? 'Connected' : 'Offline (Saved)'}
        </span>
      </div>

      <h2 id="today-title" style={{ fontSize: '1.45rem', marginBottom: '0.4rem', color: 'var(--color-text)' }}>
        Today’s Recommended Activity
      </h2>
      <p style={{ fontSize: '1.05rem', color: 'var(--color-text-secondary)', marginBottom: '1.25rem', lineHeight: '1.5' }}>
        Start your gentle memory practice for today. A few minutes helps keep your mind sharp and refreshed.
      </p>

      <button
        className="btn btn-primary btn-block btn-lg"
        onClick={onStartActivity}
        style={{
          boxShadow: '0 4px 12px rgba(34, 84, 61, 0.3)',
          fontSize: '1.2rem',
          fontWeight: 700
        }}
      >
        <span style={{ fontSize: '1.3rem' }} aria-hidden="true">▶</span>
        <span>Start Today’s Activity</span>
      </button>
    </section>
  )
}
