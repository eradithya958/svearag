"""Unit tests for generation, prompt building, citation extraction, and RAGEngine."""

from unittest.mock import MagicMock, patch

import pytest

from svearag.core.models import Chunk, RetrievalQuery, SearchResult
from svearag.generation.engine import RAGEngine
from svearag.generation.llm import FakeLLMClient, OllamaLLMClient
from svearag.generation.prompt import PromptBuilder
from svearag.retrieval.bm25 import BM25Index
from svearag.retrieval.embeddings import MockEmbeddingProvider
from svearag.retrieval.hybrid import RRFHybridRetriever
from svearag.retrieval.vector_store import QdrantVectorStore


def test_fake_llm_client_generation():
    client = FakeLLMClient()
    res1 = client.generate("What is the maintenance requirement of 10314 SEK?")
    assert "SEK 10,314" in res1.text
    assert "[DOC_1]" in res1.text
    assert res1.model == "fake-llm-v1"

    res2 = client.generate("How to get a personnummer at Skatteverket?")
    assert "personnummer" in res2.text

    res3 = client.generate("Tell me an unrelated topic not mentioned")
    assert "I do not have sufficient information" in res3.text


def test_fake_llm_custom_canned_response():
    client = FakeLLMClient(canned_response="Custom answer [DOC_1].")
    res = client.generate("Any question")
    assert res.text == "Custom answer [DOC_1]."


def test_ollama_llm_client_mocked():
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "Grounded answer [DOC_1]",
            "prompt_eval_count": 25,
            "eval_count": 10,
        }
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value.__enter__.return_value = mock_client

        ollama = OllamaLLMClient(model="test-llama")
        result = ollama.generate("Test prompt", system_prompt="Sys")

        assert result.text == "Grounded answer [DOC_1]"
        assert result.model == "test-llama"
        assert result.prompt_tokens == 25
        assert result.completion_tokens == 10


def test_ollama_llm_client_error():
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.post.side_effect = Exception("Connection refused")
        mock_client_cls.return_value.__enter__.return_value = mock_client

        ollama = OllamaLLMClient()
        with pytest.raises(RuntimeError, match="Ollama generation error"):
            ollama.generate("Test prompt")


def test_prompt_builder_and_citations(sample_chunks: list[Chunk]):
    builder = PromptBuilder()
    results = [
        SearchResult(chunk=sample_chunks[0], score=0.9, retrieval_type="hybrid", rank=1),
        SearchResult(chunk=sample_chunks[1], score=0.7, retrieval_type="hybrid", rank=2),
    ]

    user_prompt, sys_prompt = builder.build_prompt("How much funds needed?", results)
    assert "[DOC_1]" in user_prompt
    assert "[DOC_2]" in user_prompt
    assert "Student residence permit requires" in user_prompt
    assert "SveaRAG" in sys_prompt

    # Test citation extraction
    generated_text = "Students need 10314 SEK monthly [DOC_1] and can work [DOC_2]."
    citations = builder.parse_citations(generated_text, results)
    assert len(citations) == 2
    assert citations[0].doc_tag == "[DOC_1]"
    assert citations[0].agency == "Migrationsverket"
    assert citations[1].doc_tag == "[DOC_2]"


def test_prompt_builder_empty_results():
    builder = PromptBuilder()
    user_prompt, _ = builder.build_prompt("Any question", [])
    assert "No official documents found" in user_prompt


def test_rag_engine_end_to_end(
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
    llm = FakeLLMClient()
    engine = RAGEngine(retriever=retriever, llm_client=llm)

    query = RetrievalQuery(text="10314 maintenance", top_k=2)
    answer = engine.answer_query(query)

    assert answer.question == "10314 maintenance"
    assert "SEK 10,314" in answer.answer
    assert len(answer.citations) >= 1
    assert answer.retrieval_latency_ms >= 0
    assert answer.llm_latency_ms >= 0
    assert answer.total_latency_ms >= 0
