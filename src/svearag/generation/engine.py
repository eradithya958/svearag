"""End-to-end RAG query orchestrator and engine."""

import time
import uuid

from pydantic import BaseModel, Field

from svearag.core.logging import logger
from svearag.core.models import RetrievalQuery, SearchResult
from svearag.generation.llm import LLMClient
from svearag.generation.prompt import CitedSource, PromptBuilder
from svearag.retrieval.hybrid import RRFHybridRetriever


class RAGAnswer(BaseModel):
    """Structured end-to-end RAG response."""

    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated grounded response")
    citations: list[CitedSource] = Field(
        default_factory=list, description="Extracted cited sources"
    )
    retrieved_documents: list[SearchResult] = Field(
        default_factory=list, description="All candidate chunks retrieved"
    )
    retrieval_latency_ms: float = Field(default=0.0)
    llm_latency_ms: float = Field(default=0.0)
    total_latency_ms: float = Field(default=0.0)
    model_name: str = Field(default="unknown")


class RAGEngine:
    """Orchestrates hybrid retrieval, prompt engineering, generation, and citation extraction."""

    def __init__(
        self,
        retriever: RRFHybridRetriever,
        llm_client: LLMClient,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self.retriever = retriever
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder or PromptBuilder()

    def answer_query(self, query: RetrievalQuery) -> RAGAnswer:
        """Executes full RAG workflow and returns verified answer with citations."""
        start_total = time.perf_counter()
        query_id = str(uuid.uuid4())

        # 1. Retrieval
        retrieval_start = time.perf_counter()
        retrieved_results = self.retriever.retrieve(query)
        retrieval_latency_ms = (time.perf_counter() - retrieval_start) * 1000.0

        # 2. Prompt Building
        user_prompt, system_prompt = self.prompt_builder.build_prompt(
            question=query.text,
            retrieved_results=retrieved_results,
        )

        # 3. LLM Generation
        llm_start = time.perf_counter()
        gen_result = self.llm_client.generate(prompt=user_prompt, system_prompt=system_prompt)
        llm_latency_ms = (time.perf_counter() - llm_start) * 1000.0

        # 4. Citation Extraction
        citations = self.prompt_builder.parse_citations(
            generated_text=gen_result.text,
            retrieved_results=retrieved_results,
        )

        total_latency_ms = (time.perf_counter() - start_total) * 1000.0

        logger.info(
            "Processed RAG query",
            extra_data={
                "query_id": query_id,
                "question": query.text,
                "citations_count": len(citations),
                "retrieval_latency_ms": round(retrieval_latency_ms, 2),
                "llm_latency_ms": round(llm_latency_ms, 2),
                "total_latency_ms": round(total_latency_ms, 2),
                "model": gen_result.model,
            },
        )

        return RAGAnswer(
            query_id=query_id,
            question=query.text,
            answer=gen_result.text,
            citations=citations,
            retrieved_documents=retrieved_results,
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            llm_latency_ms=round(llm_latency_ms, 2),
            total_latency_ms=round(total_latency_ms, 2),
            model_name=gen_result.model,
        )
