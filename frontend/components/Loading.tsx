'use client'

interface LoadingProps {
  message?: string
  size?: 'sm' | 'md' | 'lg'
  fullScreen?: boolean
}

export default function Loading({ 
  message = 'Loading...', 
  size = 'md',
  fullScreen = false 
}: LoadingProps) {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  }

  const spinner = (
    <div className="text-center">
      <div className={`animate-spin rounded-full border-b-2 border-gray-900 dark:border-white mx-auto ${sizeClasses[size]}`}></div>
      {message && (
        <p className={`mt-4 text-gray-600 dark:text-gray-300 ${size === 'sm' ? 'text-sm' : ''}`}>
          {message}
        </p>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        {spinner}
      </main>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-12">
      {spinner}
    </div>
  )
}

interface LoadingSkeletonProps {
  lines?: number
  className?: string
}

export function LoadingSkeleton({ lines = 3, className = '' }: LoadingSkeletonProps) {
  return (
    <div className={`animate-pulse space-y-4 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
      ))}
    </div>
  )
}

interface LoadingSpinnerProps {
  className?: string
}

export function LoadingSpinner({ className = '' }: LoadingSpinnerProps) {
  return (
    <div className={`animate-spin rounded-full border-b-2 border-gray-900 dark:border-white ${className}`}></div>
  )
}

