'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import PromptForm from '@/components/PromptForm'

export default function Home() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (prompt: string) => {
    setIsSubmitting(true)
    try {
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) {
        throw new Error('Failed to start generation')
      }

      const data = await response.json()
      router.push(`/status/${data.job_id}`)
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to start generation. Please try again.')
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
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
      </div>
    </main>
  )
}

