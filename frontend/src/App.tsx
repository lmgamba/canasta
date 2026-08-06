import { useState } from 'react'
import History from './pages/History'
import './App.css'

function App() {
  // Minimal client-side view switcher — no router dependency yet.
  // Upload is a placeholder until its own feature is built.
  const [view, setView] = useState<'upload' | 'history'>('history')

  return (
    <main>
      <nav className="nav">
        <button
          className={view === 'upload' ? 'navLink active' : 'navLink'}
          onClick={() => setView('upload')}
        >
          Upload
        </button>
        <button
          className={view === 'history' ? 'navLink active' : 'navLink'}
          onClick={() => setView('history')}
        >
          History
        </button>
      </nav>

      {view === 'history' ? (
        <History />
      ) : (
        <p className="placeholder">Upload page coming soon.</p>
      )}
    </main>
  )
}

export default App