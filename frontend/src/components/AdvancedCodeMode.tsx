import { useState, useEffect, useRef } from 'react'
import Editor from '@monaco-editor/react'
import { executeCode, getCompletions, validateCode, getDiagramUrl } from '../services/api'

interface AdvancedCodeModeProps {
  provider: 'aws' | 'azure' | 'gcp'
  initialCode?: string
  onDiagramGenerated: (diagramUrl: string) => void
}

function AdvancedCodeMode({ provider, initialCode, onDiagramGenerated }: AdvancedCodeModeProps) {
  const [code, setCode] = useState(initialCode || getDefaultCode(provider))
  const [diagramUrl, setDiagramUrl] = useState<string | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [errors, setErrors] = useState<string[]>([])
  const [warnings, setWarnings] = useState<string[]>([])
  const [completions, setCompletions] = useState<any>(null)
  const editorRef = useRef<any>(null)

  // Load completions on mount
  useEffect(() => {
    loadCompletions()
  }, [provider])

  const loadCompletions = async () => {
    try {
      const data = await getCompletions(provider)
      setCompletions(data)
    } catch (error) {
      console.error('Failed to load completions:', error)
    }
  }

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor
    
    // Configure Monaco for Python
    monaco.languages.setLanguageConfiguration('python', {
      comments: {
        lineComment: '#',
        blockComment: ['"""', '"""']
      },
      brackets: [
        ['{', '}'],
        ['[', ']'],
        ['(', ')']
      ],
      autoClosingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' },
        { open: "'", close: "'" }
      ]
    })

    // Register custom completion provider
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions: any[] = []
        const textUntilPosition = model.getValueInRange({
          startLineNumber: 1,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column
        })

        // Import statement completions
        if (textUntilPosition.includes('from diagrams.') && textUntilPosition.endsWith('import ')) {
          const moduleMatch = textUntilPosition.match(/from diagrams\.(\w+)\.(\w+) import $/)
          if (moduleMatch && completions) {
            const category = moduleMatch[2]
            const classes = completions.classes[category] || []
            classes.forEach((className: string) => {
              suggestions.push({
                label: className,
                kind: monaco.languages.CompletionItemKind.Class,
                insertText: className,
                detail: `from diagrams.${provider}.${category} import ${className}`,
                documentation: completions.imports[className] || ''
              })
            })
          }
        }

        // Class instantiation completions
        if (textUntilPosition.match(/\w+\s*=\s*$/)) {
          if (completions) {
            Object.keys(completions.imports).forEach((className) => {
              suggestions.push({
                label: className,
                kind: monaco.languages.CompletionItemKind.Class,
                insertText: `${className}("Label")`,
                detail: completions.imports[className],
                documentation: `Instantiate ${className} component`
              })
            })
          }
        }

        // Operator completions
        if (textUntilPosition.match(/\w+\s*$/)) {
          completions?.operators.forEach((op: string) => {
            suggestions.push({
              label: op,
              kind: monaco.languages.CompletionItemKind.Operator,
              insertText: op,
              detail: `Connection operator: ${op === '>>' ? 'Forward flow' : op === '<<' ? 'Reverse flow' : 'Bidirectional'}`
            })
          })
        }

        return { suggestions }
      }
    })
  }

  const handleExecute = async () => {
    setIsExecuting(true)
    setErrors([])
    setWarnings([])

    try {
      // Validate code first
      const validation = await validateCode(code)
      
      if (!validation.valid && validation.errors.length > 0) {
        setErrors(validation.errors)
        setWarnings(validation.suggestions)
        setIsExecuting(false)
        return
      }

      // Execute code
      const result = await executeCode({
        code,
        provider,
        title: 'Diagram',
        outformat: 'png'
      })

      if (result.errors && result.errors.length > 0) {
        setErrors(result.errors)
      } else {
        const url = getDiagramUrl(result.diagram_url.split('/').pop() || '')
        setDiagramUrl(url)
        onDiagramGenerated(url)
      }

      if (result.warnings && result.warnings.length > 0) {
        setWarnings(result.warnings)
      }
    } catch (error) {
      setErrors([error instanceof Error ? error.message : 'Failed to execute code'])
    } finally {
      setIsExecuting(false)
    }
  }

  const handleFormat = () => {
    // Basic formatting - indent with 4 spaces
    const lines = code.split('\n')
    let indentLevel = 0
    const formatted = lines.map(line => {
      const trimmed = line.trim()
      if (trimmed.endsWith(':')) {
        const result = '    '.repeat(indentLevel) + trimmed
        indentLevel++
        return result
      }
      if (trimmed && !trimmed.startsWith('#')) {
        if (trimmed.startsWith('with ')) {
          const result = '    '.repeat(indentLevel) + trimmed
          indentLevel++
          return result
        }
      }
      if (trimmed === '' && indentLevel > 0) {
        indentLevel--
      }
      return '    '.repeat(Math.max(0, indentLevel - (trimmed.startsWith('except') || trimmed.startsWith('else') || trimmed.startsWith('elif') ? 1 : 0))) + trimmed
    })
    setCode(formatted.join('\n'))
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Advanced Code Mode</h3>
        <div className="flex gap-2">
          <button
            onClick={handleFormat}
            className="px-3 py-1 text-sm border rounded-md hover:bg-gray-50"
          >
            Format Code
          </button>
          <button
            onClick={handleExecute}
            disabled={isExecuting || !code.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isExecuting ? 'Executing...' : 'Generate Diagram'}
          </button>
        </div>
      </div>

      {/* Code Editor */}
      <div className="border rounded-lg overflow-hidden" style={{ height: '500px' }}>
        <Editor
          height="100%"
          defaultLanguage="python"
          value={code}
          onChange={(value) => setCode(value || '')}
          onMount={handleEditorDidMount}
          theme="vs-light"
          options={{
            minimap: { enabled: true },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: 'on'
          }}
        />
      </div>

      {/* Errors and Warnings */}
      {errors.length > 0 && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <h4 className="font-semibold text-red-800 mb-2">Errors:</h4>
          <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
            {errors.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <h4 className="font-semibold text-yellow-800 mb-2">Suggestions:</h4>
          <ul className="list-disc list-inside text-sm text-yellow-600 space-y-1">
            {warnings.map((warning, idx) => (
              <li key={idx}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Diagram Preview */}
      {diagramUrl && (
        <div className="mt-4">
          <h4 className="font-semibold mb-2">Generated Diagram:</h4>
          <div className="border rounded-lg p-4 bg-gray-50">
            <img
              src={diagramUrl}
              alt="Generated diagram"
              className="w-full max-w-4xl mx-auto"
            />
          </div>
        </div>
      )}
    </div>
  )
}

function getDefaultCode(provider: string): string {
  const baseImports = {
    aws: `from diagrams import Diagram
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.network import APIGateway, ALB`,
    azure: `from diagrams import Diagram
from diagrams.azure.compute import Function, VM
from diagrams.azure.database import CosmosDb
from diagrams.azure.storage import BlobStorage`,
    gcp: `from diagrams import Diagram
from diagrams.gcp.compute import CloudFunctions, ComputeEngine
from diagrams.gcp.database import Firestore
from diagrams.gcp.storage import GCS`
  }

  return `${baseImports[provider as keyof typeof baseImports] || baseImports.aws}

with Diagram("My Architecture", show=False, direction="TB"):
    # Add your components here
    # Example:
    # api = APIGateway("API")
    # func = Lambda("Function")
    # db = Dynamodb("Database")
    # api >> func >> db
`
}

export default AdvancedCodeMode

