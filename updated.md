You are a senior full-stack engineer and AI systems architect. You write 
production-grade, fully typed, modern code. You always use the latest stable 
versions of every library and follow current best practices as of April 2026.

We are building "AnnaAi" — a fully autonomous AI marketing agent platform.
AnnaAi connects to a business's website, analytics, CMS, and social platforms. 
Every morning, a crew of AI agents researches competitors and trends, analyses 
performance data, creates content, generates images, and publishes or queues 
everything for human approval — then sends a daily email brief to the owner.

The platform is multi-tenant SaaS. Each organisation has isolated data, brand 
memory, OAuth connections, and agent runs. "Anna" is the AI persona: warm, 
proactive, intelligent.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERIFIED STACK — DO NOT DEVIATE FROM THESE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Python:          3.12
FastAPI:         0.135.x
Pydantic:        v2 only (model_config = ConfigDict(...), not class Config)
pydantic-settings: 2.6+
CrewAI:          1.9.x  (standalone — NO langchain, NO langchain-anthropic)
Supabase Python: 2.x client + vecs library for pgvector
pgvector index:  HNSW (not IVFFlat — HNSW is now the default)
Package manager: uv (not pip) — use in Dockerfile and all install instructions
Celery:          5.4+
Redis client:    redis>=5.0
PyJWT:           2.x (replaces python-jose)
Anthropic SDK:   latest (0.40+)
sentence-transformers: latest stable

Frontend:
Next.js:         16.x (NOT 14 — async params mandatory, Turbopack top-level)
React:           19.2
@supabase/ssr:   latest (replaces @supabase/auth-helpers-nextjs — deprecated)
TanStack Query:  v5.96.x (isPending not isLoading, gcTime not cacheTime, 
                           single object API only)
Tailwind CSS:    v4 (new config format — no tailwind.config.ts, uses CSS)
lucide-react:    latest
sonner:          latest (replaces react-hot-toast)
date-fns:        v4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1: COMPLETE PROJECT STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scaffold the COMPLETE project directory. Write full file content for every 
file — no empty files, no placeholders. Structure:

annaai/
├── backend/
│   ├── pyproject.toml          (uv/PEP 517 — not requirements.txt)
│   ├── uv.lock                 (generated, leave empty with comment)
│   ├── .python-version         (contains: 3.12)
│   ├── Dockerfile
│   ├── .env.example
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── crew.py             (CrewAI 1.9 @CrewBase pattern)
│   │   ├── tools.py
│   │   ├── prompts.py
│   │   └── pipeline.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── scraper.py
│   │   ├── embedder.py
│   │   └── vector_store.py     (uses supabase vecs library)
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── google_analytics.py
│   │   ├── google_search_console.py
│   │   ├── wordpress.py
│   │   └── email_sender.py     (Resend)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── middleware.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── onboarding.py
│   │       ├── runs.py
│   │       ├── drafts.py
│   │       ├── integrations.py
│   │       ├── chat.py
│   │       ├── webhooks.py
│   │       └── scheduler.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── migrations/
│   │       ├── 001_schema.sql
│   │       ├── 002_rls.sql
│   │       └── 003_functions.sql
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── tasks.py            (Celery 5.4)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── encryption.py
│   │   ├── logger.py
│   │   └── helpers.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_agents.py
│       └── test_api.py
├── frontend/
│   ├── package.json
│   ├── next.config.ts          (TypeScript config — Next.js 16)
│   ├── tsconfig.json
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css         (Tailwind v4 — @import "tailwindcss")
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── drafts/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/page.tsx
│   │   │   ├── runs/page.tsx
│   │   │   ├── integrations/page.tsx
│   │   │   ├── settings/page.tsx
│   │   │   └── chat/page.tsx
│   │   ├── onboard/page.tsx
│   │   └── api/
│   │       └── auth/
│   │           └── callback/route.ts   (Supabase SSR OAuth callback)
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── input.tsx
│   │   │   ├── modal.tsx
│   │   │   └── spinner.tsx
│   │   ├── layout/
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   └── dashboard-shell.tsx
│   │   ├── dashboard/
│   │   │   ├── metric-card.tsx
│   │   │   ├── runs-table.tsx
│   │   │   ├── traffic-chart.tsx
│   │   │   └── recent-drafts.tsx
│   │   ├── drafts/
│   │   │   ├── draft-card.tsx
│   │   │   ├── draft-editor.tsx
│   │   │   └── approval-controls.tsx
│   │   ├── chat/
│   │   │   ├── chat-window.tsx
│   │   │   ├── message-bubble.tsx
│   │   │   └── chat-input.tsx
│   │   └── onboarding/
│   │       ├── wizard.tsx
│   │       ├── step-website.tsx
│   │       ├── step-brand-voice.tsx
│   │       ├── step-connect-accounts.tsx
│   │       └── step-goals.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── supabase/
│   │   │   ├── client.ts       (browser client — @supabase/ssr)
│   │   │   ├── server.ts       (server client — @supabase/ssr)
│   │   │   └── middleware.ts   (Next.js 16 proxy.ts pattern)
│   │   ├── hooks/
│   │   │   ├── use-runs.ts     (TanStack Query v5)
│   │   │   ├── use-drafts.ts
│   │   │   └── use-organization.ts
│   │   └── types.ts
│   └── public/
│       └── anna-avatar.svg
├── .github/
│   └── workflows/
│       ├── daily_anna.yml
│       ├── deploy_backend.yml
│       └── deploy_frontend.yml
├── docker-compose.yml
└── README.md

