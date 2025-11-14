'use client'

interface BuildResultProps {
  status: string
  downloadUrl: string | null
  githubUrl: string | null
  deploymentUrl: string | null
  error: string | null
}

export default function BuildResult({
  status,
  downloadUrl,
  githubUrl,
  deploymentUrl,
  error,
}: BuildResultProps) {
  const isSuccess = status === 'complete'
  const isFailed = status === 'failed'

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="text-center">
        {isSuccess ? (
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900 mb-4">
            <svg
              className="w-8 h-8 text-green-600 dark:text-green-400"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
        ) : (
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 dark:bg-red-900 mb-4">
            <svg
              className="w-8 h-8 text-red-600 dark:text-red-400"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
        )}

        <h2
          className={`text-3xl font-bold mb-2 ${
            isSuccess
              ? 'text-green-600 dark:text-green-400'
              : 'text-red-600 dark:text-red-400'
          }`}
        >
          {isSuccess ? 'Build Complete!' : 'Build Failed'}
        </h2>
        {error && (
          <div className="mt-4">
            {error.includes('No entry point found') || error.includes('missing a runnable file') ? (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <p className="text-yellow-800 dark:text-yellow-200 font-medium mb-2">
                  Missing Entry Point
                </p>
                <p className="text-yellow-700 dark:text-yellow-300 text-sm">
                  The generated app is missing a runnable file (e.g. app.py, main.py, or index.js). Please try again or refine your prompt.
                </p>
              </div>
            ) : (
              <p className="text-red-600 dark:text-red-400 mt-2">{error}</p>
            )}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {isSuccess && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Download ZIP */}
          {downloadUrl && (
            <a
              href={downloadUrl}
              download
              className="flex flex-col items-center justify-center p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
            >
              <svg
                className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-2"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
              <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                Download ZIP
              </span>
            </a>
          )}

          {/* GitHub Link */}
          {githubUrl && (
            <a
              href={githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center justify-center p-6 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <svg
                className="w-8 h-8 text-gray-900 dark:text-gray-100 mb-2"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  fillRule="evenodd"
                  d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                View on GitHub
              </span>
            </a>
          )}

          {/* Deployment Link */}
          {deploymentUrl && (
            <a
              href={deploymentUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center justify-center p-6 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-200 dark:border-green-800 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
            >
              <svg
                className="w-8 h-8 text-green-600 dark:text-green-400 mb-2"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
              </svg>
              <span className="text-sm font-semibold text-green-600 dark:text-green-400">
                View Live App
              </span>
            </a>
          )}
        </div>
      )}

      {/* Info Message */}
      {isSuccess && !downloadUrl && !githubUrl && !deploymentUrl && (
        <div className="text-center text-gray-600 dark:text-gray-300">
          <p>Your application has been generated successfully!</p>
          <p className="text-sm mt-2">Download and deployment links will appear here when available.</p>
        </div>
      )}
    </div>
  )
}

