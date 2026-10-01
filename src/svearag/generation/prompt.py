"""Prompt construction and citation parsing engine."""

import re

from pydantic import BaseModel, Field

from svearag.core.models import SearchResult


class CitedSource(BaseModel):
    """Source document snippet cited by LLM."""

    doc_tag: str = Field(..., description="Citation tag, e.g. [DOC_1]")
    doc_id: str = Field(..., description="Document ID, e.g. MV-EDU-001")
    title: str = Field(..., description="Document title")
    agency: str = Field(..., description="Issuing agency")
    source_url: str = Field(..., description="Official web source URL")
    snippet: str = Field(..., description="Relevant text excerpt")
    relevance_score: float = Field(default=0.0, description="Retrieval similarity or RRF score")


SYSTEM_PROMPT_TEMPLATE = """You are SveaRAG, an authoritative AI assistant specialized in Swedish public administrative regulations (Migrationsverket & Skatteverket).

CRITICAL INSTRUCTIONS:
1. Grounding: Answer the user's question relying ONLY on the official document excerpts provided below.
2. Citations: Every single factual claim must be followed immediately by its corresponding source tag, such as [DOC_1] or [DOC_2].
3. Honest Refusal: If the provided excerpts do not contain enough facts to answer the question with certainty, answer strictly with:
"I do not have sufficient information in the official documents to answer this question."
4. Multilingual: If the user asks in Swedish, respond in Swedish. If in English, respond in English. Always use official terminology (e.g. folkbokföring, personnummer, uppehållstillstånd, SINK).
5. Tone: Professional, precise, factual. Never speculate or hallucinate outside the given text."""


class PromptBuilder:
    """Builds grounded context prompts and parses generated citations."""

    def __init__(self, system_prompt: str = SYSTEM_PROMPT_TEMPLATE) -> None:
        self.system_prompt = system_prompt

    def build_prompt(
        self,
        question: str,
        retrieved_results: list[SearchResult],
    ) -> tuple[str, str]:
        """Constructs formatted user prompt containing numbered context documents and returns (user_prompt, system_prompt)."""
        if not retrieved_results:
            context_str = "No official documents found matching the query."
        else:
            context_blocks = []
            for idx, res in enumerate(retrieved_results, start=1):
                chunk = res.chunk
                header = (
                    f"--- [DOC_{idx}] ---\n"
                    f"Agency: {chunk.metadata.agency}\n"
                    f"Document ID: {chunk.document_id}\n"
                    f"Title: {chunk.metadata.extra.get('title') or chunk.document_id}\n"
                    f"Source URL: {chunk.metadata.source_url}\n"
                    f"Content:\n{chunk.text.strip()}"
                )
                context_blocks.append(header)
            context_str = "\n\n".join(context_blocks)

        user_prompt = (
            f"OFFICIAL DOCUMENT EXCERPTS:\n{context_str}\n\n"
            f"USER QUESTION:\n{question}\n\n"
            f"ANSWER (with [DOC_N] citations):"
        )

        return user_prompt, self.system_prompt

    def parse_citations(
        self,
        generated_text: str,
        retrieved_results: list[SearchResult],
    ) -> list[CitedSource]:
        """Extracts [DOC_N] tags from text and maps them to metadata of retrieved results."""
        doc_indices = re.findall(r"\[DOC_(\d+)\]", generated_text)
        unique_indices = sorted({int(idx) for idx in doc_indices})

        citations: list[CitedSource] = []
        for idx in unique_indices:
            if 1 <= idx <= len(retrieved_results):
                res = retrieved_results[idx - 1]
                chunk = res.chunk
                citations.append(
                    CitedSource(
                        doc_tag=f"[DOC_{idx}]",
                        doc_id=chunk.document_id,
                        title=chunk.metadata.extra.get("title") or chunk.document_id,
                        agency=chunk.metadata.agency,
                        source_url=chunk.metadata.source_url,
                        snippet=chunk.text[:300] + ("..." if len(chunk.text) > 300 else ""),
                        relevance_score=round(res.score, 4),
                    )
                )

        return citations
