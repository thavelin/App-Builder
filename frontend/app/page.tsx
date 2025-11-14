'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import PromptForm, { Attachment } from '@/components/PromptForm'
import { useToast } from '@/hooks/useToast'
import { useAuth, getAuthHeaders } from '@/hooks/useAuth'
import { fetchWithRetry } from '@/utils/fetchWithRetry'
import { AuthGuard } from '@/components/AuthGuard'
import Navbar from '@/components/Navbar'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const toast = useToast()
  const { token } = useAuth()

  const handleSubmit = async (
    payload: { prompt: string; threshold: number; attachments: Attachment[] }
  ) => {
    setIsSubmitting(true)

    try {
      const data = await fetchWithRetry(
        `${API_BASE_URL}/api/generate`,
        {
          method: 'POST',
          headers: getAuthHeaders(token),
          body: JSON.stringify({
            prompt: payload.prompt,
            review_threshold: payload.threshold,
            attachments: payload.attachments.length > 0 ? payload.attachments : undefined,
          }),
          onProgress: (message) => {
            console.log(message)
          },
        }
      )

      toast.success('Build started successfully!')
      router.push(`/status/${data.job_id}`)
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      toast.error(`Failed to start generation: ${errorMessage}`)
      setIsSubmitting(false)
    }
  }

  return (
    <AuthGuard>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-3xl mx-auto animate-fade-in">
            {/* Header */}
            <div className="text-center mb-12">
              <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
                AI App Builder
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Generate complete applications from natural language prompts
              </p>
            </div>

          {/* Prompt Form */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <PromptForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
          </div>

          {/* Features */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Multi-Agent System
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Specialized AI agents work together to design, code, and review your application
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Complete Stack
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Get full-stack applications with code, UI, and deployment ready to go
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-md">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                GitHub Integration
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Automatically push your generated app to GitHub for version control
              </p>
            </div>
          </div>
        </div>
      </main>
    </AuthGuard>
  )
}

