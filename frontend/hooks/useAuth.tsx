'use client'

import React, { useState, useEffect, useCallback, createContext, useContext } from 'react'
import { useRouter } from 'next/navigation'
import { fetchWithRetry } from '@/utils/fetchWithRetry'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface User {
  id: string
  email: string
  username: string
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  const fetchUser = useCallback(async (authToken: string) => {
    try {
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 5000) // 5 second timeout
      })
      
      const fetchPromise = fetchWithRetry(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
        maxRetries: 1, // Reduce retries for auth check to fail faster
        retryDelay: 500,
      })
      
      const data = await Promise.race([fetchPromise, timeoutPromise]) as any
      setUser(data)
    } catch (error) {
      // Token invalid or backend unreachable, clear it
      console.warn('Auth check failed:', error)
      localStorage.removeItem('auth_token')
      setToken(null)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Load token and user from localStorage on mount
  useEffect(() => {
    // Check if we're in the browser (localStorage is available)
    if (typeof window === 'undefined') {
      setIsLoading(false)
      return
    }
    
    try {
      const storedToken = localStorage.getItem('auth_token')
      if (storedToken) {
        setToken(storedToken)
        // Fetch user info with timeout protection
        fetchUser(storedToken).catch((error) => {
          console.error('Failed to fetch user:', error)
          setIsLoading(false)
        })
      } else {
        setIsLoading(false)
      }
    } catch (error) {
      // localStorage might not be available (e.g., in private browsing)
      console.warn('localStorage not available:', error)
      setIsLoading(false)
    }
  }, [fetchUser])

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true)
    try {
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Login request timeout - is the backend running?')), 10000) // 10 second timeout
      })
      
      const fetchPromise = fetchWithRetry(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        maxRetries: 2, // Reduce retries for faster failure
        retryDelay: 500,
      })
      
      const data = await Promise.race([fetchPromise, timeoutPromise]) as any
      
      const authToken = data.access_token
      if (!authToken) {
        throw new Error('No access token received from server')
      }
      
      localStorage.setItem('auth_token', authToken)
      setToken(authToken)
      setUser(data.user)
    } catch (error) {
      // Re-throw error so login page can handle it
      const errorMessage = error instanceof Error ? error.message : 'Login failed'
      console.error('Login error:', errorMessage)
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(async (email: string, username: string, password: string) => {
    setIsLoading(true)
    try {
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Registration request timeout - is the backend running?')), 10000) // 10 second timeout
      })
      
      const fetchPromise = fetchWithRetry(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, username, password }),
        maxRetries: 2, // Reduce retries for faster failure
        retryDelay: 500,
      })
      
      const data = await Promise.race([fetchPromise, timeoutPromise]) as any
      
      const authToken = data.access_token
      if (!authToken) {
        throw new Error('No access token received from server')
      }
      
      localStorage.setItem('auth_token', authToken)
      setToken(authToken)
      setUser(data.user)
    } catch (error) {
      // Re-throw error so register page can handle it
      const errorMessage = error instanceof Error ? error.message : 'Registration failed'
      console.error('Registration error:', errorMessage)
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
    router.push('/login')
  }, [router])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
        isAuthenticated: !!token && !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Helper to get auth headers for API calls
export function getAuthHeaders(token: string | null): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

