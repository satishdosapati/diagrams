import { useState } from 'react'
import { generateDiagram, getDiagramUrl } from '../services/api'
import ProviderSelector from './ProviderSelector'
import DiagramChat from './DiagramChat'
import ExamplesPanel from './ExamplesPanel'
import AdvancedCodeMode from './AdvancedCodeMode'

type Provider = 'aws' | 'azure' | 'gcp'
type Mode = 'natural-language' | 'advanced-code'

function DiagramGenerator() {
  const [mode, setMode] = useState<Mode>('natural-language')
  const [description, setDescription] = useState('')
  const [selectedProvider, setSelectedProvider] = useState<Provider>('aws')
  const [diagramUrl, setDiagramUrl] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [showChat, setShowChat] = useState(false)
  const [showExamples, setShowExamples] = useState(true)

  const handleGenerate = async () => {
    if (mode === 'advanced-code') {
      // Advanced code mode handles its own generation
      return
    }

    if (!description.trim()) {
      setError('Please enter an architecture description')
      return
    }

    setIsGenerating(true)
    setError(null)
    setMessage(null)
    setDiagramUrl(null)

    try {
      const response = await generateDiagram(description, selectedProvider)
      setMessage(response.message)
      setSessionId(response.session_id)
      
      // Extract filename from URL
      const filename = response.diagram_url.split('/').pop()
      if (filename) {
        const url = getDiagramUrl(filename)
        setDiagramUrl(url)
        setShowChat(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate diagram')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleExampleSelect = (prompt: string) => {
    setDescription(prompt)
    setShowExamples(false)
  }

  const handleDiagramGenerated = (url: string) => {
    setDiagramUrl(url)
    setShowChat(true)
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Generate Architecture Diagram</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowExamples(!showExamples)}
            className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50"
          >
            {showExamples ? 'Hide' : 'Show'} Examples
          </button>
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="mb-4">
        <div className="flex border rounded-md p-1 bg-gray-50">
          <button
            onClick={() => setMode('natural-language')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'natural-language'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Natural Language
          </button>
          <button
            onClick={() => setMode('advanced-code')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'advanced-code'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Advanced Code
          </button>
        </div>
      </div>
      
      <div className="space-y-4">
        <ProviderSelector
          selectedProvider={selectedProvider}
          onSelectionChange={setSelectedProvider}
        />

        {/* Examples Panel */}
        {showExamples && mode === 'natural-language' && (
          <ExamplesPanel
            provider={selectedProvider}
            onSelectExample={handleExampleSelect}
          />
        )}

        {/* Natural Language Mode */}
        {mode === 'natural-language' && (
          <>
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Describe your {selectedProvider.toUpperCase()} architecture
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., Create a serverless API with API Gateway, Lambda, and DynamoDB"
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                disabled={isGenerating}
              />
              <p className="mt-1 text-sm text-gray-500">
                Describe the {selectedProvider.toUpperCase()} architecture you want to visualize
              </p>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !description.trim()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isGenerating ? 'Generating...' : 'Generate Diagram'}
            </button>
          </>
        )}

        {/* Advanced Code Mode */}
        {mode === 'advanced-code' && (
          <AdvancedCodeMode
            provider={selectedProvider}
            onDiagramGenerated={handleDiagramGenerated}
          />
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {message && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-600">{message}</p>
          </div>
        )}

        {diagramUrl && (
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Generated Diagram</h3>
            <div className="border rounded-lg p-4 bg-gray-50">
              <img
                src={diagramUrl}
                alt="Generated architecture diagram"
                className="w-full max-w-4xl mx-auto"
              />
            </div>
            <div className="mt-4 flex gap-2">
              <a
                href={diagramUrl}
                download
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                Download PNG
              </a>
            </div>
          </div>
        )}

        {showChat && diagramUrl && sessionId && (
          <div className="mt-6 border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Modify Diagram</h3>
            <div className="border rounded-lg" style={{ height: '600px' }}>
              <DiagramChat
                initialDiagramUrl={diagramUrl}
                sessionId={sessionId}
                onDiagramUpdate={(url) => setDiagramUrl(url)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DiagramGenerator

