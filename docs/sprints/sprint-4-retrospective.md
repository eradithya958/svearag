# Sprint 4 Retrospective & Metrics Report

**Sprint Goal:** Deliver empirical RAG evaluation benchmarks (Hit Rate@k, MRR, Faithfulness) comparing retrieval configurations, full observability instrumentation (OpenTelemetry, Prometheus `/metrics`, Grafana dashboards), and comprehensive technical documentation (`ARCHITECTURE.md`, `README.md`).  
**Sprint Period:** Sprint 4 (2 Weeks)  
**Status:** ✅ Completed  

---

## 1. Velocity & Sprint Burndown Metrics

| Metric | Target / Planned | Actual Achieved | Status |
| :--- | :--- | :--- | :--- |
| **Committed Story Points** | 21 Pts | 21 Pts | 100% committed delivered |
| **Completed Story Points** | 21 Pts | 21 Pts | US-401, US-402, US-501, US-502, US-503 Done |
| **Delivered Velocity** | 21 Pts | **21 Pts** | Sprint 4 Target Met |
| **Total Project Velocity** | **72 Pts** | **72 Pts** (S1: 21, S2: 16, S3: 14, S4: 21) | **100% On Schedule** |
| **Measured Test Coverage** | $\ge 85\%$ | **93.90%** | Measured by `pytest-cov` (54 tests) |
| **Retrieval Hit Rate@3** | $\ge 85\%$ | **100.0%** | Measured across 40 golden evaluation queries |
| **Retrieval MRR** | $\ge 0.75$ | **0.9238** | Hybrid RRF retrieval |
| **Honest Refusal Rate** | 100% | **100.0%** | Out-of-domain query boundary enforcement |

---

## 2. Completed User Stories

| Story ID | Title | Estimate | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **US-401** | Golden Evaluation Benchmark | 5 Pts | **Done** | [ground_truth.json](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/eval/data/ground_truth.json) (40 bilingual Swedish & English questions). |
| **US-402** | Automated Evaluation & Regression Pipeline | 5 Pts | **Done** | [run_eval.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/eval/run_eval.py) and [benchmark_report.md](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/eval/results/benchmark_report.md). |
| **US-501** | Structured Logging & Correlation IDs | 3 Pts | **Done** | [logging.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/core/logging.py) & [app.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/api/app.py) (`X-Request-ID`). |
| **US-502** | Prometheus Metrics Instrumentation | 5 Pts | **Done** | [telemetry.py](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/core/telemetry.py) and `/api/v1/metrics`. |
| **US-503** | Grafana Dashboards Provisioning | 3 Pts | **Done** | [svearag_overview.json](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/monitoring/grafana/dashboards/svearag_overview.json) & [docker-compose.yml](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/docker-compose.yml). |

---

## 3. Retrospective Discussion

### 🟢 What Went Well
1. **Measurable Accuracy Gains:** The comparative evaluation demonstrated that Hybrid RRF search ($\alpha=0.5$) achieved **100.0% Hit Rate@3** and **0.9238 MRR**, outperforming pure dense search (94.29% Hit Rate@3, 0.8748 MRR).
2. **True Full-Stack Observability:** Prometheus latency histograms and Grafana dashboards allow real-time monitoring of P50/P95/P99 latency, request volume, and user feedback ratios.
3. **Engineering Portfolio Rigor:** Every number on the project is measured directly from automated benchmarks and tests.

---

## 4. Overall Project Summary & Portfolio Highlights
- **Total Story Points Delivered:** 72 Story Points across 4 Sprints.
- **Code Test Coverage:** 93.90% with 54 passing tests in 0.64s.
- **Zero Ongoing Cost:** Local embeddings + local Ollama support + in-memory testing.
