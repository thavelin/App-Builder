'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth, getAuthHeaders } from '@/hooks/useAuth'
import { useToast } from '@/hooks/useToast'
import { fetchWithRetry } from '@/utils/fetchWithRetry'
import { useWebSocket } from '@/hooks/useWebSocket'
import { AuthGuard } from '@/components/AuthGuard'
import Navbar from '@/components/Navbar'
import Loading from '@/components/Loading'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface JobListItem {
  id: string
  prompt: string
  status: string
  step: string
  created_at: string | null
  updated_at: string | null
}

export default function HistoryPage() {
  const router = useRouter()
  const { token } = useAuth()
  const toast = useToast()
  const [jobs, setJobs] = useState<JobListItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')

  // WebSocket connection for real-time updates
  const wsUrl = `${API_BASE_URL}/api/ws/jobs`
  const { isConnected, hasReceivedMessage } = useWebSocket({
    url: wsUrl,
    onMessage: (message) => {
      console.log('[HistoryPage] WebSocket message received:', message)
      if (message.type === 'job_created' || message.type === 'job_updated') {
        // Refresh the job list
        fetchJobs()
      }
    },
    onError: () => {
      console.warn('[HistoryPage] WebSocket error - will use polling fallback')
    },
    reconnect: true,
  })

  const fetchJobs = async () => {
    try {
      setIsLoading(true)
      const params = new URLSearchParams({
        limit: '50',
        ...(statusFilter !== 'all' && { status: statusFilter }),
        ...(searchQuery && { q: searchQuery }),
      })

      const data = await fetchWithRetry(
        `${API_BASE_URL}/api/jobs?${params.toString()}`,
        {
          headers: getAuthHeaders(token),
        }
      )

      setJobs(data)
      setError(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load jobs'
      setError(errorMessage)
      toast.error('Failed to load build history')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (token) {
      fetchJobs()
    }
  }, [token, statusFilter, searchQuery])

  const handleRepeatBuild = async (prompt: string) => {
    try {
      const data = await fetchWithRetry(
        `${API_BASE_URL}/api/generate`,
        {
          method: 'POST',
          headers: getAuthHeaders(token),
          body: JSON.stringify({
            prompt,
            review_threshold: 80,
            attachments: undefined,
          }),
        }
      )

      toast.success('Build started!')
      router.push(`/status/${data.job_id}`)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start build'
      toast.error(errorMessage)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
    }
  }

  const formatTimeAgo = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
      if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
      return date.toLocaleDateString()
    } catch {
      return dateString
    }
  }

  return (
    <AuthGuard>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                    Build History
                  </h1>
                  <p className="text-gray-600 dark:text-gray-300">
                    View all your generated applications
                  </p>
                </div>
                {/* Connection status */}
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    isConnected && hasReceivedMessage 
                      ? 'bg-green-500' 
                      : isConnected 
                      ? 'bg-yellow-500' 
                      : 'bg-gray-400'
                  }`} />
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    {isConnected && hasReceivedMessage 
                      ? 'Live' 
                      : isConnected 
                      ? 'Connecting...' 
                      : 'Offline'}
                  </span>
                </div>
              </div>

              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Search by prompt..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="all">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="complete">Complete</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
            </div>

            {/* Loading State */}
            {isLoading && (
              <Loading message="Loading build history..." />
            )}

            {/* Error State */}
            {error && !isLoading && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-red-800 dark:text-red-200">Error: {error}</p>
              </div>
            )}

            {/* Jobs List */}
            {!isLoading && !error && (
              <>
                {jobs.length === 0 ? (
                  <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-12 text-center">
                    <p className="text-gray-600 dark:text-gray-300 mb-4">
                      No builds found. Create your first app!
                    </p>
                    <button
                      onClick={() => router.push('/')}
                      className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                      Start Building
                    </button>
                  </div>
                ) : (
                  <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden animate-fade-in">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Prompt
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Step
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Created
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Actions
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {jobs.map((job) => (
                            <tr key={job.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                              <td className="px-6 py-4">
                                <div className="text-sm font-medium text-gray-900 dark:text-white max-w-md truncate">
                                  {job.prompt}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span
                                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                                    job.status
                                  )}`}
                                >
                                  {job.status}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                                {job.step}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                                {formatTimeAgo(job.created_at)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                                <button
                                  onClick={() => router.push(`/status/${job.id}`)}
                                  className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                                >
                                  View
                                </button>
                                <button
                                  onClick={() => handleRepeatBuild(job.prompt)}
                                  className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                                >
                                  Repeat
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>
    </AuthGuard>
  )
}
