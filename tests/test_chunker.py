"""Unit tests for chunking strategies."""

import pytest

from svearag.core.models import Document, DocumentMetadata
from svearag.ingestion.chunker import (
    RecursiveTokenChunker,
    SemanticHeaderChunker,
    approximate_token_count,
)


def test_approximate_token_count():
    text = "This is a simple sentence."
    tokens = approximate_token_count(text)
    assert tokens >= 5


def test_recursive_token_chunker_basic(sample_document: Document):
    chunker = RecursiveTokenChunker(chunk_size=15, chunk_overlap=2)
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) > 0
    assert chunks[0].document_id == sample_document.id
    assert chunks[0].metadata.agency == "Migrationsverket"
    for idx, c in enumerate(chunks):
        assert c.chunk_index == idx
        assert c.chunk_id == f"TEST-DOC-001_c{idx:03d}"


def test_recursive_token_chunker_invalid_overlap():
    with pytest.raises(ValueError, match="chunk_overlap must be strictly less than chunk_size"):
        RecursiveTokenChunker(chunk_size=50, chunk_overlap=60)


def test_recursive_token_chunker_empty_content(sample_metadata: DocumentMetadata):
    doc = Document(id="EMPTY-01", title="Empty", content="", metadata=sample_metadata)
    chunker = RecursiveTokenChunker(chunk_size=100, chunk_overlap=10)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 0


def test_semantic_header_chunker(sample_document: Document):
    chunker = SemanticHeaderChunker()
    chunks = chunker.chunk_document(sample_document)

    assert len(chunks) == 2
    assert "General Information" in chunks[0].text
    assert "Detailed Rules" in chunks[1].text
    assert chunks[0].chunk_id.startswith("TEST-DOC-001_sec_")


def test_chunk_documents_batch(sample_document: Document):
    chunker = RecursiveTokenChunker(chunk_size=50)
    docs = [sample_document, sample_document]
    all_chunks = chunker.chunk_documents(docs)
    assert len(all_chunks) == len(chunker.chunk_document(sample_document)) * 2
