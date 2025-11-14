'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams } from 'next/navigation'
import LoadingSteps from '@/components/LoadingSteps'
import BuildResult from '@/components/BuildResult'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useToast } from '@/hooks/useToast'
import { ToastContainer } from '@/components/Toast'

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
  const retryCountRef = useRef(0)
  const maxRetries = 3
  const toast = useToast()

  // Fetch initial status with retry logic
  const fetchStatus = async (retryCount = 0): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`)
      
      if (!response.ok) {
        const errorText = await response.text().catch(() => '')
        throw new Error(`HTTP ${response.status}: ${errorText || 'Failed to fetch status'}`)
      }

      const data = await response.json()
      setStatusData(data)
      setIsLoading(false)
      retryCountRef.current = 0 // Reset retry count on success
      
      // Show toast notifications for status changes
      if (data.status === 'complete') {
        toast.success('Build completed successfully!')
      } else if (data.status === 'failed') {
        toast.error(data.error || 'Build failed')
      }
    } catch (err) {
      let errorMessage = 'Unknown error'
      
      if (err instanceof Error) {
        // Distinguish between network errors and HTTP errors
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
          errorMessage = 'Server unreachable – is the backend running?'
        } else {
          errorMessage = err.message
        }
      }
      
      if (retryCount < maxRetries) {
        retryCountRef.current = retryCount + 1
        setTimeout(() => fetchStatus(retryCount + 1), 2000 * (retryCount + 1))
      } else {
        setError(errorMessage)
        setIsLoading(false)
        toast.error(`Failed to load status after ${maxRetries} attempts: ${errorMessage}`)
      }
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

  // Polling fallback - continues even when WebSocket is connected as a backup
  // Polls at a slower rate (10s) when WebSocket is connected and receiving messages
  // Polls at normal rate (3s) when WebSocket is not connected or not receiving messages
  useEffect(() => {
    // Only poll if job is still in progress
    if (!statusData || (statusData.status !== 'in_progress' && statusData.status !== 'pending')) {
      return
    }
    
    // Determine polling interval based on WebSocket state
    // If WebSocket is connected AND we've received at least one message, poll less frequently as backup
    // Otherwise, poll more frequently as primary update mechanism
    const pollInterval = isConnected && hasReceivedMessage ? 10000 : 3000
    
    console.log(`[StatusPage] Starting polling with interval ${pollInterval}ms (WebSocket: ${isConnected ? 'connected' : 'disconnected'}, received messages: ${hasReceivedMessage})`)
    
    const pollIntervalId = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`)
        if (!response.ok) {
          return
        }
        
        const currentStatus = await response.json()
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
          // Only update if status actually changed to avoid unnecessary re-renders
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
    }, pollInterval)
    
    return () => {
      console.log('[StatusPage] Stopping polling')
      clearInterval(pollIntervalId)
    }
  }, [isConnected, hasReceivedMessage, statusData, jobId, toast])

  useEffect(() => {
    // Initial fetch
    fetchStatus(0)
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
      <ToastContainer toasts={toast.toasts} removeToast={toast.removeToast} />
      
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
  )
}

