'use client'

interface LoadingStepsProps {
  currentStep: string
  status: string
}

const steps = [
  { id: 'initializing', label: 'Initializing', description: 'Setting up the generation process' },
  { id: 'design', label: 'Design', description: 'Creating UI layouts and wireframes' },
  { id: 'coding', label: 'Coding', description: 'Generating application code' },
  { id: 'reviewing', label: 'Reviewing', description: 'Reviewing code quality and completeness' },
  { id: 'validating', label: 'Validating', description: 'Validating the generated application' },
  { id: 'packaging', label: 'Packaging', description: 'Creating deployment package' },
  { id: 'deploying', label: 'Deploying', description: 'Pushing to GitHub and deploying' },
  { id: 'complete', label: 'Complete', description: 'Application ready!' },
]

export default function LoadingSteps({ currentStep, status }: LoadingStepsProps) {
  const currentStepIndex = steps.findIndex((step) => step.id === currentStep)
  const activeIndex = currentStepIndex >= 0 ? currentStepIndex : 0

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Building Your Application
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          {steps[activeIndex]?.description || 'Processing...'}
        </p>
      </div>

      <div className="relative">
        {/* Progress Line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700">
          <div
            className="absolute top-0 left-0 w-full bg-blue-600 transition-all duration-500"
            style={{
              height: `${(activeIndex / (steps.length - 1)) * 100}%`,
            }}
          />
        </div>

        {/* Steps */}
        <div className="space-y-6">
          {steps.map((step, index) => {
            const isActive = index === activeIndex
            const isCompleted = index < activeIndex
            const isPending = index > activeIndex

            return (
              <div key={step.id} className="relative flex items-start">
                {/* Step Circle */}
                <div
                  className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all duration-300 ${
                    isCompleted
                      ? 'bg-blue-600 border-blue-600'
                      : isActive
                      ? 'bg-blue-600 border-blue-600 animate-pulse'
                      : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600'
                  }`}
                >
                  {isCompleted ? (
                    <svg
                      className="w-5 h-5 text-white"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M5 13l4 4L19 7"></path>
                    </svg>
                  ) : (
                    <div
                      className={`w-2 h-2 rounded-full ${
                        isActive ? 'bg-white' : 'bg-gray-400'
                      }`}
                    />
                  )}
                </div>

                {/* Step Content */}
                <div className="ml-4 flex-1 pt-1">
                  <h3
                    className={`text-sm font-semibold ${
                      isActive || isCompleted
                        ? 'text-gray-900 dark:text-white'
                        : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {step.label}
                  </h3>
                  <p
                    className={`text-xs mt-1 ${
                      isActive || isCompleted
                        ? 'text-gray-600 dark:text-gray-300'
                        : 'text-gray-400 dark:text-gray-500'
                    }`}
                  >
                    {step.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Loading Animation */}
      {status === 'in_progress' && (
        <div className="text-center pt-4">
          <div className="inline-flex items-center space-x-2 text-gray-600 dark:text-gray-300">
            <div className="animate-bounce">●</div>
            <div className="animate-bounce" style={{ animationDelay: '0.1s' }}>
              ●
            </div>
            <div className="animate-bounce" style={{ animationDelay: '0.2s' }}>
              ●
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

