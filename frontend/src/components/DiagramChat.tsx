import { useState, useRef, useEffect } from 'react'
import { generateDiagram, getDiagramUrl } from '../services/api'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  diagramUrl?: string
  changes?: string[]
}

interface DiagramChatProps {
  initialDiagramUrl: string | null
  sessionId: string | null
  onDiagramUpdate: (diagramUrl: string) => void
}

async function modifyDiagram(sessionId: string, modification: string) {
  const response = await fetch('http://localhost:8000/api/modify-diagram', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, modification }),
  })
  if (!response.ok) throw new Error('Failed to modify diagram')
  return response.json()
}

async function undoDiagram(sessionId: string) {
  const response = await fetch('http://localhost:8000/api/undo-diagram', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  })
  if (!response.ok) throw new Error('Failed to undo')
  return response.json()
}

function DiagramChat({ initialDiagramUrl, sessionId, onDiagramUpdate }: DiagramChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentDiagramUrl, setCurrentDiagramUrl] = useState<string | null>(initialDiagramUrl)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (initialDiagramUrl && messages.length === 0) {
      setMessages([{
        id: '1',
        role: 'assistant',
        content: 'I\'ve generated your initial architecture diagram. How would you like to modify it?',
        timestamp: new Date(),
        diagramUrl: initialDiagramUrl,
      }])
      setCurrentDiagramUrl(initialDiagramUrl)
    }
  }, [initialDiagramUrl])

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isProcessing || !sessionId) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsProcessing(true)

    try {
      const data = await modifyDiagram(sessionId, input)
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || 'Diagram updated successfully',
        timestamp: new Date(),
        diagramUrl: getDiagramUrl(data.diagram_url.split('/').pop() || ''),
        changes: data.changes,
      }

      setMessages(prev => [...prev, assistantMessage])
      setCurrentDiagramUrl(assistantMessage.diagramUrl || null)
      if (assistantMessage.diagramUrl) {
        onDiagramUpdate(assistantMessage.diagramUrl)
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to modify diagram'}`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleUndo = async () => {
    if (!sessionId || messages.length <= 1) return

    setIsProcessing(true)
    try {
      const data = await undoDiagram(sessionId)
      setCurrentDiagramUrl(getDiagramUrl(data.diagram_url.split('/').pop() || ''))
      setMessages(prev => prev.slice(0, -1))
      if (data.diagram_url) {
        onDiagramUpdate(getDiagramUrl(data.diagram_url.split('/').pop() || ''))
      }
    } catch (error) {
      console.error('Undo failed:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  if (!sessionId) {
    return (
      <div className="p-4 text-center text-gray-500">
        Generate a diagram first to enable chat modifications
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-4 bg-gray-50">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">Current Diagram</h3>
          <button
            onClick={handleUndo}
            disabled={messages.length <= 1 || isProcessing}
            className="px-3 py-1 text-sm border rounded-md hover:bg-gray-100 disabled:bg-gray-200 disabled:cursor-not-allowed"
          >
            Undo
          </button>
        </div>
        {currentDiagramUrl && (
          <img
            src={currentDiagramUrl}
            alt="Current architecture diagram"
            className="w-full max-h-64 object-contain border rounded"
          />
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              
              {message.changes && message.changes.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  <p className="text-xs font-semibold mb-1">Changes:</p>
                  <ul className="text-xs space-y-1">
                    {message.changes.map((change, idx) => (
                      <li key={idx}>• {change}</li>
                    ))}
                  </ul>
                </div>
              )}

              {message.diagramUrl && message.role === 'assistant' && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  <img
                    src={message.diagramUrl}
                    alt="Updated diagram"
                    className="w-full max-h-32 object-contain rounded"
                  />
                </div>
              )}

              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Describe how to modify the diagram... (e.g., 'Add a CDN', 'Remove the database')"
            disabled={isProcessing}
            className="flex-1 px-3 py-2 border rounded-md"
          />
          <button
            onClick={handleSend}
            disabled={isProcessing || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default DiagramChat

