/**
 * Attention & Concentration Game — Tap the Odd One Out
 * Shows a grid of items; one is different. Patient taps the odd one.
 */
import React, { useState, useEffect, useRef } from 'react'

const SETS = {
  easy: [
    { normal: '🌸', odd: '🌼', count: 6 },
    { normal: '🐘', odd: '🦁', count: 6 },
    { normal: '🍎', odd: '🍊', count: 6 },
  ],
  medium: [
    { normal: '🌸', odd: '🌼', count: 9 },
    { normal: '🐘', odd: '🦁', count: 9 },
    { normal: '🍎', odd: '🍊', count: 9 },
  ],
  hard: [
    { normal: '🌸', odd: '🌺', count: 12 },
    { normal: '🐘', odd: '🦏', count: 12 },
    { normal: '🍎', odd: '🍑', count: 12 },
  ],
}

function buildGrid(set) {
  const oddIdx = Math.floor(Math.random() * set.count)
  return Array.from({ length: set.count }, (_, i) => ({
    idx: i, val: i === oddIdx ? set.odd : set.normal, isOdd: i === oddIdx
  }))
}

export default function AttentionGame({ difficulty = 'easy', onComplete }) {
  const rounds = difficulty === 'easy' ? 3 : difficulty === 'medium' ? 5 : 7
  const [round, setRound] = useState(0)
  const [grid, setGrid] = useState(() => buildGrid(SETS[difficulty][0]))
  const [errors, setErrors] = useState(0)
  const [correct, setCorrect] = useState(0)
  const [feedback, setFeedback] = useState(null)
  const startTime = useRef(Date.now())
  const reactionTimes = useRef([])
  const roundStart = useRef(Date.now())

  const nextRound = (wasCorrect) => {
    const rt = Date.now() - roundStart.current
    reactionTimes.current.push(rt)
    const nextRound = round + 1
    if (nextRound >= rounds) {
      const totalAns = rounds
      const acc = (correct + (wasCorrect ? 1 : 0)) / totalAns * 100
      const avgRt = Math.round(reactionTimes.current.reduce((a, b) => a + b, 0) / reactionTimes.current.length)
      const err = errors + (wasCorrect ? 0 : 1)
      onComplete(Math.round(acc * 10), acc, avgRt, err)
    } else {
      const setIdx = nextRound % SETS[difficulty].length
      setGrid(buildGrid(SETS[difficulty][setIdx]))
      setRound(nextRound)
      roundStart.current = Date.now()
      setFeedback(null)
    }
  }

  const tap = (item) => {
    if (feedback) return
    if (item.isOdd) {
      setCorrect((c) => c + 1)
      setFeedback('correct')
      setTimeout(() => nextRound(true), 700)
    } else {
      setErrors((e) => e + 1)
      setFeedback('wrong')
      setTimeout(() => nextRound(false), 700)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <span>Round {round + 1}/{rounds}</span>
        <span>✅ {correct} ❌ {errors}</span>
      </div>
      {feedback && (
        <div style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '0.5rem' }}>
          {feedback === 'correct' ? '✅ Correct!' : '❌ Try again!'}
        </div>
      )}
      <div className="grid-3" style={{ gap: '0.75rem' }}>
        {grid.map((item) => (
          <button key={item.idx} onClick={() => tap(item)}
            style={{ minHeight: '72px', fontSize: '2.2rem', borderRadius: '12px',
                     border: '3px solid var(--color-border)', background: '#fff', cursor: 'pointer' }}>
            {item.val}
          </button>
        ))}
      </div>
    </div>
  )
}
