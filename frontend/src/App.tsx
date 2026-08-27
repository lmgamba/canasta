import { useState } from 'react'
import NavBar, { type View } from './components/NavBar'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import './App.css'

function App() {
  // Minimal client-side view switcher — no router dependency yet.
  // Upload is a placeholder until its own feature is built.
  const [view, setView] = useState<View>('history')

  return (
    <main>
      <NavBar view={view} onChange={setView} />

      {view === 'history' && <History />}
      {view === 'dashboard' && <Dashboard />}
      {view === 'upload' && <p className="placeholder">Upload page coming soon.</p>}
    </main>
  )
}

export default App