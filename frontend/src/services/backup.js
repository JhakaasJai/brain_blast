import { db } from './db'

const BACKUP_VERSION = 1
const TABLES = ['game_sessions', 'reminder_events', 'reminders', 'patient_profile', 'sync_queue']

export async function createBackup() {
  const tables = {}
  for (const table of TABLES) tables[table] = await db[table].toArray()
  return {
    format: 'cognitive-care-local-backup',
    version: BACKUP_VERSION,
    created_at: new Date().toISOString(),
    tables,
  }
}

export function validateBackup(backup) {
  if (!backup || backup.format !== 'cognitive-care-local-backup' || backup.version !== BACKUP_VERSION) {
    throw new Error('Unsupported backup file.')
  }
  if (!backup.tables || typeof backup.tables !== 'object') throw new Error('Backup tables are missing.')
  for (const table of TABLES) if (!Array.isArray(backup.tables[table])) throw new Error(`Backup table missing: ${table}`)
  return true
}

export async function restoreBackup(backup) {
  validateBackup(backup)
  await db.transaction('rw', TABLES.map((table) => db[table]), async () => {
    for (const table of TABLES) {
      await db[table].clear()
      if (backup.tables[table].length) await db[table].bulkAdd(backup.tables[table])
    }
  })
}

export async function downloadBackup() {
  const backup = await createBackup()
  const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `cognitive-care-backup-${new Date().toISOString().slice(0, 10)}.json`
  link.click()
  URL.revokeObjectURL(url)
  return backup
}

export { TABLES, BACKUP_VERSION }
