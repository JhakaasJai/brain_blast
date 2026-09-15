// Local-first reminder scheduler.
// It polls cached reminders so the patient can still receive prompts offline.
import { getCloudTTS } from './voice'

let timer = null
let lastFired = new Map()

function reminderKey(reminder, now) {
  const date = now.toISOString().slice(0, 10)
  const time = now.toTimeString().slice(0, 5)
  return `${reminder.id}:${date}:${time}`
}

function isDue(reminder, now) {
  if (!reminder.active) return false
  const rule = reminder.schedule_rule || {}
  const time = now.toTimeString().slice(0, 5)
  if (rule.type === 'daily') return time === rule.time
  if (rule.type === 'weekly') {
    const day = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase()
    return day === rule.day && time === rule.time
  }
  if (rule.type === 'once') {
    const at = new Date(rule.at)
    return Math.abs(now.getTime() - at.getTime()) < 60_000
  }
  return false
}

async function notify(reminder, onDue) {
  const key = reminderKey(reminder, new Date())
  if (lastFired.has(key)) return
  lastFired.set(key, Date.now())

  // MOCK: browser Notification is the real local fallback; cloud push is out of scope.
  if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
    new Notification(reminder.message, { body: `Reminder: ${reminder.category}` })
  }
  await getCloudTTS(reminder.message).catch(() => {})
  onDue(reminder)
}

export function startReminderScheduler(reminders, onDue) {
  stopReminderScheduler()
  const check = () => {
    const now = new Date()
    reminders.filter((r) => isDue(r, now)).forEach((r) => notify(r, onDue))
  }
  check()
  timer = window.setInterval(check, 30_000)
  return stopReminderScheduler
}

export function stopReminderScheduler() {
  if (timer !== null) window.clearInterval(timer)
  timer = null
}

export async function requestNotificationPermission() {
  if (typeof Notification === 'undefined') return 'unsupported'
  if (Notification.permission === 'default') return Notification.requestPermission()
  return Notification.permission
}

export function resetReminderHistory() {
  lastFired = new Map()
}
