"""Unit tests for Qdrant vector store adapter."""

import pytest

from svearag.core.models import Chunk
from svearag.retrieval.embeddings import MockEmbeddingProvider
from svearag.retrieval.vector_store import QdrantVectorStore


def test_qdrant_vector_store_in_memory(
    sample_chunks: list[Chunk], mock_embedding_provider: MockEmbeddingProvider
):
    store = QdrantVectorStore(in_memory=True)
    col_name = "test_col"
    store.create_collection(col_name, vector_size=mock_embedding_provider.dimension, recreate=True)

    embeddings = mock_embedding_provider.embed_batch([c.text for c in sample_chunks])
    count = store.upsert_chunks(col_name, sample_chunks, embeddings)
    assert count == 3

    # Search without filters
    query_vec = mock_embedding_provider.embed_text("Student residence permit")
    results = store.search(col_name, query_vector=query_vec, top_k=2)

    assert len(results) == 2
    assert results[0].retrieval_type == "dense"
    assert results[0].rank == 1
    assert results[0].score >= -1.0  # Cosine similarity range


def test_qdrant_vector_store_with_filter(
    sample_chunks: list[Chunk], mock_embedding_provider: MockEmbeddingProvider
):
    store = QdrantVectorStore(in_memory=True)
    col_name = "filter_col"
    store.create_collection(col_name, vector_size=mock_embedding_provider.dimension, recreate=True)

    embeddings = mock_embedding_provider.embed_batch([c.text for c in sample_chunks])
    store.upsert_chunks(col_name, sample_chunks, embeddings)

    query_vec = mock_embedding_provider.embed_text("Registration")
    results = store.search(
        col_name, query_vector=query_vec, top_k=5, filters={"agency": "Skatteverket"}
    )

    assert len(results) == 1
    assert results[0].chunk.metadata.agency == "Skatteverket"
    assert results[0].chunk.document_id == "SKV-TEST-002"


def test_qdrant_upsert_mismatch_error(sample_chunks: list[Chunk]):
    store = QdrantVectorStore(in_memory=True)
    with pytest.raises(ValueError, match="Chunk count"):
        store.upsert_chunks("col", sample_chunks, [[0.1, 0.2]])


def test_qdrant_upsert_empty():
    store = QdrantVectorStore(in_memory=True)
    assert store.upsert_chunks("col", [], []) == 0


def test_qdrant_vector_store_initializations():
    store1 = QdrantVectorStore(in_memory=False, host="localhost", port=6333)
    assert store1.client is not None

    store2 = QdrantVectorStore(in_memory=False, url="http://localhost:6333")
    assert store2.client is not None

    from qdrant_client import QdrantClient

    custom_client = QdrantClient(location=":memory:")
    store3 = QdrantVectorStore(client=custom_client)
    assert store3.client == custom_client
