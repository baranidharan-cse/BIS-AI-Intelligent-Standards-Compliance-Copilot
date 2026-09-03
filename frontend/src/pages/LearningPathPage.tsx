import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { Material, LearningPathDetail, LearningStep } from '../api/types'
import styles from './LearningPathPage.module.css'

export default function LearningPathPage() {
  const [materials, setMaterials] = useState<Material[]>([])
  const [selectedId, setSelectedId] = useState<number | ''>('')
  const [goal, setGoal] = useState('')
  const [path, setPath] = useState<LearningPathDetail | null>(null)
  const [generating, setGenerating] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listMaterials()
      .then(ms => {
        setMaterials(ms.filter(m => m.status === 'ready'))
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const generate = async () => {
    if (!selectedId) return
    setGenerating(true)
    setError(null)
    try {
      const p = await api.generateLearningPath(selectedId as number, goal || undefined)
      const detail = await api.getLearningPath(p.id)
      setPath(detail)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setGenerating(false)
    }
  }

  const updateStep = async (stepId: number, status: LearningStep['status']) => {
    if (!path) return
    try {
      const updated = await api.updateStepStatus(stepId, status)
      setPath(prev =>
        prev
          ? { ...prev, steps: prev.steps.map(s => (s.id === stepId ? { ...s, ...updated } : s)) }
          : prev
      )
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const completedCount = path ? path.steps.filter(s => s.status === 'completed').length : 0
  const totalSteps = path ? path.steps.length : 0
  const progressPct = totalSteps > 0 ? Math.round((completedCount / totalSteps) * 100) : 0

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Learning Path</h1>

      {loading && <div className={styles.spinner} />}
      {error && <div className={styles.error}>⚠ {error}</div>}

      {!loading && (
        <div className={styles.controls}>
          <select
            className={styles.select}
            value={selectedId}
            onChange={e => {
              setSelectedId(e.target.value ? Number(e.target.value) : '')
              setPath(null)
            }}
          >
            <option value="">— Select a material —</option>
            {materials.map(m => (
              <option key={m.id} value={m.id}>
                {m.title}
              </option>
            ))}
          </select>

          <input
            className={styles.goalInput}
            placeholder="Optional: describe your learning goal…"
            value={goal}
            onChange={e => setGoal(e.target.value)}
          />

          <button
            className={styles.generateBtn}
            onClick={generate}
            disabled={!selectedId || generating}
          >
            {generating ? 'Generating…' : '🗺️ Generate Learning Path'}
          </button>
        </div>
      )}

      {path && (
        <div className={styles.pathSection}>
          <div className={styles.pathHeader}>
            <div>
              <h2 className={styles.pathTitle}>{path.title}</h2>
              {path.description && <p className={styles.pathDesc}>{path.description}</p>}
              <span className={styles.durationBadge}>
                ⏱ Est. {path.estimated_duration_minutes} min
              </span>
            </div>
          </div>

          <div className={styles.progressBar}>
            <div className={styles.progressFill} style={{ width: `${progressPct}%` }} />
          </div>
          <div className={styles.progressLabel}>
            {completedCount}/{totalSteps} steps completed ({progressPct}%)
          </div>

          <div className={styles.timeline}>
            {path.steps
              .slice()
              .sort((a, b) => a.order_index - b.order_index)
              .map(step => (
                <StepCard key={step.id} step={step} onUpdate={updateStep} />
              ))}
          </div>
        </div>
      )}

      {!path && !loading && !generating && selectedId && (
        <p className={styles.hint}>Click "Generate Learning Path" to create a study plan for this material.</p>
      )}
      {!path && !loading && !selectedId && materials.length === 0 && (
        <p className={styles.hint}>No ready materials found. Upload and process a material first.</p>
      )}
    </div>
  )
}

function StepCard({
  step,
  onUpdate,
}: {
  step: LearningStep
  onUpdate: (id: number, status: LearningStep['status']) => void
}) {
  const statusClass = {
    not_started: styles.statusNotStarted,
    in_progress: styles.statusInProgress,
    completed: styles.statusCompleted,
    skipped: styles.statusSkipped,
  }[step.status]

  return (
    <div className={`${styles.step} ${statusClass}`}>
      <div className={styles.stepDot}>
        {step.status === 'completed' ? '✓' : step.order_index + 1}
      </div>
      <div className={styles.stepBody}>
        <div className={styles.stepTop}>
          <span className={styles.stepTitle}>{step.title}</span>
          <span className={styles.timeBadge}>⏱ {step.estimated_minutes} min</span>
        </div>
        {step.description && <p className={styles.stepDesc}>{step.description}</p>}
        {step.prerequisites && (
          <p className={styles.stepPre}>Prerequisites: {step.prerequisites}</p>
        )}
        <div className={styles.stepActions}>
          {step.status !== 'completed' && (
            <button
              className={styles.btnComplete}
              onClick={() => onUpdate(step.id, 'completed')}
            >
              ✓ Mark Complete
            </button>
          )}
          {step.status === 'not_started' && (
            <button
              className={styles.btnProgress}
              onClick={() => onUpdate(step.id, 'in_progress')}
            >
              ▶ Start
            </button>
          )}
          {step.status === 'completed' && (
            <button
              className={styles.btnReset}
              onClick={() => onUpdate(step.id, 'not_started')}
            >
              ↩ Reset
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
