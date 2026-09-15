// Dexie (IndexedDB) database schema.
// Every patient-facing write is persisted locally before network sync.
import Dexie from 'dexie'

export const db = new Dexie('CognitiveCareDB')

db.version(1).stores({
  game_sessions: '++id, patient_id, game_type, completed_at, sync_status, client_uuid',
  reminder_events: '++id, reminder_id, patient_id, fired_at, sync_status, client_uuid',
  reminders: 'id, patient_id, category, active',
  patient_profile: 'user_id',
  sync_queue: '++id, table_name, client_uuid, sync_status, created_at',
})

// v2 makes the client timestamp queryable for conflict resolution and resumes
// older local databases without deleting patient progress.
db.version(2).stores({
  game_sessions: '++id, patient_id, game_type, completed_at, sync_status, client_uuid, client_timestamp',
  reminder_events: '++id, reminder_id, patient_id, fired_at, sync_status, client_uuid, client_timestamp',
  reminders: 'id, patient_id, category, active',
  patient_profile: 'user_id',
  sync_queue: '++id, table_name, client_uuid, sync_status, created_at',
})

export default db
