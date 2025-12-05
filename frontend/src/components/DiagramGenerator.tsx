import { useState } from 'react'
import { generateDiagram, getDiagramUrl, regenerateFormat } from '../services/api'
import ProviderSelector from './ProviderSelector'
import ExamplesPanel from './ExamplesPanel'
import AdvancedCodeMode from './AdvancedCodeMode'
import { useToast } from '../hooks/useToast'
import { DiagramLoadingSkeleton } from './LoadingSkeleton'

type Provider = 'aws' | 'azure' | 'gcp'
type Mode = 'natural-language' | 'advanced-code'
type OutputFormat = 'png' | 'svg' | 'pdf' | 'dot'

interface DiagramGeneratorProps {
  toast?: ReturnType<typeof useToast>
}

function DiagramGenerator({ toast: toastProp }: DiagramGeneratorProps) {
  const defaultToast = useToast()
  const toast = toastProp || defaultToast
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
  const [showExamples, setShowExamples] = useState(true)

  const handleGenerate = async () => {
    if (mode === 'advanced-code') {
      // Advanced code mode handles its own generation
      return
    }

    if (!description.trim()) {
      toast.error('Please enter an architecture description')
      return
    }

    setIsGenerating(true)
    setDiagramUrl(null)

    try {
      const response = await generateDiagram(description, selectedProvider, outputFormat)
      toast.success(response.message || 'Diagram generated successfully!')
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
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to generate diagram')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleExampleSelect = (prompt: string) => {
    setDescription(prompt)
  }

  const handleDiagramGenerated = (url: string) => {
    setDiagramUrl(url)
  }

  const handleFormatChange = async (newFormat: OutputFormat) => {
    if (!sessionId || !diagramUrl) return
    
    setDownloadFormat(newFormat)
    setIsRegenerating(true)
    
    try {
      const response = await regenerateFormat(sessionId, newFormat)
      toast.success(`Diagram converted to ${newFormat.toUpperCase()} format`)
      const filename = response.diagram_url.split('/').pop()
      if (filename) {
        const url = getDiagramUrl(filename)
        setDiagramUrl(url)
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to regenerate format')
    } finally {
      setIsRegenerating(false)
    }
  }

  return (
    <div className="bg-white shadow-lg rounded-xl p-6 border border-gray-200/50 hover:shadow-xl transition-shadow duration-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Generate Architecture Diagram</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowExamples(!showExamples)}
            className="px-4 py-2 text-sm border-2 border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 font-medium transition-all duration-200"
          >
            {showExamples ? 'Hide' : 'Show'} Examples
          </button>
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="mb-6">
        <div className="flex border-2 border-gray-200 rounded-xl p-1 bg-gray-50/50">
          <button
            onClick={() => setMode('natural-language')}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
              mode === 'natural-language'
                ? 'bg-white text-blue-600 shadow-md scale-[1.02]'
                : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
            }`}
          >
            Natural Language
          </button>
          <button
            onClick={() => setMode('advanced-code')}
            className={`flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
              mode === 'advanced-code'
                ? 'bg-white text-blue-600 shadow-md scale-[1.02]'
                : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
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
            <label htmlFor="outputFormat" className="block text-sm font-semibold text-gray-700 mb-2">
              Output Format
            </label>
            <select
              id="outputFormat"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value as OutputFormat)}
              className="w-full px-4 py-2.5 border-2 border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white font-medium transition-all duration-200 hover:border-gray-400"
              disabled={isGenerating}
            >
              <option value="png">PNG (Image)</option>
              <option value="svg">SVG (Editable Vector)</option>
              <option value="pdf">PDF (Document)</option>
              <option value="dot">DOT (Source Code)</option>
            </select>
            <p className="mt-2 text-xs text-gray-600">
              {outputFormat === 'svg' && 'SVG can be edited in Draw.io, Figma, or Inkscape'}
              {outputFormat === 'dot' && 'DOT is the Graphviz source code - edit and regenerate'}
              {outputFormat === 'pdf' && 'PDF format for documents and presentations'}
              {outputFormat === 'png' && 'Raster image format'}
            </p>
          </div>

          {/* Natural Language Mode */}
          {mode === 'natural-language' && (
            <>
              <div>
                <label htmlFor="description" className="block text-sm font-semibold text-gray-700 mb-2">
                  Describe your {selectedProvider.toUpperCase()} architecture
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g., Create a serverless API with API Gateway, Lambda, and DynamoDB"
                  rows={4}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 hover:border-gray-400 font-medium"
                  disabled={isGenerating}
                />
                <p className="mt-2 text-sm text-gray-600">
                  Describe the {selectedProvider.toUpperCase()} architecture you want to visualize
                </p>
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !description.trim()}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg shadow-lg hover:shadow-xl hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed disabled:shadow-none font-semibold transition-all duration-200 transform hover:scale-[1.02] disabled:transform-none"
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </span>
                ) : (
                  'Generate Diagram'
                )}
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

          {isGenerating && !diagramUrl && (
            <div className="mt-6">
              <DiagramLoadingSkeleton />
            </div>
          )}

          {diagramUrl && (
            <div className="mt-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 tracking-tight">Generated Diagram</h3>
              <div className="border-2 border-gray-200 rounded-xl p-4 bg-gray-50/50 shadow-sm">
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
                  </select>
                  {isRegenerating && (
                    <span className="text-sm text-gray-500">Regenerating...</span>
                  )}
                </div>
                <div className="flex gap-3">
                  <a
                    href={diagramUrl}
                    download
                    className="px-5 py-2.5 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg hover:from-gray-700 hover:to-gray-800 shadow-md hover:shadow-lg font-semibold transition-all duration-200 transform hover:scale-[1.02]"
                  >
                    Download {downloadFormat.toUpperCase()}
                  </a>
                  {downloadFormat === 'svg' && (
                    <a
                      href="https://app.diagrams.net/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 shadow-md hover:shadow-lg font-semibold transition-all duration-200 transform hover:scale-[1.02]"
                    >
                      Open in Draw.io
                    </a>
                  )}
                  {downloadFormat === 'dot' && (
                    <a
                      href="https://edotor.net/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 shadow-md hover:shadow-lg font-semibold transition-all duration-200 transform hover:scale-[1.02]"
                    >
                      Open in Edotor
                    </a>
                  )}
                </div>
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

