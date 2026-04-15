# AnnaAi

Autonomous AI marketing agent. Free-tier stack, CrewAI 1.9 + Claude Sonnet 4
under the hood, Next.js 16 + Supabase on the front end.

## Stack (verified, April 2026)

| Layer           | Tech                                                              |
|-----------------|-------------------------------------------------------------------|
| Backend         | Python 3.12 · FastAPI 0.135 · Pydantic v2 · uv                    |
| Agents          | CrewAI 1.9 (standalone) · Anthropic Claude Sonnet 4 · vecs        |
| Database        | Supabase Postgres · pgvector HNSW                                 |
| Queue           | Celery 5.4 · Redis 5 (Upstash free tier)                          |
| Email           | Resend                                                            |
| Frontend        | Next.js 16 · React 19.2 · Tailwind v4 · TanStack Query v5         |
| Auth            | @supabase/ssr · PyJWT                                             |
| Hosting         | Render (backend) · Vercel (frontend) · Supabase (db)              |

## Quick start — backend

```bash
cd backend
uv python install 3.12
uv pip install --system -e ".[dev]"
uv pip install --system torch --index-url https://download.pytorch.org/whl/cpu

cp .env.example .env
# fill in ANTHROPIC_API_KEY and SUPABASE_* at minimum

uvicorn main:app --reload
# → http://localhost:8000/health
```

### Database setup

In the Supabase SQL editor, run these three files in order:

1. [backend/db/migrations/001_schema.sql](backend/db/migrations/001_schema.sql)
2. [backend/db/migrations/002_rls.sql](backend/db/migrations/002_rls.sql)
3. [backend/db/migrations/003_functions.sql](backend/db/migrations/003_functions.sql)

## Quick start — frontend

Arrives in Batch 4. Will be:

```bash
cd frontend
npm install
npm run dev
```

## Project layout

```
annaai/
├── backend/
│   ├── pyproject.toml          uv / PEP 517
│   ├── Dockerfile              uv-based image
│   ├── main.py                 FastAPI entry point (lifespan)
│   ├── config.py               Pydantic v2 Settings
│   ├── dependencies.py         PyJWT auth + Annotated deps
│   ├── agents/                 CrewAI 1.9 crew + tools + prompts + pipeline
│   ├── memory/                 scraper (httpx async) + embedder + vecs store
│   ├── integrations/           google, wordpress, resend, paystack
│   ├── api/                    middleware + routes/
│   ├── db/
│   │   ├── client.py           supabase-py v2 (anon + admin)
│   │   ├── models.py           Pydantic v2 API shapes
│   │   └── migrations/         001_schema · 002_rls · 003_functions
│   ├── scheduler/              Celery 5.4 tasks + beat
│   └── utils/                  encryption · logger (structlog) · helpers
├── frontend/                   Next.js 16 · React 19.2 · Tailwind v4
├── .github/workflows/          daily cron · backend CI · frontend build
└── docker-compose.yml          backend + redis + celery worker + beat
```

## Build batches

- **Batch 1 — scaffold.** Project skeleton, pyproject, Dockerfile, config,
  migrations, utilities, `main.py`, workflows, docker-compose.
- **Batch 2 — AI brain.** Scraper (async httpx), embedder, vecs store,
  CrewAI 1.9 tools + prompts + @CrewBase crew + pipeline.
- **Batch 3 — API.** FastAPI routes (auth, onboarding, runs, drafts, chat,
  integrations, webhooks, scheduler), Google/WordPress/Resend integrations,
  middleware.
- **Batch 4 — Frontend.** Next.js 16 App Router, Supabase SSR, Tailwind v4,
  TanStack Query v5 hooks, onboarding wizard, dashboard, drafts, chat.
- **Batch 5 — Runtime.** Celery tasks, Celery Beat, email brief template,
  Render/Vercel configs, tests, deployment runbook.
- **Batch 6 — Billing + learning.** Paystack GHS billing, performance
  feedback loop, settings, UI polish, final runbook.
