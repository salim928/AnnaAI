import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import { Toaster } from 'sonner'
import { Providers } from '@/app/providers'
import './globals.css'

export const metadata: Metadata = {
  title: 'AnnaAi — Your autonomous marketing crew',
  description:
    'Five AI agents. One daily crew. Anna researches, writes, and publishes content for your brand — every morning, in your voice.',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable}`}
    >
      <body className="min-h-screen bg-bg text-ink antialiased">
        <Providers>{children}</Providers>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  )
}
