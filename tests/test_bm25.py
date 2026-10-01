"""Unit tests for BM25 lexical retrieval and Swedish/English tokenization."""

from svearag.core.models import Chunk
from svearag.retrieval.bm25 import BM25Index, tokenize_text


def test_tokenize_text_multilingual():
    english_text = "Residence permit application for Master's degree."
    swedish_text = "Ansökan om uppehållstillstånd för doktorander och forskare."

    en_tokens = tokenize_text(english_text)
    sv_tokens = tokenize_text(swedish_text)

    assert "residence" in en_tokens
    assert "permit" in en_tokens
    assert "uppehållstillstånd" in sv_tokens
    assert "doktorander" in sv_tokens
    assert "forskare" in sv_tokens


def test_bm25_search_scoring(sample_chunks: list[Chunk]):
    index = BM25Index()
    index.index_chunks(sample_chunks)

    # Search for specific term in chunk 1
    results = index.search("10314 SEK maintenance", top_k=2)
    assert len(results) >= 1
    assert results[0].chunk.chunk_id == "TEST-DOC-001_c001"
    assert results[0].retrieval_type == "sparse"
    assert results[0].score > 0


def test_bm25_search_agency_filter(sample_chunks: list[Chunk]):
    index = BM25Index()
    index.index_chunks(sample_chunks)

    results = index.search("studies registration", top_k=5, agency_filter="Skatteverket")
    for r in results:
        assert r.chunk.metadata.agency == "Skatteverket"


def test_bm25_empty_query_or_index(sample_chunks: list[Chunk]):
    index = BM25Index()
    assert index.search("query") == []

    index.index_chunks(sample_chunks)
    assert index.search("") == []
    assert index.search("   ") == []


def test_bm25_index_empty_chunks():
    index = BM25Index()
    count = index.index_chunks([])
    assert count == 0
