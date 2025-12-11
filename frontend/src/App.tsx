import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import DiagramGenerator from './components/DiagramGenerator'
import HelpPage from './pages/HelpPage'
import './App.css'

function App() {
  return (
    <Router>
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Turn Your Architecture Ideas Into Professional Diagrams
          </h1>
          <p className="mt-1 text-sm text-gray-500">
                  For architects and engineers who need diagrams fast
          </p>
              </div>
              <nav className="flex gap-4">
                <Link
                  to="/"
                  className="px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors"
                >
                  Home
                </Link>
                <Link
                  to="/help"
                  className="px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors"
                >
                  Help
                </Link>
              </nav>
            </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<DiagramGenerator />} />
            <Route path="/help" element={<HelpPage />} />
          </Routes>
      </main>
    </div>
    </Router>
  )
}

export default App

