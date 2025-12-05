import { useState } from 'react'
import { submitFeedback } from '../services/api'

interface FeedbackWidgetProps {
  generationId: string
  sessionId: string
  code?: string
  onFeedbackSubmitted?: () => void
}

function FeedbackWidget({
  generationId,
  sessionId,
  code,
  onFeedbackSubmitted
}: FeedbackWidgetProps) {
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFeedback = async (thumbsUp: boolean) => {
    if (feedbackSubmitted) return

    setIsSubmitting(true)
    setError(null)

    try {
      // Calculate code hash if code provided
      // Note: Hash can be calculated on backend if crypto.subtle is not available
      let codeHash: string | undefined
      if (code) {
        try {
          // Check if crypto.subtle is available (requires HTTPS or localhost)
          if (window.crypto && window.crypto.subtle) {
            const encoder = new TextEncoder()
            const data = encoder.encode(code)
            const hashBuffer = await window.crypto.subtle.digest('SHA-256', data)
            const hashArray = Array.from(new Uint8Array(hashBuffer))
            codeHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
          } else {
            // Fallback: Backend will calculate hash if not provided
            // Or use a simple hash for non-critical use cases
            console.warn('crypto.subtle not available, backend will calculate hash')
          }
        } catch (hashError) {
          // If hash calculation fails, continue without hash
          // Backend can calculate it from the code
          console.warn('Failed to calculate hash:', hashError)
        }
      }

      await submitFeedback({
        generation_id: generationId,
        session_id: sessionId,
        thumbs_up: thumbsUp,
        code_hash: codeHash, // May be undefined if crypto.subtle unavailable
        code: code // Include code for pattern extraction (backend can hash it)
      })

      setFeedbackSubmitted(true)
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback')
      setIsSubmitting(false)
    }
  }

  if (feedbackSubmitted) {
    return (
      <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-md">
        <span className="text-green-600 text-sm">✓ Thank you for your feedback!</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-200 rounded-md">
      <span className="text-sm text-gray-700">Was this helpful?</span>
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleFeedback(true)}
          disabled={isSubmitting}
          className="p-2 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Thumbs up"
          aria-label="Thumbs up"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-green-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
            />
          </svg>
        </button>
        <button
          onClick={() => handleFeedback(false)}
          disabled={isSubmitting}
          className="p-2 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Thumbs down"
          aria-label="Thumbs down"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-red-600 rotate-180"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
            />
          </svg>
        </button>
      </div>
      {error && (
        <span className="text-xs text-red-600">{error}</span>
      )}
      {isSubmitting && (
        <span className="text-xs text-gray-500">Submitting...</span>
      )}
    </div>
  )
}

export default FeedbackWidget
