# Sprint 2 Plan: Generation Engine, Citations & FastAPI Service

**Sprint Period:** Sprint 2 (2 Weeks)  
**Sprint Goal:** Build the generation engine with swappable LLM adapters, grounded citation prompts with honest refusals, and a robust FastAPI REST API service with complete integration test coverage and Docker packaging.  
**Planned Story Points:** 16 Points  

---

## 1. Committed User Stories

| Story ID | Title | Estimate (Pts) | DoD Criteria Summary |
| :--- | :--- | :--- | :--- |
| **US-201** | Swappable LLM Generation Interface | 3 | Abstract `LLMClient` with local `OllamaLLMClient` and deterministic `FakeLLMClient`. |
| **US-202** | Grounded Prompting & Citation Enforcement | 3 | Prompt template forcing grounded answers, citing `[DOC_N]`, and explicit refusal behavior. |
| **US-203** | FastAPI Service & REST Endpoints | 5 | `/api/v1/ask`, `/api/v1/health`, `/api/v1/ingest`, `/api/v1/feedback` with Pydantic validation and latency tracking. |
| **US-204** | API Integration Test Suite | 3 | Fast, zero-network integration tests verifying end-to-end request-response lifecycle with FakeLLM. |
| **US-205** | Production Dockerization | 2 | Multi-stage Dockerfile with non-root security user and healthcheck. |

**Total Sprint 2 Points:** **16 Story Points**

---

## 2. Technical Architecture & Decisions for Sprint 2

1. **LLM Interface Decoupling:** `LLMClient` base class defines `generate(prompt: str, system_prompt: str) -> GenerationResult`. This allows instantaneous testing without running Ollama, while supporting local Ollama (`llama3.2` / `mistral`) and cloud fallback.
2. **Strict Grounding:** The prompt builder numbers retrieved chunks as `[DOC_1]`, `[DOC_2]`, etc., and instructs the model:
   - Only use facts stated in the context.
   - Attach citation tags immediately after claims.
   - Output exact refusal token when context does not contain the answer.
3. **API Middleware:** Request ID generation, latency instrumentation (retrieval vs generation latency), and CORS middleware for frontend integration.
