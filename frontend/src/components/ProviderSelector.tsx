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
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        Select Cloud Provider
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {PROVIDER_OPTIONS.map((provider) => {
          const isSelected = selectedProvider === provider.id

          return (
            <div
              key={provider.id}
              className={`
                relative flex items-start space-x-2 p-3 border rounded-lg
                cursor-pointer transition-all
                ${isSelected 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
              onClick={() => onSelectionChange(provider.id)}
            >
              <input
                type="radio"
                name="provider"
                value={provider.id}
                checked={isSelected}
                onChange={() => onSelectionChange(provider.id)}
                className="mt-1"
              />
              <div className="flex-1 min-w-0">
                <label className="text-sm font-medium text-gray-900 cursor-pointer">
                  {provider.label}
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  {provider.description}
                </p>
              </div>
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </div>
          )
        })}
      </div>
      {selectedProvider && (
        <div className="p-2 bg-gray-50 rounded-md">
          <p className="text-sm font-medium text-gray-700">
            Selected: {PROVIDER_OPTIONS.find(p => p.id === selectedProvider)?.label}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            All components will use {selectedProvider.toUpperCase()} icons only
          </p>
        </div>
      )}
    </div>
  )
}

export default ProviderSelector