Write full content for every file listed above. Start here.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2: pyproject.toml (replaces requirements.txt)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write the complete backend/pyproject.toml using PEP 517 / uv format.
Use [project] table, not setup.py. Pin minimum versions only (>=), 
not exact pins, so uv can resolve. Group dev dependencies separately.

[project]
name = "annaai-backend"
version = "0.1.0"
requires-python = ">=3.12"

Dependencies to include (minimum versions):

Core:
  fastapi>=0.135.0
  uvicorn[standard]>=0.32.0
  pydantic>=2.10.0
  pydantic-settings>=2.6.0
  python-multipart>=0.0.20   (FastAPI file uploads)

Database / Supabase:
  supabase>=2.10.0
  vecs>=0.4.3                (Supabase pgvector Python client)
  asyncpg>=0.30.0

AI / Agents:
  crewai>=1.9.0              (standalone, no langchain dependency)
  crewai-tools>=0.20.0
  anthropic>=0.40.0
  sentence-transformers>=3.3.0

NOTE: Do NOT include torch in pyproject.toml — explain in a comment 
that torch must be installed separately with the CPU wheel URL:
  uv pip install torch --index-url https://download.pytorch.org/whl/cpu
This avoids pulling the 2GB CUDA build.

Scraping:
  beautifulsoup4>=4.12.0
  trafilatura>=2.0.0
  httpx>=0.28.0
  lxml>=5.0.0

Search (free, no API key):
  duckduckgo-search>=6.0.0

Encryption / Auth:
  cryptography>=44.0.0
  PyJWT>=2.9.0              (NOT python-jose — use PyJWT directly)
  passlib[bcrypt]>=1.7.4

Email:
  resend>=2.5.0

Google APIs:
  google-analytics-data>=0.18.0
  google-auth>=2.35.0
  google-auth-oauthlib>=1.2.0

Task queue:
  celery>=5.4.0
  redis>=5.2.0

Image processing:
  Pillow>=11.0.0

Utilities:
  tenacity>=9.0.0
  structlog>=24.4.0
  markdown>=3.7

[project.optional-dependencies]
dev:
  pytest>=8.3.0
  pytest-asyncio>=0.24.0
  httpx>=0.28.0
  ruff>=0.8.0               (replaces flake8 + black + isort)
  mypy>=1.13.0

Also write a complete Dockerfile using uv:

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install system deps for lxml, asyncpg, Pillow
RUN apt-get update && apt-get install -y \
    gcc libpq-dev libffi-dev libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps via uv (much faster than pip)
COPY pyproject.toml .
RUN uv pip install --system -e ".[dev]"

# Install torch CPU separately (avoids 2GB CUDA download)
RUN uv pip install --system torch \
    --index-url https://download.pytorch.org/whl/cpu

COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3: config.py — Pydantic v2 Settings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write complete backend/config.py using Pydantic v2 BaseSettings.

CRITICAL Pydantic v2 patterns to use:
  - from pydantic import field_validator, model_validator
  - from pydantic_settings import BaseSettings, SettingsConfigDict
  - model_config = SettingsConfigDict(env_file=".env", extra="ignore")
  - Do NOT use class Config — that is Pydantic v1

Settings groups and all variables:

# Application
APP_NAME: str = "AnnaAi"
APP_VERSION: str = "0.1.0"
ENVIRONMENT: str = "development"  # development | staging | production
DEBUG: bool = False
SECRET_KEY: str = ""
ENCRYPTION_KEY: str = ""  # 32-byte Fernet key

# Supabase
SUPABASE_URL: str = ""
SUPABASE_ANON_KEY: str = ""
SUPABASE_SERVICE_ROLE_KEY: str = ""
SUPABASE_DB_URL: str = ""  # direct postgres URL for vecs: 
                            # postgresql://postgres:[pass]@db.[ref].supabase.co:5432/postgres

# Anthropic
ANTHROPIC_API_KEY: str = ""
ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
ANTHROPIC_MAX_TOKENS: int = 4096

