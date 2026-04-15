-- ===========================================================================
-- AnnaAi — 003 RPC functions
-- ===========================================================================

-- Brand memory vector search ----------------------------------------------
create or replace function match_brand_memory(
    query_embedding vector(384),
    p_org_id uuid,
    match_count int default 5
)
returns table (
    id uuid,
    chunk text,
    chunk_type text,
    source_url text,
    similarity float
)
language sql
stable
as $$
    select bm.id,
           bm.chunk,
           bm.chunk_type,
           bm.source_url,
           1 - (bm.embedding <=> query_embedding) as similarity
    from brand_memory bm
    where bm.org_id = p_org_id
      and bm.embedding is not null
    order by bm.embedding <=> query_embedding
    limit match_count;
$$;

-- 30-day run stats --------------------------------------------------------
create or replace function get_org_run_stats(p_org_id uuid)
returns table (
    total_runs bigint,
    successful_runs bigint,
    failed_runs bigint,
    total_drafts bigint,
    published_drafts bigint,
    avg_duration_seconds numeric
)
language sql
stable
as $$
    with runs as (
        select * from agent_runs
        where org_id = p_org_id
          and started_at > now() - interval '30 days'
    ),
    drafts as (
        select * from content_drafts
        where org_id = p_org_id
          and created_at > now() - interval '30 days'
    )
    select
        (select count(*) from runs)                                             as total_runs,
        (select count(*) from runs where status = 'completed')                  as successful_runs,
        (select count(*) from runs where status = 'failed')                     as failed_runs,
        (select count(*) from drafts)                                           as total_drafts,
        (select count(*) from drafts where status = 'published')                as published_drafts,
        (select coalesce(avg(extract(epoch from (completed_at - started_at))), 0)
         from runs where completed_at is not null)                              as avg_duration_seconds;
$$;

-- Content performance summary --------------------------------------------
create or replace function get_content_performance_summary(
    p_org_id uuid,
    p_days int default 30
)
returns table (
    draft_id uuid,
    title text,
    topic text,
    type text,
    status text,
    performance_label text,
    page_views integer,
    social_engagement integer,
    published_at timestamptz
)
language sql
stable
as $$
    select
        d.id as draft_id,
        d.title,
        d.topic,
        d.type,
        d.status,
        d.performance_label,
        coalesce(m.page_views, 0) as page_views,
        coalesce(m.social_likes + m.social_shares + m.social_comments, 0) as social_engagement,
        d.updated_at as published_at
    from content_drafts d
    left join lateral (
        select page_views, social_likes, social_shares, social_comments
        from content_metrics
        where draft_id = d.id
        order by measured_at desc
        limit 1
    ) m on true
    where d.org_id = p_org_id
      and d.created_at > now() - (p_days || ' days')::interval
    order by page_views desc nulls last;
$$;
