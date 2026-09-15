/**
 * Voice service — Web Speech API wrapper.
 * // MOCK: getCloudSTT() and getCloudTTS() currently call Web Speech fallbacks.
 * // In production, swap their bodies to call /voice/stt and /voice/tts endpoints.
 */

// Check browser support
const hasSpeechRecognition =
  typeof window !== 'undefined' &&
  ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

const hasSpeechSynthesis =
  typeof window !== 'undefined' && 'speechSynthesis' in window

// Browser voice packs vary by device. These locale tags select the best
// available regional voice; production can replace this map with Bhashini/TTS.
export const VOICE_PACKS = {
  en: { label: 'English', lang: 'en-IN', source: 'Web Speech regional fallback' },
  hi: { label: 'हिंदी', lang: 'hi-IN', source: 'Web Speech regional fallback' },
  as: { label: 'অসমীয়া', lang: 'as-IN', source: 'Web Speech regional fallback' },
  kha: { label: 'Khasi', lang: 'en-IN', source: 'Web Speech fallback (Khasi pack unavailable)' },
  mni: { label: 'মণিপুরী', lang: 'en-IN', source: 'Web Speech fallback (Meitei pack unavailable)' },
}

export function getVoicePack(locale = 'en') {
  return VOICE_PACKS[locale] || VOICE_PACKS.en
}

/**
 * Speak text aloud using Web Speech API SpeechSynthesis.
 * Falls back silently if not supported.
 */
export function speak(text, lang = 'en-IN') {
  if (!hasSpeechSynthesis) return
  window.speechSynthesis.cancel()
  const utt = new SpeechSynthesisUtterance(text)
  utt.lang = lang
  utt.rate = 0.85   // slightly slower for elderly users
  utt.pitch = 1.0
  utt.volume = 1.0
  window.speechSynthesis.speak(utt)
}

/**
 * Stop any in-progress speech.
 */
export function stopSpeaking() {
  if (hasSpeechSynthesis) window.speechSynthesis.cancel()
}

/**
 * Listen for a spoken answer and resolve with the transcript.
 * Returns a Promise<string>.
 */
export function listen(lang = 'en-IN') {
  return new Promise((resolve, reject) => {
    if (!hasSpeechRecognition) {
      reject(new Error('Speech recognition not available in this browser'))
      return
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const rec = new SR()
    rec.lang = lang
    rec.interimResults = false
    rec.maxAlternatives = 1
    rec.onresult = (e) => resolve(e.results[0][0].transcript)
    rec.onerror = (e) => reject(e.error)
    rec.start()
  })
}

/**
 * // MOCK: Cloud STT stub.
 * Currently delegates to Web Speech API (listen()).
 * To swap in Bhashini: replace body with a POST to /voice/stt.
 */
export function getCloudSTT(lang = 'en-IN') {
  // MOCK: real Bhashini call goes here in production
  return listen(lang)
}

/**
 * // MOCK: Cloud TTS stub.
 * Currently uses Web Speech API (speak()).
 * To swap in Bhashini: POST to /voice/tts, play returned audio URL.
 */
export function getCloudTTS(text, lang = 'en-IN') {
  // MOCK: real Bhashini call goes here in production
  speak(text, lang)
  return Promise.resolve({ source: 'web_speech_fallback' })
}

export const isSpeechSupported = hasSpeechRecognition
export const isTTSSupported = hasSpeechSynthesis
