import { useState, useRef, useEffect } from 'react'

interface DiagramViewerProps {
  diagramUrl: string
  alt?: string
  className?: string
}

function DiagramViewer({ diagramUrl, alt = 'Generated architecture diagram', className = '' }: DiagramViewerProps) {
  const [zoomLevel, setZoomLevel] = useState(100)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const containerRef = useRef<HTMLDivElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)

  const MIN_ZOOM = 25
  const MAX_ZOOM = 500
  const ZOOM_STEP = 25

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + ZOOM_STEP, MAX_ZOOM))
  }

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - ZOOM_STEP, MIN_ZOOM))
  }

  const handleResetZoom = () => {
    setZoomLevel(100)
    setPosition({ x: 0, y: 0 })
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoomLevel > 100) {
      setIsDragging(true)
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y })
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && zoomLevel > 100) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      })
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleWheel = (e: React.WheelEvent) => {
    // Zoom with Ctrl+Wheel or Cmd+Wheel
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault()
      if (e.deltaY < 0) {
        handleZoomIn()
      } else {
        handleZoomOut()
      }
    }
  }

  // Reset position when zoom resets to 100%
  useEffect(() => {
    if (zoomLevel === 100) {
      setPosition({ x: 0, y: 0 })
    }
  }, [zoomLevel])

  return (
    <div className="relative">
      {/* Zoom Controls */}
      <div className="absolute top-2 right-2 z-10 flex flex-col gap-1 bg-white rounded-lg shadow-lg border border-gray-200 p-1">
        <button
          onClick={handleZoomIn}
          disabled={zoomLevel >= MAX_ZOOM}
          className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Zoom In"
          aria-label="Zoom In"
        >
          <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
          </svg>
          Zoom In
        </button>
        <button
          onClick={handleZoomOut}
          disabled={zoomLevel <= MIN_ZOOM}
          className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 rounded-md border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
          </svg>
          Zoom Out
        </button>
        <button
          onClick={handleResetZoom}
          className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 rounded-md border border-gray-300 transition-colors"
          title="Reset Zoom"
          aria-label="Reset Zoom"
        >
          <svg className="w-4 h-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Reset
        </button>
        <div className="px-3 py-1 text-xs text-center text-gray-600 border-t border-gray-200 mt-1 pt-1">
          {zoomLevel}%
        </div>
      </div>

      {/* Diagram Container */}
      <div
        ref={containerRef}
        className={`relative overflow-auto border rounded-lg bg-gray-50 ${className}`}
        style={{
          cursor: zoomLevel > 100 ? (isDragging ? 'grabbing' : 'grab') : 'default',
          maxHeight: '80vh'
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      >
        <div
          style={{
            transform: `translate(${position.x}px, ${position.y}px) scale(${zoomLevel / 100})`,
            transformOrigin: 'top left',
            transition: isDragging ? 'none' : 'transform 0.2s ease-out',
            display: 'inline-block'
          }}
        >
          <img
            ref={imageRef}
            src={diagramUrl}
            alt={alt}
            className="max-w-full h-auto"
            draggable={false}
            style={{
              display: 'block'
            }}
          />
        </div>
      </div>

      {/* Zoom Level Indicator (bottom) */}
      {zoomLevel !== 100 && (
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded z-10">
          Zoom: {zoomLevel}% {zoomLevel > 100 && '(Drag to pan, Ctrl+Wheel to zoom)'}
        </div>
      )}
    </div>
  )
}

export default DiagramViewer
