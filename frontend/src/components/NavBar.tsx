import styles from './NavBar.module.css'

export type View = 'upload' | 'history' | 'dashboard'

interface NavBarProps {
  view: View
  onChange: (view: View) => void
}

const LINKS: { view: View; label: string }[] = [
  { view: 'upload', label: 'Upload' },
  { view: 'history', label: 'History' },
  { view: 'dashboard', label: 'Dashboard' },
]

function NavBar({ view, onChange }: NavBarProps) {
  return (
    <nav className={styles.nav}>
      {LINKS.map((link) => (
        <button
          key={link.view}
          className={view === link.view ? `${styles.navLink} ${styles.active}` : styles.navLink}
          onClick={() => onChange(link.view)}
        >
          {link.label}
        </button>
      ))}
    </nav>
  )
}

export default NavBar
