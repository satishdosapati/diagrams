import { useState } from 'react'
import { generateDiagram, getDiagramUrl, regenerateFormat } from '../services/api'
import ProviderSelector from './ProviderSelector'
import ExamplesPanel from './ExamplesPanel'
import AdvancedCodeMode from './AdvancedCodeMode'
import FeedbackWidget from './FeedbackWidget'
import ProgressBar from './ProgressBar'
import { ErrorDisplay } from './ErrorDisplay'

type Provider = 'aws' | 'azure' | 'gcp'
type Mode = 'natural-language' | 'advanced-code'
type OutputFormat = 'png' | 'svg' | 'pdf' | 'dot'

function DiagramGenerator() {
  const [mode, setMode] = useState<Mode>('natural-language')
  const [description, setDescription] = useState('')
  const [selectedProvider, setSelectedProvider] = useState<Provider>('aws')
  const [outputFormat, setOutputFormat] = useState<OutputFormat>('png')
  const [diagramUrl, setDiagramUrl] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [generationId, setGenerationId] = useState<string | null>(null)
  const [generatedCode, setGeneratedCode] = useState<string | null>(null)
  const [downloadFormat, setDownloadFormat] = useState<OutputFormat>('png')
  const [isGenerating, setIsGenerating] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorContext, setErrorContext] = useState<{
    requestId: string | null;
    prompt: string | null;
    provider: string | null;
    errorType: 'generation' | 'execution' | 'validation' | 'other';
    showReportButton?: boolean;
  } | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [showExamples, setShowExamples] = useState(true)
  const [showUrgencyBanner, setShowUrgencyBanner] = useState(true)
  const [showSuccessMetrics, setShowSuccessMetrics] = useState(true)

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
    setErrorContext(null)
    setMessage(null)
    setDiagramUrl(null)

    try {
      const response = await generateDiagram(description, selectedProvider, outputFormat)
      setMessage(response.message)
      setSessionId(response.session_id)
      setGenerationId(response.generation_id)
      
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
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate diagram'
      const requestId = (err as any).requestId || null
      
      setError(errorMessage)
      
      // Set errorContext for all errors - show report button for all errors
      setErrorContext({
        requestId,
        prompt: description,
        provider: selectedProvider,
        errorType: 'generation',
        showReportButton: true
      })
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
    setError(null)
    setErrorContext(null)
    
    try {
      const response = await regenerateFormat(sessionId, newFormat)
      const filename = response.diagram_url.split('/').pop()
      if (filename) {
        const url = getDiagramUrl(filename)
        setDiagramUrl(url)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to regenerate format'
      const requestId = (err as any).requestId || null
      
      setError(errorMessage)
      
      // Set errorContext for all errors - show report button for all errors
      setErrorContext({
        requestId,
        prompt: description,
        provider: selectedProvider,
        errorType: 'generation',
        showReportButton: true
      })
    } finally {
      setIsRegenerating(false)
    }
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      {/* StoryBrand: Problem Statement */}
      <div className="mb-4 p-3 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg">
        <p className="text-sm text-gray-700 mb-1.5">
          <span className="font-semibold">Tired of spending hours manually creating architecture diagrams?</span> 
          <span className="text-gray-600"> Struggling to visualize your cloud infrastructure?</span>
        </p>
        <p className="text-sm text-gray-600">
          Our AI-powered generator understands your natural language and creates professional diagrams in seconds.
        </p>
      </div>

      {/* StoryBrand: Urgency/Failure (Subtle) */}
      {showUrgencyBanner && !diagramUrl && mode === 'natural-language' && (
        <div className="mb-3 p-2 bg-amber-50 border border-amber-200 rounded-lg flex items-start justify-between">
          <div className="flex-1">
            <p className="text-xs text-amber-800">
              <span className="font-medium">Without clear diagrams,</span> your team wastes time explaining architecture instead of building features.
            </p>
          </div>
          <button
            onClick={() => setShowUrgencyBanner(false)}
            className="ml-3 text-amber-600 hover:text-amber-800 flex-shrink-0"
            aria-label="Dismiss"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* StoryBrand: 3-Step Process */}
      {mode === 'natural-language' && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <div className={`flex-1 flex items-center transition-all duration-300 ${isGenerating ? 'opacity-50' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300 ${
                description.trim() ? 'bg-blue-600 text-white shadow-md scale-110' : 'bg-gray-200 text-gray-600'
              }`}>
                {description.trim() && !isGenerating && !diagramUrl ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  '1'
                )}
              </div>
              <span className={`ml-2 text-sm transition-colors duration-300 ${
                description.trim() ? 'text-gray-900 font-medium' : 'text-gray-700'
              }`}>Describe</span>
            </div>
            <div className={`flex-1 h-0.5 mx-2 transition-colors duration-300 ${
              description.trim() ? 'bg-blue-300' : 'bg-gray-200'
            }`}></div>
            <div className={`flex-1 flex items-center transition-all duration-300 ${isGenerating ? '' : 'opacity-50'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300 ${
                isGenerating ? 'bg-blue-600 text-white shadow-md animate-pulse scale-110' : diagramUrl ? 'bg-green-600 text-white shadow-md scale-110' : 'bg-gray-200 text-gray-600'
              }`}>
                {diagramUrl ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  '2'
                )}
              </div>
              <span className={`ml-2 text-sm transition-colors duration-300 ${
                (isGenerating || diagramUrl) ? 'text-gray-900 font-medium' : 'text-gray-700'
              }`}>Generate</span>
            </div>
            <div className={`flex-1 h-0.5 mx-2 transition-colors duration-300 ${
              (isGenerating || diagramUrl) ? 'bg-blue-300' : 'bg-gray-200'
            }`}></div>
            <div className={`flex-1 flex items-center transition-all duration-300 ${diagramUrl ? '' : 'opacity-50'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300 ${
                diagramUrl ? 'bg-green-600 text-white shadow-md scale-110' : 'bg-gray-200 text-gray-600'
              }`}>
                {diagramUrl ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  '3'
                )}
              </div>
              <span className={`ml-2 text-sm transition-colors duration-300 ${
                diagramUrl ? 'text-gray-900 font-medium' : 'text-gray-700'
              }`}>Download</span>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Generate Architecture Diagram</h2>
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
      <div className="mb-3">
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
        <div className="flex-1 space-y-3">
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
            </select>
            <p className="mt-1 text-xs text-gray-500">
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
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Describe your {selectedProvider.toUpperCase()} architecture
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g., Create a serverless API with API Gateway, Lambda, and DynamoDB"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  disabled={isGenerating}
                />
                <p className="mt-1 text-xs text-gray-500">
                  Describe the {selectedProvider.toUpperCase()} architecture you want to visualize
                </p>
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !description.trim()}
                className="w-full bg-blue-600 text-white py-2.5 px-6 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Generate My Diagram
                  </>
                )}
              </button>
              
              {isGenerating && (
                <ProgressBar isActive={isGenerating} />
              )}
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
            <ErrorDisplay
              error={error}
              requestId={errorContext?.requestId || null}
              prompt={errorContext?.prompt || description}
              provider={errorContext?.provider || selectedProvider}
              errorType={errorContext?.errorType || 'generation'}
              showReportButton={errorContext?.showReportButton !== false}
            />
          )}

          {message && (
            <div className="p-3 bg-green-50 border-l-4 border-green-500 rounded-r-lg animate-fade-in">
              <div className="flex items-start gap-2">
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-green-600 animate-checkmark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-green-800 mb-0.5">Diagram generated successfully!</p>
                      <p className="text-sm text-green-700">{message}</p>
                      <p className="text-xs text-green-600 mt-0.5">Ready to share with your team.</p>
                      
                      {/* Success Metrics */}
                      {showSuccessMetrics && (
                        <div className="mt-2 pt-2 border-t border-green-200">
                          <div className="grid grid-cols-3 gap-2 text-center">
                            <div>
                              <p className="text-lg font-bold text-green-800">2+ hrs</p>
                              <p className="text-xs text-green-600">Time saved</p>
                            </div>
                            <div>
                              <p className="text-lg font-bold text-green-800">100%</p>
                              <p className="text-xs text-green-600">AI-powered</p>
                            </div>
                            <div>
                              <p className="text-lg font-bold text-green-800">Instant</p>
                              <p className="text-xs text-green-600">Generation</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    {showSuccessMetrics && (
                      <button
                        onClick={() => setShowSuccessMetrics(false)}
                        className="ml-3 text-green-600 hover:text-green-800 flex-shrink-0"
                        aria-label="Dismiss metrics"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {diagramUrl && (
            <div className="mt-4 animate-fade-in">
              {/* Success Celebration Banner */}
              <div className="mb-3 p-2 bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg flex items-center gap-2">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center animate-checkmark">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">Your diagram is ready!</p>
                  <p className="text-xs text-gray-600">Download, refine, or create another one.</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-semibold">Generated Diagram</h3>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setMode('advanced-code')
                    }}
                    className="px-4 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors flex items-center gap-2"
                    title="Refine this diagram using code editor"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Refine Diagram
                  </button>
                  <button
                    onClick={() => {
                      setDescription('')
                      setDiagramUrl(null)
                      setMessage(null)
                      setError(null)
                      setErrorContext(null)
                      setSessionId(null)
                      setGenerationId(null)
                      setGeneratedCode(null)
                    }}
                    className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Create Another
                  </button>
                </div>
              </div>
              <div className="border rounded-lg p-3 bg-gray-50 animate-slide-up">
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
                ) : downloadFormat === 'svg' ? (
                  <div className="w-full max-w-4xl mx-auto">
                    <object
                      data={diagramUrl}
                      type="image/svg+xml"
                      className="w-full"
                      aria-label="Generated architecture diagram"
                    >
                      <img
                        src={diagramUrl}
                        alt="Generated architecture diagram"
                        className="w-full max-w-4xl mx-auto"
                        onError={(e) => {
                          // Fallback: if object fails, try img directly
                          const target = e.target as HTMLImageElement;
                          if (target.src !== diagramUrl) {
                            target.src = diagramUrl || '';
                          }
                        }}
                      />
                    </object>
                  </div>
                ) : (
                  <img
                    src={diagramUrl}
                    alt="Generated architecture diagram"
                    className="w-full max-w-4xl mx-auto"
                  />
                )}
              </div>
              <div className="mt-3 space-y-2">
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
                {/* Feedback Widget */}
                {generationId && sessionId && (
                  <div className="mt-4">
                    <FeedbackWidget
                      generationId={generationId}
                      sessionId={sessionId}
                      code={generatedCode || undefined}
                    />
                  </div>
                )}
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

