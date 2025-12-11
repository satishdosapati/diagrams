import { useEffect, useState, useRef } from 'react'

interface ProgressStage {
  progress: number
  message: string
}

const HUMOROUS_STAGES: ProgressStage[] = [
  { progress: 10, message: '📝 Analyzing your brilliant architecture idea...' },
  { progress: 20, message: '🤖 Consulting with AI architects (they\'re very opinionated)...' },
  { progress: 35, message: '🔍 Decoding cloud provider hieroglyphics...' },
  { progress: 50, message: '📦 Drawing pretty boxes and arrows...' },
  { progress: 65, message: '🎨 Making it look professional (and colorful)...' },
  { progress: 80, message: '✨ Adding the magic sprinkles...' },
  { progress: 90, message: '🏗️ Finalizing your masterpiece...' },
  { progress: 95, message: '🎉 Almost there! Buffing the pixels...' },
]

interface ProgressBarProps {
  isActive: boolean
}

export default function ProgressBar({ isActive }: ProgressBarProps) {
  const [currentStage, setCurrentStage] = useState(0)
  const [progress, setProgress] = useState(0)
  const stageIndexRef = useRef(0)

  useEffect(() => {
    if (!isActive) {
      setCurrentStage(0)
      setProgress(0)
      stageIndexRef.current = 0
      return
    }

    const interval = setInterval(() => {
      if (stageIndexRef.current < HUMOROUS_STAGES.length) {
        const stage = HUMOROUS_STAGES[stageIndexRef.current]
        setCurrentStage(stageIndexRef.current)
        setProgress(stage.progress)
        stageIndexRef.current++
      } else {
        // Hold at final stage - don't increment further
        // Keep showing the last message until generation completes
        setCurrentStage(HUMOROUS_STAGES.length - 1)
        // Add a subtle pulsing effect by oscillating between 95-98%
        const pulseProgress = 95 + (Math.sin(Date.now() / 1000) * 1.5 + 1.5) / 2 * 3
        setProgress(Math.min(pulseProgress, 98))
      }
    }, 800) // Change stage every 800ms

    return () => clearInterval(interval)
  }, [isActive])

  if (!isActive) return null

  const currentMessage = HUMOROUS_STAGES[currentStage]?.message || '✨ Working on it...'

  return (
    <div className="w-full space-y-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-700 font-medium">{currentMessage}</span>
        <span className="text-gray-500">{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}

