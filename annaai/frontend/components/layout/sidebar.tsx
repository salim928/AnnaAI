'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  FileText,
  Play,
  Plug,
  MessageSquare,
  Settings,
  Menu,
  X,
} from 'lucide-react'
import Image from 'next/image'

const NAV = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/drafts', label: 'Drafts', icon: FileText },
  { href: '/runs', label: 'Agent runs', icon: Play },
  { href: '/chat', label: 'Chat with Anna', icon: MessageSquare },
  { href: '/integrations', label: 'Integrations', icon: Plug },
  { href: '/settings', label: 'Settings', icon: Settings },
]

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname()
  return (
    <nav className="flex flex-col gap-1">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`)
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={clsx(
              'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition',
              active
                ? 'bg-primary text-white'
                : 'text-ink hover:bg-accent',
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        )
      })}
    </nav>
  )
}

/** Desktop sidebar — hidden on mobile */
export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-white p-4 md:flex">
      <Link href="/dashboard" className="mb-8 flex items-center gap-2 px-2">
        <Image src="/anna-avatar.svg" alt="Anna" width={32} height={32} />
        <span className="text-lg font-bold">AnnaAi</span>
      </Link>
      <NavLinks />
    </aside>
  )
}

/** Mobile menu button — visible only on small screens */
export function MobileMenuButton() {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()

  // Close drawer on route change
  useEffect(() => {
    setOpen(false)
  }, [pathname])

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-ink transition hover:bg-accent md:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Drawer */}
      <div
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-white p-4 shadow-xl transition-transform duration-200 md:hidden',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="mb-6 flex items-center justify-between">
          <Link
            href="/dashboard"
            onClick={() => setOpen(false)}
            className="flex items-center gap-2"
          >
            <Image src="/anna-avatar.svg" alt="Anna" width={28} height={28} />
            <span className="text-lg font-bold">AnnaAi</span>
          </Link>
          <button
            onClick={() => setOpen(false)}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-ink hover:bg-accent"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <NavLinks onNavigate={() => setOpen(false)} />
      </div>
    </>
  )
}
