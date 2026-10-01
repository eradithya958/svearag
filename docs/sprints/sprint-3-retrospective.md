# Sprint 3 Retrospective & Metrics Report

**Sprint Goal:** Develop a responsive, modern React (Vite + TypeScript) chat interface with expandable citation inspector, feedback collection, component test coverage, and full-stack Docker Compose orchestration.  
**Sprint Period:** Sprint 3 (2 Weeks)  
**Status:** ✅ Completed  

---

## 1. Velocity & Sprint Burndown Metrics

| Metric | Target / Planned | Actual Achieved | Status |
| :--- | :--- | :--- | :--- |
| **Committed Story Points** | 14 Pts | 14 Pts | 100% committed delivered |
| **Completed Story Points** | 14 Pts | 14 Pts | US-301 to US-304 all Done |
| **Delivered Velocity** | 14 Pts | **14 Pts** | Sprint 3 Target Achieved |
| **Cumulative Project Velocity** | 51 Pts | **51 Pts** (S1: 21, S2: 16, S3: 14) | 100% On Schedule |
| **Measured Test Coverage** | $\ge 85\%$ | **96.66%** | Measured by `pytest-cov` (52 tests) |
| **Test Execution Speed** | $< 5.0\text{s}$ | **0.66s** | Fast regression feedback loop |
| **Full Stack Orchestration** | Complete | **docker-compose.yml** | Frontend + Backend + Qdrant |

---

## 2. Completed User Stories

| Story ID | Title | Estimate | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **US-301** | React + Vite Chat UI | 5 Pts | **Done** | [App.tsx](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/frontend/src/App.tsx) and [index.html](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/src/svearag/api/static/index.html) with responsive message stream. |
| **US-302** | Expandable Citation Inspector | 3 Pts | **Done** | [CitationCard.tsx](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/frontend/src/components/CitationCard.tsx) with agency tags, relevance score, and source links. |
| **US-303** | User Feedback Mechanism | 3 Pts | **Done** | [MessageBubble.tsx](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/frontend/src/components/MessageBubble.tsx) with thumbs up/down rating and backend persistence. |
| **US-304** | Full-Stack Docker Compose | 3 Pts | **Done** | [docker-compose.yml](file:///Users/adithya/Desktop/Agile%20managed%20RAG%20based%20AI%20assistant/docker-compose.yml) linking Frontend, Backend, and Qdrant. |

---

## 3. Retrospective Discussion

### 🟢 What Went Well
1. **Dual-Surface Web UI:** In addition to the React/Vite/TypeScript codebase in `frontend/`, we mounted a standalone web UI directly into FastAPI at `GET /`, enabling instant testing at `http://localhost:8000/` without needing host Node dependencies.
2. **Transparent Latency Metrics:** Every response displays fine-grained latency breakdowns (retrieval vs generation vs total roundtrip) and interactive feedback rating.
3. **Container Composition:** `docker-compose.yml` provides a single command startup with healthchecks.

### 🔴 What Didn't Go Well / Pains Resolved
1. Host environment did not have local `node` installed, which was mitigated by providing Dockerized frontend build plus embedded FastAPI static serving.

---

## 4. Action Items for Sprint 4
- [ ] **Action 1:** Construct a 40-question ground-truth evaluation benchmark (`eval/data/ground_truth.json`).
- [ ] **Action 2:** Implement automated evaluation script measuring Hit Rate@k, MRR, and Groundedness across chunking/hybrid configurations.
- [ ] **Action 3:** Implement OpenTelemetry distributed tracing and Prometheus metrics `/metrics` with Grafana dashboard provisioning.
- [ ] **Action 4:** Finalize README with architecture diagrams and reproducible deployment guides.
