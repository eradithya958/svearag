"""Embedding providers and abstract interfaces for multilingual vector generation."""

import hashlib
from abc import ABC, abstractmethod

import numpy as np

from svearag.core.logging import logger

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


class EmbeddingProvider(ABC):
    """Abstract base class for text embedding models."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimensionality of the embedding model."""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generates an embedding vector for a single string."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a batch of strings."""
        pass


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Local multilingual embedding provider using HuggingFace sentence-transformers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        dimension: int = 384,
        device: str | None = None,
    ) -> None:
        self.model_name = model_name
        self._dimension = dimension
        self._model = None
        self._device = device

    def _load_model(self):
        """Lazy loader for sentence-transformers model."""
        if self._model is None:
            if SentenceTransformer is None:
                from sentence_transformers import SentenceTransformer as STCls  # type: ignore

                st_cls = STCls
            else:
                st_cls = SentenceTransformer
            logger.info("Loading SentenceTransformer model", extra_data={"model": self.model_name})
            self._model = st_cls(self.model_name, device=self._device)
        return self._model

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> list[float]:
        model = self._load_model()
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._load_model()
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic pseudo-embedding provider for instant, zero-network unit tests."""

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> list[float]:
        """Generates deterministic pseudo-vector using SHA-256 hash seed."""
        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        # Seed numpy RNG with digest
        seed = int.from_bytes(hash_digest[:4], byteorder="little")
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self._dimension).astype(np.float32)
        # Normalize to unit length
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]
