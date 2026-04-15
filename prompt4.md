You are continuing to build AnnaAi. The backend (Batches 1-3) is complete.
Now build the complete Next.js 14 frontend using the App Router.

Design philosophy for AnnaAi's dashboard:
- Clean, modern, professional — not flashy
- Colour palette: 
    Primary bg: #0f0f1a (very dark navy)
    Surface: #1a1a2e (dark navy)
    Surface elevated: #16213e (slightly lighter)
    Accent: #e94560 (coral red — use for CTAs, active states, badges)
    Accent secondary: #0f3460 (deep blue)
    Text primary: #eaeaea
    Text secondary: #8892a4
    Success: #4caf7d
    Warning: #f5a623
    Border: rgba(255,255,255,0.08)
- Typography: 
    Headings: 'Sora', sans-serif (Google Fonts)
    Body: 'Inter', sans-serif
- Dark theme only (no light mode toggle needed for MVP)
- Anna's avatar: a simple, geometric SVG face/icon 
  (not a photo — abstract, friendly, professional)
- Sidebar navigation, not top nav
- Mobile-responsive (sidebar collapses to hamburger on mobile)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1: CONFIGURATION FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write the complete contents of:

package.json:
Dependencies:
- next: 16.2.x
- react: 19.x
- react-dom: 19.x
- typescript
- @supabase/supabase-js
- @supabase/auth-helpers-nextjs
- tailwindcss
- @tailwindcss/typography
- autoprefixer
- postcss
- recharts (for charts)
- react-markdown (for rendering draft content)
- react-hot-toast (for notifications)
- date-fns (for date formatting)
- lucide-react (for icons)
- clsx (for conditional classnames)
- @tanstack/react-query (for server state management)

Scripts: dev, build, start, lint, type-check

tailwind.config.ts:
- Extend the color palette with the exact AnnaAi colours above
- Add Sora and Inter to font family
- Content paths for tree-shaking
- Enable @tailwindcss/typography plugin

next.config.js:
- Image domains: image.pollinations.ai, and your Supabase project domain
- Environment variables exposure to client 
  (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, 
   NEXT_PUBLIC_API_URL)
- Strict mode: true

