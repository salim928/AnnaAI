-- ===========================================================================
-- AnnaAi — 002 row-level security
-- Each org sees only its own data.
-- ===========================================================================

-- Helper ------------------------------------------------------------------
create or replace function get_user_org_id()
returns uuid
language sql
stable
security definer
as $$
    select org_id from users where id = auth.uid()
$$;

-- Enable RLS --------------------------------------------------------------
alter table organizations    enable row level security;
alter table users            enable row level security;
alter table brand_memory     enable row level security;
alter table oauth_tokens     enable row level security;
alter table agent_runs       enable row level security;
alter table content_drafts   enable row level security;
alter table content_metrics  enable row level security;
alter table daily_briefs     enable row level security;
alter table chat_messages    enable row level security;
alter table scheduled_tasks  enable row level security;

-- organizations -----------------------------------------------------------
drop policy if exists organizations_select on organizations;
create policy organizations_select on organizations
    for select using (id = get_user_org_id());

drop policy if exists organizations_update on organizations;
create policy organizations_update on organizations
    for update using (id = get_user_org_id());

-- users -------------------------------------------------------------------
drop policy if exists users_select on users;
create policy users_select on users
    for select using (org_id = get_user_org_id());

drop policy if exists users_update_self on users;
create policy users_update_self on users
    for update using (id = auth.uid());

-- Generic org-scoped policies ---------------------------------------------
-- brand_memory
drop policy if exists brand_memory_all on brand_memory;
create policy brand_memory_all on brand_memory
    for all using (org_id = get_user_org_id())
    with check (org_id = get_user_org_id());

-- oauth_tokens
drop policy if exists oauth_tokens_all on oauth_tokens;
create policy oauth_tokens_all on oauth_tokens
    for all using (org_id = get_user_org_id())
    with check (org_id = get_user_org_id());

-- agent_runs
drop policy if exists agent_runs_all on agent_runs;
create policy agent_runs_all on agent_runs
    for all using (org_id = get_user_org_id())
    with check (org_id = get_user_org_id());

-- content_drafts
drop policy if exists content_drafts_all on content_drafts;
create policy content_drafts_all on content_drafts
    for all using (org_id = get_user_org_id())
    with check (org_id = get_user_org_id());

-- content_metrics (via draft_id)
drop policy if exists content_metrics_all on content_metrics;
create policy content_metrics_all on content_metrics
    for all using (
        exists (
            select 1 from content_drafts d
            where d.id = content_metrics.draft_id
              and d.org_id = get_user_org_id()
        )
    );

-- daily_briefs
drop policy if exists daily_briefs_all on daily_briefs;
create policy daily_briefs_all on daily_briefs
    for all using (org_id = get_user_org_id())
    with check (org_id = get_user_org_id());

-- chat_messages
drop policy if exists chat_messages_all on chat_messages;
create policy chat_messages_all on chat_messages
    for all using (org_id = get_user_org_id())
    with check (org_id = get_user_org_id());

-- scheduled_tasks
drop policy if exists scheduled_tasks_all on scheduled_tasks;
create policy scheduled_tasks_all on scheduled_tasks
    for all using (org_id = get_user_org_id())
    with check (org_id = get_user_org_id());
