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
      let codeHash: string | undefined
      if (code) {
        // Simple hash calculation (in production, use crypto.subtle)
        const encoder = new TextEncoder()
        const data = encoder.encode(code)
        const hashBuffer = await crypto.subtle.digest('SHA-256', data)
        const hashArray = Array.from(new Uint8Array(hashBuffer))
        codeHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
      }

      await submitFeedback({
        generation_id: generationId,
        session_id: sessionId,
        thumbs_up: thumbsUp,
        code_hash: codeHash,
        code: code // Include code for pattern extraction
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
