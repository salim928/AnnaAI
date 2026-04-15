"""AnnaAi FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from config import settings
from db.client import get_supabase_admin_client
from utils.logger import configure_logging, get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info(
        "startup",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Supabase smoke check
    sb = get_supabase_admin_client()
    app.state.supabase_connected = sb is not None
    if sb is None:
        logger.warning("supabase_not_configured")

    # Warm the embedding model so the first request isn't slow.
    app.state.embedding_model_loaded = False
    try:
        from memory.embedder import get_embedding_service

        get_embedding_service().ensure_loaded()
        app.state.embedding_model_loaded = True
    except Exception as exc:  # noqa: BLE001
        logger.warning("embedding_model_preload_failed", error=str(exc))

    yield

    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AnnaAi — autonomous AI marketing agent backend",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# --- Middleware (outermost first) -------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# --- Routers ----------------------------------------------------------------
def _mount_routers() -> None:
    """Routers are included lazily so Batch 1 boots even before Batch 3 lands."""
    try:
        from api.routes import (
            auth,
            billing,
            chat,
            drafts,
            integrations,
            onboarding,
            runs,
            scheduler,
            webhooks,
        )
    except ImportError as exc:  # Batch 3 not yet installed
        logger.info("routes_not_mounted", reason=str(exc))
        return

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
    app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
    app.include_router(drafts.router, prefix="/api/drafts", tags=["drafts"])
    app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
    app.include_router(scheduler.router, prefix="/api/scheduler", tags=["scheduler"])
    app.include_router(billing.router, prefix="/api/billing", tags=["billing"])


_mount_routers()


# --- Exception handlers -----------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_exception", request_id=request_id, path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "Something went wrong. Anna will try again.",
            "request_id": request_id,
        },
    )


# --- Routes -----------------------------------------------------------------
@app.get("/", tags=["root"])
async def root() -> dict[str, Any]:
    return {
        "name": settings.APP_NAME,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["root"])
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "supabase_connected": getattr(app.state, "supabase_connected", False),
        "embedding_model_loaded": getattr(app.state, "embedding_model_loaded", False),
    }
