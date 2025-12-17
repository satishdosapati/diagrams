import { useState } from 'react'
import { rewritePrompt } from '../services/api'

interface PromptRewriterProps {
  description: string
  provider: string
  onRewrite: (rewritten: string) => void
  disabled?: boolean
}

export default function PromptRewriter({
  description,
  provider,
  onRewrite,
  disabled = false
}: PromptRewriterProps) {
  const [isRewriting, setIsRewriting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Only show icon when there's text
  if (!description.trim()) {
    return null
  }

  const handleRewrite = async () => {
    if (disabled || isRewriting || !description.trim()) {
      return
    }

    setIsRewriting(true)
    setError(null)

    try {
      const response = await rewritePrompt(description, provider)
      onRewrite(response.rewritten_description)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to rewrite prompt'
      setError(errorMessage)
      // Keep original text on error
    } finally {
      setIsRewriting(false)
    }
  }

  return (
    <div className="absolute bottom-2 right-2">
      <button
        onClick={handleRewrite}
        disabled={disabled || isRewriting}
        className={`
          p-1.5 rounded-md transition-all
          ${disabled || isRewriting
            ? 'opacity-50 cursor-not-allowed'
            : 'hover:bg-blue-50 cursor-pointer hover:text-blue-600'
          }
        `}
        title={error || (isRewriting ? 'Rewriting...' : 'Rewrite prompt with clustering hints')}
        type="button"
      >
        {isRewriting ? (
          <svg
            className="animate-spin h-5 w-5 text-blue-600"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        ) : (
          <svg
            className={`h-5 w-5 ${error ? 'text-red-500' : 'text-gray-400'}`}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
            />
          </svg>
        )}
      </button>
      {error && (
        <div className="absolute bottom-full right-0 mb-1 w-64 p-2 bg-red-50 border border-red-200 rounded-md shadow-lg z-10">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}
    </div>
  )
}

