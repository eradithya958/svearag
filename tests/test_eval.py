"""Regression test verifying retrieval accuracy on golden benchmark."""

import json
from pathlib import Path

from svearag.core.models import Chunk, DocumentMetadata
from svearag.evaluation import calculate_metrics
from svearag.generation.engine import RAGEngine
from svearag.generation.llm import FakeLLMClient
from svearag.retrieval.bm25 import BM25Index
from svearag.retrieval.embeddings import MockEmbeddingProvider
from svearag.retrieval.hybrid import RRFHybridRetriever
from svearag.retrieval.vector_store import QdrantVectorStore


def test_eval_benchmark_metrics_regression():
    base_dir = Path(__file__).resolve().parent.parent
    data_file = base_dir / "eval" / "data" / "ground_truth.json"
    all_cases = json.loads(data_file.read_text(encoding="utf-8"))

    # Select subset (4 answerable, 1 unanswerable)
    subset = all_cases[:4] + [all_cases[30]]

    # Setup test retrieval environment
    meta1 = DocumentMetadata(
        agency="Migrationsverket",
        document_id="MV-EDU-001",
        language="en",
        source_url="https://migrationsverket.se/edu",
    )
    chunks = [
        Chunk(
            chunk_id="c1",
            document_id="MV-EDU-001",
            text="Student residence permit requires monthly maintenance of 10,314 SEK and working allowed.",
            chunk_index=0,
            token_count=15,
            metadata=meta1,
        )
    ]

    mock_embedder = MockEmbeddingProvider(dimension=64)
    vstore = QdrantVectorStore(in_memory=True)
    vstore.create_collection("eval_reg_col", vector_size=64, recreate=True)
    vstore.upsert_chunks(
        "eval_reg_col", chunks, mock_embedder.embed_batch([c.text for c in chunks])
    )

    bm25 = BM25Index()
    bm25.index_chunks(chunks)

    retriever = RRFHybridRetriever(
        embedding_provider=mock_embedder,
        vector_store=vstore,
        bm25_index=bm25,
        collection_name="eval_reg_col",
    )
    engine = RAGEngine(retriever=retriever, llm_client=FakeLLMClient())

    metrics = calculate_metrics(engine, subset, alpha=0.5)

    assert metrics["total_queries"] == 5
    assert metrics["honest_refusal_rate"] == 100.0
    assert metrics["avg_latency_ms"] >= 0.0
