'use client'

import React from 'react'
import { AuthProvider } from '@/hooks/useAuth'
import { ToastProvider } from '@/components/ToastProvider'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <ToastProvider>
        {children}
      </ToastProvider>
    </AuthProvider>
  )
}

