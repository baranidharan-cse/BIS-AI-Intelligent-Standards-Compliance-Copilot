import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { Material } from '../api/types'
import styles from './MyMaterialsPage.module.css'

type Tab = 'text' | 'file'

export default function MyMaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('text')

  // paste-text form
  const [textTitle, setTextTitle] = useState('')
  const [rawText, setRawText] = useState('')
  const [textSubmitting, setTextSubmitting] = useState(false)
  const [textError, setTextError] = useState<string | null>(null)

  // upload-file form
  const [fileTitle, setFileTitle] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [fileSubmitting, setFileSubmitting] = useState(false)
  const [fileError, setFileError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null)
  const navigate = useNavigate()

  const load = () => {
    api
      .listMaterials()
      .then(setMaterials)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  // Poll processing materials every 3s
  useEffect(() => {
    const processing = materials.filter(m => m.status === 'processing' || m.status === 'pending')
    if (processing.length === 0) return
    const id = setInterval(() => {
      api.listMaterials().then(updated => {
        setMaterials(updated)
        const stillProcessing = updated.filter(m => m.status === 'processing' || m.status === 'pending')
        if (stillProcessing.length === 0) clearInterval(id)
      }).catch(() => { /* ignore poll errors */ })
    }, 3000)
    return () => clearInterval(id)
  }, [materials])

  const submitText = async () => {
    if (!textTitle.trim() || !rawText.trim()) {
      setTextError('Title and content are required.')
      return
    }
    setTextSubmitting(true)
    setTextError(null)
    try {
      const m = await api.createMaterial({ title: textTitle.trim(), raw_text: rawText.trim() })
      setMaterials(prev => [m, ...prev])
      setTextTitle('')
      setRawText('')
    } catch (e) {
      setTextError((e as Error).message)
    } finally {
      setTextSubmitting(false)
    }
  }

  const submitFile = async () => {
    if (!file || !fileTitle.trim()) {
      setFileError('Title and file are required.')
      return
    }
    setFileSubmitting(true)
    setFileError(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('title', fileTitle.trim())
      const m = await api.uploadMaterial(fd)
      setMaterials(prev => [m, ...prev])
      setFileTitle('')
      setFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (e) {
      setFileError((e as Error).message)
    } finally {
      setFileSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await api.deleteMaterial(id)
      setMaterials(prev => prev.filter(m => m.id !== id))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setDeleteConfirm(null)
    }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>My Materials</h1>

      {/* Upload area */}
      <div className={styles.uploadBox}>
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${tab === 'text' ? styles.tabActive : ''}`}
            onClick={() => setTab('text')}
          >
            📝 Paste Text
          </button>
          <button
            className={`${styles.tab} ${tab === 'file' ? styles.tabActive : ''}`}
            onClick={() => setTab('file')}
          >
            📎 Upload File
          </button>
        </div>

        {tab === 'text' && (
          <div className={styles.form}>
            <input
              className={styles.input}
              placeholder="Title"
              value={textTitle}
              onChange={e => setTextTitle(e.target.value)}
            />
            <textarea
              className={styles.textarea}
              placeholder="Paste your study text here…"
              value={rawText}
              onChange={e => setRawText(e.target.value)}
              rows={6}
            />
            {textError && <div className={styles.formError}>{textError}</div>}
            <button
              className={styles.submitBtn}
              onClick={submitText}
              disabled={textSubmitting}
            >
              {textSubmitting ? 'Submitting…' : 'Create Material'}
            </button>
          </div>
        )}

        {tab === 'file' && (
          <div className={styles.form}>
            <input
              className={styles.input}
              placeholder="Title"
              value={fileTitle}
              onChange={e => setFileTitle(e.target.value)}
            />
            <input
              ref={fileInputRef}
              className={styles.fileInput}
              type="file"
              accept=".txt"
              onChange={e => setFile(e.target.files?.[0] ?? null)}
            />
            {fileError && <div className={styles.formError}>{fileError}</div>}
            <button
              className={styles.submitBtn}
              onClick={submitFile}
              disabled={fileSubmitting}
            >
              {fileSubmitting ? 'Uploading…' : 'Upload File'}
            </button>
          </div>
        )}
      </div>

      {/* List */}
      {loading && <div className={styles.spinner} />}
      {error && <div className={styles.error}>⚠ {error}</div>}

      {!loading && materials.length === 0 && (
        <p className={styles.empty}>No materials yet. Upload one above to get started.</p>
      )}

      <div className={styles.grid}>
        {materials.map(m => (
          <div key={m.id} className={styles.card} onClick={() => navigate(`/study`)}>
            <div className={styles.cardHeader}>
              <span className={styles.cardTitle}>{m.title}</span>
              <StatusBadge status={m.status} />
            </div>
            {m.summary && <p className={styles.cardSummary}>{m.summary}</p>}
            <div className={styles.cardFooter}>
              <span className={styles.cardDate}>
                {new Date(m.created_at).toLocaleDateString()}
              </span>
              <button
                className={styles.deleteBtn}
                onClick={e => {
                  e.stopPropagation()
                  setDeleteConfirm(m.id)
                }}
              >
                🗑
              </button>
            </div>

            {deleteConfirm === m.id && (
              <div className={styles.confirm} onClick={e => e.stopPropagation()}>
                <span>Delete this material?</span>
                <button className={styles.confirmYes} onClick={() => handleDelete(m.id)}>
                  Yes, delete
                </button>
                <button className={styles.confirmNo} onClick={() => setDeleteConfirm(null)}>
                  Cancel
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: Material['status'] }) {
  const cls = {
    ready: styles.badgeReady,
    processing: styles.badgeProcessing,
    pending: styles.badgePending,
    error: styles.badgeError,
  }[status]
  const label = {
    ready: '✓ Ready',
    processing: '⟳ Processing…',
    pending: '⏳ Pending',
    error: '✗ Error',
  }[status]
  return <span className={`${styles.badge} ${cls}`}>{label}</span>
}
