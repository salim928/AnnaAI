"""Rate limiting — slowapi wrapper for AnnaAi."""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by client IP.  When behind a reverse proxy (Render / Vercel),
# X-Forwarded-For is used automatically by get_remote_address.
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

# Re-usable per-route limit strings
AUTH_LIMIT = "5/minute"          # login / register brute-force protection
CHAT_LIMIT = "20/minute"        # LLM calls are expensive
SCHEDULER_LIMIT = "4/minute"    # only GitHub Actions should hit this
ONBOARDING_LIMIT = "3/minute"   # heavy scrape + AI pipeline
