/**
 * Sync manager — queues local Dexie writes and flushes to backend when online.
 * Uses Workbox Background Sync for automatic retry.
 */
import { db } from './db'
import { syncGameSessions, syncReminderEvents } from './api'

const stripLocalFields = ({ id, sync_status, client_timestamp, ...serverRecord }) => serverRecord

async function markSynced(table, records, result) {
  // The API is idempotent: synced + skipped both mean the client record is
  // safely present on the server. Leave records untouched on transport errors.
  if (!result || typeof result.synced !== 'number') return 0
  const uuids = records.map((record) => record.client_uuid)
  await db[table].where('client_uuid').anyOf(uuids).modify({ sync_status: 'synced' })
  await db.sync_queue.where('client_uuid').anyOf(uuids).modify({ sync_status: 'synced' })
  return result.synced
}

export async function flushSyncQueue() {
  if (!navigator.onLine) return { flushed: 0 }

  let flushed = 0
  const pendingSessions = await db.game_sessions.where('sync_status').equals('pending').toArray()
  if (pendingSessions.length > 0) {
    try {
      const payload = pendingSessions.map(stripLocalFields)
      const result = await syncGameSessions(payload)
      flushed += await markSynced('game_sessions', pendingSessions, result)
    } catch (e) {
      const status = e.response?.status
      const nextStatus = status && status >= 400 && status < 500 ? 'conflict' : 'pending'
      await db.game_sessions.where('client_uuid').anyOf(pendingSessions.map((record) => record.client_uuid)).modify({ sync_status: nextStatus })
      await db.sync_queue.where('client_uuid').anyOf(pendingSessions.map((record) => record.client_uuid)).modify({ sync_status: nextStatus })
      console.warn('[sync] game sessions sync failed:', e.message)
    }
  }

  const pendingEvents = await db.reminder_events.where('sync_status').equals('pending').toArray()
  if (pendingEvents.length > 0) {
    try {
      const payload = pendingEvents.map(stripLocalFields)
      const result = await syncReminderEvents(payload)
      flushed += await markSynced('reminder_events', pendingEvents, result)
    } catch (e) {
      const status = e.response?.status
      const nextStatus = status && status >= 400 && status < 500 ? 'conflict' : 'pending'
      await db.reminder_events.where('client_uuid').anyOf(pendingEvents.map((record) => record.client_uuid)).modify({ sync_status: nextStatus })
      await db.sync_queue.where('client_uuid').anyOf(pendingEvents.map((record) => record.client_uuid)).modify({ sync_status: nextStatus })
      console.warn('[sync] reminder events sync failed:', e.message)
    }
  }

  return { flushed }
} 

export async function queueWrite(tableName, record) {
  const table = db[tableName]
  const now = record.client_timestamp || new Date().toISOString()
  const enriched = { ...record, client_timestamp: now, sync_status: 'pending' }
  const id = await table.add(enriched)
  await db.sync_queue.put({
    table_name: tableName,
    client_uuid: record.client_uuid,
    sync_status: 'pending',
    created_at: now,
  })
  return { ...enriched, id }
}

export async function getSyncStatus() {
  const [pendingSessions, pendingEvents, conflictSessions, conflictEvents] = await Promise.all([
    db.game_sessions.where('sync_status').equals('pending').toArray(),
    db.reminder_events.where('sync_status').equals('pending').toArray(),
    db.game_sessions.where('sync_status').equals('conflict').toArray(),
    db.reminder_events.where('sync_status').equals('conflict').toArray(),
  ])
  return {
    pending: pendingSessions.length + pendingEvents.length,
    conflicts: [
      ...conflictSessions.map((record) => ({ ...record, table_name: 'game_sessions' })),
      ...conflictEvents.map((record) => ({ ...record, table_name: 'reminder_events' })),
    ],
  }
}

export async function discardConflict(tableName, id) {
  const local = await db[tableName].get(id)
  if (local?.client_uuid) {
    await db.sync_queue.where('client_uuid').equals(local.client_uuid).delete()
  }
  await db[tableName].delete(id)
}

export async function getPendingCount() {
  const status = await getSyncStatus()
  return status.pending
}

// Auto-flush when coming back online
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    flushSyncQueue().catch(console.warn)
  })
}
