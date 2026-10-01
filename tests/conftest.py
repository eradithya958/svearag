"""Pytest fixtures and test configuration."""

import pytest

from svearag.core.models import Chunk, Document, DocumentMetadata
from svearag.retrieval.bm25 import BM25Index
from svearag.retrieval.embeddings import MockEmbeddingProvider
from svearag.retrieval.vector_store import QdrantVectorStore


@pytest.fixture
def sample_metadata() -> DocumentMetadata:
    return DocumentMetadata(
        agency="Migrationsverket",
        document_id="TEST-DOC-001",
        language="en",
        source_url="https://example.com/test",
        last_updated="2024-01-01",
        category="Test",
    )


@pytest.fixture
def sample_document(sample_metadata: DocumentMetadata) -> Document:
    content = (
        "# General Information\n\n"
        "This is paragraph one explaining residence permit criteria.\n\n"
        "## Detailed Rules\n\n"
        "Applicants must show financial funds of 10,000 SEK per month and valid health insurance."
    )
    return Document(
        id="TEST-DOC-001",
        title="Sample Test Document",
        content=content,
        metadata=sample_metadata,
    )


@pytest.fixture
def sample_chunks(sample_metadata: DocumentMetadata) -> list[Chunk]:
    meta_skv = DocumentMetadata(
        agency="Skatteverket",
        document_id="SKV-TEST-002",
        language="en",
        source_url="https://skatteverket.se/test",
        last_updated="2024-01-01",
        category="Tax",
    )
    return [
        Chunk(
            chunk_id="TEST-DOC-001_c001",
            document_id="TEST-DOC-001",
            text="Student residence permit requires monthly maintenance of 10314 SEK.",
            chunk_index=0,
            token_count=10,
            metadata=sample_metadata,
        ),
        Chunk(
            chunk_id="TEST-DOC-001_c002",
            document_id="TEST-DOC-001",
            text="International students can work during their studies without extra work permit.",
            chunk_index=1,
            token_count=12,
            metadata=sample_metadata,
        ),
        Chunk(
            chunk_id="SKV-TEST-002_c001",
            document_id="SKV-TEST-002",
            text="Personnummer requires staying in Sweden for at least 12 months with registration at Skatteverket.",
            chunk_index=0,
            token_count=15,
            metadata=meta_skv,
        ),
    ]


@pytest.fixture
def mock_embedding_provider() -> MockEmbeddingProvider:
    return MockEmbeddingProvider(dimension=64)


@pytest.fixture
def in_memory_vector_store(
    mock_embedding_provider: MockEmbeddingProvider, sample_chunks: list[Chunk]
) -> QdrantVectorStore:
    store = QdrantVectorStore(in_memory=True)
    store.create_collection(
        "test_collection", vector_size=mock_embedding_provider.dimension, recreate=True
    )
    embeddings = mock_embedding_provider.embed_batch([c.text for c in sample_chunks])
    store.upsert_chunks("test_collection", sample_chunks, embeddings)
    return store


@pytest.fixture
def populated_bm25_index(sample_chunks: list[Chunk]) -> BM25Index:
    index = BM25Index()
    index.index_chunks(sample_chunks)
    return index
