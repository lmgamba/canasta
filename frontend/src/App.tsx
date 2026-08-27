import { Navigate, Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import ItemDetail from './pages/ItemDetail'
import './App.css'

function App() {
  return (
    <main>
      <NavBar />

      <Routes>
        <Route path="/" element={<Navigate to="/history" replace />} />
        <Route path="/history" element={<History />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/items/detail" element={<ItemDetail />} />
        {/* Upload is a placeholder until its own feature is built. */}
        <Route path="/upload" element={<p className="placeholder">Upload page coming soon.</p>} />
      </Routes>
    </main>
  )
}

export default App
