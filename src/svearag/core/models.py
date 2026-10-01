"""Data models and schemas for SveaRAG."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata attributes associated with a source document."""

    agency: str = Field(..., description="Issuing agency, e.g. Migrationsverket, Skatteverket")
    document_id: str = Field(..., description="Unique agency reference id")
    language: str = Field(default="en", description="Document primary language (en/sv)")
    source_url: str = Field(..., description="Official web source URL")
    last_updated: str | None = Field(default=None, description="Last updated date string")
    category: str | None = Field(default=None, description="Domain category")
    extra: dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")


class Document(BaseModel):
    """Raw or normalized document loaded from corpus."""

    id: str = Field(..., description="Unique document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Full text content of document")
    metadata: DocumentMetadata = Field(..., description="Document metadata")


class Chunk(BaseModel):
    """Text chunk derived from a source document."""

    chunk_id: str = Field(..., description="Deterministic chunk identifier (e.g. MV-EDU-001_c001)")
    document_id: str = Field(..., description="Parent document ID")
    text: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Zero-based index of chunk in document")
    token_count: int = Field(default=0, description="Approximate token or word count")
    metadata: DocumentMetadata = Field(..., description="Inherited parent metadata")


class SearchResult(BaseModel):
    """Retrieved search result with score and lineage."""

    chunk: Chunk = Field(..., description="Retrieved chunk payload")
    score: float = Field(..., description="Relevance or fusion score")
    retrieval_type: Literal["dense", "sparse", "hybrid"] = Field(
        default="hybrid", description="Retrieval method used"
    )
    rank: int = Field(default=1, description="Rank in the returned list")


class RetrievalQuery(BaseModel):
    """Query parameters for retrieval engine."""

    text: str = Field(..., min_length=1, description="User search query string")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to retrieve")
    language: str | None = Field(default=None, description="Optional language filter (en/sv)")
    agency: str | None = Field(default=None, description="Optional agency filter")
    alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Hybrid weighting factor: 1.0=pure dense, 0.0=pure BM25",
    )
