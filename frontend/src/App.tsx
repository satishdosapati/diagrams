import { useState } from 'react'
import DiagramGenerator from './components/DiagramGenerator'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Architecture Diagram Generator
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Generate AWS architecture diagrams from natural language
          </p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <DiagramGenerator />
      </main>
    </div>
  )
}

export default App

