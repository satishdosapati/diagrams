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
    <div className="bg-white border rounded-lg p-2 h-full w-full flex flex-col">
      <h3 className="text-xs font-semibold text-gray-700 mb-1.5">
        Examples ({provider.toUpperCase()})
      </h3>
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-1">
          {examples.map(example => (
            <button
              key={example.id}
              onClick={() => handleUseExample(example)}
              className="w-full text-left px-1.5 py-1 text-xs bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded transition-all group"
              title={example.description}
            >
              <span className="text-gray-700 group-hover:text-blue-700 leading-tight line-clamp-2">
                {example.prompt}
              </span>
            </button>
          ))}
        </div>
        
        {examples.length === 0 && (
          <div className="text-center py-4 text-xs text-gray-500">
            No examples found
          </div>
        )}
      </div>
    </div>
  )
}

export default ExamplesPanel

