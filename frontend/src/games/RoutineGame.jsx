/**
 * Daily Routine Recall Game — Sequence the Day
 * Patient drags/taps to put morning routine pictures in order.
 */
import React, { useState, useRef } from 'react'

const SEQUENCES = {
  easy: [
    { id: 'wake',    emoji: '☀️',  label: 'Wake up',    order: 0 },
    { id: 'brush',   emoji: '🪥',  label: 'Brush teeth', order: 1 },
    { id: 'eat',     emoji: '🍽️', label: 'Eat breakfast', order: 2 },
    { id: 'medicine',emoji: '💊',  label: 'Take medicine', order: 3 },
  ],
  medium: [
    { id: 'wake',    emoji: '☀️',  label: 'Wake up',     order: 0 },
    { id: 'brush',   emoji: '🪥',  label: 'Brush teeth',  order: 1 },
    { id: 'bath',    emoji: '🚿',  label: 'Bathe',        order: 2 },
    { id: 'eat',     emoji: '🍽️', label: 'Eat breakfast', order: 3 },
    { id: 'medicine',emoji: '💊',  label: 'Take medicine', order: 4 },
  ],
  hard: [
    { id: 'wake',    emoji: '☀️',  label: 'Wake up',     order: 0 },
    { id: 'brush',   emoji: '🪥',  label: 'Brush teeth',  order: 1 },
    { id: 'bath',    emoji: '🚿',  label: 'Bathe',        order: 2 },
    { id: 'eat',     emoji: '🍽️', label: 'Eat breakfast', order: 3 },
    { id: 'medicine',emoji: '💊',  label: 'Take medicine', order: 4 },
    { id: 'walk',    emoji: '🚶',  label: 'Morning walk',  order: 5 },
    { id: 'water',   emoji: '💧',  label: 'Drink water',   order: 6 },
  ],
}

function shuffled(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

export default function RoutineGame({ difficulty = 'easy', onComplete }) {
  const steps = SEQUENCES[difficulty]
  const [items, setItems] = useState(() => shuffled(steps))
  const [submitted, setSubmitted] = useState(false)
  const [score, setScore] = useState(null)
  const startTime = useRef(Date.now())
  const dragIdx = useRef(null)

  const moveUp = (i) => {
    if (i === 0) return
    const next = [...items]
    ;[next[i - 1], next[i]] = [next[i], next[i - 1]]
    setItems(next)
  }
  const moveDown = (i) => {
    if (i === items.length - 1) return
    const next = [...items]
    ;[next[i + 1], next[i]] = [next[i], next[i + 1]]
    setItems(next)
  }

  const checkAnswer = () => {
    let correct = 0
    items.forEach((item, i) => { if (item.order === i) correct++ })
    const accuracy = (correct / steps.length) * 100
    const rt = Math.round((Date.now() - startTime.current) / steps.length)
    const errors = steps.length - correct
    const sc = Math.round(accuracy * 10)
    setScore({ accuracy, errors, sc })
    setSubmitted(true)
    setTimeout(() => onComplete(sc, accuracy, rt, errors), 1500)
  }

  return (
    <div>
      <p style={{ marginBottom: '1rem', fontWeight: 700, fontSize: 'var(--font-size-lg)' }}>
        Put the daily routine in order ↓
      </p>
      {items.map((item, i) => (
        <div key={item.id}
          style={{ display: 'flex', alignItems: 'center', gap: '0.75rem',
                   background: submitted
                     ? (item.order === i ? '#e8f5e9' : '#fdecea')
                     : '#fff',
                   border: '2px solid var(--color-border)',
                   borderRadius: '12px', padding: '0.75rem 1rem', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '2rem' }}>{item.emoji}</span>
          <span style={{ flex: 1, fontSize: 'var(--font-size-lg)' }}>{item.label}</span>
          {!submitted && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <button onClick={() => moveUp(i)}
                style={{ minHeight: '40px', minWidth: '40px', fontSize: '1.2rem',
                         border: '1px solid #ccc', borderRadius: '8px', background: '#f5f5f5', cursor: 'pointer' }}>
                ↑
              </button>
              <button onClick={() => moveDown(i)}
                style={{ minHeight: '40px', minWidth: '40px', fontSize: '1.2rem',
                         border: '1px solid #ccc', borderRadius: '8px', background: '#f5f5f5', cursor: 'pointer' }}>
                ↓
              </button>
            </div>
          )}
          {submitted && (
            <span style={{ fontSize: '1.5rem' }}>{item.order === i ? '✅' : '❌'}</span>
          )}
        </div>
      ))}
      {!submitted && (
        <button className="btn btn-primary btn-block btn-lg mt-2" onClick={checkAnswer}>
          Submit Order
        </button>
      )}
      {submitted && score && (
        <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: 'var(--font-size-lg)' }}>
          Score: {score.sc} · Accuracy: {score.accuracy.toFixed(0)}%
        </div>
      )}
    </div>
  )
}
