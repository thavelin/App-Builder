'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import LoadingSteps from '@/components/LoadingSteps'
import BuildResult from '@/components/BuildResult'

interface StatusData {
  job_id: string
  status: string
  step: string
  download_url: string | null
  github_url: string | null
  deployment_url: string | null
  error: string | null
}

export default function StatusPage() {
  const params = useParams()
  const jobId = params.id as string
  const [statusData, setStatusData] = useState<StatusData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/status/${jobId}`)
        
        if (!response.ok) {
          throw new Error('Failed to fetch status')
        }

        const data = await response.json()
        setStatusData(data)
        setIsLoading(false)

        // Continue polling if not complete or failed
        if (data.status === 'in_progress' || data.status === 'pending') {
          setTimeout(fetchStatus, 2000) // Poll every 2 seconds
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setIsLoading(false)
      }
    }

    fetchStatus()
  }, [jobId])

  if (isLoading && !statusData) {
    return (
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-white mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading status...</p>
        </div>
      </main>
    )
  }

  if (error || !statusData) {
    return (
      <main className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400">Error: {error || 'Failed to load status'}</p>
        </div>
      </main>
    )
  }

  const isComplete = statusData.status === 'complete'
  const isFailed = statusData.status === 'failed'

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Build Status
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Job ID: <span className="font-mono text-sm">{jobId}</span>
            </p>
          </div>

          {/* Status Display */}
          {!isComplete && !isFailed && (
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
              <LoadingSteps currentStep={statusData.step} status={statusData.status} />
            </div>
          )}

          {/* Results */}
          {(isComplete || isFailed) && (
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
              <BuildResult
                status={statusData.status}
                downloadUrl={statusData.download_url}
                githubUrl={statusData.github_url}
                deploymentUrl={statusData.deployment_url}
                error={statusData.error}
              />
            </div>
          )}
        </div>
      </div>
    </main>
  )
}

