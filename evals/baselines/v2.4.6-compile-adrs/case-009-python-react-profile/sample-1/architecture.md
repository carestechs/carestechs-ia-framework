<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# System Architecture

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 System Summary

<!-- TODO: One paragraph describing what the system does and its primary architectural style — project-specific content. -->

### 1.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Web framework | FastAPI for all HTTP endpoints — async-native, dependency injection, auto OpenAPI docs, Pydantic validation | Industry standard for modern Python APIs: high performance, automatic docs, and native async in a single framework <!-- from: adrs/python/fastapi-framework.md --> |
| Architecture style | Modular monolith — single deployable composed of feature modules as Python packages with clear boundaries | Organizational benefits of microservices (bounded contexts, team ownership) without the operational complexity of distributed systems <!-- from: adrs/python/modular-packages.md --> |
| Business logic placement | Service layer owns all business logic; route handlers stay thin | Single, testable location for domain rules — services can be tested without spinning up the ASGI server <!-- from: adrs/python/service-layer-logic.md --> |
| API boundary schemas | Dedicated Pydantic schemas for all request/response payloads; SQLAlchemy models never exposed | Exposing ORM models couples the API contract to the database schema; schemas provide a stable, validated API surface <!-- from: adrs/python/pydantic-at-boundary.md --> |
| Concurrency model | async/await for all I/O, from route handlers through services to database calls, on an ASGI server (Uvicorn) | Synchronous I/O blocks the event loop in an ASGI application, degrading throughput under concurrent load <!-- from: adrs/python/async-all-the-way.md --> |
| ORM & migrations | SQLAlchemy 2.0 async (asyncpg driver) with Alembic handling all migrations | Mature, battle-tested ORM with first-class async support — the standard Python ORM for PostgreSQL <!-- from: adrs/python/sqlalchemy-async.md --> |
| Frontend component model | Functional React components with hooks only, organized by feature | Standard React pattern since 16.8 — simpler, more composable, better supported by the React team and ecosystem <!-- from: adrs/react/functional-components.md --> |
| Containerization | All components packaged as Docker images using multi-stage builds with slim final stages | Multi-stage builds produce significantly smaller production images — faster pulls, reduced attack surface, lower storage costs <!-- from: adrs/deployment/docker-multi-stage-builds.md --> |
| Configuration | All runtime config via environment variables; external services referenced by connection URLs; typed settings validated at startup | Connection URLs decouple the application from its infrastructure topology — a core tenet of twelve-factor app methodology <!-- from: adrs/deployment/env-connection-urls.md --> |
| Process topology | One process type per container (API, worker, frontend), reusing the same image with different command overrides | Independent scaling and restarts per process type, plus clearer resource monitoring <!-- from: adrs/deployment/container-per-process.md --> |
| Compose strategy | `docker-compose.yml` for local dev infrastructure only; `docker-compose.prod.yml` for application services on an external shared network | Clean boundary — dev Compose owns infrastructure lifecycle, prod Compose owns application lifecycle <!-- from: adrs/deployment/local-dev-compose.md --> |
| Primary keys | UUIDs, generated server-side or by the database; auto-increment integers never used | UUIDs enable distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Database naming | snake_case tables and columns; PascalCase properties translated automatically by the naming convention package | snake_case is the PostgreSQL idiomatic convention and avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Timestamp storage | `timestamptz` for all datetime columns, values stored in UTC | `timestamptz` stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Deletion strategy | Soft deletes via nullable `deleted_at` column; application code never hard-deletes | Soft deletes preserve audit trails and allow recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |
| API response format | Standard `{ data, meta }` envelope on all responses | A uniform envelope means the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Authentication | JWT Bearer tokens — short-lived access tokens plus long-lived, rotated refresh tokens | Stateless tokens let the API validate requests without a session store <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination | Offset-based with `page`/`pageSize` query parameters and `sortBy`/`sortDir` sorting | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

---

## 2. Technology Stack

### 2.1 Frontend

<!-- TODO: Frontend technology table with versions — project-specific content. -->

### 2.2 Backend

<!-- TODO: Backend technology table with versions — project-specific content. -->

### 2.3 Data Storage

<!-- TODO: Data storage table — project-specific content. -->

### 2.4 Infrastructure

<!-- TODO: Infrastructure table — project-specific content. -->

---

## 3. Component Architecture

### 3.1 High-Level Component Diagram

<!-- TODO: Component diagram — project-specific content. -->

### 3.2 Component Descriptions

<!-- TODO: One block per component/service with purpose, responsibilities, dependencies, and data owned — project-specific content. -->

---

## 4. Data Flow

<!-- TODO: Primary and secondary user flows — project-specific content. -->

---

## 5. Integration Points

### 5.1 External Services

<!-- TODO: External service table with protocol, auth, and failure strategy — project-specific content. -->

### 5.2 Internal Communication

<!-- TODO: Internal communication table — project-specific content. -->

---

## 6. Security & Observability

### 6.1 Authentication

<!-- TODO: Method, token storage, and refresh strategy — project-specific content; compiled auth decisions live in docs/api-spec/index.md. -->

### 6.2 Authorization

<!-- TODO: Authorization model, enforcement point, and roles — project-specific content. -->

### 6.3 Data Protection

<!-- TODO: Data protection table — project-specific content. -->

### 6.4 Observability

<!-- TODO: Logging, metrics, tracing, and alerting rows — project-specific content. -->

---

## 7. Scalability Considerations

### 7.1 Current Capacity

<!-- TODO: Expected users, requests/second, and data volume — project-specific content. -->

### 7.2 Scaling Strategy

<!-- TODO: Scaling table — project-specific content. -->

---

## 8. Development & Deployment

### 8.1 Repository Structure

<!-- TODO: Repository directory tree — project-specific content. -->

### 8.2 Environment Strategy

<!-- TODO: Environment table — project-specific content. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: Copy from the architecture.md template — static framework content, not derived from ADRs. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version — Key Architectural Decisions compiled from 18 ADRs | — |
