"""Integration tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from svearag.api.app import app
from svearag.api.dependencies import AppContainer, set_container
from svearag.core.config import Settings
from svearag.generation.llm import FakeLLMClient
from svearag.retrieval.embeddings import MockEmbeddingProvider
from svearag.retrieval.vector_store import QdrantVectorStore


@pytest.fixture(autouse=True)
def setup_test_api_container():
    """Sets up a fully initialized in-memory test container before tests."""
    settings = Settings(
        environment="testing",
        use_in_memory_vector_store=True,
        qdrant_collection_name="test_api_collection",
    )
    container = AppContainer(settings=settings)
    container.embedding_provider = MockEmbeddingProvider(dimension=64)
    container.vector_store = QdrantVectorStore(in_memory=True)
    container.llm_client = FakeLLMClient()

    # Reconnect retriever and RAGEngine
    container.retriever.embedding_provider = container.embedding_provider
    container.retriever.vector_store = container.vector_store
    container.retriever.collection_name = "test_api_collection"
    container.rag_engine.retriever = container.retriever
    container.rag_engine.llm_client = container.llm_client

    # Index sample corpus
    container.initialize_corpus()
    set_container(container)
    return container


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] == "testing"
    assert data["vector_store_healthy"] is True
    assert data["total_documents_indexed"] >= 5


def test_ask_endpoint_success(client: TestClient):
    payload = {
        "query": "What is the maintenance requirement for student residence permit?",
        "top_k": 3,
        "alpha": 0.5,
    }
    response = client.post("/api/v1/ask", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "query_id" in data
    assert data["question"] == payload["query"]
    assert "SEK 10,314" in data["answer"]
    assert len(data["citations"]) >= 1
    assert data["citations"][0]["agency"] == "Migrationsverket"
    assert "X-Request-ID" in response.headers


def test_ask_endpoint_with_agency_filter(client: TestClient):
    payload = {
        "query": "How to register personnummer?",
        "top_k": 2,
        "agency": "Skatteverket",
    }
    response = client.post("/api/v1/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "personnummer" in data["answer"].lower()


def test_ask_endpoint_validation_error(client: TestClient):
    # Query too short
    response = client.post("/api/v1/ask", json={"query": "a"})
    assert response.status_code == 422


def test_ingest_endpoint(client: TestClient):
    response = client.post("/api/v1/ingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["documents_indexed"] >= 5
    assert data["chunks_generated"] >= 10


def test_feedback_endpoint(client: TestClient):
    payload = {
        "query_id": "test-uuid-1234",
        "rating": "up",
        "comment": "Very accurate and cited the right section!",
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["query_id"] == "test-uuid-1234"


def test_app_lifespan():
    with TestClient(app) as test_client:
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200


def test_root_web_interface(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "SveaRAG" in response.text


def test_metrics_endpoint(client: TestClient):
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "rag_requests_total" in response.text
    assert "rag_indexed_documents" in response.text
