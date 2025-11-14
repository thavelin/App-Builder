/**
 * Robust fetch utility with retry logic and error handling.
 * 
 * Performs fetch with exponential backoff retry on network/HTTP errors.
 * Provides hooks for progress reporting and error handling.
 */

export interface FetchWithRetryOptions extends RequestInit {
  maxRetries?: number
  retryDelay?: number
  timeout?: number // Timeout in milliseconds
  onRetry?: (attempt: number, error: Error) => void
  onProgress?: (message: string) => void
}

export class FetchError extends Error {
  constructor(
    message: string,
    public status?: number,
    public statusText?: string,
    public response?: Response
  ) {
    super(message)
    this.name = 'FetchError'
  }
}

/**
 * Fetch with automatic retry on failure.
 * 
 * @param url - URL to fetch
 * @param options - Fetch options including retry configuration
 * @returns Promise resolving to the response JSON
 * @throws FetchError on final failure after all retries
 */
export async function fetchWithRetry(
  url: string,
  options: FetchWithRetryOptions = {}
): Promise<any> {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    timeout = 30000, // Default 30 second timeout
    onRetry,
    onProgress,
    ...fetchOptions
  } = options

  let lastError: Error | null = null

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      if (attempt > 0 && onProgress) {
        onProgress(`Retrying... (attempt ${attempt + 1}/${maxRetries + 1})`)
      }

      // Create AbortController for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      try {
        const response = await fetch(url, {
          ...fetchOptions,
          signal: controller.signal,
        })
        clearTimeout(timeoutId)

        if (!response.ok) {
          const errorText = await response.text().catch(() => '')
          const error = new FetchError(
            `HTTP ${response.status}: ${errorText || response.statusText || 'Request failed'}`,
            response.status,
            response.statusText,
            response
          )

          // Don't retry on 4xx client errors (except 408, 429)
          if (response.status >= 400 && response.status < 500 && 
              response.status !== 408 && response.status !== 429) {
            throw error
          }

          // Retry on server errors and specific client errors
          if (attempt < maxRetries) {
            lastError = error
            if (onRetry) {
              onRetry(attempt + 1, error)
            }
            // Exponential backoff with jitter
            const delay = retryDelay * Math.pow(2, attempt) + Math.random() * 1000
            await new Promise(resolve => setTimeout(resolve, delay))
            continue
          }

          throw error
        }

        // Success - parse and return JSON
        const data = await response.json()
        return data
      } catch (fetchError) {
        clearTimeout(timeoutId)
        // Re-throw if it was an abort (timeout)
        if (fetchError instanceof Error && fetchError.name === 'AbortError') {
          throw new Error(`Request timeout after ${timeout}ms`)
        }
        throw fetchError
      }

    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))

      // Check if it's a network error
      const isNetworkError = 
        lastError.message.includes('Failed to fetch') ||
        lastError.message.includes('NetworkError') ||
        lastError.message.includes('Network request failed')

      // Don't retry on non-network errors that are FetchErrors (already handled above)
      if (error instanceof FetchError) {
        throw error
      }

      // Retry on network errors
      if (isNetworkError && attempt < maxRetries) {
        if (onRetry) {
          onRetry(attempt + 1, lastError)
        }
        // Exponential backoff with jitter
        const delay = retryDelay * Math.pow(2, attempt) + Math.random() * 1000
        await new Promise(resolve => setTimeout(resolve, delay))
        continue
      }

      // Final attempt failed
      if (attempt === maxRetries) {
        if (isNetworkError) {
          throw new FetchError(
            'Server unreachable – is the backend running?',
            undefined,
            undefined,
            undefined
          )
        }
        throw lastError
      }
    }
  }

  // Should never reach here, but TypeScript needs it
  throw lastError || new Error('Unknown error')
}

