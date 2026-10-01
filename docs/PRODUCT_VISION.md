# Product Vision: Swedish Public Services RAG Assistant (SveaRAG)

## 1. Executive Summary
**SveaRAG** is an agile-managed, production-grade Retrieval-Augmented Generation (RAG) assistant designed to help international students, researchers, and foreign professionals navigate Swedish public sector regulations and processes (specifically **Migrationsverket** residence permit rules and **Skatteverket** civil registration/tax guidance).

Rather than serving as a black-box AI toy, this project is architected to demonstrate **professional software engineering rigor**: test-driven retrieval verification, strict citation grounding ("no hallucinations / honest refusals"), end-to-end OpenTelemetry tracing, Prometheus observability metrics, reproducible Docker deployments, and documented Agile sprints with empirical metrics.

---

## 2. Target Audience & Core Problem

### Primary Users
- International students, researchers, and engineers moving to or living in Sweden.
- English-speaking residents needing precise, cited guidance on Swedish administrative bureaucracy without misinterpreting official policies.

### Problem Statement
Official Swedish public sector websites provide authoritative guidance in Swedish and English, but finding precise requirements across multi-page manuals (e.g., maintenance requirement proofs, study-to-work visa transitions, personnummer documentation) is fragmented. Generic LLMs frequently hallucinate outdated migration rules or provide generic EU advice that does not apply to Sweden.

### Solution
A domain-specific RAG system indexing curated Swedish official agency guidance (Migrationsverket & Skatteverket), supporting both Swedish and English queries, strictly returning cited paragraph sources with exact confidence boundaries, zero network dependency during unit/integration tests, and full telemetry into retrieval latency and LLM behavior.

---

## 3. Key Product Goals & Measurable Engineering Objectives

| Objective | Target Metric / Acceptance Threshold |
| :--- | :--- |
| **Strict Grounding & Citation** | 100% of generated responses must cite document IDs and page/section titles. Explicit refusal ("I do not have sufficient information in the corpus") on out-of-domain queries. |
| **Multilingual Retrieval Accuracy** | Hit Rate@3 $\ge 85\%$ and MRR $\ge 0.75$ across a golden evaluation dataset (Swedish & English queries). |
| **Latency SLA** | Median retrieval latency $< 150\text{ms}$; end-to-end P95 request latency $< 2.5\text{s}$ (local Ollama) or $< 1.2\text{s}$ (hosted fallback). |
| **Test Discipline** | Real code test coverage $\ge 85\%$ across core chunking, retrieval, and API logic without mock leaks or live network calls in CI. |
| **Observability** | 100% of requests tracked with trace IDs, structured JSON logs, and Prometheus metrics (P50/P90/P99 latency, error rates, thumbs up/down user feedback ratio). |
| **Reproducibility** | Zero-to-running local stack via a single `docker compose up` command. |

---

## 4. Non-Functional Requirements & Constraints
- **Zero Ongoing Cost:** Local embeddings (HuggingFace `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` or `intfloat/multilingual-e5-small`) and local LLM execution via Ollama (`llama3.2:3b` or `mistral:7b`), with an interchangeable hosted adapter interface.
- **Reliable Data Integrity:** Ingestion pipeline validates metadata, deduplicates chunks, and retains document lineage.
- **No Fabricated Data:** Sprint velocity, test coverage, latency figures, and evaluation accuracy are computed from actual test runs and logged metrics.
