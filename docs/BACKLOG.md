# Product Backlog & User Stories

**Estimation Scale:** Fibonacci story points (1 = trivial/quick config, 2 = small feature/test, 3 = medium feature with unit tests, 5 = substantial feature with multi-component logic, 8 = complex system/infrastructure integration).

---

## Epic 1: Data Ingestion & Retrieval Pipeline (Sprint 1)

### US-101: Swedish Public Domain Document Acquisition & Preprocessing
- **Description:** As a data engineer, I want an automated ingestion script that downloads and normalizes official Swedish public agency guidance (Migrationsverket residence permit rules, Skatteverket personnummer/tax registration guides) into standard Markdown/JSON format with metadata.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - Ingestion loader extracts text, titles, sections, source URLs, and language tags (Swedish/English).
  - Documents are stored in `data/raw/` and processed into `data/processed/`.
  - Ingestion script handles missing metadata gracefully and logs statistics.

### US-102: Configurable Text Chunking with Overlap & Boundary Preservation
- **Description:** As an ML engineer, I want a modular chunking strategy that splits documents by semantic boundaries (headers, paragraphs) while supporting configurable chunk size (e.g. 250 vs 500 tokens) and overlap (e.g. 50 tokens).
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - Implements recursive character and semantic header-aware chunkers.
  - Generates deterministic chunk IDs and attaches parent document metadata (source url, title, chunk index).
  - Unit tests verify chunk boundaries, token length limits, and overlap correctness with 100% pass rate.

