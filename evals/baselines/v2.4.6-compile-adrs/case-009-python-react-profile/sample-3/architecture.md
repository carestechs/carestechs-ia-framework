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
| Web framework | FastAPI for all HTTP endpoints — async-native, auto OpenAPI docs, dependency injection, Pydantic validation | Industry standard for modern Python APIs: high performance, automatic docs, native async in one framework <!-- from: adrs/python/fastapi-framework.md --> |
| Architecture style | Modular monolith — single deployable composed of feature modules as Python packages with clear boundaries | Organizational benefits of microservices without the operational complexity of distributed systems <!-- from: adrs/python/modular-packages.md --> |
| Business logic placement | All business logic in service classes/functions per module; route handlers stay thin | Single, testable location for domain rules — services can be tested without spinning up the ASGI server <!-- from: adrs/python/service-layer-logic.md --> |
| API boundary schemas | Dedicated Pydantic schemas for all request/response payloads; ORM models never exposed | Exposing ORM models couples the API contract to the database schema, blocking independent evolution <!-- from: adrs/python/pydantic-at-boundary.md --> |
| Concurrency model | async/await for all I/O from route handlers through services to database calls; ASGI server (Uvicorn) | Synchronous I/O blocks the event loop in an ASGI application, degrading throughput under concurrent load <!-- from: adrs/python/async-all-the-way.md --> |
| ORM & migrations | SQLAlchemy 2.0 async (asyncpg driver) with Alembic migrations | Mature, battle-tested ORM with first-class async support — the standard Python ORM for PostgreSQL <!-- from: adrs/python/sqlalchemy-async.md --> |
| Frontend component model | Functional React components with hooks only; feature-based folder organization | Standard React pattern since 16.8 — simpler, more composable, best supported by the React team and ecosystem <!-- from: adrs/react/functional-components.md --> |
| Packaging | All components as Docker images with multi-stage builds; slim runtime final stages | Smaller production images — faster pulls, reduced attack surface, lower storage costs <!-- from: adrs/deployment/docker-multi-stage-builds.md --> |
| Configuration | All config via environment variables; external services via connection URLs; typed settings validated at startup | Connection URLs decouple the application from its infrastructure topology (twelve-factor) <!-- from: adrs/deployment/env-connection-urls.md --> |
| Process topology | One process type per container (API, worker, frontend); same image with different command overrides | Independent scaling, independent restarts, and clearer resource monitoring per process type <!-- from: adrs/deployment/container-per-process.md --> |
| Compose strategy | `docker-compose.yml` for dev infrastructure only; `docker-compose.prod.yml` for app services on an external shared network | Clean boundary: dev Compose owns infrastructure lifecycle, prod Compose owns application lifecycle <!-- from: adrs/deployment/local-dev-compose.md --> |
| Primary keys | UUIDs generated server-side or by the database; never auto-increment | Distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Database naming | snake_case tables and columns; code properties auto-translated by naming convention package | PostgreSQL idiomatic convention; avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Datetime storage | `timestamptz` columns, all values stored in UTC | Stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Deletion strategy | Soft deletes via nullable `deleted_at` column; application code never hard-deletes | Preserves audit trails and allows recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |
| API response format | Standard `{ data, meta }` envelope on all responses | Uniform envelope — the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Authentication | JWT Bearer tokens — short-lived access tokens, long-lived rotated refresh tokens | Stateless request validation without a session store <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination | Offset-based with `page`/`pageSize`; sorting via `sortBy`/`sortDir` | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

---

## 2. Technology Stack

### 2.1 Frontend

<!-- TODO: Add frontend technology table (framework, state management, styling, build tool with versions). -->

### 2.2 Backend

<!-- TODO: Add backend technology table (runtime, framework, ORM/DB client, validation with versions). -->

### 2.3 Data Storage

<!-- TODO: Add data storage table (primary DB, cache, file storage, search). -->

### 2.4 Infrastructure

<!-- TODO: Add infrastructure table (hosting, CDN, DNS, secrets). -->

---

## 3. Component Architecture

### 3.1 High-Level Component Diagram

<!-- TODO: Add component diagram. -->

### 3.2 Component Descriptions

<!-- TODO: Add per-component purpose, responsibilities, dependencies, and data owned. -->

---

## 4. Data Flow

### 4.1 Primary User Flow

<!-- TODO: Add primary user flow diagram and step-by-step description. -->

### 4.2 Secondary Flows

<!-- TODO: Add other significant flows. -->

---

## 5. Integration Points

### 5.1 External Services

<!-- TODO: Add external services table (purpose, protocol, auth method, failure strategy). -->

### 5.2 Internal Communication

<!-- TODO: Add internal communication table (from, to, protocol, pattern). -->

---

## 6. Security & Observability

### 6.1 Authentication

<!-- TODO: Add authentication method, token storage, and refresh strategy (see docs/api-spec/index.md for the ADR-derived auth conventions). -->

### 6.2 Authorization

<!-- TODO: Add authorization model, enforcement point, and defined roles. -->

### 6.3 Data Protection

<!-- TODO: Add data protection table (at rest, in transit, access control). -->

### 6.4 Observability

<!-- TODO: Add observability table (logging, metrics, tracing, alerting). -->

---

## 7. Scalability Considerations

### 7.1 Current Capacity

<!-- TODO: Add expected concurrent users, requests/second, and data volume. -->

### 7.2 Scaling Strategy

<!-- TODO: Add scaling strategy table per component. -->

---

## 8. Development & Deployment

### 8.1 Repository Structure

<!-- TODO: Add repository structure. -->

### 8.2 Environment Strategy

<!-- TODO: Add environment strategy table (local, dev/staging, production). -->

---

## Usage Notes for AI Task Generation

<!-- TODO: Framework boilerplate from the architecture.md template — copy when assembling the project ARCHITECTURE.md. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version compiled from ADRs | — |
