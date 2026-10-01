"""Configuration settings for SveaRAG application."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration loaded from environment or defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project metadata
    project_name: str = "SveaRAG Assistant"
    environment: str = "development"
    debug: bool = False

    # Storage paths
    data_dir: Path = Path(__file__).resolve().parent.parent.parent.parent / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"

    # Embedding model configuration
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    # Vector store configuration (Qdrant)
    qdrant_url: str | None = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "svearag_documents"
    use_in_memory_vector_store: bool = True

    # Ingestion & Chunking parameters
    default_chunk_size: int = 350
    default_chunk_overlap: int = 50

    # Retrieval parameters
    default_top_k: int = 4
    default_hybrid_alpha: float = 0.5
    rrf_k: int = 60

    # API Server configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Cached settings getter."""
    return Settings()
