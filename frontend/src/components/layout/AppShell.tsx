import { Outlet, NavLink } from 'react-router-dom'
import styles from './AppShell.module.css'

const NAV_ITEMS = [
  { to: '/dashboard',     label: 'Dashboard',     icon: '🏠' },
  { to: '/materials',     label: 'My Materials',  icon: '📚' },
  { to: '/learning-path', label: 'Learning Path', icon: '🗺️'  },
  { to: '/study',         label: 'Study',         icon: '📖' },
  { to: '/practice',      label: 'Practice',      icon: '✏️'  },
  { to: '/revision',      label: 'Revision',      icon: '🔁' },
  { to: '/ask-buddy',     label: 'Ask Buddy',     icon: '💬' },
  { to: '/settings',      label: 'Settings',      icon: '⚙️'  },
  { to: '/profile',       label: 'Profile',       icon: '👤' },
]

export default function AppShell() {
  return (
    <div className={styles.shell}>
      <nav className={styles.sidebar}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🎓</span>
          <span className={styles.logoText}>Study Buddy</span>
        </div>
        <ul className={styles.navList}>
          {NAV_ITEMS.map(({ to, label, icon }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.active : ''}`
                }
              >
                <span className={styles.navIcon}>{icon}</span>
                <span className={styles.navLabel}>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}
