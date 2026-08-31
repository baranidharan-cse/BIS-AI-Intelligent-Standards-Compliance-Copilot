import styles from './PlaceholderPage.module.css'

interface Props {
  title: string
  description: string
  session?: string
}

/**
 * Temporary placeholder used until a feature page is implemented.
 * Replace this component with the real page in the designated session.
 */
export default function PlaceholderPage({ title, description, session }: Props) {
  return (
    <div className={styles.page}>
      <div className={styles.badge}>Coming in {session ?? 'a future session'}</div>
      <h1 className={styles.title}>{title}</h1>
      <p className={styles.description}>{description}</p>
      <div className={styles.placeholder}>
        <span className={styles.placeholderIcon}>🚧</span>
        <p>This page will be implemented in a future session.</p>
        <p>The backend models, repositories, and LLM service interfaces are already in place.</p>
      </div>
    </div>
  )
}
