"""Hybrid retrieval combining dense vector search and BM25 with Reciprocal Rank Fusion (RRF)."""

import time
from collections import defaultdict
from typing import Any

from svearag.core.logging import logger
from svearag.core.models import Chunk, RetrievalQuery, SearchResult
from svearag.retrieval.bm25 import BM25Index
from svearag.retrieval.embeddings import EmbeddingProvider
from svearag.retrieval.vector_store import VectorStore


class RRFHybridRetriever:
    """Combines dense vector similarity and sparse BM25 keyword matching via RRF."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        bm25_index: BM25Index,
        collection_name: str = "svearag_documents",
        rrf_k: int = 60,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.collection_name = collection_name
        self.rrf_k = rrf_k

    def retrieve(self, query: RetrievalQuery) -> list[SearchResult]:
        """Performs hybrid retrieval according to query parameters."""
        start_time = time.perf_counter()

        filters: dict[str, Any] = {}
        if query.agency:
            filters["agency"] = query.agency
        if query.language:
            filters["language"] = query.language

        dense_results: list[SearchResult] = []
        sparse_results: list[SearchResult] = []

        candidate_k = max(query.top_k * 3, 10)

        # 1. Dense vector search
        if query.alpha > 0.0:
            query_vector = self.embedding_provider.embed_text(query.text)
            dense_results = self.vector_store.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                top_k=candidate_k,
                filters=filters if filters else None,
            )

        # 2. Sparse BM25 search
        if query.alpha < 1.0:
            sparse_results = self.bm25_index.search(
                query=query.text,
                top_k=candidate_k,
                agency_filter=query.agency,
                language_filter=query.language,
            )

        # 3. Handle pure cases
        if query.alpha == 1.0:
            final_results = dense_results[: query.top_k]
            for idx, r in enumerate(final_results, start=1):
                r.rank = idx
            return final_results

        if query.alpha == 0.0:
            final_results = sparse_results[: query.top_k]
            for idx, r in enumerate(final_results, start=1):
                r.rank = idx
            return final_results

        # 4. Reciprocal Rank Fusion (RRF)
        rrf_scores: dict[str, float] = defaultdict(float)
        chunk_map: dict[str, Chunk] = {}

        # Weight components
        dense_weight = query.alpha
        sparse_weight = 1.0 - query.alpha

        for res in dense_results:
            cid = res.chunk.chunk_id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] += dense_weight * (1.0 / (self.rrf_k + res.rank))

        for res in sparse_results:
            cid = res.chunk.chunk_id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] += sparse_weight * (1.0 / (self.rrf_k + res.rank))

        # Sort chunks by fused score
        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        final_results = []
        for rank, (cid, score) in enumerate(sorted_chunks[: query.top_k], start=1):
            final_results.append(
                SearchResult(
                    chunk=chunk_map[cid],
                    score=score,
                    retrieval_type="hybrid",
                    rank=rank,
                )
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(
            "Hybrid retrieval finished",
            extra_data={
                "query": query.text,
                "top_k": query.top_k,
                "alpha": query.alpha,
                "results_count": len(final_results),
                "duration_ms": round(elapsed_ms, 2),
            },
        )

        return final_results
