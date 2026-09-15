import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getSyncStatus, flushSyncQueue, discardConflict } from '../services/syncManager'

export default function SyncIndicator() {
  const { t } = useTranslation()
  const [status, setStatus] = useState({ pending: 0, conflicts: [] })
  const [open, setOpen] = useState(false)

  const check = async () => setStatus(await getSyncStatus().catch(() => ({ pending: 0, conflicts: [] })))
  useEffect(() => {
    check()
    const iv = setInterval(check, 15000)
    return () => clearInterval(iv)
  }, [])

  const retry = async () => { await flushSyncQueue(); await check() }
  const discard = async (item) => { await discardConflict(item.table_name, item.id); await check() }
  if (status.pending === 0 && status.conflicts.length === 0) return null

  return <>
    <button className="sync-bar" role="status" aria-live="polite" onClick={() => setOpen((value) => !value)}>
      {status.conflicts.length > 0 ? '⚠️' : '🔄'} {status.conflicts.length > 0 ? `${status.conflicts.length} sync conflict(s)` : t('sync_pending', { count: status.pending })}
    </button>
    {open && <section className="sync-panel card" aria-label="Offline sync details">
      <p>{status.pending} item(s) waiting to sync. Conflicts need your decision.</p>
      <button className="btn btn-primary" onClick={retry}>Retry sync</button>
      {status.conflicts.map((item) => <div className="sync-conflict" key={`${item.table_name}-${item.id}`}>
        <strong>{item.table_name === 'game_sessions' ? 'Game session' : 'Reminder event'}</strong>
        <span>Saved locally at {item.client_timestamp || 'an earlier time'}.</span>
        <button className="btn btn-danger btn-outline" onClick={() => discard(item)}>Discard local copy</button>
      </div>)}
    </section>}
  </>
}
