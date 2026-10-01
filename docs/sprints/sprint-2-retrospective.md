# Sprint 2 Retrospective & Metrics Report

**Sprint Goal:** Build the generation engine with swappable LLM adapters, grounded citation prompts with honest refusals, and a robust FastAPI REST API service with complete integration test coverage and Docker packaging.  
**Sprint Period:** Sprint 2 (2 Weeks)  
**Status:** ✅ Completed  

---

## 1. Velocity & Sprint Burndown Metrics

| Metric | Target / Planned | Actual Achieved | Status |
| :--- | :--- | :--- | :--- |
| **Committed Story Points** | 16 Pts | 16 Pts | 100% committed delivered |
| **Completed Story Points** | 16 Pts | 16 Pts | US-201 to US-205 all Done |
| **Delivered Velocity** | 16 Pts | **16 Pts** | Sprint 2 Target Achieved |
| **Cumulative Project Velocity** | 37 Pts | **37 Pts** (Sprint 1: 21, Sprint 2: 16) | On track |
| **Measured Test Coverage** | $\ge 85\%$ | **96.62%** | Measured by `pytest-cov` (51 tests) |
| **Test Execution Speed** | $< 5.0\text{s}$ | **0.60s** | Full API integration tests without live LLM |
| **Containerization** | Production Ready | **Multi-stage Dockerfile** | Non-root security user & healthcheck |

---

## 2. Completed User Stories

| Story ID | Title | Estimate | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **US-201** | Swappable LLM Interface | 3 Pts | **Done** | [llm.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/generation/llm.py) with `OllamaLLMClient` & `FakeLLMClient`. |
| **US-202** | Grounded Citation Prompting | 3 Pts | **Done** | [prompt.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/generation/prompt.py) with `[DOC_N]` citation tagging & honest refusal rule. |
| **US-203** | FastAPI Service & Endpoints | 5 Pts | **Done** | [routes.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/api/routes.py) & [app.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/api/app.py) (`/ask`, `/health`, `/ingest`, `/feedback`). |
| **US-204** | API Integration Test Suite | 3 Pts | **Done** | [test_api.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/tests/test_api.py) & [test_generation.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/tests/test_generation.py) (51 tests). |
| **US-205** | Backend Dockerization | 2 Pts | **Done** | [Dockerfile](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/Dockerfile) & [.dockerignore](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/.dockerignore). |

---

## 3. Retrospective Discussion

### 🟢 What Went Well
1. **Deterministic Test Client:** The `FakeLLMClient` enabled testing the entire FastAPI `/ask` flow (hybrid retrieval $\rightarrow$ prompt formatting $\rightarrow$ LLM generation $\rightarrow$ citation extraction) in milliseconds without requiring a running Ollama daemon.
2. **Citation Lineage:** Every answer returns full source metadata (document ID, official URL, issuing agency, relevance score, and excerpt snippet).
3. **Structured API Contract:** Clean Pydantic schemas with OpenAPI interactive documentation generated at `/docs`.

### 🔴 What Didn't Go Well / Pains Resolved
1. Ruff flagged `B008` (function call in argument default) for FastAPI's standard `Depends()`, resolved by updating linter configuration.

---

## 4. Action Items for Sprint 3
- [ ] **Action 1:** Scaffold React + Vite frontend with TypeScript and clean component hierarchy.
- [ ] **Action 2:** Implement interactive chat interface with expandable citation inspector and thumbs up/down rating buttons.
- [ ] **Action 3:** Write `docker-compose.yml` orchestrating Frontend, Backend, Qdrant, and local services.