### US-103: Multilingual Embedding Generation Module
- **Description:** As a backend developer, I want a local, zero-cost embedding module using a multilingual sentence transformer (e.g. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` or `intfloat/multilingual-e5-small`) so that both Swedish and English queries produce high-quality semantic representations.
- **Priority:** High (Must Have)
- **Story Points:** 2
- **Acceptance Criteria:**
  - Standardized `EmbeddingProvider` interface with a `generate_embeddings(texts: list[str]) -> list[list[float]]` method.
  - Local embedding model runs offline on CPU/MPS/CUDA with batching support.
  - Unit tests verify output vector dimensions and mock inference for CI speed.

### US-104: Vector Database Integration (Qdrant / Chroma)
- **Description:** As a backend engineer, I want to store chunk embeddings and metadata in an embedded/containerized vector store with cosine similarity search and payload filtering.
- **Priority:** High (Must Have)
- **Story Points:** 5
- **Acceptance Criteria:**
  - Standardized `VectorStore` interface implemented for Qdrant (in Docker / local embedded mode).
  - Upsert pipeline inserts chunks with payload (document title, URL, language, text, chunk_id).
  - Vector similarity search returns top-k documents with similarity scores.
  - Integration tests verify collection creation, upsert, and retrieval without external network access.

### US-105: Hybrid Retrieval (Dense Vector + BM25 Keyword Search)
- **Description:** As a search engineer, I want hybrid retrieval combining dense semantic search and BM25 sparse keyword matching with Reciprocal Rank Fusion (RRF) to accurately match exact legal/agency terminology (e.g., "uppehållstillstånd", "samordningsnummer").
- **Priority:** High (Must Have)
- **Story Points:** 5
- **Acceptance Criteria:**
  - Implements BM25 indexing over raw chunk texts alongside dense vector retrieval.
  - Hybrid search combines scores using configurable RRF ($\alpha$ weighting parameter).
  - Unit tests demonstrate hybrid search matches exact Swedish keywords that dense search ranks low.

### US-106: Sprint 1 Test Suite & Automated CI Pipeline
- **Description:** As a DevOps engineer, I want a GitHub Actions CI workflow that runs linters (`ruff`), type checking (`mypy`), and `pytest` with code coverage reports on every push and PR.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - CI passes in under 3 minutes using cached virtual environments.
  - Coverage threshold enforced at $\ge 85\%$ for all Sprint 1 modules.
  - Zero flakiness; all mock objects strictly isolated from network calls.

---

## Epic 2: Generation Engine & Core API Service (Sprint 2)

### US-201: Swappable LLM Generation Interface & Local Ollama Adapter
- **Description:** As an AI developer, I want an abstract `LLMClient` interface with a default local Ollama adapter (e.g., `llama3.2` / `mistral`) and a mock adapter for tests so that generation is decoupled from model vendors.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - `LLMClient` interface defines `generate(prompt: str, system_prompt: str) -> GenerationResult`.
  - Ollama client supports configurable temperature, max tokens, and timeout handling.
  - `FakeLLMClient` provided for instant, deterministic unit and integration tests.

### US-202: Grounded Prompt Engineering & Citation Enforcement
- **Description:** As a user, I want answers that explicitly cite specific sources ([Source 1: Skatteverket Section X]) and clearly state "I do not have sufficient information in the official documents" when the query cannot be answered from the retrieved context.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - System prompt injects retrieved chunk context with structured citation keys `[DOC_N]`.
  - Generation post-processor maps citation tokens back to source metadata (title, URL, snippet).
  - Strict instruction prevents hallucinated extrapolation outside retrieved context.
  - Unit tests verify formatting and refusal behaviors across benchmark edge cases.

### US-203: FastAPI Service & Core Endpoints (`/ask`, `/health`, `/ingest`)
- **Description:** As a frontend developer or API consumer, I want RESTful API endpoints with Pydantic request/response validation, latency measurement, and OpenAPI documentation.
- **Priority:** High (Must Have)
- **Story Points:** 5
- **Acceptance Criteria:**
  - `POST /api/v1/ask`: Accepts query, filters (e.g. language, agency); returns answer, cited sources list, total latency, and query ID.
  - `GET /api/v1/health`: Returns service health, vector store connectivity, and model status.
  - `POST /api/v1/ingest`: Triggers background indexing of new documents.
  - Pydantic models validate all payloads with detailed validation error messages.

### US-204: API Integration Test Suite with Mock Vector Store & Fake LLM
- **Description:** As a quality engineer, I want comprehensive integration tests verifying the full `/ask` request-response lifecycle without invoking real LLM binaries or live external databases.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - Tests verify HTTP status codes, response structure, error responses (400, 422, 500).
  - Verifies end-to-end flow from request payload to response citation generation.
  - Integration suite executes in $< 5$ seconds in CI.

### US-205: Backend Dockerization & Container Build Verification
- **Description:** As a software engineer, I want a lightweight multi-stage Dockerfile for the FastAPI backend service that runs reliably across Linux/macOS environments.
- **Priority:** Medium (Should Have)
- **Story Points:** 2
- **Acceptance Criteria:**
  - Multi-stage Docker build produces an image $< 500\text{MB}$ (excluding vector model weights cache).
  - Docker container starts with non-root user and healthcheck passed.

---

## Epic 3: User Interface & Experience (Sprint 3)

### US-301: React + Vite Interactive Chat Interface
- **Description:** As a user, I want a clean, responsive chat interface where I can ask questions in English or Swedish, view streaming/loading states, and see responses formatted in clean Markdown.
- **Priority:** High (Must Have)
- **Story Points:** 5
- **Acceptance Criteria:**
  - Built with React + TypeScript + Vite.
  - Displays conversation turns with user queries and assistant answers.
  - Loading skeleton and error banners for network or backend errors.
  - Keyboard shortcuts (Enter to send, Shift+Enter for new line).

### US-302: Expandable Source Citations & Context Inspector
- **Description:** As a user, I want to click on citation badges attached to an answer to inspect the exact official excerpt, source URL, agency name, and relevance score.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - Inline citation tags `[1]`, `[2]` link to an expandable drawer or cards beneath the message.
  - Clicking a citation reveals: Agency name, document title, exact excerpt text, and external link to official portal.

### US-303: User Feedback Collection Mechanism (Thumbs Up/Down)
- **Description:** As a product owner, I want users to submit thumbs up/down feedback on responses with optional comments so that we can track response quality and log feedback metrics.
- **Priority:** Medium (Should Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - Thumbs up/down buttons on each assistant message.
  - Submits feedback to backend `POST /api/v1/feedback` with query ID, rating, and timestamp.
  - Feedback state is persisted in UI session.

### US-304: Full-Stack Docker Compose Environment
- **Description:** As a developer or evaluator, I want a single `docker-compose.yml` that orchestrates Backend, Frontend, Vector DB, and local Ollama service.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - `docker compose up` starts all services with network bridging and environment variable injection.
  - Healthcheck dependencies ensure Backend waits for Vector DB readiness.

---

## Epic 4: RAG Evaluation & Empirical Quality Benchmarks (Sprint 4)

### US-401: Ground Truth Swedish Public Services Evaluation Benchmark
- **Description:** As an ML/QA engineer, I want a curated dataset of 40 real-world bilingual question-answer pairs with reference source paragraphs and expected refusal queries.
- **Priority:** High (Must Have)
- **Story Points:** 5
- **Acceptance Criteria:**
  - Dataset in `eval/data/ground_truth.json` contains: 25 English queries, 10 Swedish queries, 5 out-of-domain refusal queries.
  - Each item includes: `question`, `expected_answer`, `relevant_doc_ids`, `is_answerable`.

### US-402: Automated Retrieval & Faithfulness Metric Pipeline
- **Description:** As a data scientist, I want an evaluation script that calculates Hit Rate@k, Mean Reciprocal Rank (MRR), and Groundedness/Faithfulness metrics across chunking and retrieval configurations.
- **Priority:** High (Must Have)
- **Story Points:** 5
- **Acceptance Criteria:**
  - Computes Hit Rate@3, Hit Rate@5, and MRR on the benchmark dataset.
  - Compares Configuration A (Small chunks 250t, Vector-only) vs Configuration B (Medium chunks 500t, Hybrid BM25+Vector).
  - Generates a markdown summary table (`eval/results/benchmark_report.md`).
  - Fast subset (5 queries) runs in CI as a regression test.

---

## Epic 5: Production Observability & Telemetry (Sprint 4)

### US-501: Structured JSON Logging & Correlation IDs
- **Description:** As a site reliability engineer, I want structured JSON logging across all backend requests with trace IDs, client IPs, retrieval counts, and latency breakdowns.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - Request middleware assigns a UUID `request_id` / `trace_id` to every request.
  - Logs emitted in machine-readable JSON format (`timestamp`, `level`, `request_id`, `duration_ms`, `retrieval_count`).
  - Sensitive content (passwords, tokens) filtered.

### US-502: OpenTelemetry Tracing & Prometheus Metrics Instrumentation
- **Description:** As a DevOps engineer, I want OpenTelemetry spans across document loading, vector retrieval, and LLM inference, plus Prometheus metrics exposed at `/metrics`.
- **Priority:** High (Must Have)
- **Story Points:** 5
- **Acceptance Criteria:**
  - Prometheus metrics exported: `rag_requests_total`, `rag_request_duration_seconds` (histogram), `rag_retrieval_duration_seconds`, `rag_llm_duration_seconds`, `rag_feedback_total`.
  - Spans for `retrieval.search`, `prompt.format`, and `llm.generate`.

### US-503: Provisioned Grafana Dashboard & Monitoring Stack
- **Description:** As an engineer, I want pre-configured Prometheus and Grafana services in Docker Compose with a provisioned dashboard visualizing latency percentiles (P50/P90/P99), request volume, error rates, and feedback ratios.
- **Priority:** High (Must Have)
- **Story Points:** 3
- **Acceptance Criteria:**
  - Grafana dashboard JSON file provisioned automatically on container start.
  - Dashboard panels visualize: Request RPS, P50/P95/P99 Latency, Vector DB Search Latency, User Satisfaction %, and Error Rates.
