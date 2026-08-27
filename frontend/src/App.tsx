import { Navigate, Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import ItemDetail from './pages/ItemDetail'
import Upload from './pages/Upload'
import './App.css'

function App() {
  return (
    <main>
      <NavBar />

      <Routes>
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/history" element={<History />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/items/detail" element={<ItemDetail />} />
      </Routes>
    </main>
  )
}

export default App
