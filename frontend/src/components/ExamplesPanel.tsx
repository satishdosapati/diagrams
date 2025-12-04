import { useState } from 'react'
import { Example, getExamplesByProvider } from '../data/examples'

interface ExamplesPanelProps {
  provider: 'aws' | 'azure' | 'gcp'
  onSelectExample: (prompt: string) => void
}

function ExamplesPanel({ provider, onSelectExample }: ExamplesPanelProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [expandedExample, setExpandedExample] = useState<string | null>(null)
  
  const examples = getExamplesByProvider(provider)
  const categories = Array.from(new Set(examples.map(ex => ex.category)))
  
  const filteredExamples = selectedCategory
    ? examples.filter(ex => ex.category === selectedCategory)
    : examples
  
  const handleUseExample = (example: Example) => {
    onSelectExample(example.prompt)
  }
  
  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">📚 Examples & Templates</h3>
        <button
          onClick={() => setSelectedCategory(null)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Show All
        </button>
      </div>
      
      {/* Category Filters */}
      <div className="flex flex-wrap gap-2 mb-4">
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category === selectedCategory ? null : category)}
            className={`px-3 py-1 text-sm rounded-md ${
              selectedCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </button>
        ))}
      </div>
      
      {/* Examples Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredExamples.map(example => (
          <div
            key={example.id}
            className="border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{example.title}</h4>
                <p className="text-sm text-gray-600 mt-1">{example.description}</p>
              </div>
              <span className={`px-2 py-1 text-xs rounded ${
                example.complexity === 'simple' ? 'bg-green-100 text-green-800' :
                example.complexity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {example.complexity}
              </span>
            </div>
            
            {/* Tags */}
            <div className="flex flex-wrap gap-1 mb-3">
              {example.tags.slice(0, 4).map(tag => (
                <span
                  key={tag}
                  className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
            
            {/* Code Preview Toggle */}
            <div className="mb-3">
              <button
                onClick={() => setExpandedExample(expandedExample === example.id ? null : example.id)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                {expandedExample === example.id ? 'Hide' : 'Show'} Code
              </button>
            </div>
            
            {/* Code Snippet */}
            {expandedExample === example.id && (
              <div className="mb-3 bg-gray-900 rounded p-3 overflow-x-auto">
                <pre className="text-xs text-gray-100">
                  <code>{example.codeSnippet}</code>
                </pre>
              </div>
            )}
            
            {/* Recommended Variations */}
            {example.recommendedVariations && example.recommendedVariations.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-semibold text-gray-700 mb-1">💡 Variations:</p>
                <ul className="text-xs text-gray-600 space-y-1">
                  {example.recommendedVariations.slice(0, 2).map((variation, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="mr-1">•</span>
                      <span>{variation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Use Example Button */}
            <button
              onClick={() => handleUseExample(example)}
              className="w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Use This Example
            </button>
          </div>
        ))}
      </div>
      
      {filteredExamples.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No examples found for this category.
        </div>
      )}
    </div>
  )
}

export default ExamplesPanel

