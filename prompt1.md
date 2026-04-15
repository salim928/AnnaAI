You are an expert full-stack AI engineer and product architect. 
Help me build "AnnaAi" — an autonomous AI marketing agent platform 
inspired by Helena (enrichlabs.ai) — but built entirely on free-tier 
infrastructure with $0 upfront cost.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCT VISION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AnnaAi is a 24/7 autonomous marketing agent that:
- Connects to a user's website, social accounts, and ad platforms via OAuth (no manual API keys)
- Scrapes their site on onboarding to build a persistent brand memory (voice, tone, positioning, products)
- Runs a daily multi-agent crew every morning to: research competitors/trends, 
  analyse their analytics, plan content, generate copy + images, and publish — 
  or queue for human approval
- Sends a clean daily brief email summarising actions taken and performance metrics
- Has a dashboard where users monitor runs, approve high-stakes actions (e.g. paid ads), 
  and chat with Anna

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HARD CONSTRAINTS (non-negotiable)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. $0 budget — use only free tiers of all services
2. No paid SaaS subscriptions during build (no Zapier Pro, no n8n Cloud paid, etc.)
3. All code must be open-source-first (CrewAI, LangChain, LangGraph, FastAPI, Next.js)
4. Must be deployable end-to-end in under 48 hours for a prototype
5. Code must be production-ready and modular — not throwaway prototypes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FREE-TIER STACK (use exactly this)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend:     Next.js 14 (App Router) → deployed on Vercel free tier
Backend:      Python FastAPI → deployed on Render free tier
Database:     Supabase (Postgres + pgvector) → free 500MB tier
Cache/Queue:  Upstash Redis → free 10K commands/day
Scheduler:    GitHub Actions cron (free 2000 min/mo) OR Render cron jobs
LLM:          Anthropic Claude (claude-sonnet-4-20250514) — use sparingly to stay in credits
Agents:       CrewAI (Phase 0-1), upgrade to LangGraph (Phase 2+)
Scraping:     BeautifulSoup4 + Trafilatura (no Firecrawl paid tier)
Vector search:Supabase pgvector (no Pinecone needed)
Email:        Resend free tier (3,000 emails/mo)
Image gen:    Pollinations.ai (totally free, no key needed) for MVP
Auth:         Supabase Auth (built-in, free)
OAuth tokens: Supabase encrypted vault columns

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0 — WORKING PROTOTYPE (Days 1–3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: A script that takes a URL → scrapes it → builds brand memory → 
      runs a 3-agent crew → outputs a draft blog post.

Task list:
1. Set up Python project with CrewAI, LangChain, anthropic, 
   beautifulsoup4, trafilatura, supabase-py
2. Build scraper:
   - scrape_site(url) → extract all text, headings, meta descriptions
   - Chunk into 500-token segments
   - Embed using sentence-transformers (free, local — "all-MiniLM-L6-v2")
   - Store embeddings in Supabase pgvector table: brand_memory(id, chunk, embedding, url, created_at)
3. Build brand_recall(query) → retrieve top-5 relevant chunks via cosine similarity
4. Create CrewAI crew with 3 agents:
   Agent 1 — Researcher:
     - Tools: SerperDevTool (free 100 searches/mo) or DuckDuckGo search (totally free)
     - Task: "Research the top 3 trending topics in [industry] this week. 
              Return bullet points."
   Agent 2 — Strategist:
     - Tools: brand_recall() as a custom LangChain tool
     - Task: "Given these trends and our brand voice (retrieved from memory), 
              choose the best topic and outline a 500-word blog post."
   Agent 3 — Writer:
     - Tools: none
     - Task: "Write the full blog post using the outline and brand voice. 
              SEO-optimised. Include a title, meta description, and 3 headers."
5. Run crew → save output to Supabase table: content_drafts(id, type, title, body, status, created_at)
6. Print result to console

Deliverable: Single Python file (anna_mvp.py) that does all of the above end-to-end.
Test it on: https://techcabal.com (or any Ghanaian/African tech news site as sample client)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1 — CORE AUTONOMY (Days 4–14)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Daily autonomous loop + basic dashboard to see runs.

Backend tasks:
1. FastAPI app with routes:
   POST /onboard      → accepts URL, runs scraper, stores brand memory
   GET  /runs         → list all daily agent runs + status
   GET  /drafts       → list content drafts with status (draft/approved/published)
   POST /drafts/{id}/approve → set status to approved
   POST /trigger-run  → manually trigger the daily agent crew

2. Daily run pipeline (triggered by GitHub Actions cron at 06:00 UTC):
   Step 1: Pull last 7 days Google Analytics data 
           (use google-analytics-data library, OAuth token from Supabase)
   Step 2: Run Researcher agent (DuckDuckGo search — trending topics + competitor headlines)
   Step 3: Run Analyst agent — summarise GA data into 3-sentence performance report
   Step 4: Run Strategist agent — decide: blog post? social post? email newsletter?
   Step 5: Run Creator agent — generate content + Pollinations.ai image
   Step 6: Save to content_drafts → send daily brief email via Resend
   
3. Daily brief email template:
   Subject: "Anna's Daily Report — [Date]"
   Body:
   - Performance summary (traffic, top pages, conversions)
   - Content created today (with preview + approve link)
   - What Anna plans to do tomorrow
   - 1 insight ("Your competitor posted about X — consider this angle")

Frontend tasks:
1. Next.js dashboard with:
   - /onboard page: paste URL + connect accounts → trigger /onboard API
   - /dashboard: cards showing runs, drafts, traffic trend (chart.js)
   - /drafts: list of AI-generated content with Approve / Edit / Reject buttons
   - /chat: simple chat UI to ask "Anna" questions about performance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 2 — INTEGRATIONS (Days 15–30)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Real publishing (not just drafts) + OAuth flow so users connect 
      their accounts without ever seeing an API key.

Priority integrations (in order of effort vs. value):
1. WordPress REST API — publish blog posts directly (easiest, huge user base)
   - Store: wp_url, wp_username, wp_app_password in Supabase (encrypted)
   - Tool: create_wordpress_post(title, content, status="draft")

2. Google Search Console API — get keyword performance data
   - OAuth 2.0 flow: user clicks "Connect Google" → OAuth callback → 
     store refresh_token encrypted in Supabase
   - Tool: get_top_keywords(site_url, days=30)

3. Instagram Graph API (free) — post images + captions
   - OAuth via Facebook Developer app (free to create)
   - Tool: publish_instagram_post(image_url, caption, hashtags)

4. Mailchimp API (free tier 500 contacts) — send email campaigns
   - Tool: send_campaign(subject, html_body, list_id)

Security rules:
- Never expose tokens to frontend — all OAuth exchanges happen server-side
- Store tokens in Supabase with pgcrypto encryption: 
  UPDATE oauth_tokens SET token = pgp_sym_encrypt(token, 'secret_key')
- Rotate tokens automatically using refresh_token flow

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 3 — SCALE + POLISH (Days 31–60)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Multi-tenant SaaS (multiple users/businesses), paid tier readiness.

1. Multi-tenancy:
   - Add organization_id to all Supabase tables
   - Row-level security (RLS) policies so each user sees only their data
   - Supabase Auth handles user sessions

2. Upgrade from CrewAI to LangGraph for reliability:
   - Stateful graph with checkpointing (resume on failure)
   - Human-in-loop: graph pauses at "publish_post" node, 
     waits for approval webhook from frontend

3. Monetisation readiness (still $0 to build):
   - Add Paystack (Ghanaian/African payment gateway — free to integrate)
     or Flutterwave for GHS billing
   - Plans: Free (1 run/week, 3 drafts), Pro GHS 149/mo (daily runs, publish), 
     Business GHS 399/mo (all integrations + priority support)

4. Performance evals:
   - After publishing, track: page views (GA4), social engagement (platform APIs)
   - Feed back into next day's Analyst agent as performance signal
   - "Anna learns" — content that performed well → weights future content decisions

5. UI polish:
   - Anna avatar (simple SVG face, not a photo)
   - Onboarding wizard (5 steps: URL → brand voice quiz → connect accounts → 
     set goals → first run)
   - Mobile-responsive dashboard
   - Slack webhook support: send daily brief to a Slack channel (free Slack webhooks)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATABASE SCHEMA (Supabase / Postgres)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Create these tables in order:

-- Users/orgs
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  website_url TEXT,
  industry TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Brand memory (RAG)
CREATE TABLE brand_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organizations(id),
  chunk TEXT NOT NULL,
  embedding VECTOR(384),  -- all-MiniLM-L6-v2 dimension
  source_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ON brand_memory USING ivfflat (embedding vector_cosine_ops);

-- OAuth tokens (encrypted)
CREATE TABLE oauth_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organizations(id),
  platform TEXT NOT NULL,  -- 'google', 'instagram', 'wordpress'
  access_token TEXT,       -- store encrypted
  refresh_token TEXT,      -- store encrypted
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily agent runs
CREATE TABLE agent_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organizations(id),
  status TEXT DEFAULT 'running',  -- running | completed | failed
  summary TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Content drafts
CREATE TABLE content_drafts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID REFERENCES organizations(id),
  run_id UUID REFERENCES agent_runs(id),
  type TEXT,        -- 'blog_post' | 'instagram_post' | 'email'
  title TEXT,
  body TEXT,
  image_url TEXT,
  status TEXT DEFAULT 'draft',   -- draft | approved | published | rejected
  platform_url TEXT,             -- URL after publishing
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE content_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  draft_id UUID REFERENCES content_drafts(id),
  page_views INT DEFAULT 0,
  social_likes INT DEFAULT 0,
  social_shares INT DEFAULT 0,
  measured_at TIMESTAMPTZ DEFAULT NOW()
);

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT TOOL CATALOGUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Build each as a LangChain @tool decorated function:

