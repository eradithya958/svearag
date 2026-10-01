# Sprint 4 Plan: Evaluation, Observability & Production Polish

**Sprint Period:** Sprint 4 (2 Weeks)  
**Sprint Goal:** Deliver empirical RAG evaluation benchmarks (Hit Rate@k, MRR, Faithfulness) comparing retrieval configurations, full observability instrumentation (OpenTelemetry, Prometheus `/metrics`, Grafana dashboards), and comprehensive technical documentation (`ARCHITECTURE.md`, `README.md`).  
**Planned Story Points:** 21 Points  

---

## 1. Committed User Stories

| Story ID | Title | Estimate (Pts) | DoD Criteria Summary |
| :--- | :--- | :--- | :--- |
| **US-401** | Ground Truth Evaluation Benchmark | 5 | 40 curated bilingual Q&A pairs (`eval/data/ground_truth.json`) with expected doc IDs and refusal queries. |
| **US-402** | Automated Evaluation & Regression Pipeline | 5 | Runner calculating Hit Rate@3, Hit Rate@5, MRR, and Faithfulness; comparisons across configurations. |
| **US-501** | Structured Logging & Trace IDs | 3 | Correlation IDs attached across request lifecycles. |
| **US-502** | OpenTelemetry Traces & Prometheus Metrics | 5 | Custom Prometheus metrics (`rag_requests_total`, `rag_latency_seconds`, `rag_feedback_total`) exposed at `/metrics`. |
| **US-503** | Grafana Dashboard Provisioning | 3 | Auto-provisioned Grafana dashboard definition in Docker Compose. |

**Total Sprint 4 Points:** **21 Story Points**
