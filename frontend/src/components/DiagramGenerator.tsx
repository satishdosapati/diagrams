import { useState } from 'react'
import { generateDiagram, getDiagramUrl } from '../services/api'
import ProviderSelector from './ProviderSelector'
import DiagramChat from './DiagramChat'

type Provider = 'aws' | 'azure' | 'gcp'

function DiagramGenerator() {
  const [description, setDescription] = useState('')
  const [selectedProvider, setSelectedProvider] = useState<Provider>('aws')
  const [diagramUrl, setDiagramUrl] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [showChat, setShowChat] = useState(false)

  const handleGenerate = async () => {
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

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Generate Architecture Diagram</h2>
      
      <div className="space-y-4">
        <ProviderSelector
          selectedProvider={selectedProvider}
          onSelectionChange={setSelectedProvider}
        />
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Describe your AWS architecture
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
            Describe the AWS architecture you want to visualize
          </p>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || !description.trim()}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isGenerating ? 'Generating...' : 'Generate Diagram'}
        </button>

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

