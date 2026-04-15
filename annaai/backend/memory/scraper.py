"""Async site scraper — httpx + trafilatura + BeautifulSoup fallback."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import httpx
import trafilatura
from bs4 import BeautifulSoup

from config import settings
from utils.helpers import clean_html, extract_domain
from utils.logger import get_logger

logger = get_logger("scraper")

USER_AGENT = "AnnaAiBot/0.1 (+https://annaai.app)"
MIN_TEXT_CHARS = 200


@dataclass(slots=True)
class ScrapedPage:
    url: str
    title: str | None
    text: str
    meta_description: str | None = None


@dataclass(slots=True)
class ScrapeResult:
    root_url: str
    domain: str
    pages: list[ScrapedPage] = field(default_factory=list)

    @property
    def total_chars(self) -> int:
        return sum(len(p.text) for p in self.pages)


def _extract_title_and_meta(html: str) -> tuple[str | None, str | None]:
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta_desc = None
    tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if tag and tag.get("content"):
        meta_desc = str(tag["content"]).strip()
    return title, meta_desc


def _extract_text(html: str) -> str:
    txt = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )
    if txt and len(txt) >= MIN_TEXT_CHARS:
        return txt
    return clean_html(html)


def _find_internal_links(html: str, base_url: str, limit: int) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    base_host = urlparse(base_url).netloc
    seen: set[str] = set()
    out: list[str] = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"]).split("#")[0]
        parsed = urlparse(href)
        if parsed.netloc != base_host or parsed.scheme not in {"http", "https"}:
            continue
        # Skip obvious non-content paths
        if any(p in parsed.path.lower() for p in ("/tag/", "/category/", "/author/", "/page/")):
            continue
        if href in seen:
            continue
        seen.add(href)
        out.append(href)
        if len(out) >= limit:
            break
    return out


async def _fetch(client: httpx.AsyncClient, url: str) -> str:
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "")
        if "html" not in ctype:
            return ""
        return resp.text
    except Exception as e:
        logger.warning("fetch_failed", url=url, error=str(e))
        return ""


async def scrape_site(
    url: str,
    max_pages: int | None = None,
) -> ScrapeResult:
    """Crawl a site: homepage + a capped set of internal pages, in parallel."""
    max_pages = max_pages or settings.SCRAPE_MAX_PAGES
    timeout = httpx.Timeout(settings.SCRAPE_TIMEOUT_SECONDS, connect=10.0)
    result = ScrapeResult(root_url=url, domain=extract_domain(url))

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
        http2=False,
    ) as client:
        home_html = await _fetch(client, url)
        if not home_html:
            logger.error("scrape_no_homepage", url=url)
            return result

        title, meta = _extract_title_and_meta(home_html)
        text = _extract_text(home_html)
        if text:
            result.pages.append(
                ScrapedPage(url=url, title=title, text=text, meta_description=meta)
            )

        links = _find_internal_links(home_html, url, max_pages - 1)
        if not links:
            return result

        htmls = await asyncio.gather(*(_fetch(client, link) for link in links))
        for link, html in zip(links, htmls, strict=True):
            if not html:
                continue
            text = _extract_text(html)
            if len(text) < MIN_TEXT_CHARS:
                continue
            title, meta = _extract_title_and_meta(html)
            result.pages.append(
                ScrapedPage(url=link, title=title, text=text, meta_description=meta)
            )

    logger.info(
        "scrape_complete",
        url=url,
        pages=len(result.pages),
        total_chars=result.total_chars,
    )
    return result
