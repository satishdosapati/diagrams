type Provider = 'aws' | 'azure' | 'gcp'

interface ProviderOption {
  id: Provider
  label: string
  description: string
}

const PROVIDER_OPTIONS: ProviderOption[] = [
  {
    id: 'aws',
    label: 'AWS',
    description: 'Amazon Web Services',
  },
  {
    id: 'azure',
    label: 'Microsoft Azure',
    description: 'Microsoft Azure Cloud',
  },
  {
    id: 'gcp',
    label: 'Google Cloud Platform',
    description: 'Google Cloud Platform',
  },
]

interface ProviderSelectorProps {
  selectedProvider: Provider
  onSelectionChange: (provider: Provider) => void
}

export function ProviderSelector({
  selectedProvider,
  onSelectionChange,
}: ProviderSelectorProps) {
  const getProviderColor = (providerId: Provider) => {
    switch (providerId) {
      case 'aws':
        return 'from-orange-500 to-orange-600'
      case 'azure':
        return 'from-blue-500 to-blue-600'
      case 'gcp':
        return 'from-green-500 to-green-600'
      default:
        return 'from-gray-500 to-gray-600'
    }
  }

  return (
    <div className="space-y-4">
      <label className="block text-sm font-semibold text-gray-700 mb-3">
        Select Cloud Provider
      </label>
      <div className="grid grid-cols-3 gap-4">
        {PROVIDER_OPTIONS.map((provider) => {
          const isSelected = selectedProvider === provider.id

          return (
            <div
              key={provider.id}
              className={`
                relative flex flex-col items-center justify-center p-5 border-2 rounded-xl
                cursor-pointer transition-all duration-200
                ${isSelected 
                  ? `border-blue-500 bg-gradient-to-br ${getProviderColor(provider.id)}/10 shadow-lg scale-[1.02]` 
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-md bg-white'
                }
              `}
              onClick={() => onSelectionChange(provider.id)}
            >
              <div className="flex items-center justify-center w-12 h-12 mb-3 rounded-lg bg-white shadow-sm">
                <span className={`text-2xl font-bold ${isSelected ? 'text-blue-600' : 'text-gray-400'}`}>
                  {provider.id === 'aws' ? '☁️' : provider.id === 'azure' ? '🔷' : '🔵'}
                </span>
              </div>
              <div className="text-center">
                <label className="text-sm font-bold text-gray-900 cursor-pointer block">
                  {provider.label}
                </label>
                <p className="text-xs text-gray-600 mt-1">
                  {provider.description}
                </p>
              </div>
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center shadow-md">
                    <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
      {selectedProvider && (
        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg shadow-sm">
          <p className="text-sm font-semibold text-gray-800">
            Selected: {PROVIDER_OPTIONS.find(p => p.id === selectedProvider)?.label}
          </p>
          <p className="text-xs text-gray-600 mt-1">
            All components will use {selectedProvider.toUpperCase()} icons only
          </p>
        </div>
      )}
    </div>
  )
}

export default ProviderSelector

