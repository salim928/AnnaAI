import { redirect } from 'next/navigation'
import { SignOutButton } from '@/components/auth/sign-out-button'
import { OnboardingWizard } from '@/components/onboarding/wizard'
import { createServerSupabase } from '@/lib/supabase/server'

export default async function OnboardPage() {
  const supabase = await createServerSupabase()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login?next=/onboard')
  }

  return (
    <main className="min-h-screen bg-bg px-6 py-12">
      <div className="mx-auto mb-8 flex max-w-2xl items-center justify-between">
        <span className="text-xs text-muted">{user.email}</span>
        <SignOutButton />
      </div>
      <div className="mx-auto mb-8 max-w-2xl text-center">
        <h1 className="text-3xl font-bold">Welcome to AnnaAi</h1>
        <p className="mt-2 text-sm text-muted">
          Four quick steps and your autonomous marketing team is live.
        </p>
      </div>
      <OnboardingWizard />
    </main>
  )
}