# Embeddings (local, no API key)
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION: int = 384

# Resend
RESEND_API_KEY: str = ""
RESEND_FROM_EMAIL: str = "anna@annaai.app"
RESEND_FROM_NAME: str = "Anna · AnnaAi"

# Frontend URL (for OAuth redirects, email links)
FRONTEND_URL: str = "http://localhost:3000"
BACKEND_URL: str = "http://localhost:8000"

# Google OAuth
GOOGLE_CLIENT_ID: str = ""
GOOGLE_CLIENT_SECRET: str = ""

# Image generation (Pollinations — free, no key)
POLLINATIONS_BASE_URL: str = "https://image.pollinations.ai/prompt"
POLLINATIONS_WIDTH: int = 1200
POLLINATIONS_HEIGHT: int = 630

# Redis / Upstash
REDIS_URL: str = "redis://localhost:6379"

# Scheduler auth
SCHEDULER_SECRET: str = ""

# Scraping
SCRAPE_MAX_PAGES: int = 20
SCRAPE_TIMEOUT_SECONDS: int = 30

# Plan limits
MAX_RUNS_PER_DAY_FREE: int = 1
MAX_DRAFTS_PER_RUN_FREE: int = 3
MAX_DRAFTS_PER_RUN_PRO: int = 10

Add a @model_validator(mode="after") that:
- Warns (logs) if SECRET_KEY or ENCRYPTION_KEY is empty in production
- Raises ValueError if SUPABASE_URL is empty when ENVIRONMENT == "production"

Export: settings = Settings()

Also write the complete .env.example with every variable, 
empty values, and a comment explaining each one.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4: DATABASE MIGRATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write complete SQL for all three migration files.
These run in Supabase SQL editor. Must be error-free.

FILE: backend/db/migrations/001_schema.sql

At top:
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

Tables (in dependency order):

1. organizations — same columns as before, plus:
   onboarding_complete: BOOLEAN DEFAULT FALSE
   onboarding_step: INTEGER DEFAULT 0

2. users — same as before

3. brand_memory
   Use HNSW index (not IVFFlat):
   CREATE INDEX ON brand_memory 
   USING hnsw (embedding vector_cosine_ops)
   WITH (m = 16, ef_construction = 64);
   
   HNSW does NOT need to be built after population 
   (unlike IVFFlat) — correct this from prior version.

4. oauth_tokens — same as before

5. agent_runs — same as before

6. content_drafts — same as before

7. content_metrics — same as before

8. daily_briefs — same as before

9. chat_messages — same as before

10. scheduled_tasks — same as before

Triggers: updated_at auto-update on organizations, 
content_drafts, oauth_tokens. Write the trigger function.

FILE: backend/db/migrations/002_rls.sql

Enable RLS on all tables. Write SELECT, INSERT, UPDATE, DELETE 
policies for each table. Include helper function:
  CREATE OR REPLACE FUNCTION get_user_org_id()
  RETURNS UUID AS $$
    SELECT org_id FROM users WHERE id = auth.uid()
  $$ LANGUAGE SQL STABLE SECURITY DEFINER;

FILE: backend/db/migrations/003_functions.sql

1. match_brand_memory(query_embedding vector(384), p_org_id uuid, match_count int)
   Uses HNSW cosine similarity: embedding <=> query_embedding
   Returns top match_count results ordered by similarity ASC 
   (lower distance = more similar in pgvector cosine ops)

2. get_org_run_stats(p_org_id uuid)
   30-day stats: total_runs, successful_runs, total_drafts, 
   published_drafts, avg_duration_seconds

3. get_content_performance_summary(p_org_id uuid, p_days int)
   Joins content_drafts + content_metrics for the window

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5: CORE UTILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write complete contents of all utility files.

FILE: backend/utils/encryption.py
Use cryptography.fernet.Fernet. 
Functions: encrypt_token, decrypt_token, hash_secret, verify_webhook_signature.
Handle DecryptionError gracefully (return None + log).

FILE: backend/utils/logger.py
Use structlog (not standard logging).
structlog is the modern choice — configure JSON output in production, 
pretty console in development. 
Functions: get_logger(name), log_agent_run_start, log_agent_run_complete,
log_agent_run_failed, log_api_request.

FILE: backend/utils/helpers.py
Functions: chunk_text, clean_html, extract_domain, truncate_text,
generate_slug, format_duration, estimate_read_time.
Use Python 3.12 syntax (match statements where appropriate).

FILE: backend/db/client.py
Use supabase-py v2 create_client pattern:
  from supabase import create_client, Client
  (v2 API — not the old acreate_client async version)
Export get_supabase_client() and get_supabase_admin_client().
Admin client uses SERVICE_ROLE_KEY.

