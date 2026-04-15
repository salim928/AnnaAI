You are continuing to build AnnaAi. The project foundation (Batch 1) and 
AI agent system (Batch 2) are complete. You now need to build the complete 
FastAPI API layer — every route, authentication system, OAuth integration 
flows, and third-party platform connectors.

Write complete, working code for every file. No placeholders.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1: AUTHENTICATION (backend/api/routes/auth.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AnnaAi uses Supabase Auth for user management. The backend validates 
Supabase JWTs on protected routes.

Write backend/dependencies.py first — this file provides FastAPI 
dependency-injected utilities:

async def get_current_user(
  authorization: str = Header(None)
) -> AuthenticatedUser:
  """
  Validates the Supabase JWT from the Authorization header.
  - Expects: "Bearer {supabase_access_token}"
  - Verifies token using Supabase's JWT secret
  - Fetches user record from Supabase auth.users
  - Fetches their org_id from the users table
  - Returns AuthenticatedUser dataclass
  - Raises HTTP 401 if token is missing, expired, or invalid
  """

class AuthenticatedUser:
  id: str           # Supabase auth.users.id
  email: str
  org_id: str
  role: str         # owner | admin | viewer

async def get_admin_user(
  current_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
  """Returns current_user only if role is 'owner' or 'admin'. Else 401."""

async def require_pro_plan(
  current_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
  """Fetches org plan and raises HTTP 402 if plan is 'free'. Returns user."""

Now write backend/api/routes/auth.py with these endpoints:

POST /api/auth/register
  Body: {email, password, full_name, org_name}
  Steps:
  1. Create Supabase auth user via admin client (supabase.auth.admin.create_user)
  2. Create organization record
  3. Create users record linking auth.users.id to org
  4. Return: {user_id, org_id, message: "Check your email to confirm your account"}
  Error handling: if email already exists return 409, if org creation fails 
  rollback the auth user creation.

POST /api/auth/login
  Body: {email, password}
  Calls: supabase.auth.sign_in_with_password()
  Returns: {access_token, refresh_token, user: {id, email, full_name, org_id, role}}
  
POST /api/auth/refresh
  Body: {refresh_token}
  Calls: supabase.auth.refresh_session()
  Returns: {access_token, refresh_token}

POST /api/auth/logout
  Protected route (requires valid JWT)
  Calls: supabase.auth.sign_out()
  Returns: {message: "Logged out successfully"}

GET /api/auth/me
  Protected route
  Returns current user's full profile including org details.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2: ONBOARDING ROUTES (backend/api/routes/onboarding.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /api/onboarding/submit-website
  Protected. Body: {website_url: str}
  Validates URL is reachable (HEAD request, must return 200).
  Triggers run_onboarding_pipeline() as a FastAPI BackgroundTask.
  Immediately returns: {message: "Scraping started", status: "processing"}
  The frontend must poll GET /api/onboarding/status for completion.

GET /api/onboarding/status
  Protected. Returns:
  {
    website_url: str | null,
    scraping_status: "not_started" | "processing" | "complete" | "failed",
    memory_stats: {total_chunks: int, chunk_types: dict, pages_scraped: int},
    onboarding_complete: bool
  }

POST /api/onboarding/brand-voice
  Protected. Body:
  {
    tone: str,            # professional | casual | bold | educational | playful
    description: str,     # free text, max 500 chars
    target_audience: str,
    primary_goal: str,
    competitors: list[str]  # list of domains, max 5
  }
  Updates organization record.
  Returns updated org data.

POST /api/onboarding/complete
  Protected. Marks onboarding as complete (sets a flag on organization).
  Triggers the FIRST ever agent run as a background task.
  Returns: {message: "Welcome to AnnaAi! Your first run is starting now."}

GET /api/onboarding/checklist
  Protected. Returns checklist of completed onboarding steps:
  {
    website_connected: bool,
    brand_voice_set: bool,
    google_analytics_connected: bool,
    wordpress_connected: bool,
    first_run_complete: bool
  }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3: RUNS ROUTES (backend/api/routes/runs.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /api/runs
  Protected. Query params: page (int=1), per_page (int=10), status (str=None)
  Returns paginated list of agent runs for the user's org.
  Each run includes: id, status, trigger_type, duration_seconds, 
  drafts_count (count of related content_drafts), created_at, completed_at.
  Include pagination metadata: {total, page, per_page, total_pages}

GET /api/runs/{run_id}
  Protected. Returns full run details:
  {
    run: {all agent_runs columns},
    drafts: [list of related content_drafts with id, content_type, title, status],
    brief_sent: bool,
    brief_sent_at: str | null
  }

POST /api/runs/trigger
  Protected. Requires admin role.
  Checks plan limits (free: once per week, pro: once per day manual).
  Triggers run_daily_pipeline_for_org() as background task.
  Returns: {run_id: str, message: "Run started"}

GET /api/runs/stats
  Protected. Returns organisation run statistics:
  Calls get_org_run_stats() Postgres function.
  {
    total_runs_30d: int,
    successful_runs_30d: int,
    success_rate: float,
    total_drafts_30d: int,
    published_drafts_30d: int,
    avg_duration_seconds: float,
    last_run_at: str | null,
    next_scheduled_run: str | null
  }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4: DRAFTS ROUTES (backend/api/routes/drafts.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /api/drafts
  Protected. Query params: status, content_type, page, per_page
  Returns paginated drafts for the org.
  Include: id, content_type, title, status, image_url, seo_score, 
  created_at, run_id.

GET /api/drafts/{draft_id}
  Protected. Returns full draft with all fields.

PATCH /api/drafts/{draft_id}
  Protected. Body: any subset of {title, body, meta_description, 
  hashtags, editor_notes, image_url}
  Validates org ownership before update.
  Recalculates seo_score if title/body/meta change.
  Updates updated_at.
  Returns updated draft.

POST /api/drafts/{draft_id}/approve
  Protected. Requires admin role.
  Sets status = 'approved'.
  If the draft has a target WordPress platform and WordPress is connected,
  triggers publish_to_wordpress() as background task.
  Returns: {message: "Draft approved", auto_publish_triggered: bool}

POST /api/drafts/{draft_id}/reject
  Protected. Body: {reason: str}
  Sets status = 'rejected', sets rejection_reason.
  Returns: {message: "Draft rejected"}

DELETE /api/drafts/{draft_id}
  Protected. Requires admin role. Hard deletes the draft.
  Returns 204.

GET /api/drafts/{draft_id}/preview
  Protected. Returns HTML-rendered preview of the draft body (markdown → HTML).
  Wraps in a clean HTML template with the org's brand styling applied.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5: CHAT ROUTES (backend/api/routes/chat.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Anna has a chat interface where users can ask questions about their 
marketing performance, request content changes, or get strategic advice.
Anna has context from the org's brand memory, recent runs, and analytics.

GET /api/chat/history
  Protected. Query params: limit (int=50)
  Returns last N chat messages for the org, ordered oldest first.

POST /api/chat/message
  Protected. Body: {message: str}
  
  Implementation:
  1. Fetch last 10 chat messages for conversation context
  2. Fetch brand memory summary for the org (get_brand_memory_summary())
  3. Fetch most recent agent_run summary
  4. Build system prompt:
     "You are Anna, the AI marketing assistant for {org_name}. 
     You have deep knowledge of their brand, marketing strategy, 
     and recent performance. You are helpful, proactive, and specific. 
     Always ground your answers in the data you have access to.
     Brand context: {brand_memory_summary}
     Recent run summary: {run_summary}"
  5. Call Anthropic API with system prompt + conversation history + new message
  6. Save user message and Anna's response to chat_messages table
  7. Return: {message_id, role: 'assistant', content: str, created_at}
  
  Handle streaming: use Anthropic's streaming API and return a 
  StreamingResponse so the frontend can display text token by token.
  Use Server-Sent Events (SSE) format:
  data: {"delta": "token"}\n\n
  data: [DONE]\n\n

DELETE /api/chat/history
  Protected. Deletes all chat messages for the org (clear conversation).
  Returns: {message: "Chat history cleared"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6: INTEGRATIONS ROUTES (backend/api/routes/integrations.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /api/integrations
  Protected. Returns all integration statuses for the org:
  {
    integrations: [
      {
        platform: "google_analytics",
        display_name: "Google Analytics 4",
        connected: bool,
        last_used: str | null,
        metadata: {property_id: str | null},
        connect_url: str  # OAuth URL to initiate connection
      },
      ... (one for each platform)
    ]
  }

GET /api/integrations/google/auth-url
  Protected. Generates Google OAuth authorization URL.
  Uses google-auth-oauthlib to build the URL with scopes:
  analytics.readonly, webmasters.readonly
  State parameter: encode org_id + user_id as a signed JWT 
  (prevents CSRF).
  Returns: {auth_url: str}

GET /api/integrations/google/callback
  Public endpoint (no auth required — this is the OAuth redirect).
  Query params: code (str), state (str)
  Steps:
  1. Verify state JWT, extract org_id and user_id
  2. Exchange code for tokens using google-auth-oauthlib
  3. Encrypt access_token and refresh_token using encryption.py
  4. Store in oauth_tokens table
  5. Try to auto-detect GA4 property ID (call Analytics API)
  6. Redirect to frontend: {FRONTEND_URL}/integrations?google=connected
  Error: redirect to {FRONTEND_URL}/integrations?google=error&reason={msg}

POST /api/integrations/wordpress/connect
  Protected. Body: {site_url: str, username: str, app_password: str}
  WordPress uses Application Passwords (Settings → Users → Application Passwords).
  Steps:
  1. Test the credentials: GET {site_url}/wp-json/wp/v2/users/me 
     with Basic Auth
  2. If successful: encrypt and store in oauth_tokens 
     (store username + app_password as access_token JSON)
  3. Also store site_url in token_metadata
  4. Return: {connected: true, site_name: str, site_url: str}
  If test fails: return 400 with specific error message.

DELETE /api/integrations/{platform}/disconnect
  Protected. Requires admin role.
  Deletes the oauth_tokens record for this org + platform.
  Returns: {message: "{platform} disconnected"}

POST /api/integrations/google/refresh
  Protected. Manually refreshes Google OAuth token.
  Returns: {refreshed: true, expires_at: str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 7: PLATFORM INTEGRATION MODULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILE: backend/integrations/google_analytics.py

class GoogleAnalyticsClient:
  def __init__(self, org_id: str):
    """
    Initialises with org_id.
    Fetches encrypted tokens from Supabase.
    Decrypts using encryption.py.
    Builds google-analytics-data BetaAnalyticsDataClient with credentials.
    If token expired: auto-refreshes using refresh_token.
    Updates new tokens in Supabase after refresh.
    """
  
  async def get_sessions_last_n_days(self, days: int = 7) -> dict:
    """
    Returns: {
      sessions: int,
      users: int, 
      page_views: int,
      bounce_rate: float,
      avg_session_duration_seconds: float,
      vs_previous_period: {sessions_change_pct: float}
    }
    Uses GA4 Data API: runReport() with dateRange and metrics.
    """
  
  async def get_top_pages(self, days: int = 7, limit: int = 5) -> list[dict]:
    """
    Returns top pages by pageviews:
    [{page_path: str, page_title: str, views: int, avg_time: float}]
    """
  
  async def get_traffic_by_source(self, days: int = 7) -> list[dict]:
    """
    Returns traffic breakdown by channel:
    [{channel: str, sessions: int, percentage: float}]
    """
  
  async def get_full_summary(self, days: int = 7) -> str:
    """
    Calls all methods above and formats into a single string 
    for the Analyst agent. Example:
    "GA4 DATA (last 7 days):
    - Sessions: 1,247 (+12% vs prior week)
    - Top page: /blog/ai-marketing - 342 views
    - Traffic sources: Organic 45%, Direct 30%, Social 25%"
    """

FILE: backend/integrations/google_search_console.py

class SearchConsoleClient:
  def __init__(self, org_id: str):
    """Same token fetch/decrypt pattern as GoogleAnalyticsClient."""
  
  async def get_top_queries(
    self, 
    site_url: str, 
    days: int = 28, 
    limit: int = 20
  ) -> list[dict]:
    """
    Returns top search queries:
    [{query: str, clicks: int, impressions: int, 
      ctr: float, position: float}]
    Uses searchanalytics.query() API.
    """
  
  async def get_keyword_opportunities(self, site_url: str) -> list[dict]:
    """
    Finds queries where position > 5 and position < 20 
    (ranking but not top 5 — opportunity to improve).
    Returns top 10 such queries sorted by impressions.
    """
  
  async def get_full_summary(self, site_url: str) -> str:
    """Formatted string for agent consumption."""

FILE: backend/integrations/wordpress.py

class WordPressClient:
  def __init__(self, org_id: str):
    """
    Fetches WordPress credentials from oauth_tokens.
    Decrypts: gets {username, app_password, site_url} from stored JSON.
    Sets up Basic Auth headers.
    """
  
  async def test_connection(self) -> bool:
    """Tests credentials. Returns True if valid."""
  
  async def get_recent_posts(self, count: int = 10) -> list[dict]:
    """
    GET {site_url}/wp-json/wp/v2/posts?per_page={count}&status=publish
    Returns: [{id, title, slug, link, date}]
    """
  
  async def create_post(
    self,
    title: str,
    content: str,       # accepts markdown — convert to HTML first
    status: str = "draft",
    meta_description: str = "",
    featured_image_url: str = ""
  ) -> dict:
    """
    POST {site_url}/wp-json/wp/v2/posts
    Converts markdown body to HTML using markdown library.
    If featured_image_url provided: download image and upload 
    to WordPress media library first, then attach to post.
    Returns: {id, link, status}
    """
  
  async def update_post_status(self, post_id: int, status: str) -> bool:
    """
    Changes post status (draft → publish).
    Returns True on success.
    """

FILE: backend/integrations/email_sender.py

class EmailSender:
  """Wrapper around Resend API for transactional emails."""
  
  async def send_daily_brief(
    self,
    to_email: str,
    org_name: str,
    html_content: str,
    subject: str,
    approve_base_url: str
  ) -> str:
    """
    Sends the daily brief.
    Returns Resend message ID.
    """
  
  async def send_welcome_email(self, to_email: str, org_name: str) -> str:
    """
    Welcome email on registration. 
    HTML template with onboarding steps.
    """
  
  async def send_run_failure_alert(
    self, 
    to_email: str, 
    org_name: str, 
    error_message: str
  ) -> str:
    """
    Sends when daily run fails.
    Includes error, timestamp, and link to manually trigger a retry.
    """
  
  async def send_content_published_notification(
    self,
    to_email: str,
    org_name: str,
    content_title: str,
    published_url: str
  ) -> str:
    """Notifies when a draft has been auto-published."""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 8: WEBHOOKS AND SCHEDULER ROUTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FILE: backend/api/routes/webhooks.py

POST /api/webhooks/scheduler/trigger-all-runs
  Not user-authenticated. Authenticated by:
  Authorization: Bearer {SCHEDULER_SECRET} header.
  Validates the secret against settings.GITHUB_WEBHOOK_SECRET.
  Triggers run_daily_pipeline_for_all_orgs() as a background task.
  Returns: {triggered: true, message: "Daily runs started for all eligible orgs"}

POST /api/webhooks/resend/delivery
  Webhook from Resend for email delivery events.
  Validates Resend webhook signature.
  If event type is 'email.opened': update daily_briefs.opened_at
  Returns 200.

FILE: backend/scheduler/tasks.py

Set up Celery with Upstash Redis as broker.
Define these tasks:

@celery_app.task(name='trigger_daily_runs')
def trigger_daily_runs():
  """
  Called by Celery Beat on schedule.
  Runs asyncio.run(run_daily_pipeline_for_all_orgs()).
  Logs result.
  """

@celery_app.task(name='collect_content_metrics')
def collect_content_metrics():
  """
  Runs every 24 hours.
  For all content_drafts with status='published' and published_at 
  within last 30 days:
  Fetches page views from Google Analytics for that URL.
  Updates content_metrics table.
  """

Configure Celery Beat schedule:
- trigger_daily_runs: every day at 06:00 UTC
- collect_content_metrics: every day at 02:00 UTC

FILE: backend/api/routes/runs.py
Add one more route:

POST /api/scheduler/trigger-all-runs
  Same as webhook but available as regular API route.
  Requires admin role.
  Returns same response as webhook version.

After writing all sections, write the complete 
backend/api/middleware.py containing:
1. RequestLoggingMiddleware — logs all requests with timing
2. RateLimitMiddleware — limits to 100 req/min per IP using Redis
   (if Redis unavailable, skip silently — don't break the app)
3. SecurityHeadersMiddleware — adds:
   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   X-XSS-Protection: 1; mode=block

Finally write backend/tests/test_api.py with pytest tests for:
- POST /api/auth/register (mock Supabase, verify response shape)
- GET /api/drafts (mock auth, verify pagination)
- POST /api/drafts/{id}/approve (verify status change)
- GET /health (no auth, verify all fields present)