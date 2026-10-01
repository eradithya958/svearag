"""Unit tests for RRF hybrid retrieval."""

from svearag.core.models import RetrievalQuery
from svearag.retrieval.bm25 import BM25Index
from svearag.retrieval.embeddings import MockEmbeddingProvider
from svearag.retrieval.hybrid import RRFHybridRetriever
from svearag.retrieval.vector_store import QdrantVectorStore


def test_rrf_hybrid_retrieval_balanced(
    mock_embedding_provider: MockEmbeddingProvider,
    in_memory_vector_store: QdrantVectorStore,
    populated_bm25_index: BM25Index,
):
    retriever = RRFHybridRetriever(
        embedding_provider=mock_embedding_provider,
        vector_store=in_memory_vector_store,
        bm25_index=populated_bm25_index,
        collection_name="test_collection",
        rrf_k=60,
    )

    query = RetrievalQuery(text="10314 maintenance", top_k=2, alpha=0.5)
    results = retriever.retrieve(query)

    assert len(results) <= 2
    assert len(results) > 0
    assert results[0].retrieval_type == "hybrid"
    assert results[0].rank == 1
    assert results[0].score > 0


def test_rrf_hybrid_pure_dense(
    mock_embedding_provider: MockEmbeddingProvider,
    in_memory_vector_store: QdrantVectorStore,
    populated_bm25_index: BM25Index,
):
    retriever = RRFHybridRetriever(
        embedding_provider=mock_embedding_provider,
        vector_store=in_memory_vector_store,
        bm25_index=populated_bm25_index,
        collection_name="test_collection",
    )

    query = RetrievalQuery(text="student work rules", top_k=2, alpha=1.0)
    results = retriever.retrieve(query)

    assert len(results) == 2
    assert results[0].retrieval_type == "dense"
    assert results[0].rank == 1


def test_rrf_hybrid_pure_sparse(
    mock_embedding_provider: MockEmbeddingProvider,
    in_memory_vector_store: QdrantVectorStore,
    populated_bm25_index: BM25Index,
):
    retriever = RRFHybridRetriever(
        embedding_provider=mock_embedding_provider,
        vector_store=in_memory_vector_store,
        bm25_index=populated_bm25_index,
        collection_name="test_collection",
    )

    query = RetrievalQuery(text="Personnummer registration", top_k=1, alpha=0.0)
    results = retriever.retrieve(query)

    assert len(results) == 1
    assert results[0].retrieval_type == "sparse"
    assert results[0].chunk.chunk_id == "SKV-TEST-002_c001"


def test_rrf_hybrid_with_filters(
    mock_embedding_provider: MockEmbeddingProvider,
    in_memory_vector_store: QdrantVectorStore,
    populated_bm25_index: BM25Index,
):
    retriever = RRFHybridRetriever(
        embedding_provider=mock_embedding_provider,
        vector_store=in_memory_vector_store,
        bm25_index=populated_bm25_index,
        collection_name="test_collection",
    )

    query = RetrievalQuery(text="residence", top_k=5, agency="Migrationsverket", alpha=0.5)
    results = retriever.retrieve(query)

    for r in results:
        assert r.chunk.metadata.agency == "Migrationsverket"
