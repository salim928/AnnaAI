import Link from 'next/link'
import Image from 'next/image'
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  Sparkles,
} from 'lucide-react'
import { SignOutButton } from '@/components/auth/sign-out-button'
import { createServerSupabase } from '@/lib/supabase/server'

export default async function LandingPage() {
  const supabase = await createServerSupabase()
  const {
    data: { user },
  } = await supabase.auth.getUser()
  const authed = Boolean(user)

  return (
    <div className="relative min-h-screen bg-bg font-sans text-ink">
      <Nav authed={authed} />
      <Hero />
      <Marquee />
      <Manifesto />
      <Agents />
      <ProductCanvas />
      <Capabilities />
      <Metrics />
      <Pricing />
      <FAQ />
      <CTA />
      <Footer />
    </div>
  )
}

/* ----------------------------------------------------------------------- */
/*  Nav                                                                     */
/* ----------------------------------------------------------------------- */

function Nav({ authed }: { authed: boolean }) {
  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-bg/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink">
            <Image
              src="/anna-avatar.svg"
              alt="AnnaAi"
              width={22}
              height={22}
              className="invert"
              priority
            />
          </div>
          <span className="font-display text-[17px] font-semibold tracking-tight">
            AnnaAi
          </span>
        </Link>

        <nav className="hidden items-center gap-9 text-[13.5px] font-medium text-muted md:flex">
          <a href="#agents" className="transition hover:text-ink">Agents</a>
          <a href="#product" className="transition hover:text-ink">Product</a>
          <a href="#pricing" className="transition hover:text-ink">Pricing</a>
          <a href="#faq" className="transition hover:text-ink">FAQ</a>
        </nav>

        <div className="flex items-center gap-2">
          {authed ? (
            <>
              <Link
                href="/dashboard"
                className="group inline-flex items-center gap-1.5 rounded-lg bg-ink px-3.5 py-2 text-[13.5px] font-medium text-white transition hover:bg-ink-2"
              >
                Dashboard
                <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" />
              </Link>
              <SignOutButton />
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="hidden rounded-lg px-3 py-2 text-[13.5px] font-medium text-ink transition hover:bg-accent sm:inline-flex"
              >
                Sign in
              </Link>
              <Link
                href="/register"
                className="group inline-flex items-center gap-1.5 rounded-lg bg-ink px-3.5 py-2 text-[13.5px] font-medium text-white transition hover:bg-ink-2"
              >
                Start free
                <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" />
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

/* ----------------------------------------------------------------------- */
/*  Hero                                                                    */
/* ----------------------------------------------------------------------- */

function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      <div className="pointer-events-none absolute inset-0 grid-bg [mask-image:radial-gradient(ellipse_60%_60%_at_50%_30%,#000_40%,transparent_100%)]" />
      <div className="pointer-events-none absolute -top-40 left-1/2 h-[520px] w-full max-w-[820px] -translate-x-1/2 rounded-full bg-[radial-gradient(closest-side,rgba(233,69,96,0.18),transparent)]" />

      <div className="relative mx-auto max-w-6xl px-6 pt-24 pb-28 md:pt-32 md:pb-40">
        <div className="mx-auto max-w-4xl text-center fade-up">
          <h1 className="font-display mt-8 text-balance text-5xl font-semibold leading-[1.02] tracking-tight text-ink sm:text-6xl md:text-[80px]">
            Marketing that runs
            <br />
            <span className="text-gradient-brand">while you sleep.</span>
          </h1>

          <p className="mx-auto mt-7 max-w-2xl text-pretty text-[17px] leading-relaxed text-muted md:text-[19px]">
            AnnaAi is a crew of five autonomous agents that research, write,
            and publish content for your brand every morning. You wake up,
            you approve, they ship.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/register"
              className="group inline-flex items-center gap-2 rounded-xl bg-ink px-5 py-3.5 text-[14px] font-semibold text-white shadow-[0_1px_0_0_rgba(255,255,255,0.15)_inset,0_8px_32px_-8px_rgba(10,10,10,0.4)] transition hover:bg-ink-2"
            >
              Deploy your crew
              <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
            </Link>
            <a
              href="#product"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface px-5 py-3.5 text-[14px] font-semibold text-ink transition hover:border-border-strong"
            >
              See the product
              <ArrowUpRight className="h-4 w-4" />
            </a>
          </div>

        </div>

        <BrowserMock />
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Browser mock under hero                                                 */
/* ----------------------------------------------------------------------- */

function BrowserMock() {
  return (
    <div className="relative mx-auto mt-20 max-w-5xl fade-up">
      <div className="absolute -inset-4 rounded-[28px] bg-linear-to-br from-primary/10 via-ink/5 to-transparent blur-2xl" />
      <div className="relative overflow-hidden rounded-2xl border border-border bg-surface shadow-[0_1px_0_0_rgba(255,255,255,0.8)_inset,0_30px_80px_-20px_rgba(10,10,10,0.25),0_8px_24px_-8px_rgba(10,10,10,0.15)]">
        {/* Window chrome */}
        <div className="flex items-center justify-between border-b border-border bg-bg px-4 py-2.5">
          <div className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
            <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
            <span className="h-3 w-3 rounded-full bg-[#28c840]" />
          </div>
          <div className="flex items-center gap-1.5 rounded-md bg-surface px-3 py-1 font-mono text-[11px] text-muted">
            <span className="text-primary">●</span> app.annaai.io /
            dashboard
          </div>
          <div className="h-3 w-3" />
        </div>

        {/* App body */}
        <div className="grid grid-cols-1 gap-0 sm:grid-cols-12">
          {/* Sidebar — hidden on very small screens */}
          <div className="hidden border-r border-border bg-bg p-4 sm:col-span-3 sm:block">
            <div className="flex items-center gap-2 rounded-md bg-ink px-2.5 py-1.5 text-[11px] font-semibold text-white">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Dashboard
            </div>
            {['Drafts', 'Runs', 'Chat', 'Integrations'].map((item) => (
              <div
                key={item}
                className="mt-1 px-2.5 py-1.5 text-[11px] text-muted"
              >
                {item}
              </div>
            ))}
          </div>

          {/* Main */}
          <div className="col-span-1 p-4 sm:col-span-9 sm:p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-muted">
                  Today · Apr 14
                </div>
                <div className="font-display mt-0.5 text-lg font-semibold tracking-tight">
                  Morning brief
                </div>
              </div>
              <div className="rounded-md bg-primary px-2.5 py-1 text-[10px] font-semibold text-white">
                CREW ACTIVE
              </div>
            </div>

            <div className="mt-4 grid grid-cols-3 gap-3">
              {[
                { k: 'Sessions', v: '+42%', trend: true },
                { k: 'Drafts', v: '3 ready', trend: false },
                { k: 'Queue', v: '2 posts', trend: false },
              ].map((s) => (
                <div
                  key={s.k}
                  className="rounded-lg border border-border bg-bg p-3"
                >
                  <div className="text-[10px] uppercase tracking-wide text-muted">
                    {s.k}
                  </div>
                  <div
                    className={
                      s.trend
                        ? 'font-display mt-1 text-lg font-semibold text-primary'
                        : 'font-display mt-1 text-lg font-semibold text-ink'
                    }
                  >
                    {s.v}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 rounded-lg border border-border bg-linear-to-br from-primary/5 to-transparent p-4">
              <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-primary">
                <Sparkles className="h-3 w-3" />
                Draft ready
              </div>
              <div className="mt-2 text-[14px] font-semibold tracking-tight">
                The 5 onboarding metrics we stopped tracking
              </div>
              <div className="mt-1 font-mono text-[10.5px] text-muted">
                1,214 words · seo 87 · voice match 96%
              </div>
              <div className="mt-3 flex gap-2">
                <button className="rounded-md bg-ink px-3 py-1.5 text-[11px] font-semibold text-white">
                  Approve
                </button>
                <button className="rounded-md border border-border px-3 py-1.5 text-[11px] font-semibold">
                  Edit
                </button>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between font-mono text-[10px] text-muted">
              <span>researcher · analyst · strategist · creator · publisher</span>
              <span>5/5 idle · next run 06:00</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ----------------------------------------------------------------------- */
/*  Marquee                                                                 */
/* ----------------------------------------------------------------------- */

function Marquee() {
  const integrations = [
    'WordPress',
    'Google Analytics',
    'Search Console',
    'Ghost (soon)',
  ]
  return (
    <section className="border-b border-border bg-surface">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <p className="text-center font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
          Plugs into the tools you already use
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-x-12 gap-y-4 text-[15px] font-medium text-ink/70">
          {integrations.map((name) => (
            <span key={name} className="font-display tracking-tight">
              {name}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Manifesto                                                               */
/* ----------------------------------------------------------------------- */

function Manifesto() {
  return (
    <section className="relative border-b border-border">
      <div className="mx-auto grid max-w-6xl gap-8 px-6 py-16 md:gap-16 md:py-28 md:grid-cols-12">
        <div className="md:col-span-4">
          <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
            01 — The shift
          </div>
        </div>
        <div className="md:col-span-8">
          <h2 className="font-display text-balance text-4xl font-semibold leading-[1.1] tracking-tight text-ink sm:text-5xl md:text-[56px]">
            You don't need another
            <br />
            <span className="text-muted">content tool.</span>{' '}
            You need a team.
          </h2>
          <div className="mt-8 space-y-5 text-[17px] leading-relaxed text-muted">
            <p>
              Generic AI writers give you 10,000 words of average. Agencies give
              you invoices. Freelancers ghost. Meanwhile, the one thing that
              actually grows your business — consistent, on-brand publishing —
              is quietly the one thing you've stopped doing.
            </p>
            <p className="text-ink">
              Anna is different. Five specialists. One coordinated crew.
              Daily. Autonomous. In your voice.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Agents                                                                  */
/* ----------------------------------------------------------------------- */

function Agents() {
  const agents = [
    {
      n: '01',
      name: 'Researcher',
      role: 'Scouts the web',
      body: 'Watches your industry, competitors, and trending topics every morning before you wake up.',
    },
    {
      n: '02',
      name: 'Analyst',
      role: 'Reads your numbers',
      body: 'Pulls Google Analytics and Search Console to know exactly what worked and what tanked.',
    },
    {
      n: '03',
      name: 'Strategist',
      role: 'Picks the angle',
      body: 'Synthesizes research plus analytics into the single best content angle for today.',
    },
    {
      n: '04',
      name: 'Creator',
      role: 'Writes the draft',
      body: 'Produces a full post in your brand voice — headline, body, meta description, hero image.',
    },
    {
      n: '05',
      name: 'Publisher',
      role: 'Ships on approval',
      body: 'Files the draft for your review. One click and it goes live on WordPress, scheduled and tagged.',
    },
  ]

  return (
    <section id="agents" className="relative border-b border-border bg-ink text-white">
      <div className="pointer-events-none absolute inset-0 opacity-[0.08] bg-[radial-gradient(circle,#ffffff_1px,transparent_1px)] bg-size-[24px_24px]" />

      <div className="relative mx-auto max-w-6xl px-6 py-28">
        <div className="flex items-end justify-between">
          <div>
            <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
              02 — The crew
            </div>
            <h2 className="font-display mt-4 text-balance text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl md:text-[56px]">
              Five specialists.
              <br />
              <span className="text-white/50">One daily hand-off.</span>
            </h2>
          </div>
          <div className="hidden font-mono text-[11px] uppercase tracking-wider text-white/40 md:block">
            [crew.sequential]
          </div>
        </div>

        <div className="mt-16 grid gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/5 md:grid-cols-5">
          {agents.map((a) => (
            <div
              key={a.name}
              className="group relative bg-ink p-6 transition hover:bg-white/3"
            >
              <div className="font-mono text-[10px] uppercase tracking-wider text-primary">
                {a.n}
              </div>
              <div className="font-display mt-8 text-xl font-semibold tracking-tight">
                {a.name}
              </div>
              <div className="mt-1 text-[12px] text-white/50">{a.role}</div>
              <p className="mt-5 text-[13.5px] leading-relaxed text-white/70">
                {a.body}
              </p>
              <div className="absolute bottom-0 left-0 h-px w-0 bg-primary transition-all duration-700 group-hover:w-full" />
            </div>
          ))}
        </div>

        <div className="mt-8 flex items-center gap-2 font-mono text-[11px] uppercase tracking-wider text-white/40">
          <span className="h-px flex-1 bg-white/10" />
          Sequential pipeline · per-tenant memory · ship on approval
          <span className="h-px flex-1 bg-white/10" />
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Product canvas (big product moment)                                     */
/* ----------------------------------------------------------------------- */

function ProductCanvas() {
  return (
    <section
      id="product"
      className="relative overflow-hidden border-b border-border"
    >
      <div className="mx-auto max-w-6xl px-6 py-28">
        <div className="max-w-2xl">
          <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
            03 — The product
          </div>
          <h2 className="font-display mt-4 text-balance text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl md:text-[56px]">
            A dashboard that does
            <br />
            <span className="text-muted">the work for you.</span>
          </h2>
          <p className="mt-6 text-[17px] leading-relaxed text-muted">
            Approve, edit, chat, publish. Everything in one place — no prompt
            engineering, no copy-pasting, no tabs.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {[
            {
              tag: 'Drafts',
              title: 'Inline approval flow',
              body: 'Edit headlines and body in the same view you approve in. Reject with feedback — Anna learns.',
            },
            {
              tag: 'Runs',
              title: 'Full audit trail',
              body: 'Every decision by every agent, logged. Know what shipped, when, and why.',
            },
            {
              tag: 'Chat',
              title: 'Streaming Q&A',
              body: 'Ask Anna what to write next. She answers with your data, not guesses.',
            },
          ].map((c) => (
            <div
              key={c.tag}
              className="group relative overflow-hidden rounded-2xl border border-border bg-surface p-7 transition hover:border-ink"
            >
              <div className="font-mono text-[10.5px] uppercase tracking-wider text-primary">
                {c.tag}
              </div>
              <h3 className="font-display mt-8 text-xl font-semibold tracking-tight">
                {c.title}
              </h3>
              <p className="mt-3 text-[14px] leading-relaxed text-muted">
                {c.body}
              </p>
              <ArrowUpRight className="absolute right-6 top-6 h-4 w-4 text-muted-2 transition group-hover:text-ink group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Capabilities                                                            */
/* ----------------------------------------------------------------------- */

function Capabilities() {
  const rows = [
    {
      label: 'Brand voice',
      value: 'Learned from your site on day one. Reinforced every approval.',
    },
    {
      label: 'Publishing',
      value: 'WordPress (REST), Ghost (soon), manual HTML export.',
    },
    {
      label: 'Analytics',
      value: 'Google Analytics 4, Search Console, post-publish feedback loop.',
    },
    {
      label: 'Memory',
      value: 'Vector memory, per-tenant isolated. Learns from every approval.',
    },
    {
      label: 'Model',
      value: 'Frontier LLMs, orchestrated as a multi-agent pipeline.',
    },
    {
      label: 'Runtime',
      value: 'Queue-backed workers. Scheduled daily runs in your timezone.',
    },
    {
      label: 'Tenancy',
      value: 'Row-level tenant isolation. Zero cross-tenant reads.',
    },
    {
      label: 'Billing',
      value: 'Monthly subscription in GHS. Pro and Business tiers.',
    },
  ]

  return (
    <section className="border-b border-border bg-surface">
      <div className="mx-auto max-w-6xl px-6 py-28">
        <div className="grid gap-8 md:gap-16 md:grid-cols-12">
          <div className="md:col-span-4">
            <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
              04 — Under the hood
            </div>
            <h2 className="font-display mt-4 text-balance text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
              Seriously built.
            </h2>
            <p className="mt-5 text-[15.5px] leading-relaxed text-muted">
              No prompt hacks. No scraping loopholes. Production-grade
              architecture from day one.
            </p>
          </div>

          <div className="md:col-span-8">
            <div className="divide-y divide-border border-y border-border">
              {rows.map((r) => (
                <div
                  key={r.label}
                  className="grid gap-1 py-5 sm:grid-cols-12 sm:gap-4"
                >
                  <div className="font-mono text-[11px] uppercase tracking-wider text-muted sm:col-span-4">
                    {r.label}
                  </div>
                  <div className="text-[15px] text-ink sm:col-span-8">
                    {r.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Metrics band                                                            */
/* ----------------------------------------------------------------------- */

function Metrics() {
  const stats = [
    { k: '5', label: 'Specialist agents' },
    { k: '<5 min', label: 'Per draft' },
    { k: '06:00', label: 'Daily kickoff' },
    { k: '100%', label: 'Human approved' },
  ]
  return (
    <section className="border-b border-border bg-bg">
      <div className="mx-auto grid max-w-6xl grid-cols-2 divide-border px-6 py-14 sm:grid-cols-4 sm:divide-x">
        {stats.map((s, i) => (
          <div
            key={s.k}
            className={i === 0 ? 'px-4 sm:px-8' : 'px-4 sm:px-8'}
          >
            <div className="font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
              {s.k}
            </div>
            <div className="mt-2 font-mono text-[11px] uppercase tracking-wider text-muted">
              {s.label}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Pricing                                                                 */
/* ----------------------------------------------------------------------- */

function Pricing() {
  const tiers = [
    {
      name: 'Free',
      price: 'GHS 0',
      interval: 'forever',
      tagline: 'For solo founders getting started.',
      cta: 'Start free',
      highlight: false,
      features: [
        '1 daily run',
        '3 drafts per run',
        'WordPress publishing',
        'Email brief',
        'Community support',
      ],
    },
    {
      name: 'Pro',
      price: 'GHS 120',
      interval: '/ month',
      tagline: 'For growing brands publishing daily.',
      cta: 'Upgrade to Pro',
      highlight: true,
      features: [
        '3 daily runs',
        '10 drafts per run',
        'Full analytics feedback loop',
        'Brand voice learning',
        'Priority queue',
        'Priority support',
      ],
    },
    {
      name: 'Business',
      price: 'GHS 480',
      interval: '/ month',
      tagline: 'For teams running multi-site operations.',
      cta: 'Talk to us',
      highlight: false,
      features: [
        'Unlimited runs',
        'Unlimited drafts',
        'Multi-site support',
        'Custom integrations',
        'Dedicated onboarding',
        'SLA',
      ],
    },
  ]

  return (
    <section id="pricing" className="border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-28">
        <div className="mx-auto max-w-2xl text-center">
          <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
            05 — Pricing
          </div>
          <h2 className="font-display mt-4 text-balance text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl md:text-[56px]">
            Start free. Scale when you win.
          </h2>
          <p className="mt-5 text-[17px] leading-relaxed text-muted">
            Every plan includes the full five-agent crew. Upgrades unlock more
            runs and tighter feedback loops.
          </p>
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          {tiers.map((t) => (
            <div
              key={t.name}
              className={
                t.highlight
                  ? 'relative flex flex-col rounded-2xl border border-ink bg-ink p-8 text-white shadow-[0_30px_80px_-20px_rgba(10,10,10,0.35)]'
                  : 'relative flex flex-col rounded-2xl border border-border bg-surface p-8'
              }
            >
              {t.highlight ? (
                <div className="absolute -top-2.5 left-8 rounded-full bg-primary px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-wider text-white">
                  Most popular
                </div>
              ) : null}
              <div className="font-display text-lg font-semibold tracking-tight">
                {t.name}
              </div>
              <div
                className={
                  t.highlight
                    ? 'mt-1 text-[13px] text-white/60'
                    : 'mt-1 text-[13px] text-muted'
                }
              >
                {t.tagline}
              </div>

              <div className="mt-6 flex items-baseline gap-1.5">
                <span className="font-display text-4xl font-semibold tracking-tight">
                  {t.price}
                </span>
                <span
                  className={
                    t.highlight
                      ? 'text-[13px] text-white/60'
                      : 'text-[13px] text-muted'
                  }
                >
                  {t.interval}
                </span>
              </div>

              <Link
                href="/register"
                className={
                  t.highlight
                    ? 'mt-7 inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-[14px] font-semibold text-white transition hover:bg-primary-hover'
                    : 'mt-7 inline-flex items-center justify-center gap-2 rounded-lg bg-ink px-5 py-3 text-[14px] font-semibold text-white transition hover:bg-ink-2'
                }
              >
                {t.cta}
                <ArrowRight className="h-4 w-4" />
              </Link>

              <div
                className={
                  t.highlight
                    ? 'mt-8 h-px w-full bg-white/10'
                    : 'mt-8 h-px w-full bg-border'
                }
              />

              <ul
                className={
                  t.highlight
                    ? 'mt-6 space-y-3 text-[14px] text-white/80'
                    : 'mt-6 space-y-3 text-[14px] text-ink'
                }
              >
                {t.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5">
                    <Check
                      className={
                        t.highlight
                          ? 'mt-0.5 h-4 w-4 shrink-0 text-primary'
                          : 'mt-0.5 h-4 w-4 shrink-0 text-ink'
                      }
                    />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  FAQ                                                                     */
/* ----------------------------------------------------------------------- */

function FAQ() {
  const items = [
    {
      q: 'Does Anna publish without asking me?',
      a: 'No. Every draft waits in your dashboard until you approve. Anna can auto-publish to WordPress once you press the button — never before.',
    },
    {
      q: 'How does Anna learn my brand voice?',
      a: 'On day one she crawls your site and stores every page in a per-tenant vector memory. After that, every approval and rejection becomes training signal. She sounds more like you over time, not less.',
    },
    {
      q: 'What if I already have a content team?',
      a: 'Anna pairs well with senior strategists. She handles volume — drafting, research, first passes. Your team edits and directs. Most customers use her as a junior writer that never sleeps.',
    },
    {
      q: 'Is my data used to train models?',
      a: 'No. Your content, analytics, and brand memory stay in per-tenant isolated storage. We use Anthropic Claude via API — Anthropic does not train on API inputs.',
    },
    {
      q: 'Can I cancel anytime?',
      a: 'Yes. One click from the billing tab. You keep access until the end of your paid period.',
    },
  ]

  return (
    <section id="faq" className="border-b border-border bg-surface">
      <div className="mx-auto grid max-w-6xl gap-8 px-6 py-16 md:gap-16 md:py-28 md:grid-cols-12">
        <div className="md:col-span-4">
          <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary">
            06 — FAQ
          </div>
          <h2 className="font-display mt-4 text-balance text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl">
            Questions,
            <br />
            <span className="text-muted">answered.</span>
          </h2>
        </div>
        <div className="md:col-span-8">
          <div className="divide-y divide-border border-y border-border">
            {items.map((item) => (
              <details
                key={item.q}
                className="group py-5 transition"
              >
                <summary className="flex cursor-pointer items-center justify-between gap-4 text-[16px] font-semibold tracking-tight text-ink">
                  {item.q}
                  <span className="font-mono text-[14px] text-muted transition group-open:rotate-45">
                    +
                  </span>
                </summary>
                <p className="mt-3 max-w-2xl text-[14.5px] leading-relaxed text-muted">
                  {item.a}
                </p>
              </details>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  CTA                                                                     */
/* ----------------------------------------------------------------------- */

function CTA() {
  return (
    <section className="relative border-b border-border">
      <div className="mx-auto max-w-6xl px-6 py-28">
        <div className="relative overflow-hidden rounded-3xl border border-ink bg-ink p-8 text-center text-white sm:p-12 md:p-20">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 opacity-10 bg-[radial-gradient(circle,#ffffff_1px,transparent_1px)] bg-size-[24px_24px]"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute -top-40 left-1/2 h-125 w-125 -translate-x-1/2 rounded-full bg-[radial-gradient(closest-side,rgba(233,69,96,0.35),transparent)]"
          />

          <div className="relative">
            <h2 className="font-display mx-auto max-w-3xl text-balance text-5xl font-semibold leading-[1.02] tracking-tight sm:text-6xl md:text-[72px]">
              Your new marketing team
              <br />
              <span className="text-white/40">starts tomorrow.</span>
            </h2>
            <p className="mx-auto mt-7 max-w-xl text-[17px] leading-relaxed text-white/60">
              Five minutes to set up. Your first draft lands in your inbox in
              the morning.
            </p>
            <div className="mt-10 flex flex-wrap justify-center gap-3">
              <Link
                href="/register"
                className="group inline-flex items-center gap-2 rounded-xl bg-white px-6 py-4 text-[14px] font-semibold text-ink shadow-[0_30px_80px_-20px_rgba(255,255,255,0.25)] transition hover:bg-white/90"
              >
                Deploy your crew
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/5 px-6 py-4 text-[14px] font-semibold text-white transition hover:bg-white/10"
              >
                Sign in
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

/* ----------------------------------------------------------------------- */
/*  Footer                                                                  */
/* ----------------------------------------------------------------------- */

function Footer() {
  return (
    <footer className="bg-bg">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid gap-10 md:grid-cols-12">
          <div className="md:col-span-5">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink">
                <Image
                  src="/anna-avatar.svg"
                  alt="AnnaAi"
                  width={22}
                  height={22}
                  className="invert"
                />
              </div>
              <span className="font-display text-[17px] font-semibold tracking-tight">
                AnnaAi
              </span>
            </div>
            <p className="mt-4 max-w-sm text-[14px] text-muted">
              Five autonomous agents that research, write, and publish content
              for your brand — every single morning.
            </p>
          </div>

          <div className="md:col-span-7 grid grid-cols-2 gap-8 sm:grid-cols-3">
            <FooterCol
              title="Product"
              links={[
                { label: 'Agents', href: '#agents' },
                { label: 'Dashboard', href: '#product' },
                { label: 'Pricing', href: '#pricing' },
              ]}
            />
            <FooterCol
              title="Resources"
              links={[
                { label: 'FAQ', href: '#faq' },
                { label: 'Docs', href: '#' },
                { label: 'Changelog', href: '#' },
              ]}
            />
            <FooterCol
              title="Account"
              links={[
                { label: 'Sign in', href: '/login' },
                { label: 'Sign up', href: '/register' },
                { label: 'Contact', href: 'mailto:hello@annaai.io' },
              ]}
            />
          </div>
        </div>

        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-border pt-8 text-[12px] text-muted sm:flex-row">
          <div className="font-mono">
            © {new Date().getFullYear()} AnnaAi · all rights reserved
          </div>
          <div className="flex gap-4 font-mono">
            <a href="/terms" className="hover:text-ink transition">Terms</a>
            <a href="/privacy" className="hover:text-ink transition">Privacy</a>
          </div>
          <div className="font-mono uppercase tracking-wider">
            built in africa · running everywhere
          </div>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({
  title,
  links,
}: {
  title: string
  links: { label: string; href: string }[]
}) {
  return (
    <div>
      <div className="font-mono text-[10.5px] uppercase tracking-wider text-muted">
        {title}
      </div>
      <ul className="mt-4 space-y-2.5 text-[14px]">
        {links.map((l) => (
          <li key={l.label}>
            <Link
              href={l.href}
              className="text-ink transition hover:text-primary"
            >
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
