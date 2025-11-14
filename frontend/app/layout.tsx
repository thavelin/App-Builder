import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI App Builder',
  description: 'Generate applications from natural language prompts',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

