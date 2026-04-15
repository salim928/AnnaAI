'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { clsx } from 'clsx'
import {
  LayoutDashboard,
  FileText,
  Play,
  Plug,
  MessageSquare,
  Settings,
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

export function Sidebar() {
  const pathname = usePathname()
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-white p-4 md:flex">
      <Link href="/dashboard" className="mb-8 flex items-center gap-2 px-2">
        <Image src="/anna-avatar.svg" alt="Anna" width={32} height={32} />
        <span className="text-lg font-bold">AnnaAi</span>
      </Link>

      <nav className="flex flex-col gap-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(`${href}/`)
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition',
                active
                  ? 'bg-primary text-white'
                  : 'text-surface hover:bg-border',
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
