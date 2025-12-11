import { useEffect, useState } from 'react'

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
  onComplete?: () => void
}

export default function ProgressBar({ isActive, onComplete }: ProgressBarProps) {
  const [currentStage, setCurrentStage] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!isActive) {
      setCurrentStage(0)
      setProgress(0)
      return
    }

    let stageIndex = 0
    let currentProgress = 0
    const interval = setInterval(() => {
      if (stageIndex < HUMOROUS_STAGES.length) {
        const stage = HUMOROUS_STAGES[stageIndex]
        setCurrentStage(stageIndex)
        setProgress(stage.progress)
        stageIndex++
      } else {
        // Slow down near the end
        if (currentProgress < 98) {
          currentProgress += 0.5
          setProgress(currentProgress)
        }
      }
    }, 800) // Change stage every 800ms

    return () => clearInterval(interval)
  }, [isActive])

  useEffect(() => {
    if (isActive && progress >= 98 && onComplete) {
      // Small delay before calling onComplete
      const timer = setTimeout(() => {
        onComplete()
      }, 200)
      return () => clearTimeout(timer)
    }
  }, [progress, isActive, onComplete])

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

