import styles from './DashboardPage.module.css'

/**
 * Dashboard — landing page after login.
 * Session 1: skeleton only. Will show progress summary, upcoming revisions,
 * and quick-access cards in a future session.
 */
export default function DashboardPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Dashboard</h1>
      <p className={styles.subtitle}>
        Welcome to Study Buddy. Your learning overview will appear here once you
        upload your first material.
      </p>

      <div className={styles.grid}>
        <StatCard label="Materials" value="0" icon="📚" />
        <StatCard label="Concepts Mastered" value="0%" icon="🧠" />
        <StatCard label="Study Streak" value="0 days" icon="🔥" />
        <StatCard label="Due for Revision" value="0" icon="🔁" />
      </div>

      <div className={styles.placeholder}>
        <p>📂 Upload a study document in <strong>My Materials</strong> to get started.</p>
      </div>
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
