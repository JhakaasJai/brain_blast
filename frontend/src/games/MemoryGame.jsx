/**
 * Memory Improvement Game — Card Flip Matching
 * Regional theme: Assam/NER items (can be extended via theme config)
 * Writes: score, accuracy, reaction_time_avg_ms, errors to parent via onComplete()
 */
import React, { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'

const CARD_SETS = {
  easy:   ['🌾', '🐅', '🦚', '🎋'],
  medium: ['🌾', '🐅', '🦚', '🎋', '🍃', '🌿'],
  hard:   ['🌾', '🐅', '🦚', '🎋', '🍃', '🌿', '🌺', '🦋'],
}

function shuffle(arr) {
  const a = [...arr, ...arr].map((v, i) => ({ id: i, val: v, flipped: false, matched: false }))
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

export default function MemoryGame({ difficulty = 'easy', onComplete }) {
  const { t } = useTranslation()
  const [cards, setCards] = useState(() => shuffle(CARD_SETS[difficulty]))
  const [selected, setSelected] = useState([])
  const [errors, setErrors] = useState(0)
  const [matched, setMatched] = useState(0)
  const startTime = useRef(Date.now())
  const reactionTimes = useRef([])
  const lastFlipTime = useRef(Date.now())

  const total = cards.length / 2

  useEffect(() => {
    if (selected.length === 2) {
      const [a, b] = selected
      const rt = Date.now() - lastFlipTime.current
      reactionTimes.current.push(rt)

      if (cards[a].val === cards[b].val) {
        setCards((prev) => prev.map((c, i) => (i === a || i === b) ? { ...c, matched: true } : c))
        setMatched((m) => m + 1)
      } else {
        setErrors((e) => e + 1)
        setTimeout(() => {
          setCards((prev) => prev.map((c, i) => (i === a || i === b) ? { ...c, flipped: false } : c))
        }, 900)
      }
      setTimeout(() => setSelected([]), 950)
    }
  }, [selected])

  useEffect(() => {
    if (matched === total && total > 0) {
      const elapsed = Date.now() - startTime.current
      const avgRt = reactionTimes.current.length
        ? Math.round(reactionTimes.current.reduce((a, b) => a + b, 0) / reactionTimes.current.length)
        : 2000
      const accuracy = Math.max(0, 100 - (errors / (total + errors)) * 100)
      const score = Math.round(accuracy * 10 - errors * 5)
      onComplete(Math.max(0, score), accuracy, avgRt, errors)
    }
  }, [matched, total])

  const flip = (idx) => {
    if (selected.length >= 2 || cards[idx].flipped || cards[idx].matched) return
    lastFlipTime.current = Date.now()
    setCards((prev) => prev.map((c, i) => i === idx ? { ...c, flipped: true } : c))
    setSelected((prev) => [...prev, idx])
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <span>✅ {matched}/{total}</span>
        <span>❌ {errors}</span>
      </div>
      <div className="grid-3" style={{ gap: '0.75rem' }}>
        {cards.map((card, idx) => (
          <button key={card.id}
            onClick={() => flip(idx)}
            style={{
              minHeight: '80px', fontSize: '2rem', borderRadius: '12px',
              border: '3px solid var(--color-border)',
              background: card.matched ? '#e8f5e9' : card.flipped ? '#fff' : '#1a73e8',
              cursor: card.matched ? 'default' : 'pointer',
              transition: 'background 0.2s',
            }}>
            {(card.flipped || card.matched) ? card.val : '?'}
          </button>
        ))}
      </div>
    </div>
  )
}
