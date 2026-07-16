<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# System Architecture

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 System Summary

<!-- TODO: One paragraph describing what the system does and its primary architectural style. -->

### 1.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Web framework | FastAPI for all HTTP endpoints — async-native handling, auto OpenAPI docs, dependency injection, Pydantic validation | Industry standard for modern Python APIs: high performance, automatic docs, and native async in one framework <!-- from: adrs/python/fastapi-framework.md --> |
| Architecture style | Modular monolith — single deployable composed of feature modules as Python packages with clear boundaries | Organizational benefits of microservices (bounded contexts, team ownership) without distributed-systems complexity <!-- from: adrs/python/modular-packages.md --> |
| Business logic placement | All business logic in service classes/functions in each module's `service.py`; route handlers stay thin | Centralizing logic in the service layer gives a single, testable location for domain rules, separated from HTTP concerns <!-- from: adrs/python/service-layer-logic.md --> |
| API boundary schemas | Dedicated Pydantic schemas for all request/response payloads; SQLAlchemy models never exposed directly | Exposing ORM models couples the API contract to the database schema; Pydantic provides a stable, validated API surface <!-- from: adrs/python/pydantic-at-boundary.md --> |
| Concurrency model | `async`/`await` for all I/O from route handlers through services to database calls; ASGI server (Uvicorn) | Synchronous I/O blocks the event loop in an ASGI application, degrading throughput under concurrent load <!-- from: adrs/python/async-all-the-way.md --> |
| ORM & migrations | SQLAlchemy 2.0 with async engine/sessions; Alembic handles all database migrations | Mature, battle-tested ORM with first-class async support — the standard Python ORM for PostgreSQL <!-- from: adrs/python/sqlalchemy-async.md --> |
| Frontend component model | Functional React components with hooks only; feature-based folder organization | The standard React pattern since 16.8 — simpler, more composable, better supported by the React team and ecosystem <!-- from: adrs/react/functional-components.md --> |
| Packaging | All application components as Docker images with multi-stage builds; build tooling never in the final image | Multi-stage builds produce significantly smaller production images — faster pulls, reduced attack surface, lower storage costs <!-- from: adrs/deployment/docker-multi-stage-builds.md --> |
| Configuration | All runtime config via environment variables; external services referenced by connection URLs; typed settings validated at startup | Connection URLs decouple the application from its infrastructure topology — the same image runs everywhere, only the URL changes <!-- from: adrs/deployment/env-connection-urls.md --> |
| Process topology | One process type per container (API, worker, frontend); shared-runtime containers reuse the same image with command overrides | Separate containers enable independent scaling, independent restarts, and clearer per-process resource monitoring <!-- from: adrs/deployment/container-per-process.md --> |
| Environment orchestration | `docker-compose.yml` for dev infrastructure only; `docker-compose.prod.yml` for app services on an external shared infra network | Separating dev and prod Compose enforces a clean boundary: dev owns infrastructure lifecycle, prod owns application lifecycle <!-- from: adrs/deployment/local-dev-compose.md --> |
| Primary keys | UUIDs for all primary keys, generated server-side or by the database; no auto-increment integers | UUIDs enable distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Database naming | snake_case tables and columns; PascalCase C# properties translated automatically by the naming convention package | snake_case is the PostgreSQL idiomatic convention and avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Datetime storage | All datetime columns use `timestamptz` (`DateTimeOffset` in C#); all values stored in UTC | `timestamptz` stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Deletion strategy | Soft deletion via nullable `deleted_at` (`timestamptz`) column; application code never hard-deletes | Soft deletes preserve audit trails and allow recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |
| API response format | Standard `{ data, meta }` envelope for all API responses | A uniform envelope means the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Authentication | JWT Bearer tokens via the Authorization header; short-lived access tokens, long-lived rotated refresh tokens | JWT Bearer tokens are stateless and allow the API to validate requests without a session store <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination | Offset-based pagination with `page`/`pageSize` parameters; sorting via `sortBy`/`sortDir` | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

---

## 2. Technology Stack

### 2.1 Frontend

<!-- TODO: frontend technology table (framework, state management, styling, build tool with versions). -->

### 2.2 Backend

<!-- TODO: backend technology table (runtime, framework, ORM/DB client, validation with versions). -->

### 2.3 Data Storage

<!-- TODO: data storage table (primary DB, cache, file storage, search). -->

### 2.4 Infrastructure

<!-- TODO: infrastructure table (hosting, CDN, DNS, secrets). -->

---

## 3. Component Architecture

### 3.1 High-Level Component Diagram

<!-- TODO: component diagram. -->

### 3.2 Component Descriptions

<!-- TODO: one block per component/service (purpose, responsibilities, dependencies, data owned). -->

---

## 4. Data Flow

<!-- TODO: primary and secondary user flows. -->

---

## 5. Integration Points

### 5.1 External Services

<!-- TODO: external services table (purpose, protocol, auth method, failure strategy). -->

### 5.2 Internal Communication

<!-- TODO: internal communication table. -->

---

## 6. Security & Observability

### 6.1 Authentication

<!-- TODO: authentication method, token storage, refresh strategy. -->

### 6.2 Authorization

<!-- TODO: authorization model, enforcement point, roles. -->

### 6.3 Data Protection

<!-- TODO: data protection table. -->

### 6.4 Observability

<!-- TODO: logging, metrics, tracing, alerting table. -->

---

## 7. Scalability Considerations

### 7.1 Current Capacity

<!-- TODO: expected concurrent users, requests/second, data volume. -->

### 7.2 Scaling Strategy

<!-- TODO: scaling strategy table. -->

---

## 8. Development & Deployment

### 8.1 Repository Structure

<!-- TODO: repository directory tree. -->

### 8.2 Environment Strategy

<!-- TODO: environment strategy table. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: static template content — copy verbatim from the architecture.md template. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version (compiled from ADRs) | — |
