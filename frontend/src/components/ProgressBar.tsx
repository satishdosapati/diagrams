import { useEffect, useState } from 'react'

const HUMOROUS_MESSAGES = [
  '📝 Analyzing your brilliant architecture idea...',
  '🤖 Consulting with AI architects (they\'re very opinionated)...',
  '🔍 Decoding cloud provider hieroglyphics...',
  '📦 Drawing pretty boxes and arrows...',
  '🎨 Making it look professional (and colorful)...',
  '✨ Adding the magic sprinkles...',
  '🏗️ Finalizing your masterpiece...',
  '🎉 Almost there! Buffing the pixels...',
]

interface ProgressBarProps {
  isActive: boolean
}

export default function ProgressBar({ isActive }: ProgressBarProps) {
  const [currentMessage, setCurrentMessage] = useState(0)

  useEffect(() => {
    if (!isActive) {
      setCurrentMessage(0)
      return
    }

    const interval = setInterval(() => {
      setCurrentMessage((prev) => {
        if (prev < HUMOROUS_MESSAGES.length - 1) {
          return prev + 1
        }
        // Hold at last message
        return prev
      })
    }, 800)

    return () => clearInterval(interval)
  }, [isActive])

  if (!isActive) return null

  return (
    <div className="flex items-center gap-2 text-sm text-gray-500 mt-2">
      <svg
        className="animate-spin h-4 w-4 text-gray-400"
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
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span>{HUMOROUS_MESSAGES[currentMessage]}</span>
    </div>
  )
}

