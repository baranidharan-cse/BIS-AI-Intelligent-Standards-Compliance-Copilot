import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { ProfileStats } from '../api/types'
import styles from './ProfilePage.module.css'

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getProfileStats()
      .then(setProfile)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className={styles.page}>
      {/* Header Profile Banner */}
      <div className={styles.banner}>
        <div className={styles.avatar}>🎓</div>
        <div className={styles.profileInfo}>
          <h1 className={styles.userName}>Student Learner</h1>
          <p className={styles.userRole}>Active Learner · Study Buddy Member</p>
          {profile && (
            <div className={styles.badgesInline}>
              <span className={styles.pill}>⏱ {profile.total_study_time_minutes} min total study time</span>
              <span className={styles.pill}>🔁 {profile.total_tasks_completed} reviews completed</span>
            </div>
          )}
        </div>
      </div>

      {loading && <div className={styles.spinner} aria-label="Loading profile…" />}
      {error && <div className={styles.error}>⚠ {error}</div>}

      {!loading && profile && (
        <>
          {/* Key Metrics */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>📊 Learning Overview</h2>
            <div className={styles.metricsGrid}>
              <MetricCard
                icon="📚"
                label="Study Materials"
                value={String(profile.dashboard.total_materials)}
              />
              <MetricCard
                icon="🧠"
                label="Concepts Mastered"
                value={`${profile.dashboard.mastered_concepts} / ${profile.dashboard.total_concepts}`}
              />
              <MetricCard
                icon="✏️"
                label="Quizzes Completed"
                value={String(profile.dashboard.total_quizzes_taken)}
              />
              <MetricCard
                icon="🎯"
                label="Avg Quiz Score"
                value={`${Math.round(profile.dashboard.avg_quiz_score)}%`}
              />
            </div>
          </section>

          {/* Per-Material Mastery Breakdown */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>📖 Material Mastery Breakdown</h2>
            {profile.materials_progress.length === 0 ? (
              <p className={styles.emptyText}>No ready materials yet. Ingest a document in My Materials to track progress.</p>
            ) : (
              <div className={styles.materialList}>
                {profile.materials_progress.map(m => (
                  <div key={m.id} className={styles.materialCard}>
                    <div className={styles.matHeader}>
                      <span className={styles.matTitle}>{m.title}</span>
                      <span className={styles.matTime}>⏱ {m.time_studied_minutes} min</span>
                    </div>
                    
                    <div className={styles.progressRow}>
                      <span className={styles.progLabel}>Concept Mastery</span>
                      <div className={styles.barOuter}>
                        <div
                          className={`${styles.barInner} ${styles.barMastery}`}
                          style={{ width: `${m.mastery_pct}%` }}
                        />
                      </div>
                      <span className={styles.progVal}>{m.mastery_pct}%</span>
                    </div>

                    <div className={styles.progressRow}>
                      <span className={styles.progLabel}>Path Progress</span>
                      <div className={styles.barOuter}>
                        <div
                          className={`${styles.barInner} ${styles.barPath}`}
                          style={{ width: `${m.completion_pct}%` }}
                        />
                      </div>
                      <span className={styles.progVal}>{m.completion_pct}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Badges & Achievements */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>🏆 Achievements & Badges</h2>
            <div className={styles.badgeGrid}>
              {profile.badges.map(b => (
                <div
                  key={b.id}
                  className={`${styles.badgeCard} ${b.unlocked ? styles.badgeUnlocked : styles.badgeLocked}`}
                >
                  <span className={styles.badgeIcon}>{b.icon}</span>
                  <div className={styles.badgeContent}>
                    <div className={styles.badgeTop}>
                      <strong className={styles.badgeTitle}>{b.title}</strong>
                      <span className={b.unlocked ? styles.tagUnlocked : styles.tagLocked}>
                        {b.unlocked ? 'Unlocked ✓' : 'Locked'}
                      </span>
                    </div>
                    <p className={styles.badgeDesc}>{b.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}

function MetricCard({ icon, label, value }: { icon: string; label: string; value: string }) {
  return (
    <div className={styles.metricCard}>
      <span className={styles.metricIcon}>{icon}</span>
      <span className={styles.metricValue}>{value}</span>
      <span className={styles.metricLabel}>{label}</span>
    </div>
  )
}
