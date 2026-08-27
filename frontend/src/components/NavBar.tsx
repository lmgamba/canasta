import { NavLink } from 'react-router-dom'
import styles from './NavBar.module.css'

const LINKS = [
  { to: '/upload', label: 'Upload' },
  { to: '/history', label: 'History' },
  { to: '/dashboard', label: 'Dashboard' },
]

function NavBar() {
  return (
    <nav className={styles.nav}>
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            isActive ? `${styles.navLink} ${styles.active}` : styles.navLink
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  )
}

export default NavBar
