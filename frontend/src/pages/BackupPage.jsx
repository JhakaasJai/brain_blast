import React, { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { downloadBackup, restoreBackup } from '../services/backup'

export default function BackupPage() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function exportData() {
    setError('')
    try {
      const backup = await downloadBackup()
      setMessage(`Backup created from ${backup.created_at}.`)
    } catch (e) { setError(e.message || 'Unable to create backup.') }
  }

  function importData(event) {
    const file = event.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = async () => {
      try {
        const backup = JSON.parse(reader.result)
        if (!window.confirm('Restore this backup? Existing local data will be replaced.')) return
        await restoreBackup(backup)
        setMessage('Backup restored. Reload the app to see all local data.')
      } catch (e) { setError(e.message || 'Unable to restore backup.') }
      event.target.value = ''
    }
    reader.readAsText(file)
  }

  return <main className="page" aria-labelledby="backup-title">
    <header className="app-header" style={{ margin: '-1rem -1rem 1rem' }}>
      <button className="btn btn-ghost" style={{ color: '#fff' }} onClick={() => navigate(-1)}>← Back</button>
      <h1 id="backup-title">Backup and restore</h1><span />
    </header>
    <div className="disclaimer">Backups contain local app data. Store the file securely and do not share it publicly.</div>
    <div className="card">
      <h2>Save a backup</h2><p>Download your locally stored games, reminders, and sync queue.</p>
      <button className="btn btn-primary" onClick={exportData}>Download backup</button>
    </div>
    <div className="card">
      <h2>Restore a backup</h2><p>Restoring replaces current local data on this device.</p>
      <input ref={inputRef} type="file" accept="application/json,.json" onChange={importData} aria-label="Choose backup file" />
    </div>
    {message && <p role="status" className="success-text">{message}</p>}
    {error && <p role="alert" className="error-text">{error}</p>}
  </main>
}

export { BackupPage }
