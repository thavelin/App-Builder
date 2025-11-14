'use client'

import { AuthProvider } from '@/hooks/useAuth'
import { useToast } from '@/hooks/useToast'
import { ToastContainer } from '@/components/Toast'

export function Providers({ children }: { children: React.ReactNode }) {
  const toast = useToast()
  return (
    <AuthProvider>
      <ToastContainer toasts={toast.toasts} removeToast={toast.removeToast} />
      {children}
    </AuthProvider>
  )
}

