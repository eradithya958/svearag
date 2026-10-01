"""BM25 sparse lexical retrieval engine with Swedish & English tokenization."""

import re

from rank_bm25 import BM25Okapi

from svearag.core.logging import logger
from svearag.core.models import Chunk, SearchResult


def tokenize_text(text: str) -> list[str]:
    """Tokenizes Swedish and English text into normalized words."""
    # Retain alphanumeric characters including Swedish letters (å, ä, ö, é)
    cleaned = re.sub(r"[^\w\s\u00C0-\u017F]", " ", text.lower())
    tokens = [t for t in cleaned.split() if len(t) > 1]
    return tokens


class BM25Index:
    """BM25 Okapi lexical index over chunk corpus."""

    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.tokenized_corpus: list[list[str]] = []
        self._bm25: BM25Okapi | None = None

    def index_chunks(self, chunks: list[Chunk]) -> int:
        """Indexes a list of chunks into BM25 model."""
        if not chunks:
            return 0

        self.chunks = list(chunks)
        self.tokenized_corpus = [tokenize_text(c.text) for c in self.chunks]
        self._bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info("Indexed chunks in BM25", extra_data={"count": len(chunks)})
        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        agency_filter: str | None = None,
        language_filter: str | None = None,
    ) -> list[SearchResult]:
        """Queries the BM25 index and returns top-k matching search results."""
        if not self._bm25 or not self.chunks:
            return []

        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []

        raw_scores = self._bm25.get_scores(query_tokens)

        # Pair with chunks and filter
        scored_pairs: list[tuple[float, Chunk]] = []
        for score, chunk in zip(raw_scores, self.chunks, strict=False):
            if score <= 0:
                continue
            if agency_filter and chunk.metadata.agency != agency_filter:
                continue
            if language_filter and chunk.metadata.language != language_filter:
                continue
            scored_pairs.append((float(score), chunk))

        # Sort descending by score
        scored_pairs.sort(key=lambda x: x[0], reverse=True)
        top_results = scored_pairs[:top_k]

        results: list[SearchResult] = []
        for rank, (score, chunk) in enumerate(top_results, start=1):
            results.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                    retrieval_type="sparse",
                    rank=rank,
                )
            )

        return results
