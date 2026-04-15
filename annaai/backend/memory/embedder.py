"""Singleton embedding service — sentence-transformers 3.x."""
from __future__ import annotations

from typing import TYPE_CHECKING

from config import settings
from utils.logger import get_logger

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = get_logger("embedder")

_instance: "EmbeddingService | None" = None


class EmbeddingService:
    """Lazy-loaded, process-wide embedding model.

    The first call to `encode` (or `ensure_loaded`) loads the model weights,
    which can take a few seconds. Main.py pre-warms on startup.
    """

    def __init__(self) -> None:
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self._model: "SentenceTransformer | None" = None

    def ensure_loaded(self) -> None:
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer

        logger.info("embedder_loading", model=self.model_name)
        self._model = SentenceTransformer(self.model_name)
        logger.info("embedder_loaded", model=self.model_name, dim=self.dimension)

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self.ensure_loaded()
        assert self._model is not None
        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return [v.tolist() for v in vectors]

    def encode_one(self, text: str) -> list[float]:
        return self.encode([text])[0]


def get_embedding_service() -> EmbeddingService:
    global _instance
    if _instance is None:
        _instance = EmbeddingService()
    return _instance
