You are continuing to build AnnaAi, an autonomous AI marketing agent platform.
The project structure, database schema, configuration, and utilities are already 
built (Batch 1). You now need to build the complete AI brain of the system:
the web scraper that builds brand memory, the vector embedding pipeline,
and the full multi-agent crew that runs every day.

All code must be production-grade, fully typed, and completely implemented.
No placeholders. No "TODO: implement this". Every function must work.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1: WEB SCRAPER (backend/memory/scraper.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write the complete scraper module. This scraper crawls a business's 
entire website to build their brand memory. It must be polite, robust, 
and handle real-world messy websites gracefully.

Implement these functions:

class SiteScrapingResult:
  url: str
  pages_scraped: int
  total_chunks: int
  content_types_found: list[str]
  errors: list[str]
  duration_seconds: float

async def scrape_website(url: str, max_pages: int = 20) -> list[PageContent]:
  """
  Crawls a website starting from the given URL.
  - Validates the URL is reachable before starting
  - Discovers internal links by parsing <a href> tags
  - Only follows links on the same domain (no external links)
  - Skips: /wp-admin, /cart, /checkout, /account, 
    /?s=, /tag/, /page/, .pdf, .jpg, .png, .zip
  - Adds a 1-second delay between each page fetch (politeness)
  - Sets a realistic User-Agent header
  - Handles: connection errors, timeouts, non-200 responses, 
    encoding issues — log errors but continue to next page
  - Maximum depth: 3 levels from the starting URL
  - Returns list of PageContent objects
  """

class PageContent:
  url: str
  title: str
  meta_description: str
  headings: list[str]  # All h1-h3 text
  body_text: str       # Clean text, HTML stripped
  content_type: str    # 'homepage' | 'about' | 'product' | 'blog' | 'contact' | 'other'
  word_count: int

def classify_page_type(url: str, title: str, headings: list[str]) -> str:
  """
  Heuristically classify page type from URL patterns and content.
  Rules:
  - URL contains /about, /who-we-are → 'about'
  - URL contains /product, /service, /shop → 'product'  
  - URL contains /blog, /news, /article → 'blog'
  - URL contains /contact → 'contact'
  - URL is the root / → 'homepage'
  - Otherwise → 'other'
  """

def extract_page_content(url: str, html: str) -> PageContent:
  """
  Uses trafilatura for main content extraction.
  Falls back to BeautifulSoup if trafilatura returns empty.
  Extracts: title (from <title> or og:title), 
            meta description (from <meta name=description> or og:description),
            headings (all h1, h2, h3 text),
            body_text (trafilatura main content extraction)
  Cleans text: collapse multiple whitespace, strip HTML entities.
  """

def prepare_chunks_for_embedding(pages: list[PageContent]) -> list[TextChunk]:
  """
  Converts PageContent objects into chunks ready for embedding.
  Strategy:
  - For each page, create a "header chunk" with: title + meta_description + headings
    (This chunk carries high-level brand info — always include it)
  - For body_text > 100 words: chunk into 400-token segments with 50-token overlap
    using the chunk_text() helper from utils
  - Tag each chunk with its chunk_type (from PageContent.content_type)
  - Include source_url in each chunk
  - Skip chunks with fewer than 20 words
  Returns list of TextChunk objects
  """

class TextChunk:
  text: str
  source_url: str
  chunk_type: str
  page_title: str

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2: EMBEDDER (backend/memory/embedder.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write the complete embedder module. This uses sentence-transformers 
locally — no API call, no cost, no rate limits.

class EmbeddingService:
  """
  Singleton embedding service that loads the model once at startup
  and reuses it across all requests. Thread-safe.
  """
  
  _instance = None
  _model = None
  _model_name: str = settings.EMBEDDING_MODEL_NAME
  
  @classmethod
  def get_instance(cls) -> 'EmbeddingService':
    """Returns the singleton instance, creating it if needed."""
  
  def load_model(self) -> None:
    """
    Loads sentence-transformers model.
    Logs start and completion with duration.
    Stores model in self._model.
    """
  
  def embed_text(self, text: str) -> list[float]:
    """
    Embeds a single string. Returns list of 384 floats.
    Normalises the embedding to unit length.
    """
  
  def embed_batch(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """
    Embeds a list of texts efficiently in batches.
    Shows progress for batches > 10.
    Returns list of embedding vectors.
    """
  
  def embed_query(self, query: str) -> list[float]:
    """
    Embeds a search query. Identical to embed_text but 
    semantically distinct (for future asymmetric embedding support).
    """
  
  @property
  def is_loaded(self) -> bool:
    """Returns True if model is loaded and ready."""

def get_embedder() -> EmbeddingService:
  """FastAPI dependency that returns the singleton EmbeddingService."""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3: VECTOR STORE (backend/memory/vector_store.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write the complete vector store module. This handles all brand memory 
storage and retrieval in Supabase pgvector.

async def store_brand_memory(
  org_id: str,
  chunks: list[TextChunk],
  embeddings: list[list[float]]
) -> int:
  """
  Stores chunks + embeddings in the brand_memory table.
  - Deletes ALL existing brand_memory for this org_id first 
    (full refresh on re-onboard)
  - Inserts all chunks in batches of 50 (Supabase limit)
  - Returns count of stored chunks
  - Uses the admin Supabase client (bypasses RLS for background task)
  """

async def recall_brand_memory(
  org_id: str,
  query: str,
  top_k: int = 5,
  chunk_type_filter: str | None = None
) -> list[MemoryResult]:
  """
  Retrieves the most relevant brand memory chunks for a query.
  - Embeds the query using EmbeddingService
  - Calls the match_brand_memory Postgres function via Supabase RPC
  - Optionally filters by chunk_type
  - Returns list of MemoryResult ordered by similarity (highest first)
  """

class MemoryResult:
  chunk: str
  chunk_type: str
  source_url: str
  similarity: float

async def get_brand_memory_summary(org_id: str) -> str:
  """
  Returns a concise text summary of the organisation's brand memory.
  Retrieves the top homepage and about page chunks, 
  formats them into a readable paragraph that agents can use 
  as context in their system prompts.
  Truncated to 800 tokens maximum.
  """

async def get_memory_stats(org_id: str) -> dict:
  """
  Returns:
  {
    total_chunks: int,
    chunk_types: dict[str, int],  # e.g. {'homepage': 3, 'about': 5, 'product': 12}
    last_updated: str,
    pages_scraped: int (approximate from distinct source_urls)
  }
  """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4: AGENT TOOLS (backend/agents/tools.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write every agent tool as a proper LangChain @tool decorated function.
Each tool must have a detailed docstring (this is what the agent sees 
when deciding which tool to use — make it clear and specific).
Each tool must handle errors gracefully and return a string even on failure 
(the agent needs to continue if one tool fails).

Implement ALL of these tools:

1. recall_brand_memory
   Input: query (str), org_id (str)
   Calls vector_store.recall_brand_memory()
   Returns formatted string of relevant brand memory chunks with their types.
   Format: "BRAND MEMORY RESULTS:\n\n[chunk_type]: [chunk]\nSource: [url]\n\n..."

2. search_web
   Input: query (str)
   Uses duckduckgo-search (DDGS) to search for up to 5 results.
   Returns formatted string: each result as "Title: X\nURL: Y\nSnippet: Z\n\n"
   Implements retry (up to 3 times) if DDGS raises an exception.
   Respects rate limits by sleeping 2 seconds between searches.

3. search_competitor_content
   Input: competitor_domain (str), topic (str)
   Builds a DuckDuckGo query: "site:{competitor_domain} {topic}"
   Returns the top 3 results formatted as above.
   Used to see what competitors are publishing.

4. get_trending_topics
   Input: industry (str), location (str = "Ghana")
   Searches DuckDuckGo for: "trending {industry} topics {location} {current_month} {current_year}"
   Also searches: "{industry} news this week"
   Returns combined results formatted as a numbered list.

5. generate_image
   Input: prompt (str), width (int = 1200), height (int = 630)
   Calls Pollinations.ai: GET https://image.pollinations.ai/prompt/{encoded_prompt}?width=W&height=H&nologo=true
   The URL itself IS the image (no download needed).
   Returns the image URL string.
   Enhances the prompt automatically: prepend "professional marketing photo, " 
   and append ", high quality, commercial photography style"

6. save_content_draft
   Input: org_id (str), run_id (str), content_type (str), title (str), 
          body (str), meta_description (str = ""), hashtags (list[str] = []),
          image_url (str = ""), image_prompt (str = ""), seo_score (int = 0)
   Saves to content_drafts table via Supabase admin client.
   Returns: "Draft saved. ID: {draft_id}"

7. get_analytics_summary
   Input: org_id (str), days (int = 7)
   Fetches from google_analytics.py module.
   If no Google token exists for this org, returns:
   "No Google Analytics connected. Skipping analytics data."
   Returns formatted summary string.

8. get_search_console_data
   Input: org_id (str), days (int = 28)
   Fetches top 10 queries from Google Search Console.
   If no token, returns graceful skip message.
   Returns formatted: "TOP SEARCH QUERIES:\n1. [query] - [clicks] clicks, position [pos]\n..."

9. get_wordpress_recent_posts
   Input: org_id (str), count (int = 5)
   Fetches recent posts from WordPress REST API if connected.
   Returns list of recent post titles and dates.
   Used by Strategist to avoid duplicating topics.

10. publish_to_wordpress
    Input: org_id (str), draft_id (str), status (str = "draft")
    Fetches the draft from Supabase.
    Posts to WordPress REST API.
    Updates draft status and published_url in Supabase.
    Returns: "Published to WordPress: {url}" or error message.
    Note: Default status is "draft" — never auto-publish without approval.

11. send_daily_brief
    Input: org_id (str), run_id (str), html_content (str), subject (str)
    Gets user email from Supabase.
    Sends via Resend API.
    Saves to daily_briefs table.
    Returns: "Brief sent to {email}" or error.

12. calculate_seo_score
    Input: title (str), body (str), meta_description (str), keywords (list[str])
    Calculates a simple SEO score (0-100) based on:
    - Title length 50-60 chars: +20 pts
    - Meta description 150-160 chars: +20 pts  
    - Body word count 800-2000 words: +20 pts
    - Keywords appear in title: +10 pts each (max +20)
    - Headers present in body (## or ###): +10 pts
    - Internal linking potential (body has URLs): +10 pts
    Returns: integer score

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5: AGENT PROMPTS (backend/agents/prompts.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write detailed, production-quality system prompts for each agent.
These are NOT one-liners. Each prompt must be 150–300 words, specific,
opinionated, and guide the agent to produce high-quality marketing outputs.

RESEARCHER_SYSTEM_PROMPT
Anna's Researcher agent. Purpose, capabilities, how to use its tools,
what to look for (trends, competitor moves, viral content angles),
what to return (structured research report with 3-5 key findings),
what NOT to do (hallucinate facts, use stale knowledge without searching).

ANALYST_SYSTEM_PROMPT
Anna's Analytics Analyst agent. How to interpret GA4 and GSC data,
what patterns matter (traffic spikes, top pages, declining pages,
keyword opportunities), how to write the analytics summary 
(specific numbers only, no vague statements), what insights to surface.

STRATEGIST_SYSTEM_PROMPT
Anna's Content Strategist agent. How to make decisions about what content
to create (weighing: trending topics + brand voice + analytics gaps + 
competitor moves + content type variety), the decision output format 
(must specify: content_type, topic, angle, target_keywords, why_this_works),
rules (never repeat a topic published in the last 14 days), 
how to balance short-form vs long-form.

CREATOR_SYSTEM_PROMPT
Anna's Content Creator agent. How to write each content type 
(blog post: structure with intro + 3 sections + CTA; 
Instagram: hook + value + CTA + hashtags;
email: subject A/B option + preview text + body + CTA),
brand voice adherence, SEO best practices, image prompt writing.

PUBLISHER_SYSTEM_PROMPT
Anna's Publisher agent. How to save drafts, when to auto-publish 
vs queue for approval (RULE: always queue if content involves 
paid promotion, pricing claims, or competitive comparisons),
how to write the daily brief summary, cleanup tasks.

Also write these template strings (use Python f-string format with {placeholders}):

DAILY_RUN_TASK_DESCRIPTION — The task description given to the crew 
for each daily run. Must include placeholders for:
{org_name}, {website_url}, {industry}, {brand_voice_tone}, 
{brand_voice_description}, {target_audience}, {primary_goal},
{competitors_list}, {today_date}, {day_of_week}

BRIEF_EMAIL_HTML_TEMPLATE — Full HTML email template for the daily brief.
Use inline CSS only (email clients strip <style> tags).
Include placeholders for:
{org_name}, {date}, {performance_summary}, {content_created_section},
{tomorrow_plan}, {key_insight}, {approve_link_base_url}
Design it to look professional but warm — AnnaAi brand colours: 
primary #1a1a2e (deep navy), accent #e94560 (coral red), 
background #f8f8f8, font: system-ui.
Must include the AnnaAi logo text at top (text, not image).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6: CREW DEFINITION (backend/agents/crew.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write the complete CrewAI crew definition.

class AnnaCrewConfig:
  org_id: str
  run_id: str
  org_name: str
  website_url: str
  industry: str
  brand_voice_tone: str
  brand_voice_description: str
  target_audience: str
  primary_goal: str
  competitors: list[str]

class AnnaCrew:
  """
  The core AnnaAi agent crew. 5 agents running sequentially.
  Each agent's output feeds into the next agent's context.
  """
  
  def __init__(self, config: AnnaCrewConfig):
    self.config = config
    self.llm = self._build_llm()
    self.tools = self._build_tools()
  
  def _build_llm(self) -> ChatAnthropic:
    """
    Returns LangChain ChatAnthropic client.
    Model: claude-sonnet-4-20250514
    Temperature: 0.7 for creative tasks
    Max tokens: 4096
    """
  
  def _build_tools(self) -> dict[str, list]:
    """
    Returns tool sets for each agent role.
    Researcher gets: [search_web, search_competitor_content, get_trending_topics]
    Analyst gets: [get_analytics_summary, get_search_console_data, recall_brand_memory]
    Strategist gets: [recall_brand_memory, get_wordpress_recent_posts, calculate_seo_score]
    Creator gets: [recall_brand_memory, generate_image, calculate_seo_score]
    Publisher gets: [save_content_draft, send_daily_brief]
    
    All tools are partially applied with the org_id so agents 
    don't need to know the org_id explicitly.
    Use functools.partial for this.
    """
  
  def build_researcher(self) -> Agent:
    """
    CrewAI Agent:
    role: "Marketing Researcher"
    goal: "Find the most relevant trending topics and competitor activities 
           in {industry} that {org_name} should respond to today."
    backstory: [Use RESEARCHER_SYSTEM_PROMPT]
    tools: researcher tools
    llm: self.llm
    verbose: True
    max_iter: 3
    allow_delegation: False
    """
  
  def build_analyst(self) -> Agent:
    """
    CrewAI Agent:
    role: "Analytics Analyst"
    goal: "Analyse {org_name}'s recent performance data and identify 
           the most important patterns and opportunities."
    backstory: [Use ANALYST_SYSTEM_PROMPT]
    tools: analyst tools
    llm: self.llm
    verbose: True
    max_iter: 3
    allow_delegation: False
    """
  
  def build_strategist(self) -> Agent:
    """
    CrewAI Agent:
    role: "Content Strategist"
    goal: "Decide exactly what content to create today for {org_name} 
           based on research, analytics, and brand guidelines."
    backstory: [Use STRATEGIST_SYSTEM_PROMPT]
    tools: strategist tools
    llm: self.llm
    verbose: True
    max_iter: 3
    allow_delegation: False
    """
  
  def build_creator(self) -> Agent:
    """
    CrewAI Agent:
    role: "Content Creator"
    goal: "Create complete, publish-ready content for {org_name} 
           that is on-brand, SEO-optimised, and engaging."
    backstory: [Use CREATOR_SYSTEM_PROMPT]
    tools: creator tools
    llm: self.llm
    verbose: True
    max_iter: 5
    allow_delegation: False
    """
  
  def build_publisher(self) -> Agent:
    """
    CrewAI Agent:
    role: "Publishing Manager"
    goal: "Save all created content as drafts and compile the daily 
           brief for {org_name}'s team."
    backstory: [Use PUBLISHER_SYSTEM_PROMPT]
    tools: publisher tools
    llm: self.llm
    verbose: True
    max_iter: 3
    allow_delegation: False
    """
  
  def build_tasks(
    self, 
    researcher: Agent, 
    analyst: Agent, 
    strategist: Agent, 
    creator: Agent, 
    publisher: Agent
  ) -> list[Task]:
    """
    Returns 5 CrewAI Tasks in order.
    
    Task 1 - Research:
    description: Full task description using DAILY_RUN_TASK_DESCRIPTION template
    agent: researcher
    expected_output: "A structured research report with exactly 5 findings. 
                      Format: FINDING [N]: [title]\nContext: [2-3 sentences]\n
                      Source: [URL or 'Market knowledge']\n\n"
    
    Task 2 - Analysis:
    description: "Using the research above, now analyse {org_name}'s recent 
                  analytics performance. Pull GA4 data for the last 7 days 
                  and Search Console data for the last 28 days. Identify: 
                  top 3 performing pages, traffic trend (up/down/flat), 
                  best keyword opportunities (queries ranking 5-20 that 
                  could move to top 3 with good content)."
    agent: analyst
    context: [task_1]  # receives researcher output
    expected_output: "ANALYTICS SUMMARY with exact numbers. Format:
                      TRAFFIC: [X] sessions last 7 days ([+/-Y]% vs prior week)
                      TOP PAGES: 1. [page] - [views]\n2. [page]...
                      KEYWORD OPPORTUNITIES: [list 3]
                      KEY INSIGHT: [one actionable sentence]"
    
    Task 3 - Strategy:
    description: "Based on the research and analytics, decide what content 
                  to create today. You must pick ONE primary content piece 
                  (blog post or email campaign) AND ONE social post 
                  (Instagram or LinkedIn). Avoid any topic published on 
                  {website_url} in the last 14 days — check WordPress posts. 
                  Explain your decision in 2-3 sentences."
    agent: strategist
    context: [task_1, task_2]
    expected_output: "STRATEGY DECISION:
                      PRIMARY CONTENT: [content_type]
                      TOPIC: [specific topic title]
                      ANGLE: [the unique angle or hook]
                      TARGET KEYWORDS: [keyword1], [keyword2], [keyword3]
                      WHY: [2-3 sentence rationale]
                      
                      SOCIAL CONTENT: [content_type]
                      TOPIC: [topic]
                      ANGLE: [hook]"
    
    Task 4 - Creation:
    description: "Create the complete content decided by the Strategist. 
                  For the blog post: write a full 800-1200 word article 
                  with title, meta description (155 chars), and body using 
                  markdown headers. Use {org_name}'s brand voice: {brand_voice_tone}.
                  For social: write the caption/thread with hashtags.
                  For each piece: generate an image using the image generation tool.
                  Ensure the brand voice matches: {brand_voice_description}."
    agent: creator
    context: [task_2, task_3]
    expected_output: "BLOG POST:
                      TITLE: [title]
                      META: [meta description]
                      BODY: [full markdown article]
                      IMAGE_PROMPT: [image prompt used]
                      IMAGE_URL: [URL from Pollinations]
                      SEO_SCORE: [0-100]
                      
                      SOCIAL POST:
                      TYPE: [instagram|linkedin]
                      CAPTION: [full caption with hashtags]
                      IMAGE_URL: [URL]"
    
    Task 5 - Publishing:
    description: "Save all created content as drafts in the system. 
                  Save the blog post as a 'blog_post' draft. 
                  Save the social post as the appropriate type draft. 
                  Then compile and send the daily brief email to the 
                  organization owner. The brief must include:
                  performance summary from analytics, what was created today,
                  one key insight worth acting on, what Anna plans to do tomorrow."
    agent: publisher
    context: [task_2, task_3, task_4]
    expected_output: "PUBLISHING COMPLETE:
                      Blog post draft saved: [draft_id]
                      Social post draft saved: [draft_id]
                      Daily brief sent to: [email]
                      
                      BRIEF SUMMARY:
                      [2-3 sentence summary of everything done today]"
    """
  
  def run(self) -> CrewOutput:
    """
    Assembles and runs the full crew.
    Returns CrewAI CrewOutput.
    Logs start and completion.
    """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 7: DAILY PIPELINE (backend/agents/daily_pipeline.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write the orchestration layer that runs for each organization.
This is what gets called by the scheduler.

async def run_daily_pipeline_for_org(org_id: str) -> PipelineResult:
  """
  Complete daily run pipeline for one organization.
  
  Steps:
  1. Fetch org details from Supabase (org info, settings)
  2. Check plan limits (free: 1 run/day max, check last run time)
  3. Create agent_runs record with status='running'
  4. Build AnnaCrewConfig from org data
  5. Instantiate AnnaCrew and run
  6. On success: update agent_runs with status='completed', 
     duration, token count estimate, summaries extracted from crew output
  7. On failure: update agent_runs with status='failed', error_message
  8. Return PipelineResult
  
  Error handling: 
  - If Anthropic API returns rate limit: wait 60 seconds and retry once
  - If any tool fails: log but let crew continue
  - If crew completely fails: mark run as failed, send failure notification email
  - Always update agent_runs, even on failure — never leave a run stuck on 'running'
  """

class PipelineResult:
  org_id: str
  run_id: str
  success: bool
  drafts_created: int
  error: str | None
  duration_seconds: float

async def run_daily_pipeline_for_all_orgs() -> list[PipelineResult]:
  """
  Fetches all orgs where daily_run_enabled = True 
  and plan is in ('pro', 'business').
  Also includes free orgs if they haven't had a run in the last 7 days.
  
  IMPORTANT: Run orgs sequentially, not in parallel.
  Parallel runs would exhaust Anthropic API rate limits.
  Add a 30-second delay between each org.
  
  Returns list of all results.
  Logs a summary table at the end.
  """

async def run_onboarding_pipeline(org_id: str, website_url: str) -> OnboardingResult:
  """
  Full onboarding flow when a new user connects their website.
  
  Steps:
  1. Scrape website using scraper.scrape_website()
  2. Prepare chunks using scraper.prepare_chunks_for_embedding()
  3. Embed all chunks using EmbeddingService.embed_batch()
  4. Store in Supabase using vector_store.store_brand_memory()
  5. Update organization record: set website_url, mark onboarding complete
  6. Return OnboardingResult with stats
  
  This can take 30-120 seconds. It must be run as a background task,
  not blocking the HTTP request. Use FastAPI BackgroundTasks.
  """

class OnboardingResult:
  org_id: str
  website_url: str
  pages_scraped: int
  chunks_stored: int
  duration_seconds: float
  success: bool
  error: str | None

After writing all sections, write a standalone test script 
(backend/tests/test_agents.py) that:
1. Tests scraper on https://example.com (or a real simple site)
2. Tests embedding a sample text and confirms dimension = 384
3. Tests DuckDuckGo search tool with query "AI marketing trends 2025"
4. Tests the full crew on a mock org config (no real Supabase needed — 
   mock the DB calls with pytest monkeypatch)
5. Each test has setup, execution, and assertion clearly labelled

The tests must actually run with: pytest backend/tests/test_agents.py -v