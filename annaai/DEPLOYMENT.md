# AnnaAi Deployment Runbook

Everything you need to take AnnaAi from a local checkout to a fully running
production stack on free tiers. Read top to bottom on first deploy — the
order matters because each step produces a credential the next step needs.

## 0. Free-tier accounts

| Service     | Purpose                               | URL                             |
|-------------|---------------------------------------|---------------------------------|
| Supabase    | Postgres + pgvector + auth            | https://supabase.com            |
| Upstash     | Redis for Celery broker + backend     | https://upstash.com             |
| Render      | Backend web service + Celery workers  | https://render.com              |
| Vercel      | Next.js frontend                      | https://vercel.com              |
| Anthropic   | Claude Sonnet 4 API                   | https://console.anthropic.com   |
| Resend      | Transactional email                   | https://resend.com              |
| Google Cloud| GA4 + Search Console OAuth            | https://console.cloud.google.com|
| Paystack    | GHS billing (Batch 6)                 | https://dashboard.paystack.com  |

## 1. Supabase

1. Create a new project. Region close to Render Oregon.
2. `Settings → API`: copy `URL`, `anon key`, `service_role key`.
3. `Settings → Database`: copy the connection string (URI) → `SUPABASE_DB_URL`.
4. Open the SQL editor and run in order:
   1. `backend/db/migrations/001_schema.sql`
   2. `backend/db/migrations/002_rls.sql`
   3. `backend/db/migrations/003_functions.sql`
5. Verify: `select * from pg_indexes where indexname like '%hnsw%';` — you
   should see the HNSW index on `brand_memory`.

## 2. Upstash Redis

1. Create a Redis database, TLS enabled.
2. Copy the `redis://` connection string → `REDIS_URL`.

## 3. Anthropic + Resend + Google

- Anthropic: create an API key → `ANTHROPIC_API_KEY`.
- Resend: verify a sending domain; create API key → `RESEND_API_KEY`.
- Google Cloud: OAuth client (Web), redirect URI
  `https://YOUR-BACKEND.onrender.com/api/integrations/google/callback`.

## 4. Backend on Render

1. New → Blueprint → connect this repo → select `backend/render.yaml`.
2. Fill secrets for the `annaai-shared` env var group.
3. Apply. Render spins up:
   - `annaai-backend` (FastAPI web)
   - `annaai-celery-worker`
   - `annaai-celery-beat`
4. Health check: `https://YOUR-BACKEND.onrender.com/health` returns
   `{"status":"ok"}`.

## 5. Frontend on Vercel

1. New project → import repo → root `frontend/`.
2. Environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_BACKEND_URL=https://YOUR-BACKEND.onrender.com`
3. Deploy. Vercel runs `next build` with Turbopack.

## 6. Supabase auth callback

In Supabase `Authentication → URL Configuration`:
- Site URL: `https://YOUR-FRONTEND.vercel.app`
- Redirect URLs: `https://YOUR-FRONTEND.vercel.app/api/auth/callback`

## 7. Daily cron (GitHub Actions fallback)

Render's free beat worker sleeps after 15 minutes idle. The
`.github/workflows/daily_anna.yml` action fires a POST at 06:00 UTC to
`/api/scheduler/trigger-all-runs` with the `SCHEDULER_SECRET` bearer token,
which wakes Render and triggers the daily pipeline for every org.

Configure the GitHub repo secrets:
- `BACKEND_URL`
- `SCHEDULER_SECRET`

## 8. Smoke test

1. Register a new account on the frontend.
2. Complete the onboarding wizard with a real website URL.
3. Wait 3–5 minutes; watch Render logs — you should see scrape → embed →
   crew.kickoff → draft saved.
4. Dashboard should list the run and at least one draft.
5. Approve a draft → confirm it appears in WordPress (if connected).

## 9. Rotating secrets

- `ENCRYPTION_KEY` is used to encrypt stored OAuth tokens. Rotate by
  generating a new Fernet key and re-encrypting existing `oauth_tokens`
  rows. Do not rotate casually — broken tokens mean users re-authenticate.
- `SECRET_KEY` (JWT signing): rotating invalidates all active sessions.
- `SCHEDULER_SECRET`: update both Render env and GitHub secret together.

## 10. Shutdown / teardown

The project is designed to sit on free tiers indefinitely. To wind down:
1. Delete Render services (web + both workers).
2. Delete Vercel project.
3. Pause or delete the Supabase project (data export first if needed).
4. Revoke Anthropic, Resend, Google OAuth credentials.