@tool def recall_brand_memory(query: str) -> str
@tool def search_web(query: str) -> str          # DuckDuckGo, free
@tool def get_ga4_metrics(days: int) -> dict     # Google Analytics Data API
@tool def get_gsc_keywords(days: int) -> list    # Search Console API
@tool def generate_image(prompt: str) -> str     # Pollinations.ai, returns URL
@tool def create_wp_post(title, content, status) -> str
@tool def post_to_instagram(image_url, caption) -> str
@tool def send_email_campaign(subject, body) -> str
@tool def save_draft(type, title, body, image_url) -> str
@tool def get_competitor_headlines(domain: str) -> list

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT TO BUILD FIRST — RIGHT NOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Start with Phase 0. Build and test anna_mvp.py. Do not touch 
the frontend until the agent crew produces a complete, coherent 
blog post from a real URL.

The first successful run is the proof of concept. Everything else 
is iteration.

Begin by scaffolding the project structure:

annaai/
├── backend/
│   ├── main.py              (FastAPI app)
│   ├── agents/
│   │   ├── crew.py          (CrewAI crew definition)
│   │   ├── tools.py         (all @tool functions)
│   │   └── prompts.py       (agent system prompts)
│   ├── memory/
│   │   ├── scraper.py       (BeautifulSoup + Trafilatura)
│   │   └── vector_store.py  (Supabase pgvector operations)
│   ├── integrations/
│   │   ├── google.py        (GA4 + GSC)
│   │   ├── wordpress.py
│   │   ├── instagram.py
│   │   └── email_sender.py  (Resend)
│   ├── scheduler/
│   │   └── daily_run.py     (orchestrates full pipeline)
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx         (landing / onboard)
│   │   ├── dashboard/
│   │   ├── drafts/
│   │   └── chat/
│   └── package.json
├── .github/
│   └── workflows/
│       └── daily_anna.yml   (cron: '0 6 * * *')
└── README.md

Now write the complete anna_mvp.py for Phase 0. 
Use Claude (claude-sonnet-20250514) as the LLM.
Use DuckDuckGo search (duckduckgo-search pip package) — no API key needed.
Use sentence-transformers locally for embeddings — no OpenAI key needed.
Make the output a clean markdown blog post ready to copy-paste.








