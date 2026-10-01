"""LLM client abstractions and adapters for local Ollama and mock generation."""

import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel, Field

from svearag.core.logging import logger


class GenerationResult(BaseModel):
    """Result of an LLM generation call."""

    text: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Model identifier used for generation")
    latency_ms: float = Field(default=0.0, description="Inference latency in milliseconds")
    prompt_tokens: int = Field(default=0, description="Estimated prompt tokens")
    completion_tokens: int = Field(default=0, description="Estimated completion tokens")
    raw_response: dict[str, Any] = Field(default_factory=dict, description="Raw provider metadata")


class LLMClient(ABC):
    """Abstract interface for LLM text generation providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> GenerationResult:
        """Generates completion text from prompt and system instructions."""
        pass


class OllamaLLMClient(LLMClient):
    """Local LLM client using Ollama HTTP API (zero cost)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> GenerationResult:
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        start_time = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            generated_text = data.get("response", "").strip()

            return GenerationResult(
                text=generated_text,
                model=self.model,
                latency_ms=round(elapsed_ms, 2),
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                raw_response=data,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                "Ollama generation failed", extra_data={"error": str(e), "model": self.model}
            )
            raise RuntimeError(f"Ollama generation error: {e}") from e


class FakeLLMClient(LLMClient):
    """Deterministic fake LLM client for unit & integration testing with zero external calls."""

    def __init__(self, canned_response: str | None = None, model: str = "fake-llm-v1") -> None:
        self.canned_response = canned_response
        self.model = model
        self.calls: list[dict[str, Any]] = []

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> GenerationResult:
        start_time = time.perf_counter()
        self.calls.append(
            {
                "prompt": prompt,
                "system_prompt": system_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )

        if self.canned_response is not None:
            reply = self.canned_response
        else:
            # Refusal check on out-of-domain queries
            if any(
                term in prompt.lower()
                for term in [
                    "not mentioned",
                    "unrelated",
                    "norwegian",
                    "finnish",
                    "danish",
                    "frankrike",
                    "france",
                    "gmbh",
                    "berlin",
                ]
            ):
                reply = "I do not have sufficient information in the official documents to answer this question."
            elif "10314" in prompt or "maintenance" in prompt.lower():
                reply = (
                    "According to Migrationsverket guidelines, the monthly maintenance requirement "
                    "for higher education students is SEK 10,314 [DOC_1]."
                )
            elif "personnummer" in prompt.lower() or "folkbokföring" in prompt.lower():
                reply = (
                    "To register in the Swedish Population Register (Folkbokföring) and obtain a personnummer, "
                    "you must stay in Sweden for at least 12 months and visit a Skatteverket service office in person [DOC_1]."
                )
            else:
                reply = (
                    "Based on official Swedish regulations, the requirement is verified [DOC_1]."
                )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return GenerationResult(
            text=reply,
            model=self.model,
            latency_ms=round(elapsed_ms, 2),
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(reply.split()),
        )
