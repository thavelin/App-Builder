'use client'

import { useState, FormEvent } from 'react'

interface PromptFormProps {
  onSubmit: (prompt: string) => void
  isSubmitting: boolean
}

export default function PromptForm({ onSubmit, isSubmitting }: PromptFormProps) {
  const [prompt, setPrompt] = useState('')

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (prompt.trim() && !isSubmitting) {
      onSubmit(prompt.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label
          htmlFor="prompt"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Describe the application you want to build
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., Create a todo list app with add, edit, and delete functionality. Include dark mode support and local storage persistence."
          rows={6}
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
          disabled={isSubmitting}
          required
          minLength={10}
          maxLength={2000}
        />
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {prompt.length}/2000 characters
        </p>
      </div>

      <button
        type="submit"
        disabled={!prompt.trim() || isSubmitting}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
      >
        {isSubmitting ? (
          <span className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Starting generation...
          </span>
        ) : (
          'Generate App'
        )}
      </button>
    </form>
  )
}

