import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import DiagramGenerator from './components/DiagramGenerator'
import HelpPage from './pages/HelpPage'
import { ToastContainer } from './components/Toast'
import { useToast } from './hooks/useToast'
import './App.css'

function App() {
  const toast = useToast()

  return (
    <Router>
      <>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
          <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-sm">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between">
                  <div>
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
                Architecture Diagram Generator
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                      Generate cloud architecture diagrams from natural language
              </p>
                  </div>
                  <nav className="flex gap-2">
                    <Link
                      to="/"
                      className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg transition-all duration-200 font-medium"
                    >
                      Home
                    </Link>
                    <Link
                      to="/help"
                      className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50/50 rounded-lg transition-all duration-200 font-medium"
                    >
                      Help
                    </Link>
                  </nav>
                </div>
            </div>
          </header>
          
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/" element={<DiagramGenerator toast={toast} />} />
                <Route path="/help" element={<HelpPage />} />
              </Routes>
          </main>
        </div>
        <ToastContainer toasts={toast.toasts} onClose={toast.removeToast} />
      </>
    </Router>
  )
}

export default App

