export function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  )
}

export function DiagramLoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="bg-gray-200 rounded-xl h-64 w-full mb-4"></div>
      <div className="flex gap-3">
        <div className="h-10 bg-gray-200 rounded-lg w-32"></div>
        <div className="h-10 bg-gray-200 rounded-lg w-32"></div>
      </div>
    </div>
  )
}

export function ButtonLoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-12 bg-gray-200 rounded-lg w-full"></div>
    </div>
  )
}