tsconfig.json: Standard Next.js TypeScript config with path aliases:
- @/* maps to ./*
- @components/* maps to ./components/*
- @lib/* maps to ./lib/*

frontend/lib/types.ts:
Write TypeScript interfaces for every data type:
Organization, User, AgentRun, ContentDraft, 
ContentMetrics, ChatMessage, OAuthIntegration, 
OnboardingStatus, PaginatedResponse<T>, RunStats,
BrandVoice, OnboardingChecklist

frontend/lib/api.ts:
Write a typed API client that wraps all backend calls.
Base URL from NEXT_PUBLIC_API_URL env var.
Every method must:
- Include the Supabase access token in Authorization header
- Handle 401 by redirecting to /login
- Handle network errors gracefully
- Be fully typed with request and response types

Implement methods:
// Auth
register(email, password, fullName, orgName): Promise<AuthResponse>
login(email, password): Promise<AuthResponse>
logout(): Promise<void>
getMe(): Promise<User>

// Onboarding
submitWebsite(url): Promise<void>
getOnboardingStatus(): Promise<OnboardingStatus>
saveBrandVoice(data): Promise<Organization>
completeOnboarding(): Promise<void>

// Runs
getRuns(params): Promise<PaginatedResponse<AgentRun>>
getRun(id): Promise<RunDetail>
triggerRun(): Promise<{run_id: string}>
getRunStats(): Promise<RunStats>

// Drafts
getDrafts(params): Promise<PaginatedResponse<ContentDraft>>
getDraft(id): Promise<ContentDraft>
updateDraft(id, data): Promise<ContentDraft>
approveDraft(id): Promise<void>
rejectDraft(id, reason): Promise<void>
deleteDraft(id): Promise<void>

// Chat
getChatHistory(): Promise<ChatMessage[]>
sendMessage(content): Promise<ReadableStream>  // SSE stream
clearChatHistory(): Promise<void>

// Integrations
getIntegrations(): Promise<OAuthIntegration[]>
getGoogleAuthUrl(): Promise<{auth_url: string}>
connectWordPress(siteUrl, username, appPassword): Promise<void>
disconnectIntegration(platform): Promise<void>

frontend/lib/supabase.ts:
Set up Supabase client for the frontend.
Export createClient() and the auth helpers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2: ROOT LAYOUT AND GLOBAL STYLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write frontend/app/globals.css:
- Import Google Fonts: Sora (600, 700) and Inter (400, 500)
- CSS custom properties for all colours and spacing
- Base styles: html, body background, font, color
- Scrollbar styling: thin, dark, matches the theme
- Selection highlight: accent colour
- Smooth scrolling
- Focus visible styles (accessibility)

Write frontend/app/layout.tsx:
- Root layout with html, body
- Loads Sora and Inter fonts
- Wraps children in QueryClientProvider (react-query)
- Wraps in Toaster (react-hot-toast)
- Sets metadata: title "AnnaAi — Your Autonomous Marketing Agent",
  description, OpenGraph tags
- Dark color-scheme meta

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3: UI PRIMITIVE COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write each component completely with full TypeScript props and styling:

frontend/components/ui/Button.tsx
Props: variant ('primary'|'secondary'|'ghost'|'danger'), 
       size ('sm'|'md'|'lg'), loading (bool), disabled (bool),
       children, onClick, type, className
Primary: coral red bg, white text, hover darkens
Secondary: surface bg, accent border, accent text
Ghost: transparent, text only, hover surface bg
Danger: red bg, white text
Loading state: shows spinner, disables clicks

frontend/components/ui/Card.tsx
Props: children, className, padding ('sm'|'md'|'lg'), hoverable (bool)
Dark surface background, subtle border, rounded corners
Hoverable variant: slight glow on hover using box-shadow

frontend/components/ui/Badge.tsx
Props: variant ('success'|'warning'|'error'|'info'|'neutral'), children
Colour-coded pill badges for statuses

frontend/components/ui/Input.tsx
Props: label, error, hint, type, placeholder, value, onChange, 
       disabled, required, className
Dark surface input, accent border on focus
Shows error message in red below if error prop present

frontend/components/ui/Modal.tsx
Props: isOpen, onClose, title, children, size ('sm'|'md'|'lg')
Backdrop blur overlay, centered card
ESC key closes, click outside closes
Accessible: focus trap, aria-modal

frontend/components/ui/Spinner.tsx
Props: size ('sm'|'md'|'lg'), color
Animated CSS spinner, matches accent colour

frontend/components/ui/EmptyState.tsx
Props: icon (ReactNode), title, description, action (ReactNode)
Centered empty state for empty lists/tables

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4: LAYOUT COMPONENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

frontend/components/layout/Sidebar.tsx
Full sidebar with:
- AnnaAi logo (text-based with accent colour "Anna" + "Ai" in different weights)
- Navigation links with icons (Lucide):
  Dashboard (LayoutDashboard icon)
  Drafts (FileText icon) + badge showing pending drafts count
  Runs (Activity icon)
  Chat (MessageCircle icon)
  Integrations (Plug icon)
  Settings (Settings icon)
- Bottom: user avatar (initials), name, email, logout button
- On mobile (< 768px): hidden by default, slides in on hamburger click
- Active link highlighted with accent left border + subtle background

frontend/components/layout/Header.tsx
Top header bar:
- Mobile: hamburger menu button
- Page title (passed as prop)
- Right side: 
  "Trigger Run" button (visible to admins)
  Notification bell (future use — just a placeholder icon)
  User avatar with dropdown (shows name/email, logout)

frontend/components/layout/DashboardShell.tsx
Wraps authenticated pages:
- Sidebar + Header + main content area
- Checks auth: if no session, redirect to /login
- Fetches org info on mount, stores in context
- Mobile responsive: sidebar overlay on mobile

Write a simple React context in frontend/lib/hooks/useOrganization.ts:
Provides org data to all dashboard pages.
Fetches from GET /api/auth/me on mount.
Exposes: org, user, isLoading, refetch.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5: AUTHENTICATION PAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

frontend/app/(auth)/login/page.tsx
Full-page login:
- Left side (desktop): dark panel with AnnaAi branding, 
  tagline "Your marketing team. Working 24/7.", 
  3 feature highlights with icons
- Right side: login form
  Email input, password input (show/hide toggle), 
  "Log In" button, link to register page
- On submit: call api.login(), store tokens, redirect to /dashboard
- If already logged in: redirect to /dashboard immediately
- Show error toast on failed login
- Forgot password link (placeholder for now)

frontend/app/(auth)/register/page.tsx
Registration form:
- Full name, email, company/org name, password, confirm password
- Password strength indicator (show requirements: 8+ chars, 1 number)
- Terms of service checkbox
- On submit: call api.register(), auto-login, redirect to /onboard
- Show success: "Welcome! Check your email to confirm your account."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6: ONBOARDING WIZARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

frontend/app/onboard/page.tsx and 
frontend/components/onboarding/OnboardingWizard.tsx

Multi-step onboarding. 4 steps with progress indicator at top.
Each step is a separate component. State managed in wizard parent.

Step 1 — Connect Your Website (StepConnectWebsite.tsx):
  Anna avatar + speech bubble: "Hi! I'm Anna. Let's get started. 
  What's your website URL? I'll read everything on it to understand 
  your brand."
  Input for website URL (validate format)
  "Start Scraping" button → calls api.submitWebsite()
  After submit: shows animated progress with messages:
    "Reading your homepage..."
    "Exploring your product pages..."
    "Building your brand memory..."
  Polls api.getOnboardingStatus() every 3 seconds.
  Shows completion: "I've read X pages and learned about your brand!"
  Success → auto-advance to Step 2.

Step 2 — Brand Voice (StepBrandVoice.tsx):
  Anna speech bubble: "Tell me how you like to communicate. 
  I'll match your style in everything I write."
  Tone selector: card grid with 5 options each with icon + label + example line:
    Professional ("We help enterprises scale with confidence.")
    Casual ("Hey! We make marketing simple and fun 🎉")
    Bold ("We don't do average. We build legends.")
    Educational ("Learn how to double your traffic in 30 days.")
    Playful ("Marketing doesn't have to be boring. Pinky promise.")
  Target audience: text input ("e.g. Small business owners in Ghana")
  Primary goal: dropdown (Increase website traffic | Generate leads | 
    Grow social following | Increase sales | Build brand awareness)
  Competitor domains: up to 3 text inputs with add/remove
  Brand voice description: textarea ("Describe your tone in your own words")
  "Save & Continue" → api.saveBrandVoice()

Step 3 — Connect Accounts (StepConnectAccounts.tsx):
  Anna speech bubble: "Connect your accounts so I can see your 
  analytics and publish content for you."
  Integration cards (each shows connected/disconnected status):
    Google Analytics — "Connect Google" button → oauth flow
    WordPress — "Connect WordPress" → modal with site URL / app password fields
    More platforms (greyed out, "Coming soon"): Instagram, Mailchimp
  Each card has icon, description, and "Why?" tooltip.
  "Skip for now" text link at bottom (can connect later in settings).
  "Continue" button (enabled even if nothing connected).

Step 4 — Set Goals (StepSetGoals.tsx):
  Anna speech bubble: "Last step! When should I work and 
  what should I focus on?"
  Run time preference: "Anna runs at [6 AM UTC] every day" 
    (simple display, not editable in MVP)
  Content preferences: multi-select checkboxes:
    [ ] Blog posts
    [ ] Instagram posts  
    [ ] LinkedIn posts
    [ ] Email newsletters
  "Launch AnnaAi" button → api.completeOnboarding()
  After click: celebration animation (CSS confetti or simple scale animation)
  Then redirect to /dashboard after 2 seconds.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 7: DASHBOARD PAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

frontend/app/(dashboard)/dashboard/page.tsx

Main dashboard. Shows the most important info at a glance.

Top row — Anna Stat