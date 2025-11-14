'use client'

import React, { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import Loading from '@/components/Loading'

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const [hasRedirected, setHasRedirected] = useState(false)

  useEffect(() => {
    // Only redirect if we're not already on the login/register page
    if (!isLoading && !isAuthenticated && !hasRedirected) {
      const isAuthPage = pathname === '/login' || pathname === '/register'
      if (!isAuthPage) {
        setHasRedirected(true)
        router.push('/login')
      }
    }
  }, [isAuthenticated, isLoading, router, pathname, hasRedirected])

  // Show loading while checking auth
  if (isLoading) {
    return <Loading fullScreen message="Loading..." />
  }

  // If not authenticated and not on auth pages, show loading while redirecting
  if (!isAuthenticated) {
    const isAuthPage = pathname === '/login' || pathname === '/register'
    if (!isAuthPage) {
      return <Loading fullScreen message="Redirecting to login..." />
    }
    return null
  }

  return <>{children}</>
}

