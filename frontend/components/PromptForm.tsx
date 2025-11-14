'use client'

import { useState, FormEvent, ChangeEvent } from 'react'

export interface Attachment {
  name: string
  type: string
  content: string // base64 encoded
}

interface PromptFormProps {
  onSubmit: (payload: { prompt: string; threshold: number; attachments: Attachment[] }) => void
  isSubmitting: boolean
}

// Helper function to convert file to base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      const result = reader.result as string
      // Remove data URL prefix (e.g., "data:image/png;base64,")
      const base64 = result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = (error) => reject(error)
  })
}

export default function PromptForm({ onSubmit, isSubmitting }: PromptFormProps) {
  const [prompt, setPrompt] = useState('')
  const [threshold, setThreshold] = useState(80)
  const [attachments, setAttachments] = useState<File[]>([])
  const [showTemplate, setShowTemplate] = useState(false)

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      // Filter for allowed file types
      const allowedTypes = [
        'image/png', 'image/jpeg', 'image/jpg',
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
      ]
      const validFiles = files.filter(file => allowedTypes.includes(file.type))
      setAttachments(prev => [...prev, ...validFiles])
    }
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (prompt.trim() && !isSubmitting && threshold >= 0 && threshold <= 100) {
      // Convert files to base64
      const attachmentData: Attachment[] = await Promise.all(
        attachments.map(async (file) => ({
          name: file.name,
          type: file.type,
          content: await fileToBase64(file)
        }))
      )
      
      onSubmit({
        prompt: prompt.trim(),
        threshold,
        attachments: attachmentData
      })
    }
  }

  const sampleTemplate = `Create a task management application with the following features:
- Add, edit, and delete tasks
- Mark tasks as complete/incomplete
- Filter tasks by status (all, active, completed)
- Dark mode support
- Local storage persistence
- Responsive design for mobile and desktop
- Clean, modern UI with smooth animations`

  const isValid = prompt.trim().length >= 10 && 
                  prompt.trim().length <= 2000 && 
                  threshold >= 0 && 
                  threshold <= 100

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label
          htmlFor="prompt"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Describe the application you want to build
        </label>
        
        {/* Prompt template guide */}
        <div className="mb-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p className="text-sm text-gray-700 dark:text-gray-300 italic mb-2">
            💡 <strong>Tip:</strong> Include the app's purpose, features, target users, and any design or tech preferences for best results.
          </p>
          <button
            type="button"
            onClick={() => setShowTemplate(!showTemplate)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            {showTemplate ? 'Hide' : 'Show'} example template
          </button>
          {showTemplate && (
            <div className="mt-2">
              <textarea
                readOnly
                value={sampleTemplate}
                rows={8}
                className="w-full px-3 py-2 text-sm border border-blue-200 dark:border-blue-700 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-mono resize-none"
                onClick={(e) => (e.target as HTMLTextAreaElement).select()}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Click to select all, then copy and paste into the prompt field above
              </p>
            </div>
          )}
        </div>

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

      {/* Review Threshold */}
      <div>
        <label
          htmlFor="threshold"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          Project Review Threshold (0–100)
        </label>
        <div className="flex items-center space-x-4">
          <input
            type="range"
            id="threshold"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            disabled={isSubmitting}
            className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <input
            type="number"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => {
              const val = Number(e.target.value)
              if (val >= 0 && val <= 100) {
                setThreshold(val)
              }
            }}
            disabled={isSubmitting}
            className="w-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white text-center"
          />
        </div>
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Minimum quality score (0-100) required for approval. Higher values mean stricter reviews. Default: 80
        </p>
        {(threshold < 0 || threshold > 100) && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            Threshold must be between 0 and 100
          </p>
        )}
      </div>

      {/* File Attachments */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Attach Files (Optional)
        </label>
        <div className="flex items-center space-x-4">
          <label className="cursor-pointer">
            <span className="inline-flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors duration-200">
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                />
              </svg>
              Attach Files
            </span>
            <input
              type="file"
              multiple
              accept="image/png,image/jpeg,image/jpg,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
              onChange={handleFileChange}
              disabled={isSubmitting}
              className="hidden"
            />
          </label>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Accepted: Images (PNG, JPG), Documents (PDF, DOCX, TXT)
          </span>
        </div>
        {attachments.length > 0 && (
          <div className="mt-3 space-y-2">
            {attachments.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300 truncate flex-1">
                  {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </span>
                <button
                  type="button"
                  onClick={() => removeAttachment(index)}
                  disabled={isSubmitting}
                  className="ml-2 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <button
        type="submit"
        disabled={!isValid || isSubmitting}
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

