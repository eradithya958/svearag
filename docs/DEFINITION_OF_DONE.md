# Definition of Done (DoD)

To ensure high engineering quality and prevent technical debt, a User Story or Task is only considered **Done** when all the following criteria are met:

---

## 1. Code Quality & Standards
- [ ] Code follows standard style guides (enforced by `ruff` for Python / `eslint` & `prettier` for TypeScript/React).
- [ ] Code is well-structured, modular, and adheres to SOLID principles.
- [ ] No hardcoded configuration, secrets, or API keys (`.env` with validation via Pydantic Settings).
- [ ] Clean type annotations across all Python modules (`mypy` compliant) and TypeScript components.

## 2. Testing & Coverage
- [ ] Unit tests written for all new business logic (parsers, chunkers, retrieval scoring, prompt builders).
- [ ] Integration tests written for API endpoints using test fixtures and fake LLM / test vector DB.
- [ ] Zero live network calls or external API dependencies during test execution.
- [ ] Code coverage $\ge 85\%$ on new code with no reduction in overall project coverage.
- [ ] All tests pass locally and in the CI pipeline (`pytest` / `vitest`).

## 3. Architecture & Interfaces
- [ ] LLM, Vector Store, and Embedding providers adhere to abstract base interfaces (enabling zero-friction swapping).
- [ ] Clean error handling: standard HTTP status codes, structured JSON error payloads, no raw stack traces exposed to client.

## 4. Observability & Logging
- [ ] Structured JSON logging integrated with standard metadata (trace_id, request_id, timestamp, duration_ms).
- [ ] Prometheus metrics incremented/observed (latency histograms, counter metrics, error counters).
- [ ] No PII or raw user prompt sensitive content logged in plain text.

## 5. Documentation & Artifacts
- [ ] Public functions and classes documented with clear docstrings (inputs, outputs, exceptions).
- [ ] Any API changes reflected in OpenAPI docs (`/docs` endpoint).
- [ ] User story acceptance criteria verified and checked off.
- [ ] Pull request contains a clear description, summary of changes, and evidence of passing tests / metrics.
