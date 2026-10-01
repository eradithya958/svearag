# Sprint 1 Plan: Data Ingestion, Retrieval Engine & CI Pipeline

**Sprint Period:** 2-Week Sprint  
**Sprint Goal:** Build a robust, tested document ingestion and hybrid retrieval pipeline indexing Swedish public guidance (Migrationsverket & Skatteverket) with automated CI quality gates.  
**Planned Story Points:** 21 Points  

---

## 1. Committed User Stories

| Story ID | Title | Estimate (Pts) | DoD Criteria Summary |
| :--- | :--- | :--- | :--- |
| **US-101** | Swedish Public Domain Ingestion & Normalization | 3 | Download/parse Swedish & English agency docs with metadata into clean text format. |
| **US-102** | Configurable Chunking with Boundary & Overlap Preservation | 3 | Semantic & token-based chunking with parent metadata tracking; 100% unit test coverage on chunker logic. |
| **US-103** | Multilingual Embedding Generation Module | 2 | Abstract `EmbeddingProvider` interface with local multilingual model (`paraphrase-multilingual-MiniLM-L12-v2`). |
| **US-104** | Vector Database Integration (Qdrant) | 5 | Containerized & local embedded Qdrant vector store adapter with top-k cosine similarity search. |
| **US-105** | Hybrid Retrieval (Dense Vector + BM25 with RRF) | 5 | Fusion of dense semantic search + BM25 lexical search with Reciprocal Rank Fusion ranking. |
| **US-106** | Test Suite & Automated GitHub Actions CI | 3 | Linting (`ruff`), typing (`mypy`), `pytest` with coverage $\ge 85\%$, and pre-commit checks. |

**Total Sprint 1 Points:** **21 Story Points**

---

## 2. Technical Architecture & Decisions for Sprint 1

1. **Language & Environment:** Python 3.11 with modern dependency management (`pyproject.toml` / `uv` or `pip-tools`).
2. **Vector Store Selection:** **Qdrant** (local embedded mode for instant tests, Docker container for local development).
   - *Tradeoff vs Weaviate:* Qdrant supports both in-memory/embedded Python mode (`QdrantClient(":memory:")`) and standalone Docker, meaning unit tests run instantaneously without running a Docker daemon.
3. **Embedding Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions, zero cost, lightweight CPU inference, handles Swedish and English queries accurately).
4. **Hybrid Search:** Combines Qdrant dense vector search with rank-bm25 sparse keyword index, merged via Reciprocal Rank Fusion (RRF: $\text{score} = \sum \frac{1}{k + \text{rank}}$).

---

## 3. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| Embedding model downloads slow down CI tests | High | High | Use mock embedding provider in CI tests; only load actual lightweight weights during local ingestion or dedicated regression runs. |
| Swedish compound words causing sparse search misses | Medium | Medium | Include clean text normalizers and lowercased tokenization in BM25 indexer. |
| Docker setup complexity for recruiters running the repo | High | Low | Support pure local python mode with embedded Qdrant alongside standard Docker Compose. |
