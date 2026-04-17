import type { ReactNode } from 'react'
import Link from 'next/link'

export default function LegalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <nav className="mb-8">
        <Link href="/" className="text-sm text-muted hover:text-primary">
          &larr; Back to AnnaAi
        </Link>
      </nav>
      <article className="prose prose-neutral max-w-none">
        {children}
      </article>
      <footer className="mt-16 border-t border-border pt-6 text-xs text-muted">
        <div className="flex gap-4">
          <Link href="/terms" className="hover:text-primary">Terms of Service</Link>
          <Link href="/privacy" className="hover:text-primary">Privacy Policy</Link>
        </div>
      </footer>
    </div>
  )
}
