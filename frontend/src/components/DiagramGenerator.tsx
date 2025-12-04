import { useState } from 'react'
import { generateDiagram, getDiagramUrl, regenerateFormat } from '../services/api'
import ProviderSelector from './ProviderSelector'
import DiagramChat from './DiagramChat'
import ExamplesPanel from './ExamplesPanel'
import AdvancedCodeMode from './AdvancedCodeMode'

type Provider = 'aws' | 'azure' | 'gcp'
type Mode = 'natural-language' | 'advanced-code'
type OutputFormat = 'png' | 'svg' | 'pdf' | 'dot' | 'jpg'

function DiagramGenerator() {
  const [mode, setMode] = useState<Mode>('natural-language')
  const [description, setDescription] = useState('')
  const [selectedProvider, setSelectedProvider] = useState<Provider>('aws')
  const [outputFormat, setOutputFormat] = useState<OutputFormat>('png')
  const [diagramUrl, setDiagramUrl] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [generatedCode, setGeneratedCode] = useState<string | null>(null)
  const [downloadFormat, setDownloadFormat] = useState<OutputFormat>('png')
  const [isGenerating, setIsGenerating] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
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
      const response = await generateDiagram(description, selectedProvider, outputFormat)
      setMessage(response.message)
      setSessionId(response.session_id)
      
      // Store generated code for Advanced Code Mode
      if (response.generated_code) {
        setGeneratedCode(response.generated_code)
      }
      
      // Set download format to match generation format
      setDownloadFormat(outputFormat)
      
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
  }

  const handleDiagramGenerated = (url: string) => {
    setDiagramUrl(url)
    setShowChat(true)
  }

  const handleFormatChange = async (newFormat: OutputFormat) => {
    if (!sessionId || !diagramUrl) return
    
    setDownloadFormat(newFormat)
    setIsRegenerating(true)
    
    try {
      const response = await regenerateFormat(sessionId, newFormat)
      const filename = response.diagram_url.split('/').pop()
      if (filename) {
        const url = getDiagramUrl(filename)
        setDiagramUrl(url)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to regenerate format')
    } finally {
      setIsRegenerating(false)
    }
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
      
      {/* Main Content with Sidebar */}
      <div className="flex gap-4">
        {/* Main Content Area */}
        <div className="flex-1 space-y-4">
          <ProviderSelector
            selectedProvider={selectedProvider}
            onSelectionChange={setSelectedProvider}
          />

          {/* Output Format Selector */}
          <div>
            <label htmlFor="outputFormat" className="block text-sm font-medium text-gray-700 mb-2">
              Output Format
            </label>
            <select
              id="outputFormat"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value as OutputFormat)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white"
              disabled={isGenerating}
            >
              <option value="png">PNG (Image)</option>
              <option value="svg">SVG (Editable Vector)</option>
              <option value="pdf">PDF (Document)</option>
              <option value="dot">DOT (Source Code)</option>
              <option value="jpg">JPG (Image)</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">
              {outputFormat === 'svg' && 'SVG can be edited in Draw.io, Figma, or Inkscape'}
              {outputFormat === 'dot' && 'DOT is the Graphviz source code - edit and regenerate'}
              {outputFormat === 'pdf' && 'PDF format for documents and presentations'}
              {(outputFormat === 'png' || outputFormat === 'jpg') && 'Raster image format'}
            </p>
          </div>

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
              initialCode={generatedCode || undefined}
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
                {downloadFormat === 'dot' ? (
                  <div className="w-full max-w-4xl mx-auto">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-sm text-blue-800 mb-2">
                        <strong>DOT Format:</strong> Download the file to view/edit the Graphviz source code.
                      </p>
                      <p className="text-xs text-blue-600">
                        You can edit DOT files in text editors or use online tools like <a href="https://edotor.net/" target="_blank" rel="noopener noreferrer" className="underline">Edotor</a> or <a href="https://dreampuf.github.io/GraphvizOnline/" target="_blank" rel="noopener noreferrer" className="underline">Graphviz Online</a>.
                      </p>
                    </div>
                  </div>
                ) : (
                  <img
                    src={diagramUrl}
                    alt="Generated architecture diagram"
                    className="w-full max-w-4xl mx-auto"
                  />
                )}
              </div>
              <div className="mt-4 space-y-3">
                <div className="flex items-center gap-3">
                  <label htmlFor="downloadFormat" className="text-sm font-medium text-gray-700">
                    Download as:
                  </label>
                  <select
                    id="downloadFormat"
                    value={downloadFormat}
                    onChange={(e) => handleFormatChange(e.target.value as OutputFormat)}
                    disabled={isRegenerating}
                    className="px-3 py-1.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
                  >
                    <option value="png">PNG</option>
                    <option value="svg">SVG</option>
                    <option value="pdf">PDF</option>
                    <option value="dot">DOT</option>
                    <option value="jpg">JPG</option>
                  </select>
                  {isRegenerating && (
                    <span className="text-sm text-gray-500">Regenerating...</span>
                  )}
                </div>
                <div className="flex gap-2">
                  <a
                    href={diagramUrl}
                    download
                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    Download {downloadFormat.toUpperCase()}
                  </a>
                  {downloadFormat === 'svg' && (
                    <a
                      href="https://app.diagrams.net/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Open in Draw.io
                    </a>
                  )}
                  {downloadFormat === 'dot' && (
                    <a
                      href="https://edotor.net/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Open in Edotor
                    </a>
                  )}
                </div>
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

        {/* Examples Sidebar - Small */}
        {showExamples && mode === 'natural-language' && (
          <div className="w-64 flex-shrink-0">
            <ExamplesPanel
              provider={selectedProvider}
              onSelectExample={handleExampleSelect}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default DiagramGenerator

