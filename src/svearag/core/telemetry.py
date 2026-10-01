"""OpenTelemetry distributed tracing and Prometheus metrics instrumentation."""

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# 1. Prometheus Metrics Definitions
RAG_REQUESTS_TOTAL = Counter(
    "rag_requests_total",
    "Total count of incoming RAG requests",
    ["status", "endpoint"],
)

RAG_REQUEST_DURATION_SECONDS = Histogram(
    "rag_request_duration_seconds",
    "End-to-end request latency in seconds",
    ["endpoint"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

RAG_RETRIEVAL_DURATION_SECONDS = Histogram(
    "rag_retrieval_duration_seconds",
    "Hybrid retrieval duration in seconds",
    ["retrieval_type"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)

RAG_LLM_DURATION_SECONDS = Histogram(
    "rag_llm_duration_seconds",
    "LLM generation duration in seconds",
    ["model"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
)

RAG_FEEDBACK_TOTAL = Counter(
    "rag_feedback_total",
    "Total user ratings received",
    ["rating"],
)

RAG_INDEXED_DOCUMENTS = Gauge(
    "rag_indexed_documents",
    "Total number of documents indexed in vector store",
)


def get_prometheus_metrics() -> tuple[bytes, str]:
    """Generates Prometheus text representation of active metrics."""
    return generate_latest(), CONTENT_TYPE_LATEST
