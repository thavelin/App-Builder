'use client'

import Link from 'next/link'
import { useAuth } from '@/hooks/useAuth'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return null
  }

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <Link href="/" className="text-xl font-bold text-gray-900 dark:text-white">
              AI App Builder
            </Link>
            <Link
              href="/"
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              New Build
            </Link>
            <Link
              href="/history"
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              History
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {user?.username || user?.email}
            </span>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

