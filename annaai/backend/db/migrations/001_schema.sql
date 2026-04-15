-- ===========================================================================
-- AnnaAi — 001 schema
-- Run in the Supabase SQL editor. Idempotent.
-- ===========================================================================

create extension if not exists vector;
create extension if not exists pgcrypto;

-- updated_at trigger helper ------------------------------------------------
create or replace function set_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

-- 1. organizations ---------------------------------------------------------
create table if not exists organizations (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    website_url text,
    industry text,
    brand_voice text,
    brand_tone text,
    target_audience text,
    goals text,
    plan text not null default 'free',       -- free | pro | business
    onboarding_complete boolean not null default false,
    onboarding_step integer not null default 0,
    notification_email text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
drop trigger if exists organizations_set_updated_at on organizations;
create trigger organizations_set_updated_at
    before update on organizations
    for each row execute function set_updated_at();

-- 2. users -----------------------------------------------------------------
create table if not exists users (
    id uuid primary key,                     -- matches auth.users.id
    org_id uuid references organizations(id) on delete cascade,
    email text not null unique,
    full_name text,
    role text not null default 'owner',      -- owner | member
    created_at timestamptz not null default now()
);

-- 3. brand_memory ----------------------------------------------------------
create table if not exists brand_memory (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    chunk text not null,
    chunk_type text not null default 'content',
        -- content | voice | product | positive_feedback | negative_feedback
    embedding vector(384),
    source_url text,
    page_title text,
    created_at timestamptz not null default now()
);
-- HNSW index (default in pgvector 0.7+) — built online, no post-populate step
create index if not exists brand_memory_embedding_idx
    on brand_memory using hnsw (embedding vector_cosine_ops)
    with (m = 16, ef_construction = 64);
create index if not exists brand_memory_org_idx on brand_memory(org_id);

-- 4. oauth_tokens ----------------------------------------------------------
create table if not exists oauth_tokens (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    platform text not null,                  -- google | instagram | wordpress
    access_token text,                       -- Fernet-encrypted
    refresh_token text,                      -- Fernet-encrypted
    scope text,
    expires_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (org_id, platform)
);
drop trigger if exists oauth_tokens_set_updated_at on oauth_tokens;
create trigger oauth_tokens_set_updated_at
    before update on oauth_tokens
    for each row execute function set_updated_at();

-- 5. agent_runs ------------------------------------------------------------
create table if not exists agent_runs (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    status text not null default 'running',  -- running | completed | failed
    run_type text not null default 'daily',  -- daily | onboarding | manual
    summary text,
    error_message text,
    metadata jsonb not null default '{}'::jsonb,
    started_at timestamptz not null default now(),
    completed_at timestamptz
);
create index if not exists agent_runs_org_idx on agent_runs(org_id, started_at desc);

-- 6. content_drafts --------------------------------------------------------
create table if not exists content_drafts (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    run_id uuid references agent_runs(id) on delete set null,
    type text not null,                      -- blog_post | instagram_post | email
    title text,
    body text,
    meta_description text,
    image_url text,
    topic text,
    keywords text[],
    status text not null default 'draft',    -- draft | approved | published | rejected
    rejection_reason text,
    platform_url text,
    performance_label text,                  -- high_performer | average | low_performer
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
drop trigger if exists content_drafts_set_updated_at on content_drafts;
create trigger content_drafts_set_updated_at
    before update on content_drafts
    for each row execute function set_updated_at();
create index if not exists content_drafts_org_idx on content_drafts(org_id, created_at desc);

-- 7. content_metrics -------------------------------------------------------
create table if not exists content_metrics (
    id uuid primary key default gen_random_uuid(),
    draft_id uuid not null references content_drafts(id) on delete cascade,
    page_views integer not null default 0,
    unique_visitors integer not null default 0,
    social_likes integer not null default 0,
    social_shares integer not null default 0,
    social_comments integer not null default 0,
    measured_at timestamptz not null default now()
);
create index if not exists content_metrics_draft_idx on content_metrics(draft_id, measured_at desc);

-- 8. daily_briefs ----------------------------------------------------------
create table if not exists daily_briefs (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    run_id uuid references agent_runs(id) on delete set null,
    subject text not null,
    html_body text not null,
    sent_to text,
    sent_at timestamptz not null default now()
);

-- 9. chat_messages ---------------------------------------------------------
create table if not exists chat_messages (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    user_id uuid references users(id) on delete set null,
    role text not null,                      -- user | assistant | system
    content text not null,
    created_at timestamptz not null default now()
);
create index if not exists chat_messages_org_idx on chat_messages(org_id, created_at desc);

-- 10. scheduled_tasks ------------------------------------------------------
create table if not exists scheduled_tasks (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    task_name text not null,
    cron_expression text not null,
    enabled boolean not null default true,
    last_run_at timestamptz,
    next_run_at timestamptz,
    created_at timestamptz not null default now()
);
