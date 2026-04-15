'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { LogOut } from 'lucide-react'
import { toast } from 'sonner'
import { createBrowserSupabase } from '@/lib/supabase/client'

type Props = {
  variant?: 'ghost' | 'solid' | 'link'
  className?: string
  label?: string
  showIcon?: boolean
}

export function SignOutButton({
  variant = 'ghost',
  className,
  label = 'Sign out',
  showIcon = true,
}: Props) {
  const router = useRouter()
  const [pending, setPending] = useState(false)

  async function onClick() {
    setPending(true)
    try {
      const supabase = createBrowserSupabase()
      await supabase.auth.signOut()
      toast.success('Signed out.')
      router.push('/login')
      router.refresh()
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Sign-out failed')
      setPending(false)
    }
  }

  const base =
    'inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-[13.5px] font-medium transition disabled:opacity-50'
  const styles =
    variant === 'solid'
      ? 'bg-ink text-white hover:bg-ink-2'
      : variant === 'link'
        ? 'text-ink hover:text-primary'
        : 'text-ink hover:bg-accent'

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={pending}
      className={`${base} ${styles} ${className ?? ''}`.trim()}
    >
      {showIcon ? <LogOut className="h-3.5 w-3.5" /> : null}
      {pending ? 'Signing out…' : label}
    </button>
  )
}