FILE: backend/db/models.py
Pydantic v2 models for all API request/response shapes.
Use model_config = ConfigDict(from_attributes=True) on ORM-like models.
Include: OrgCreate, OrgResponse, UserResponse, AgentRunResponse,
ContentDraftResponse, ContentDraftUpdate, ChatMessageResponse,
PaginatedResponse (generic), OnboardingStatusResponse, RunStatsResponse.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6: MAIN FastAPI APPLICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write complete backend/main.py.

Key Next.js 16 / FastAPI 0.135 considerations:
- FastAPI 0.135 checks Content-Type by default — 
  document this in CORS setup
- Use lifespan context manager (not @app.on_event deprecated)
- StreamingResponse for SSE chat endpoint
- Structured JSON error responses in all exception handlers

Lifespan:
  async with lifespan(app):
    # startup: test Supabase connection, load embedding model
    yield
    # shutdown: log clean exit

Routers (all with /api prefix):
  /api/auth, /api/onboarding, /api/runs, /api/drafts,
  /api/integrations, /api/chat, /api/webhooks, /api/scheduler

Middleware (in order, outermost first):
  1. CORS — origins from settings, allow credentials
  2. SecurityHeaders — X-Content-Type-Options, X-Frame-Options, etc.
  3. RequestLogging — structlog, every request with timing

GET /health — returns:
  {status, version, environment, timestamp, 
   supabase_connected, embedding_model_loaded}

GET / — welcome JSON

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 7: docker-compose.yml + GitHub Actions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write docker-compose.yml:
Services: backend, redis (redis:7-alpine), celery_worker, celery_beat.
Backend and Celery use same Dockerfile, different CMD.
All use .env for environment.

Write .github/workflows/daily_anna.yml:
Cron: '0 6 * * *' + manual trigger.
POST to ${{ secrets.BACKEND_URL }}/api/scheduler/trigger-all-runs
Retry 3 times with 30s delay on failure (Render cold start).

