'use client'

import { useRouter } from 'next/navigation'
import { LogOut } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { MobileMenuButton } from '@/components/layout/sidebar'
import { createBrowserSupabase } from '@/lib/supabase/client'

export function Header({ email }: { email?: string | null }) {
  const router = useRouter()

  async function signOut() {
    const supabase = createBrowserSupabase()
    await supabase.auth.signOut()
    toast.success('Signed out.')
    router.push('/login')
    router.refresh()
  }

  return (
    <header className="flex items-center justify-between border-b border-border bg-white px-4 py-3 md:px-6 md:py-4">
      <div className="flex items-center gap-3">
        <MobileMenuButton />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">
          Your AI marketing crew
        </h2>
      </div>
      <div className="flex items-center gap-2 md:gap-4">
        {email ? (
          <span className="hidden text-sm text-muted md:block">
            {email}
          </span>
        ) : null}
        <Button variant="ghost" size="sm" onClick={signOut}>
          <LogOut className="h-4 w-4 md:mr-2" />
          <span className="hidden md:inline">Sign out</span>
        </Button>
      </div>
    </header>
  )
}
