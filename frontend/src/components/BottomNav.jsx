import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { HomeIcon, PlayIcon, RoutineCareIcon, SettingsIcon } from './Icons'

export default function BottomNav() {
  const navigate = useNavigate()
  const location = useLocation()

  const isHome = location.pathname === '/home' && !location.hash
  const isPlay = location.hash === '#play-section'
  const isRoutine = location.hash === '#routine-section'
  const isSettings = location.pathname === '/settings'

  const handleNav = (targetPath, sectionId) => {
    if (location.pathname === '/home' && sectionId) {
      const el = document.getElementById(sectionId)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' })
        window.location.hash = sectionId
        return
      }
    }
    navigate(targetPath)
  }

  return (
    <nav className="bottom-nav" aria-label="Main Navigation">
      <button
        type="button"
        className={`bottom-nav-item ${isHome ? 'active' : ''}`}
        onClick={() => handleNav('/home', 'top-section')}
        aria-current={isHome ? 'page' : undefined}
      >
        <HomeIcon size={26} color={isHome ? 'var(--color-primary)' : 'var(--color-text-secondary)'} />
        <span>Home</span>
      </button>

      <button
        type="button"
        className={`bottom-nav-item ${isPlay ? 'active' : ''}`}
        onClick={() => handleNav('/home#play-section', 'play-section')}
        aria-current={isPlay ? 'true' : undefined}
      >
        <PlayIcon size={26} color={isPlay ? 'var(--color-primary)' : 'var(--color-text-secondary)'} />
        <span>Play</span>
      </button>

      <button
        type="button"
        className={`bottom-nav-item ${isRoutine ? 'active' : ''}`}
        onClick={() => handleNav('/home#routine-section', 'routine-section')}
        aria-current={isRoutine ? 'true' : undefined}
      >
        <RoutineCareIcon size={26} color={isRoutine ? 'var(--color-primary)' : 'var(--color-text-secondary)'} />
        <span>Routine</span>
      </button>

      <button
        type="button"
        className={`bottom-nav-item ${isSettings ? 'active' : ''}`}
        onClick={() => handleNav('/settings')}
        aria-current={isSettings ? 'page' : undefined}
      >
        <SettingsIcon size={26} color={isSettings ? 'var(--color-primary)' : 'var(--color-text-secondary)'} />
        <span>Settings</span>
      </button>
    </nav>
  )
}
