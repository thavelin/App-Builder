import './globals.css'
import { Providers } from './providers'
import type { ReactNode } from 'react'

export const metadata = {
  title: 'AI App Builder',
  description: 'Generate applications from natural language prompts',
}

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

