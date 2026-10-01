# Sprint 1 Retrospective & Metrics Report

**Sprint Goal:** Build a robust, tested document ingestion and hybrid retrieval pipeline indexing Swedish public guidance (Migrationsverket & Skatteverket) with automated CI quality gates.  
**Sprint Period:** Sprint 1 (2 Weeks)  
**Status:** ✅ Completed  

---

## 1. Velocity & Sprint Burndown Metrics

| Metric | Target / Planned | Actual Achieved | Status |
| :--- | :--- | :--- | :--- |
| **Committed Story Points** | 21 Pts | 21 Pts | 100% committed delivered |
| **Completed Story Points** | 21 Pts | 21 Pts | US-101 to US-106 all Done |
| **Delivered Velocity** | 21 Pts | **21 Pts** | Sprint 1 Baseline Established |
| **Measured Test Coverage** | $\ge 85\%$ | **96.56%** | Verified via `pytest --cov` (37 tests) |
| **Test Execution Speed** | $< 5.0\text{s}$ | **0.23s** | Zero-network mock architecture |
| **Linters & Style Checks** | Clean | **100% Clean** | `ruff` check and format passing |
| **Indexed Corpus Size** | $\ge 5$ docs | **7 Documents (10 Chunks)** | Migrationsverket + Skatteverket |

---

## 2. Completed User Stories

| Story ID | Title | Estimate | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **US-101** | Swedish Public Guidance Ingestion | 3 Pts | **Done** | [loader.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/ingestion/loader.py) with YAML frontmatter parser and 7 official guides. |
| **US-102** | Configurable Chunking Engine | 3 Pts | **Done** | [chunker.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/ingestion/chunker.py) with `RecursiveTokenChunker` and `SemanticHeaderChunker`. |
| **US-103** | Multilingual Embeddings Module | 2 Pts | **Done** | [embeddings.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/retrieval/embeddings.py) with `SentenceTransformerEmbeddingProvider` and `MockEmbeddingProvider`. |
| **US-104** | Qdrant Vector Store Adapter | 5 Pts | **Done** | [vector_store.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/retrieval/vector_store.py) supporting in-memory mode (`:memory:`) and client mode. |
| **US-105** | Hybrid Retrieval (Dense + BM25 with RRF) | 5 Pts | **Done** | [hybrid.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/retrieval/hybrid.py) and [bm25.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/retrieval/bm25.py) with Reciprocal Rank Fusion. |
| **US-106** | Test Suite & Automated CI Pipeline | 3 Pts | **Done** | [.github/workflows/ci.yml](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/.github/workflows/ci.yml), 37 tests, 96.56% coverage. |

---

## 3. Retrospective Discussion

### 🟢 What Went Well
1. **Zero-Network Test Isolation:** Implementing `MockEmbeddingProvider` and Qdrant in-memory mode enabled 37 unit tests to run in just **0.23 seconds** with **96.56% coverage**.
2. **Multilingual Ingestion:** The parser handled both Swedish (*Migrationsverket forskare*) and English documents with structured metadata extraction.
3. **Hybrid RRF Fusion:** Combining dense vector similarity with BM25 keyword matching resolved Swedish compound terms and specific financial thresholds (e.g., *10,314 SEK*).

### 🔴 What Didn't Go Well / Blockers Encountered
1. `LogRecord` attribute collision in Python standard logging when passing keyword arguments (e.g. `module`), which was resolved by sanitizing extra parameters in `StructuredLogger`.
2. Qdrant Python Client 1.19 changed `search()` in favor of `query_points()`, requiring an API abstraction update.

### 🟡 Key Learnings
- Decoupling the `EmbeddingProvider` interface early allowed fast local unit testing without downloading model weights during development.

---

## 4. Action Items for Sprint 2
- [ ] **Action 1:** Implement abstract `LLMClient` with Ollama adapter and deterministic `FakeLLMClient` for tests.
- [ ] **Action 2:** Create FastAPI `/ask` endpoint returning answers, cited sources, and latency measurements.
- [ ] **Action 3:** Add Dockerfile for containerized backend execution.
