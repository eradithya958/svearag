"""Pydantic schemas for FastAPI endpoints."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

from svearag.generation.prompt import CitedSource


class AskRequest(BaseModel):
    """User query request payload."""

    query: str = Field(..., min_length=2, max_length=1000, description="Question text to answer")
    top_k: int = Field(default=4, ge=1, le=20, description="Max documents to retrieve")
    agency: str | None = Field(
        default=None, description="Optional agency filter (e.g. Migrationsverket, Skatteverket)"
    )
    language: str | None = Field(default=None, description="Optional language filter (en, sv)")
    alpha: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Hybrid weight (1.0=vector, 0.0=BM25)"
    )


class AskResponse(BaseModel):
    """Response payload for /api/v1/ask endpoint."""

    query_id: str = Field(..., description="Unique query trace ID")
    question: str = Field(..., description="Echo of user question")
    answer: str = Field(..., description="Grounded answer with citations")
    citations: list[CitedSource] = Field(default_factory=list, description="Source documents cited")
    retrieval_latency_ms: float = Field(..., description="Retrieval time in milliseconds")
    llm_latency_ms: float = Field(..., description="LLM generation time in milliseconds")
    total_latency_ms: float = Field(..., description="Total end-to-end request duration")
    model_name: str = Field(..., description="LLM model identifier")


class FeedbackRequest(BaseModel):
    """User feedback payload."""

    query_id: str = Field(..., description="Query ID to rate")
    rating: Literal["up", "down"] = Field(..., description="Thumbs up or thumbs down")
    comment: str | None = Field(
        default=None, max_length=1000, description="Optional feedback comment"
    )


class FeedbackResponse(BaseModel):
    """Feedback confirmation response."""

    status: str = Field(default="success")
    query_id: str
    recorded_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class HealthResponse(BaseModel):
    """System health check response."""

    status: str = Field(default="healthy")
    environment: str
    vector_store_healthy: bool
    total_documents_indexed: int
    llm_model: str
    version: str = "0.1.0"


class IngestResponse(BaseModel):
    """Document ingestion response."""

    status: str = Field(default="success")
    documents_indexed: int
    chunks_generated: int
    message: str
