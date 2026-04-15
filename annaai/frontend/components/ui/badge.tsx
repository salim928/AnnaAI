import { clsx } from 'clsx'
import type { ReactNode } from 'react'

type Tone = 'default' | 'success' | 'warning' | 'danger' | 'info'

const TONES: Record<Tone, string> = {
  default: 'bg-border text-surface',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  danger: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
}

export function Badge({
  tone = 'default',
  children,
}: {
  tone?: Tone
  children: ReactNode
}) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide',
        TONES[tone],
      )}
    >
      {children}
    </span>
  )
}
