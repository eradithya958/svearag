"""FastAPI API route handlers with telemetry."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from svearag.api.dependencies import AppContainer, get_container
from svearag.api.schemas import (
    AskRequest,
    AskResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    IngestResponse,
)
from svearag.core.models import RetrievalQuery
from svearag.core.telemetry import (
    RAG_FEEDBACK_TOTAL,
    RAG_INDEXED_DOCUMENTS,
    RAG_LLM_DURATION_SECONDS,
    RAG_REQUEST_DURATION_SECONDS,
    RAG_REQUESTS_TOTAL,
    RAG_RETRIEVAL_DURATION_SECONDS,
    get_prometheus_metrics,
)

router = APIRouter(prefix="/api/v1", tags=["SveaRAG"])


@router.post(
    "/ask", response_model=AskResponse, summary="Query the Swedish Public Services RAG Assistant"
)
def ask_question(
    request: AskRequest,
    container: AppContainer = Depends(get_container),
) -> AskResponse:
    """Answers a question using hybrid retrieval, grounding, and citation generation."""
    try:
        query = RetrievalQuery(
            text=request.query,
            top_k=request.top_k,
            agency=request.agency,
            language=request.language,
            alpha=request.alpha,
        )

        answer = container.rag_engine.answer_query(query)

        # Record metrics
        RAG_REQUESTS_TOTAL.labels(status="success", endpoint="/ask").inc()
        RAG_REQUEST_DURATION_SECONDS.labels(endpoint="/ask").observe(
            answer.total_latency_ms / 1000.0
        )
        RAG_RETRIEVAL_DURATION_SECONDS.labels(retrieval_type="hybrid").observe(
            answer.retrieval_latency_ms / 1000.0
        )
        RAG_LLM_DURATION_SECONDS.labels(model=answer.model_name).observe(
            answer.llm_latency_ms / 1000.0
        )

        return AskResponse(
            query_id=answer.query_id,
            question=answer.question,
            answer=answer.answer,
            citations=answer.citations,
            retrieval_latency_ms=answer.retrieval_latency_ms,
            llm_latency_ms=answer.llm_latency_ms,
            total_latency_ms=answer.total_latency_ms,
            model_name=answer.model_name,
        )
    except Exception as e:
        RAG_REQUESTS_TOTAL.labels(status="error", endpoint="/ask").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}",
        ) from e


@router.get("/health", response_model=HealthResponse, summary="Service health & index status")
def health_check(
    container: AppContainer = Depends(get_container),
) -> HealthResponse:
    """Returns system status, active vector store, and indexed document counts."""
    RAG_INDEXED_DOCUMENTS.set(container.indexed_doc_count)
    return HealthResponse(
        status="healthy",
        environment=container.settings.environment,
        vector_store_healthy=True,
        total_documents_indexed=container.indexed_doc_count,
        llm_model=getattr(container.llm_client, "model", "unknown"),
        version="0.1.0",
    )


@router.post("/ingest", response_model=IngestResponse, summary="Reindex corpus documents")
def trigger_ingestion(
    container: AppContainer = Depends(get_container),
) -> IngestResponse:
    """Triggers reloading and reindexing of documents from the data directory."""
    try:
        docs_count, chunks_count = container.initialize_corpus()
        RAG_INDEXED_DOCUMENTS.set(docs_count)
        return IngestResponse(
            status="success",
            documents_indexed=docs_count,
            chunks_generated=chunks_count,
            message=f"Successfully indexed {docs_count} documents into {chunks_count} chunks.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}",
        ) from e


@router.post("/feedback", response_model=FeedbackResponse, summary="Submit response rating")
def submit_feedback(
    request: FeedbackRequest,
    container: AppContainer = Depends(get_container),
) -> FeedbackResponse:
    """Records user feedback (thumbs up / thumbs down) for quality monitoring."""
    record = {
        "query_id": request.query_id,
        "rating": request.rating,
        "comment": request.comment,
    }
    container.feedback_records.append(record)
    RAG_FEEDBACK_TOTAL.labels(rating=request.rating).inc()
    return FeedbackResponse(
        status="success",
        query_id=request.query_id,
    )


@router.get("/metrics", summary="Prometheus metrics exporter")
def metrics_endpoint() -> Response:
    """Exposes Prometheus scrape metrics."""
    data, content_type = get_prometheus_metrics()
    return Response(content=data, media_type=content_type)