Write .github/workflows/deploy_backend.yml:
Trigger on push to main when backend/** changes.
Run ruff check + mypy + pytest before deploying.
Trigger Render deploy hook.
Smoke test GET /health after deploy.

Write .github/workflows/deploy_frontend.yml:
Trigger on push to main when frontend/** changes.
npm install + npm run build (Next.js 16 build).
Vercel auto-deploys on push — just validate build here.

After completing all sections, print a checklist confirming:
1. All Pydantic models use v2 syntax (no class Config)
2. CrewAI import is standalone (no langchain imports)
3. Supabase client is v2 pattern
4. HNSW index used (not IVFFlat)
5. uv used in Dockerfile (not pip)
6. PyJWT used (not python-jose)
7. structlog used (not standard logging)
8. All async functions are properly awaited
9. No deprecated Next.js 14 patterns anywhere

Write every file completely. Start with Section 1.




You are continuing to build AnnaAi. Batch 1 is complete (project structure, 
database, config, utilities). Now build the AI brain: scraper, embeddings, 
vector memory, and the full CrewAI 1.9 agent crew.

CRITICAL VERSION CONSTRAINTS:
- CrewAI 1.9.x — use the @CrewBase decorator pattern + Flows API
- CrewAI is STANDALONE — zero LangChain imports anywhere in this batch
- The correct import for the LLM wrapper is:
    from crewai import LLM
  NOT ChatAnthropic from langchain
- Tool definition uses @tool decorator from crewai.tools
- Agent/Task/Crew imports: from crewai import Agent, Task, Crew, Process
- CrewAI 1.9 Crew supports: Process.sequential and Process.hierarchical
- duckduckgo-search 6.x API: use DDGS() context manager, not DuckDuckGoSearchAPIWrapper

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1: SCRAPER (backend/memory/scraper.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Same full specification as original Batch 2 Section 1 — write in full.
Key update: use httpx.AsyncClient (not requests) for async HTTP.
Use trafilatura.extract() with include_comments=False, include_tables=False.
Use Python 3.12 type hints: list[str] not List[str], str | None not Optional[str]]

Write the full implementation. Do not abbreviate.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2: EMBEDDER (backend/memory/embedder.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Same specification as original — full EmbeddingService singleton class.
Key update: sentence-transformers 3.x uses SentenceTransformer class 
with model.encode() returning numpy arrays — convert to list[float] 
with .tolist() before storing.]

Write the full implementation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3: VECTOR STORE (backend/memory/vector_store.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use the supabase vecs library (not raw SQL inserts for vectors):

import vecs
from config import settings

def get_vecs_client():
    return vecs.create_client(settings.SUPABASE_DB_URL)

For storing: use collection.upsert(records=[(id, vector, metadata), ...])
For querying: use collection.query(data=embedding, limit=top_k, 
              filters={"org_id": {"$eq": org_id}},
              measure="cosine_distance", include_metadata=True)

The vecs collection name for brand memory: "brand_memory"
Vectors are 384-dimensional (all-MiniLM-L6-v2).
Metadata stored per vector: {org_id, chunk_type, source_url, page_title, chunk_text}

Note: vecs handles the HNSW index creation — call 
collection.create_index(method=vecs.IndexMethod.hnsw) after initial population.

Write all functions: store_brand_memory, recall_brand_memory, 
get_brand_memory_summary, get_memory_stats.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4: AGENT TOOLS (backend/agents/tools.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL: CrewAI 1.9 tool syntax:
  from crewai.tools import tool   (not from langchain.tools import tool)

  @tool("Tool Name")
  def my_tool(input: str) -> str:
      """Docstring that agents read to decide when to use this tool."""
      ...

For DuckDuckGo search — use duckduckgo-search 6.x API:
  from duckduckgo_search import DDGS
  
  with DDGS() as ddgs:
      results = list(ddgs.text(query, max_results=5))
  
  Each result: {title, href, body}

Write ALL tools specified in original Batch 2 Section 4:
recall_brand_memory, search_web, search_competitor_content,
get_trending_topics, generate_image, save_content_draft,
get_analytics_summary, get_search_console_data,
get_wordpress_recent_posts, publish_to_wordpress,
send_daily_brief, calculate_seo_score.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5: AGENT PROMPTS (backend/agents/prompts.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Same specification as original — write all 5 agent system prompts 
in full (150-300 words each) plus DAILY_RUN_TASK_DESCRIPTION and 
BRIEF_EMAIL_HTML_TEMPLATE.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6: CREW (backend/agents/crew.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use CrewAI 1.9 @CrewBase decorator pattern:

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew

@CrewBase
class AnnaCrew:
    agents_config = 'config/agents.yaml'   # optional YAML config
    tasks_config = 'config/tasks.yaml'     # optional YAML config
    
    def __init__(self, config: AnnaCrewConfig):
        self.config = config
        self.llm = LLM(
            model="anthropic/claude-sonnet-4-20250514",
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=0.7,
            max_tokens=4096
        )
    
    @agent
    def researcher(self) -> Agent: ...
    
    @agent
    def analyst(self) -> Agent: ...
    
    @agent
    def strategist(self) -> Agent: ...
    
    @agent
    def creator(self) -> Agent: ...
    
    @agent
    def publisher(self) -> Agent: ...
    
    @task
    def research_task(self) -> Task: ...
    
    # ... all 5 tasks
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

Note: In CrewAI 1.9, the LLM class takes model in 
"provider/model-name" format for Anthropic:
  "anthropic/claude-sonnet-4-20250514"

Write the full @CrewBase class with all agents and tasks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 7: PIPELINE (backend/agents/pipeline.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Same specification as original — run_daily_pipeline_for_org,
run_daily_pipeline_for_all_orgs, run_onboarding_pipeline.
All async. Uses asyncio.to_thread() to run the synchronous 
CrewAI crew.kickoff() in a thread pool without blocking the event loop.]

Critical pattern for running sync CrewAI in async FastAPI:
  result = await asyncio.to_thread(anna_crew.crew().kickoff)

Write the full implementation. from the old file 


Continuing AnnaAi build. Batches 1-2 complete. Now build all 
FastAPI 0.135 API routes, Supabase v2 auth, and integration modules.

VERSION NOTES FOR THIS BATCH:
- FastAPI 0.135 strict Content-Type: POST endpoints expecting JSON 
  will reject requests without Content-Type: application/json by default.
  Document this in error responses.
- Supabase Python v2 auth: 
    supabase.auth.sign_in_with_password({"email": ..., "password": ...})
    (dict argument, not keyword args)
- JWT validation: use PyJWT 2.x — import jwt; jwt.decode(token, key, algorithms=["HS256"])
  NOT python-jose
- Use Python 3.12 union types: str | None  not Optional[str]
- All route functions must be async def
- Use FastAPI's new Annotated dependency pattern:
    from typing import Annotated
    CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
- Pydantic v2 model validation in route bodies:
    from pydantic import BaseModel, Field, field_validator
    (not @validator — use @field_validator)

[Write complete implementations of all routes and integrations 
as specified in the original Batch 3, applying the above corrections.]

SECTION 1: dependencies.py — JWT validation using PyJWT, 
           Annotated dependency aliases

SECTION 2: auth.py — Supabase v2 auth API calls

SECTION 3: onboarding.py — background tasks, status polling

SECTION 4: runs.py — pagination, stats, trigger

SECTION 5: drafts.py — full CRUD, approval flow, markdown preview

SECTION 6: chat.py — Anthropic streaming SSE using:
  from anthropic import Anthropic
  client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
  with client.messages.stream(...) as stream:
      for text in stream.text_stream:
          yield f"data: {json.dumps({'delta': text})}\n\n"
  yield "data: [DONE]\n\n"

SECTION 7: integrations.py — Google OAuth, WordPress connect

SECTION 8: Integration modules:
  google_analytics.py — google-analytics-data 0.18+
  google_search_console.py
  wordpress.py — uses httpx.AsyncClient + Basic Auth
  email_sender.py — resend 2.x Python SDK:
    import resend
    resend.api_key = settings.RESEND_API_KEY
    resend.Emails.send({...})  (sync) or use httpx for async

SECTION 9: webhooks.py + scheduler.py

SECTION 10: middleware.py — structlog request logging, 
            rate limit with redis>=5.0 (use redis.asyncio),
            security headers

Write all sections in full from the old files, applying the corrections above.



Continuing AnnaAi. Batches 1-3 complete. Now build the complete 
Next.js 16 frontend.

CRITICAL NEXT.JS 16 RULES — BREAKING CHANGES FROM 14:
1. params and searchParams in page.tsx are now PROMISES — always await them:
   export default async function Page({ params }: { params: Promise<{id: string}> }) {
     const { id } = await params
   }

2. Turbopack config is now top-level in next.config.ts:
   const config: NextConfig = { turbopack: {} }  (not experimental.turbopack)

3. middleware.ts is deprecated — rename to proxy.ts for new behavior.
   But for auth middleware, next-js still supports middleware.ts for now.
   Use middleware.ts for Supabase SSR auth until proxy.ts is stable.

4. 'use cache' directive is available — use it for static data on 
   server components instead of the old fetch cache options.

5. React 19.2 — use() hook available for reading promises in client components.
   useFormStatus, useOptimistic are stable. 

6. NO @supabase/auth-helpers-nextjs — this package is DEPRECATED.
   Use @supabase/ssr instead:
   import { createBrowserClient } from '@supabase/ssr'  (client components)
   import { createServerClient } from '@supabase/ssr'  (server components)

7. Tailwind CSS v4 — new format:
   No tailwind.config.ts file needed.
   In globals.css:
     @import "tailwindcss";
     @theme {
       --color-primary: #e94560;
       --color-surface: #1a1a2e;
       ...
     }
   Custom utilities use @utility in CSS.
   Use v4 class names (same as v3 but configured via CSS @theme).

8. TanStack Query v5 patterns ONLY:
   - isPending (not isLoading)
   - gcTime (not cacheTime)
   - Single object argument to useQuery({ queryKey, queryFn })
   - useSuspenseQuery for guaranteed non-undefined data
   - No isInitialLoading (deprecated)

9. package.json — use next@16, react@19.2, react-dom@19.2

PACKAGE VERSIONS:
  next: ^16.2.0
  react: ^19.2.0
  react-dom: ^19.2.0
  typescript: ^5.7.0
  @supabase/supabase-js: ^2.47.0
  @supabase/ssr: ^0.5.0          (NOT auth-helpers-nextjs)
  @tanstack/react-query: ^5.96.0
  @tanstack/react-query-devtools: ^5.96.0
  tailwindcss: ^4.0.0
  lucide-react: ^0.487.0
  sonner: ^1.7.0                 (replaces react-hot-toast)
  recharts: ^2.13.0
  react-markdown: ^9.0.0
  date-fns: ^4.1.0
  clsx: ^2.1.0
  @types/react: ^19.0.0
  @types/node: ^22.0.0

[Write complete implementations of all pages, components, and lib 
files as specified in original Batch 4, applying all of the above 
corrections. Every page, every component, fully written.]

SECTION 1: Configuration files (package.json, next.config.ts, tsconfig.json)
SECTION 2: Tailwind v4 globals.css with @theme variables
SECTION 3: Root layout.tsx with QueryClientProvider + Toaster (sonner)
SECTION 4: Supabase SSR setup (lib/supabase/client.ts, server.ts, middleware.ts)
SECTION 5: lib/types.ts and lib/api.ts (fully typed)
SECTION 6: UI primitive components (button, card, badge, input, modal, spinner)
SECTION 7: Layout components (sidebar, header, dashboard-shell)
SECTION 8: Auth pages (login, register)
SECTION 9: Onboarding wizard (4 steps, full implementation)
SECTION 10: Dashboard page with all widgets
SECTION 11: Drafts list + draft detail pages
SECTION 12: Chat page with streaming SSE consumption
SECTION 13: Runs, Integrations, Settings pages
SECTION 14: TanStack Query v5 hooks (use-runs, use-drafts, use-organization)
SECTION 15: anna-avatar.svg (geometric, minimal SVG face)

Write every file completely from the old Batch 4, applying all corrections.


Continuing AnnaAi. Batches 1-4 complete. Now build:
the Celery 5.4 task system, complete email brief HTML, 
deployment configurations, and end-to-end integration tests.

STACK FOR THIS BATCH:
- Celery 5.4 with Redis 5.x broker:
    from celery import Celery
    app = Celery("annaai", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
    app.config_from_object("scheduler.celeryconfig")
    
- Redis async client for rate limiting in FastAPI:
    from redis.asyncio import Redis
    (not aioredis — redis>=5.0 includes asyncio support natively)

- Celery Beat for scheduling:
    app.conf.beat_schedule = {
        "daily-anna-run": {
            "task": "scheduler.tasks.trigger_daily_runs",
            "schedule": crontab(hour=6, minute=0),
        },
        ...
    }

SECTION 1: Complete backend/scheduler/tasks.py
  - Celery app setup with Upstash Redis
  - trigger_daily_runs task
  - collect_content_metrics task
  - Celery Beat schedule config
  - Handle asyncio.run() correctly inside Celery tasks
    (Celery tasks are sync — wrap async pipeline with asyncio.run())

SECTION 2: Complete BRIEF_EMAIL_HTML_TEMPLATE (full HTML)
  Write the complete daily brief email as a standalone HTML template.
  Inline CSS only (email client safe).
  Sections: Anna header, performance summary, content created today 
  (with approve buttons that link to frontend), key insight, 
  tomorrow's plan, footer with unsubscribe link.
  Mobile responsive (max-width: 600px, media queries).
  AnnaAi brand: #1a1a2e navy, #e94560 coral, #f8f8f8 background.

SECTION 3: Complete deployment configuration
  
  Render (backend):
  - render.yaml service definition (Web Service + Worker + Beat)
  - Environment variable setup guide
  - How to configure the deploy hook URL for GitHub Actions
  
  Vercel (frontend):
  - vercel.json configuration
  - Environment variables needed in Vercel dashboard
  - How to connect Vercel to GitHub for auto-deploy
  
  Upstash Redis:
  - Setup guide (free tier, 10K commands/day)
  - How to get REDIS_URL for both local and Render

SECTION 4: Complete backend/tests/conftest.py
  pytest fixtures using pytest-asyncio:
  - mock_supabase_client (monkeypatched)
  - mock_anthropic_client
  - test_org fixture (sample org data)
  - test_user fixture
  - async_client fixture (httpx.AsyncClient with FastAPI app)
  
  Use pytest-asyncio 0.24 asyncio_mode = "auto" in pyproject.toml:
  [tool.pytest.ini_options]
  asyncio_mode = "auto"

SECTION 5: Integration tests (backend/tests/test_agents.py)
  Test the scraper on https://example.com
  Test embedding dimension = 384
  Test DuckDuckGo search with duckduckgo-search 6.x API
  Test full crew run with mocked Anthropic API

SECTION 6: API tests (backend/tests/test_api.py)
  Test all major routes with mocked dependencies.
  Use httpx.AsyncClient as the test client.
  
SECTION 7: Complete README.md
  - One-command local setup: uv pip install + next install
  - Environment variable guide
  - First run walkthrough
  - Deployment to Render + Vercel step-by-step
  - How to add a new integration (guide for contributors)


  Final batch. Batches 1-5 complete. Now add:
multi-tenancy hardening, GHS billing via Paystack, performance 
feedback loop so Anna learns from published content, and UI polish.

STACK FOR THIS BATCH:
- Paystack Python: use httpx directly (no official SDK needed — 
  Paystack has a clean REST API)
  Paystack Ghana: https://api.paystack.co
  Accepts GHS payments via Mobile Money + card
  Free to integrate, no monthly fee

SECTION 1: Multi-tenancy hardening
  Audit all Supabase queries to ensure org_id scoping on every query.
  Add a reusable Supabase query helper that auto-injects org_id:
  
  class OrgScopedClient:
      def __init__(self, supabase_client, org_id: str):
          self.client = supabase_client
          self.org_id = org_id
      
      def table(self, name: str):
          return OrgScopedTable(self.client.table(name), self.org_id)
  
  Verify RLS is working with a test that tries to access 
  another org's data (should return empty, not error).

SECTION 2: Paystack GHS billing integration
  
  Plans (hardcoded):
    Free:     GHS 0/mo — 1 run/week, 3 drafts max, no auto-publish
    Pro:      GHS 149/mo — daily runs, 10 drafts, WordPress auto-publish
    Business: GHS 399/mo — all integrations, priority, white-label brief
  
  backend/integrations/paystack.py:
  
  class PaystackClient:
      BASE_URL = "https://api.paystack.co"
      
      async def initialize_payment(
          self, email: str, amount_ghs: float, 
          plan: str, org_id: str
      ) -> dict:
          """
          POST /transaction/initialize
          Amount in kobo (1 GHS = 100 kobo).
          Returns: {authorization_url, access_code, reference}
          """
      
      async def verify_payment(self, reference: str) -> dict:
          """
          GET /transaction/verify/{reference}
          Returns: {status, amount, plan, customer}
          """
      
      async def create_subscription_plan(
          self, name: str, amount_ghs: float, interval: str
      ) -> dict:
          """
          POST /plan
          Creates a recurring billing plan.
          interval: "monthly"
          """
  
  backend/api/routes/billing.py:
  
  GET  /api/billing/plans     — returns plan details + current plan
  POST /api/billing/subscribe — initialise Paystack payment, 
                                returns authorization_url for redirect
  GET  /api/billing/callback  — Paystack redirect after payment
  POST /api/billing/webhook   — Paystack event webhook 
                                (charge.success → upgrade org plan)
  GET  /api/billing/status    — current plan, renewal date, usage stats
  
  frontend/app/(dashboard)/billing/page.tsx:
  
  Pricing cards for the 3 plans (GHS).
  Current plan highlighted.
  "Upgrade" button → redirects to Paystack checkout.
  After return: success toast + plan badge updates.
  Show usage this month: runs used / limit, drafts used / limit.

SECTION 3: Performance feedback loop (Anna learns)
  
  After content is published, Anna should track performance and 
  use it to inform future decisions.
  
  backend/scheduler/tasks.py — add new Celery task:
  
  @celery_app.task(name="collect_published_metrics")
  def collect_published_metrics():
      """
      Runs daily at 02:00 UTC.
      For each published content_draft (published in last 30 days):
      1. If it was a blog post: fetch page views from GA4
      2. If it was an Instagram post: skip (Graph API limits)
      3. Update content_metrics table
      4. Calculate performance_score: 
           normalize page_views against org's average
           High performer: score > 1.5x average
           Low performer: score < 0.5x average
      5. Store performance_label in content_drafts: 
           'high_performer' | 'average' | 'low_performer'
      """
  
  Modify the Analyst agent tool (get_analytics_summary) to also return:
  "TOP PERFORMING CONTENT (last 30 days): 
   1. [title] — [views] views — TOPIC: [topic]
   2. ...
  
  UNDERPERFORMING CONTENT:
   1. [title] — [views] views"
  
  This data goes into the Strategist's context so Anna naturally 
  gravitates toward topics that perform well for this specific business.

SECTION 4: Anna learns brand voice over time
  
  Add a feedback mechanism to the content approval flow.
  
  When a draft is rejected: store rejection_reason in brand_memory 
  as a special chunk with chunk_type="negative_feedback":
    "Do NOT write content like this: [title]. Reason: [rejection_reason]"
  
  When a draft is approved and published: store a positive signal:
    chunk_type="positive_feedback": 
    "Content that worked well: [title]. Topic: [topic]. Style: [summary]"
  
  The Creator agent's recall_brand_memory call will naturally 
  retrieve these over time, steering Anna's output.
  
  This is a zero-config learning system — no fine-tuning needed.

SECTION 5: Settings page completion
  
  frontend/app/(dashboard)/settings/page.tsx — complete all 4 tabs:
  Tab 1 — Profile: name, email
  Tab 2 — Organisation: all brand voice settings
  Tab 3 — Anna Settings: run schedule, content types, notification email
  Tab 4 — Danger Zone: re-scrape, delete account
  
  Each tab saves via PATCH /api/settings/profile, 
  /api/settings/organization, /api/settings/anna.
  
  backend/api/routes/settings.py:
  Write all 3 PATCH endpoints.

SECTION 6: Final polish checklist — implement all of these

  Backend:
  □ Add request ID to every log line (UUID per request, in middleware)
  □ Add /api/health/ready endpoint (checks Supabase + Redis connectivity)
  □ Add response compression (GZipMiddleware from starlette)
  □ Rate limit the /api/chat/message endpoint to 20 req/min per org
  □ Add CORS preflight caching (max_age=86400)
  
  Frontend:
  □ Loading skeletons on all data-fetching components 
    (not just spinners — use CSS shimmer animation)
  □ Error boundaries on all dashboard pages
  □ Empty states on all list pages
  □ Mobile sidebar as a drawer (slides in from left)
  □ Keyboard shortcut: Cmd/Ctrl+K opens a command palette 
    (search drafts, trigger run, go to chat) — 
    implement with a simple modal + input filter, 
    no external library needed
  □ Favicon and OG image (use Anna's SVG avatar as base)

Write all sections completely. This is the final batch.
After completing, write a DEPLOYMENT RUNBOOK — a step-by-step 
numbered guide that takes a developer from zero to a live, 
fully working AnnaAi deployment on Render + Vercel + Supabase 
in under 2 hours, using only free tiers.