import { Example, getExamplesByProvider } from '../data/examples'

interface ExamplesPanelProps {
  provider: 'aws' | 'azure' | 'gcp'
  onSelectExample: (prompt: string) => void
}

function ExamplesPanel({ provider, onSelectExample }: ExamplesPanelProps) {
  const examples = getExamplesByProvider(provider)
  
  const handleUseExample = (example: Example) => {
    onSelectExample(example.prompt)
  }
  
  return (
    <div className="bg-white border-2 border-gray-200 rounded-xl p-4 overflow-y-auto shadow-sm" style={{ maxHeight: 'calc(100vh - 200px)' }}>
      <h3 className="text-sm font-bold text-gray-900 mb-3 sticky top-0 bg-white pb-2 z-10 tracking-tight">
        Examples ({provider.toUpperCase()})
      </h3>
      
      <div className="space-y-2">
        {examples.map(example => (
          <button
            key={example.id}
            onClick={() => handleUseExample(example)}
            className="w-full text-left px-3 py-2.5 text-xs bg-gray-50 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 border-2 border-gray-200 hover:border-blue-300 rounded-lg transition-all duration-200 group shadow-sm hover:shadow-md"
            title={example.description}
          >
            <span className="text-gray-700 group-hover:text-blue-800 leading-relaxed font-medium">
              {example.prompt}
            </span>
          </button>
        ))}
      </div>
      
      {examples.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">📋</div>
          <p className="text-xs text-gray-500 font-medium">No examples found</p>
        </div>
      )}
    </div>
  )
}

export default ExamplesPanel

