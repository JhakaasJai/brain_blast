import React, { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { getNextDifficulty } from '../services/api'
import { db } from '../services/db'
import { flushSyncQueue, queueWrite } from '../services/syncManager'
import { speak } from '../services/voice' 

function makeClientUuid() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`
} 
import MemoryGame from '../games/MemoryGame'
import AttentionGame from '../games/AttentionGame'
import RoutineGame from '../games/RoutineGame'
import RecognitionGame from '../games/RecognitionGame'

const GAME_COMPONENTS = {
  memory:      MemoryGame,
  attention:   AttentionGame,
  routine:     RoutineGame,
  recognition: RecognitionGame,
}

const GAME_HINTS = {
  memory: 'Look for two cards with the same picture. Take your time.',
  attention: 'Look carefully for the one picture that is different.',
  routine: 'Think about what usually happens first, then place the next step.',
  recognition: 'Look at the object and say or choose the name you know.',
}

function getEncouragement(accuracy) {
  if (accuracy >= 85) return 'Wonderful focus! You can be proud of your effort.'
  if (accuracy >= 65) return 'You stayed with it. Every round is useful practice.'
  return 'Thank you for trying. A short break and another attempt are both okay.'
}

function getHint(gameType) {
  return GAME_HINTS[gameType] || 'Take your time and try one step at a time.'
}

export default function GameShell() {
  const { gameType } = useParams()
  const { t } = useTranslation()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [phase, setPhase] = useState('intro')  // intro | playing | result
  const [result, setResult] = useState(null)
  const [difficulty, setDifficulty] = useState('easy')
  const [difficultyInfo, setDifficultyInfo] = useState(null)
  const [difficultyLoading, setDifficultyLoading] = useState(true)
  const [showHint, setShowHint] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    let cancelled = false
    setDifficultyLoading(true)
    setDifficultyInfo(null)

    // The backend remains the source of truth when online. If it is
    // unavailable, the patient can still play the cached/current tier.
    if (user?.id && navigator.onLine) {
      getNextDifficulty(user.id, gameType)
        .then((info) => {
          if (cancelled) return
          setDifficulty(info.next_tier)
          setDifficultyInfo(info)
        })
        .catch(() => {
          if (!cancelled) setDifficulty('easy')
        })
        .finally(() => {
          if (!cancelled) setDifficultyLoading(false)
        })
    } else {
      setDifficultyLoading(false)
    }

    return () => { cancelled = true }
  }, [user?.id, gameType])

  const GameComponent = GAME_COMPONENTS[gameType]

  const handleGameComplete = useCallback(async (score, accuracy, reactionMs, errors) => {
    const now = new Date().toISOString()
    const clientUuid = makeClientUuid()

    const sessionRecord = {
      patient_id: user.id,
      game_type: gameType,
      difficulty,
      score,
      accuracy,
      reaction_time_avg_ms: reactionMs,
      errors,
      started_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      completed_at: now,
      client_uuid: clientUuid,
      client_timestamp: now,
      sync_status: 'pending',
    }

    // Write to IndexedDB + sync_queue first — offline-first guarantee.
    await queueWrite('game_sessions', sessionRecord)

    // Try to flush sync queue in background
    flushSyncQueue().catch(() => {})

    setResult({ score, accuracy, errors })
    setShowHint(false)
    setPhase('result')

    const msg = accuracy >= 70 ? t('good_job') : t('try_again')
    speak(`${msg} ${t('your_score')}: ${score}`)
  }, [gameType, difficulty, user, t])

  if (!GameComponent) {
    return (
      <div className="page">
        <p>Unknown game type: {gameType}</p>
        <button className="btn btn-primary" onClick={() => navigate('/home')}>
          {t('back')}
        </button>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)' }}>
      <header className="app-header">
        <button className="btn btn-ghost" style={{ color: '#fff', minHeight: 44 }}
          onClick={() => navigate('/home')}>
          ← {t('home')}
        </button>
        <h1 style={{ fontSize: 'var(--font-size-base)' }}>{t(`${gameType}_game`)}</h1>
        <span style={{ fontSize: '0.9rem', opacity: 0.8 }}>{t(difficulty)}</span>
      </header>

      <div className="page">
        {phase === 'intro' && (
          <div className="card text-center">
            <div style={{ fontSize: '4rem', marginBottom: '0.5rem' }}>
              {gameType === 'memory' ? '🃏' : gameType === 'attention' ? '👁️' :
               gameType === 'routine' ? '📅' : '🎨'}
            </div>
            <h2 style={{ fontSize: 'var(--font-size-xl)' }}>{t(`${gameType}_game`)}</h2>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>
              {t('difficulty')}: <strong>{t(difficulty)}</strong>
            </p>
            {difficultyInfo?.reason && (
              <p className="text-sm text-muted" style={{ marginBottom: '1.5rem' }}>
                Adaptive level: {difficultyInfo.reason}
              </p>
            )}
            {difficultyLoading && (
              <p className="text-sm text-muted" aria-live="polite">Checking your level…</p>
            )}
            <button
              className="btn btn-outline btn-block"
              type="button"
              aria-expanded={showHint}
              onClick={() => setShowHint((visible) => !visible)}
              style={{ marginBottom: '0.75rem' }}
            >
              💡 {showHint ? 'Hide hint' : 'Show a hint'}
            </button>
            {showHint && (
              <p
                role="status"
                style={{
                  background: '#fff8e1',
                  border: '1px solid #f0c36d',
                  borderRadius: 8,
                  padding: '0.75rem',
                  textAlign: 'left',
                  marginBottom: '0.75rem',
                }}
              >
                💡 {getHint(gameType)}
              </p>
            )}
            <button className="btn btn-primary btn-block btn-lg"
              disabled={difficultyLoading}
              onClick={() => { setPhase('playing'); speak(t('start_game')) }}>
              {t('start_game')}
            </button>
          </div>
        )}

        {phase === 'playing' && (
          <div style={{ position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.75rem' }}>
              <button
                className="btn btn-outline"
                type="button"
                aria-pressed={isPaused}
                onClick={() => setIsPaused((paused) => !paused)}
              >
                {isPaused ? '▶ Resume' : '⏸ Pause'}
              </button>
            </div>
            <div aria-hidden={isPaused} style={{ pointerEvents: isPaused ? 'none' : 'auto', opacity: isPaused ? 0.35 : 1 }}>
              <GameComponent
                difficulty={difficulty}
                patientId={user?.id}
                onComplete={handleGameComplete}
              />
            </div>
            {isPaused && (
              <div
                role="dialog"
                aria-modal="true"
                aria-label="Game paused"
                style={{
                  position: 'absolute',
                  inset: '4rem 0 auto',
                  background: 'rgba(255,255,255,0.97)',
                  border: '2px solid var(--color-primary)',
                  borderRadius: 12,
                  padding: '1.5rem',
                  textAlign: 'center',
                  boxShadow: 'var(--shadow)',
                }}
              >
                <div style={{ fontSize: '3rem' }}>⏸</div>
                <h2 style={{ fontSize: 'var(--font-size-xl)' }}>Game paused</h2>
                <p>Take your time. Your game is waiting for you.</p>
                <button className="btn btn-primary btn-block" type="button" onClick={() => setIsPaused(false)}>
                  ▶ Resume game
                </button>
              </div>
            )}
          </div>
        )}

        {phase === 'result' && result && (
          <div className="card text-center">
            <div style={{ fontSize: '4rem', marginBottom: '0.5rem' }}>
              {result.accuracy >= 70 ? '🎉' : '💪'}
            </div>
            <h2 style={{ fontSize: 'var(--font-size-xl)' }}>
              {result.accuracy >= 70 ? t('good_job') : t('try_again')}
            </h2>
            <p style={{ fontSize: 'var(--font-size-lg)', marginBottom: '0.5rem' }}>
              {t('your_score')}: <strong>{result.score}</strong>
            </p>
            <p style={{ color: 'var(--color-text-secondary)' }}>
              Accuracy: {result.accuracy.toFixed(0)}% · Errors: {result.errors}
            </p>
            <p role="status" style={{ marginTop: '0.75rem', fontSize: 'var(--font-size-lg)' }}>
              {getEncouragement(result.accuracy)}
            </p>
            <div className="mt-3 grid-2" style={{ gap: '0.75rem' }}>
              <button className="btn btn-primary btn-lg"
                onClick={() => { setPhase('playing'); setResult(null) }}>
                {t('next')} (Play again)
              </button>
              <button className="btn btn-outline btn-lg" onClick={() => navigate('/home')}>
                {t('home')}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
