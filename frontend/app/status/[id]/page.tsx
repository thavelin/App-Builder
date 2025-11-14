'use client'

import React, { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import LoadingSteps from '@/components/LoadingSteps'
import BuildResult from '@/components/BuildResult'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useToast } from '@/hooks/useToast'
import { useAuth, getAuthHeaders } from '@/hooks/useAuth'
import { fetchWithRetry } from '@/utils/fetchWithRetry'
import { AuthGuard } from '@/components/AuthGuard'
import Navbar from '@/components/Navbar'
import Loading from '@/components/Loading'

interface StatusData {
  job_id: string
  status: string
  step: string
  download_url: string | null
  github_url: string | null
  deployment_url: string | null
  error: string | null
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function StatusPage() {
  const params = useParams()
  const jobId = params.id as string
  const [statusData, setStatusData] = useState<StatusData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const toast = useToast()
  const { token } = useAuth()

  // Fetch initial status
  const fetchStatus = async (): Promise<void> => {
    try {
      const data = await fetchWithRetry(
        `${API_BASE_URL}/api/status/${jobId}`,
        {
          headers: getAuthHeaders(token),
        }
      )

      setStatusData(data)
      setIsLoading(false)
      
      // Show toast notifications for status changes
      if (data.status === 'complete') {
        toast.success('Build completed successfully!')
      } else if (data.status === 'failed') {
        toast.error(data.error || 'Build failed')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load status'
      setError(errorMessage)
      setIsLoading(false)
      toast.error(errorMessage)
    }
  }

  // WebSocket connection for real-time updates
  const wsUrl = `${API_BASE_URL}/api/ws/status/${jobId}`
  const { isConnected, hasReceivedMessage, lastMessage } = useWebSocket({
    url: wsUrl,
    onMessage: (message) => {
      console.log('[StatusPage] WebSocket message received:', message)
      if (message.type === 'status_update' && message.data) {
        setStatusData(message.data)
        setIsLoading(false)
        
        // Show toast notifications
        if (message.data.status === 'complete') {
          toast.success('Build completed successfully!')
        } else if (message.data.status === 'failed') {
          toast.error(message.data.error || 'Build failed')
        }
      }
    },
    onError: () => {
      console.warn('[StatusPage] WebSocket error - falling back to polling')
      // Fallback to polling if WebSocket fails
      // Polling will stop automatically when status is complete or failed
    },
    reconnect: true,
  })

  // Polling fallback - only if WebSocket is not working
  useEffect(() => {
    // Only poll if WebSocket is not connected or not receiving messages
    // AND job is still in progress
    if ((isConnected && hasReceivedMessage) || 
        !statusData || 
        (statusData.status !== 'in_progress' && statusData.status !== 'pending')) {
      return
    }
    
    console.log(`[StatusPage] WebSocket not working, using polling fallback`)
    
    const pollIntervalId = setInterval(async () => {
      try {
        const currentStatus = await fetchWithRetry(
          `${API_BASE_URL}/api/status/${jobId}`,
          {
            headers: getAuthHeaders(token),
          }
        )
        
        console.log(`[StatusPage] Polling update: status=${currentStatus.status}, step=${currentStatus.step}`)
        
        // Stop polling if job is complete or failed
        if (currentStatus.status === 'complete' || currentStatus.status === 'failed') {
          clearInterval(pollIntervalId)
          setStatusData(currentStatus)
          setIsLoading(false)
          
          // Show toast notifications
          if (currentStatus.status === 'complete') {
            toast.success('Build completed successfully!')
          } else if (currentStatus.status === 'failed') {
            toast.error(currentStatus.error || 'Build failed')
          }
        } else {
          // Update status but keep polling
          if (!statusData || 
              statusData.status !== currentStatus.status || 
              statusData.step !== currentStatus.step) {
            setStatusData(currentStatus)
          }
        }
      } catch (err) {
        // Ignore polling errors, will retry on next interval
        console.error('[StatusPage] Polling error:', err)
      }
    }, 5000) // Poll every 5 seconds as fallback
    
    return () => {
      console.log('[StatusPage] Stopping polling')
      clearInterval(pollIntervalId)
    }
  }, [isConnected, hasReceivedMessage, statusData, jobId, token, toast])

  useEffect(() => {
    if (token) {
      fetchStatus()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId, token])

  if (isLoading && !statusData) {
    return (
      <AuthGuard>
        <Navbar />
        <Loading fullScreen message="Loading status..." />
      </AuthGuard>
    )
  }

  if (error || !statusData) {
    return (
      <AuthGuard>
        <Navbar />
        <main className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-600 dark:text-red-400">Error: {error || 'Failed to load status'}</p>
          </div>
        </main>
      </AuthGuard>
    )
  }

  const isComplete = statusData.status === 'complete'
  const isFailed = statusData.status === 'failed'

  return (
    <AuthGuard>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                  Build Status
                </h1>
                <p className="text-gray-600 dark:text-gray-300">
                  Job ID: <span className="font-mono text-sm">{jobId}</span>
                </p>
              </div>
              {/* Connection status indicator */}
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
                    : 'Polling'}
                </span>
              </div>
            </div>
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
                downloadUrl={
                  statusData.download_url
                    ? statusData.download_url.startsWith('http')
                      ? statusData.download_url
                      : `${API_BASE_URL}${statusData.download_url}`
                    : null
                }
                githubUrl={statusData.github_url}
                deploymentUrl={statusData.deployment_url}
                error={statusData.error}
              />
            </div>
          )}
        </div>
      </div>
      </main>
    </AuthGuard>
  )
}

