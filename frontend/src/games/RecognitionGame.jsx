/**
 * Pattern & Object Recognition Game — Culturally local object naming
 * Shows an object; patient picks the correct name from 3 options.
 * Regional NER items: Assamese/Manipuri/Khasi cultural objects.
 */
import React, { useState, useRef } from 'react'
import { speak } from '../services/voice'

const QUESTIONS = {
  easy: [
    { emoji: '🎋', answer: 'Bamboo',   options: ['Bamboo', 'Rice', 'Jute'] },
    { emoji: '🌾', answer: 'Rice',     options: ['Wheat', 'Rice', 'Corn'] },
    { emoji: '🦚', answer: 'Peacock',  options: ['Peacock', 'Parrot', 'Eagle'] },
    { emoji: '🍃', answer: 'Tea leaf', options: ['Tea leaf', 'Betel leaf', 'Neem leaf'] },
    { emoji: '🐅', answer: 'Tiger',    options: ['Tiger', 'Leopard', 'Cheetah'] },
  ],
  medium: [
    { emoji: '🎋', answer: 'Bamboo shoots', options: ['Bamboo shoots', 'Sugarcane', 'Asparagus'] },
    { emoji: '🌺', answer: 'Foxtail orchid',options: ['Foxtail orchid', 'Lotus', 'Marigold'] },
    { emoji: '🦋', answer: 'Muga silkworm', options: ['Muga silkworm', 'Monarch butterfly', 'Firefly'] },
    { emoji: '🥁', answer: 'Dhol drum',     options: ['Dhol drum', 'Tabla', 'Mridangam'] },
    { emoji: '🛶', answer: 'Country boat',  options: ['Country boat', 'Canoe', 'Kayak'] },
  ],
  hard: [
    { emoji: '🎋', answer: 'Bamboo shoots (Khorisa)', options: ['Bamboo shoots (Khorisa)', 'Bamboo pickle', 'Bamboo rice'] },
    { emoji: '🌺', answer: 'Kopou phool (orchid)',    options: ['Kopou phool (orchid)', 'Singhara flower', 'Water lily'] },
    { emoji: '🎭', answer: 'Ras Lila mask',           options: ['Ras Lila mask', 'Chhau mask', 'Yakshagana mask'] },
    { emoji: '🏺', answer: 'Longpi pottery',          options: ['Longpi pottery', 'Blue pottery', 'Khurja pottery'] },
    { emoji: '🎵', answer: 'Pena (fiddle)',            options: ['Pena (fiddle)', 'Sarangi', 'Dotara'] },
  ],
}

export default function RecognitionGame({ difficulty = 'easy', onComplete }) {
  const questions = QUESTIONS[difficulty]
  const [qIdx, setQIdx] = useState(0)
  const [selected, setSelected] = useState(null)
  const [errors, setErrors] = useState(0)
  const [correct, setCorrect] = useState(0)
  const startTime = useRef(Date.now())
  const reactionTimes = useRef([])
  const qStart = useRef(Date.now())

  const q = questions[qIdx]

  const pick = (option) => {
    if (selected) return
    const rt = Date.now() - qStart.current
    reactionTimes.current.push(rt)
    setSelected(option)

    const isCorrect = option === q.answer
    if (isCorrect) {
      setCorrect((c) => c + 1)
      speak('Correct!')
    } else {
      setErrors((e) => e + 1)
      speak(`The answer is ${q.answer}`)
    }

    setTimeout(() => {
      const next = qIdx + 1
      if (next >= questions.length) {
        const corr = correct + (isCorrect ? 1 : 0)
        const accuracy = (corr / questions.length) * 100
        const avgRt = Math.round(reactionTimes.current.reduce((a, b) => a + b, 0) / reactionTimes.current.length)
        const err = errors + (isCorrect ? 0 : 1)
        onComplete(Math.round(accuracy * 10), accuracy, avgRt, err)
      } else {
        setQIdx(next)
        setSelected(null)
        qStart.current = Date.now()
      }
    }, 1200)
  }

  return (
    <div>
      <p style={{ marginBottom: '0.5rem', color: 'var(--color-text-secondary)' }}>
        {qIdx + 1} / {questions.length}
      </p>
      <div className="card text-center" style={{ marginBottom: '1.5rem' }}>
        <div style={{ fontSize: '5rem', marginBottom: '0.5rem' }}>{q.emoji}</div>
        <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>What is this?</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {q.options.map((opt) => (
          <button key={opt}
            onClick={() => pick(opt)}
            style={{
              minHeight: '64px', fontSize: 'var(--font-size-lg)', borderRadius: '12px',
              border: '3px solid',
              borderColor: selected
                ? (opt === q.answer ? '#2e7d32' : opt === selected ? '#c62828' : '#ddd')
                : 'var(--color-border)',
              background: selected
                ? (opt === q.answer ? '#e8f5e9' : opt === selected ? '#fdecea' : '#fff')
                : '#fff',
              cursor: selected ? 'default' : 'pointer',
              fontWeight: 700, padding: '0.75rem 1rem', textAlign: 'left',
            }}>
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}
