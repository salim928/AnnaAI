"""Brand memory store — Supabase pgvector via the `vecs` library.

The `vecs` client connects directly to Postgres (SUPABASE_DB_URL) and
manages its own HNSW index. When vecs isn't configured, falls back to
an in-process list with cosine similarity so local dev still works.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from config import settings
from memory.embedder import get_embedding_service
from memory.scraper import ScrapeResult
from utils.helpers import chunk_text
from utils.logger import get_logger

logger = get_logger("vector_store")

COLLECTION_NAME = "brand_memory"


@dataclass(slots=True)
class MemoryRecord:
    id: str
    org_id: str
    chunk: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


# --- vecs client ------------------------------------------------------------
@lru_cache(maxsize=1)
def _get_vecs_client():
    if not settings.SUPABASE_DB_URL:
        return None
    try:
        import vecs

        client = vecs.create_client(settings.SUPABASE_DB_URL)
        logger.info("vecs_client_initialised")
        return client
    except Exception as e:
        logger.warning("vecs_client_init_failed", error=str(e))
        return None


@lru_cache(maxsize=1)
def _get_collection():
    client = _get_vecs_client()
    if client is None:
        return None
    try:
        import vecs

        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            dimension=settings.EMBEDDING_DIMENSION,
        )
        # vecs manages the HNSW index — cheap to re-assert (no-op if present).
        try:
            collection.create_index(method=vecs.IndexMethod.hnsw, measure=vecs.IndexMeasure.cosine_distance)
        except Exception:
            pass
        return collection
    except Exception as e:
        logger.warning("vecs_collection_init_failed", error=str(e))
        return None


# --- In-memory fallback -----------------------------------------------------
_local_store: list[MemoryRecord] = []


def _cosine(a: list[float], b: list[float]) -> float:
    import math

    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# --- Public API -------------------------------------------------------------
def store_brand_memory(
    org_id: str,
    scrape: ScrapeResult,
    chunk_size: int = 350,
) -> int:
    """Embed and store chunks from a scrape. Returns number stored."""
    embedder = get_embedding_service()

    rows_for_vecs: list[tuple[str, list[float], dict[str, Any]]] = []
    local_records: list[MemoryRecord] = []

    for page in scrape.pages:
        chunks = chunk_text(page.text, size=chunk_size, overlap=40)
        if not chunks:
            continue
        embeddings = embedder.encode(chunks)
        for chunk, vec in zip(chunks, embeddings, strict=True):
            meta = {
                "org_id": org_id,
                "chunk_type": "content",
                "source_url": page.url,
                "page_title": page.title or "",
                "chunk_text": chunk,
            }
            record_id = f"{org_id}:{uuid.uuid4().hex}"
            rows_for_vecs.append((record_id, vec, meta))
            local_records.append(
                MemoryRecord(id=record_id, org_id=org_id, chunk=chunk, embedding=vec, metadata=meta)
            )

    if not rows_for_vecs:
        return 0

    collection = _get_collection()
    if collection is not None:
        try:
            collection.upsert(records=rows_for_vecs)
            logger.info("brand_memory_stored_vecs", org_id=org_id, count=len(rows_for_vecs))
            return len(rows_for_vecs)
        except Exception as e:
            logger.warning("vecs_upsert_failed_fallback_local", error=str(e))

    _local_store.extend(local_records)
    logger.info("brand_memory_stored_local", org_id=org_id, count=len(local_records))
    return len(local_records)


def store_feedback_chunk(org_id: str, text: str, chunk_type: str) -> None:
    """Store a single feedback chunk (positive/negative). Batch 6 learning loop."""
    embedder = get_embedding_service()
    vec = embedder.encode_one(text)
    meta = {
        "org_id": org_id,
        "chunk_type": chunk_type,
        "source_url": "",
        "page_title": "feedback",
        "chunk_text": text,
    }
    record_id = f"{org_id}:{uuid.uuid4().hex}"
    collection = _get_collection()
    if collection is not None:
        try:
            collection.upsert(records=[(record_id, vec, meta)])
            return
        except Exception as e:
            logger.warning("feedback_upsert_failed_fallback_local", error=str(e))
    _local_store.append(
        MemoryRecord(id=record_id, org_id=org_id, chunk=text, embedding=vec, metadata=meta)
    )


def recall_brand_memory(
    org_id: str,
    query: str,
    top_k: int = 5,
    chunk_types: list[str] | None = None,
) -> list[str]:
    """Retrieve the top-k most relevant chunks for a natural-language query."""
    if not query:
        return []
    embedder = get_embedding_service()
    qv = embedder.encode_one(query)

    collection = _get_collection()
    if collection is not None:
        try:
            filters: dict[str, Any] = {"org_id": {"$eq": org_id}}
            if chunk_types:
                filters["chunk_type"] = {"$in": chunk_types}
            results = collection.query(
                data=qv,
                limit=top_k,
                filters=filters,
                measure="cosine_distance",
                include_metadata=True,
            )
            chunks: list[str] = []
            for row in results or []:
                # vecs returns (id, metadata) tuples when include_metadata=True
                if isinstance(row, tuple) and len(row) >= 2:
                    metadata = row[1] or {}
                    chunk = metadata.get("chunk_text")
                    if chunk:
                        chunks.append(chunk)
                elif isinstance(row, dict):
                    chunk = (row.get("metadata") or {}).get("chunk_text")
                    if chunk:
                        chunks.append(chunk)
            if chunks:
                return chunks
        except Exception as e:
            logger.warning("vecs_query_failed_fallback_local", error=str(e))

    # Local fallback
    candidates = [r for r in _local_store if r.org_id == org_id]
    if chunk_types:
        candidates = [r for r in candidates if r.metadata.get("chunk_type") in chunk_types]
    if not candidates:
        return []
    scored = [(r, _cosine(r.embedding, qv)) for r in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [r.chunk for r, _ in scored[:top_k]]


def get_brand_memory_summary(org_id: str, query: str = "brand voice and positioning") -> str:
    chunks = recall_brand_memory(org_id, query, top_k=5)
    if not chunks:
        return "No brand memory available yet."
    return "\n---\n".join(chunks)


def get_memory_stats(org_id: str) -> dict[str, Any]:
    collection = _get_collection()
    if collection is not None:
        try:
            # vecs exposes a rough count via __len__
            total = len(collection)  # type: ignore[arg-type]
        except Exception:
            total = 0
    else:
        total = sum(1 for r in _local_store if r.org_id == org_id)
    return {
        "org_id": org_id,
        "total_chunks": total,
        "backend": "vecs" if collection is not None else "local",
    }
