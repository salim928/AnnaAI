"""Small shared helpers — pure functions."""
from __future__ import annotations

import re
from datetime import timedelta
from urllib.parse import urlparse

from bs4 import BeautifulSoup


_WORD_SPLIT = re.compile(r"\s+")
_SLUG_INVALID = re.compile(r"[^a-z0-9]+")


def chunk_text(text: str, size: int = 350, overlap: int = 40) -> list[str]:
    """Word-count chunking with small overlap. Returns [] for empty input."""
    words = _WORD_SPLIT.split(text.strip())
    if not words or words == [""]:
        return []
    if size <= 0:
        return [" ".join(words)]
    step = max(1, size - overlap)
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step)]


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    return host.replace("www.", "").strip("/")


def truncate_text(text: str, limit: int, suffix: str = "…") -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - len(suffix))].rstrip() + suffix


def generate_slug(text: str, max_len: int = 80) -> str:
    lowered = text.lower().strip()
    slug = _SLUG_INVALID.sub("-", lowered).strip("-")
    return slug[:max_len].rstrip("-") or "untitled"


def format_duration(seconds: float) -> str:
    td = timedelta(seconds=int(max(0, seconds)))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    match (td.days, hours, minutes):
        case (d, _, _) if d > 0:
            return f"{d}d {hours}h"
        case (0, h, _) if h > 0:
            return f"{h}h {minutes}m"
        case (0, 0, m) if m > 0:
            return f"{m}m {secs}s"
        case _:
            return f"{secs}s"


def estimate_read_time(text: str, wpm: int = 220) -> int:
    """Return estimated minutes to read, rounded up, minimum 1."""
    words = len(_WORD_SPLIT.split(text.strip())) if text else 0
    return max(1, (words + wpm - 1) // wpm)
