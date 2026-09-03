import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { DashboardStats } from '../api/types'
import styles from './DashboardPage.module.css'

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    api
      .getDashboardStats()
      .then(setStats)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Dashboard</h1>
      <p className={styles.subtitle}>Your learning overview at a glance.</p>

      {loading && <div className={styles.spinner} aria-label="Loading…" />}
      {error && <div className={styles.error}>⚠ {error}</div>}

      {!loading && !error && stats && (
        <>
          <div className={styles.grid}>
            <StatCard label="Total Materials" value={String(stats.total_materials)} icon="📚" />
            <StatCard
              label="Concepts Mastered"
              value={`${stats.mastered_concepts} (${Math.round(stats.avg_mastery_pct)}%)`}
              icon="🧠"
            />
            <StatCard label="Study Streak" value="0 days" icon="🔥" />
            <StatCard label="Due for Revision" value={String(stats.due_today)} icon="🔁" />
          </div>

          {stats.total_quizzes_taken > 0 && (
            <div className={styles.quizStat}>
              <span>📝 Quizzes taken: <strong>{stats.total_quizzes_taken}</strong></span>
              <span>Average score: <strong>{Math.round(stats.avg_quiz_score)}%</strong></span>
            </div>
          )}

          <div className={styles.actions}>
            <h2 className={styles.sectionTitle}>Quick Actions</h2>
            <div className={styles.actionRow}>
              <button className={styles.actionBtn} onClick={() => navigate('/materials')}>
                📂 Upload Material
              </button>
              <button className={styles.actionBtn} onClick={() => navigate('/practice')}>
                ✏️ Start Quiz
              </button>
              <button className={styles.actionBtn} onClick={() => navigate('/revision')}>
                🔁 View Schedule
              </button>
            </div>
          </div>
        </>
      )}

      {!loading && !error && !stats && (
        <div className={styles.placeholder}>
          <p>📂 Upload a study document in <strong>My Materials</strong> to get started.</p>
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className={styles.card}>
      <span className={styles.cardIcon}>{icon}</span>
      <span className={styles.cardValue}>{value}</span>
      <span className={styles.cardLabel}>{label}</span>
    </div>
  )
}
