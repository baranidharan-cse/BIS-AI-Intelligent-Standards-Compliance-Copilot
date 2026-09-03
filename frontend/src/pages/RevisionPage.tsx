import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import type { Material, RevisionTask, RevisionPlan } from '../api/types'
import styles from './RevisionPage.module.css'

export default function RevisionPage() {
  const [tasks, setTasks] = useState<RevisionTask[]>([])
  const [materials, setMaterials] = useState<Material[]>([])
  const [selectedId, setSelectedId] = useState<number | ''>('')
  const [plan, setPlan] = useState<RevisionPlan | null>(null)
  const [loadingTasks, setLoadingTasks] = useState(true)
  const [loadingMaterials, setLoadingMaterials] = useState(true)
  const [generatingPlan, setGeneratingPlan] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toasts, setToasts] = useState<string[]>([])
  const [doneTasks, setDoneTasks] = useState<Set<number>>(new Set())

  const addToast = (msg: string) => {
    setToasts(prev => [...prev, msg])
    setTimeout(() => setToasts(prev => prev.slice(1)), 3000)
  }

  const loadTasks = useCallback(() => {
    api
      .getDueTasks()
      .then(setTasks)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoadingTasks(false))
  }, [])

  useEffect(() => {
    loadTasks()
    api
      .listMaterials()
      .then(ms => setMaterials(ms.filter(m => m.status === 'ready')))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoadingMaterials(false))
  }, [loadTasks])

  const markDone = async (taskId: number) => {
    try {
      await api.completeTask(taskId)
      setDoneTasks(prev => new Set(prev).add(taskId))
      setTasks(prev => prev.filter(t => t.id !== taskId))
      addToast('✓ Reviewed!')
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const generatePlan = async () => {
    if (!selectedId) return
    setGeneratingPlan(true)
    setError(null)
    try {
      const p = await api.generateRevisionPlan(selectedId as number)
      setPlan(p)
      // Reload tasks after generating a plan
      api.getDueTasks().then(setTasks).catch(() => { /* ignore */ })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setGeneratingPlan(false)
    }
  }

  const visibleTasks = tasks.filter(t => !doneTasks.has(t.id))

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Revision</h1>

      {error && <div className={styles.error}>⚠ {error}</div>}

      {/* Toasts */}
      <div className={styles.toastContainer}>
        {toasts.map((msg, i) => (
          <div key={i} className={styles.toast}>{msg}</div>
        ))}
      </div>

      {/* Today's review */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>📅 Today's Review</h2>
        {loadingTasks && <div className={styles.spinner} />}
        {!loadingTasks && visibleTasks.length === 0 && (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>🎉</span>
            <p>You're all caught up! Nothing due today.</p>
          </div>
        )}
        {!loadingTasks && visibleTasks.length > 0 && (
          <div className={styles.taskGrid}>
            {visibleTasks.map(task => (
              <TaskCard key={task.id} task={task} onDone={markDone} />
            ))}
          </div>
        )}
      </section>

      {/* Create plan */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>📋 Create Revision Plan</h2>
        {loadingMaterials && <div className={styles.spinner} />}
        {!loadingMaterials && (
          <div className={styles.planControls}>
            <select
              className={styles.select}
              value={selectedId}
              onChange={e => {
                setSelectedId(e.target.value ? Number(e.target.value) : '')
                setPlan(null)
              }}
            >
              <option value="">— Select a material —</option>
              {materials.map(m => (
                <option key={m.id} value={m.id}>{m.title}</option>
              ))}
            </select>
            <button
              className={styles.generateBtn}
              onClick={generatePlan}
              disabled={!selectedId || generatingPlan}
            >
              {generatingPlan ? 'Generating…' : '🔁 Generate Plan'}
            </button>
          </div>
        )}

        {plan && (
          <div className={styles.planResult}>
            <span className={styles.planCheck}>✓</span>
            <div>
              <strong>{plan.title}</strong>
              <p className={styles.planSub}>
                Revision plan created on {new Date(plan.created_at).toLocaleDateString()}.
                Tasks have been added to your review queue.
              </p>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}

function TaskCard({
  task,
  onDone,
}: {
  task: RevisionTask
  onDone: (id: number) => void
}) {
  const dueDate = new Date(task.due_date)
  const isOverdue = dueDate < new Date()

  return (
    <div className={`${styles.taskCard} ${isOverdue ? styles.taskOverdue : ''}`}>
      <div className={styles.taskHeader}>
        <span className={styles.intervalBadge}>Day {task.interval_days}</span>
        {isOverdue && <span className={styles.overdueBadge}>Overdue</span>}
      </div>
      <h3 className={styles.taskTitle}>{task.title}</h3>
      {task.concept_name && (
        <p className={styles.conceptName}>📌 {task.concept_name}</p>
      )}
      <p className={styles.dueDate}>
        Due: {dueDate.toLocaleDateString()}
      </p>
      <button className={styles.doneBtn} onClick={() => onDone(task.id)}>
        ✓ Mark Done
      </button>
    </div>
  )
}
