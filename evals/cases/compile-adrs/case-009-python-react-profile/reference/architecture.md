<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->
<!-- Compiled ARCHITECTURE.md sections — python-react-modular-monolith-docker-compose profile, via prompts/compile-adrs.md.
     Paste into docs/ARCHITECTURE.md and fill the TODO scaffolds with project-specific content. -->

## 1. Overview

### 1.1 System Summary

<!-- TODO: One paragraph describing what the system does and its primary architectural style — project-specific. -->

### 1.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Web framework | FastAPI for all HTTP endpoints — async-native, auto OpenAPI docs, DI, Pydantic validation | Industry standard for modern Python APIs: high performance, auto docs, native async in one framework <!-- from: adrs/python/fastapi-framework.md --> |
| Architecture style | Modular monolith — single deployable of feature modules as Python packages with clear boundaries | Organizational benefits of microservices without the operational complexity of distributed systems <!-- from: adrs/python/modular-packages.md --> |
| Business logic placement | All business logic in each module's service layer; route handlers stay thin | Single, testable location for domain rules — HTTP concerns and business concerns separated <!-- from: adrs/python/service-layer-logic.md --> |
| API boundary schemas | Dedicated Pydantic schemas for all request/response payloads; ORM models never exposed | Exposing ORM models couples the API contract to the database schema — Pydantic keeps both evolving independently <!-- from: adrs/python/pydantic-at-boundary.md --> |
| Concurrency model | `async`/`await` for all I/O from routes through services to the database; ASGI server (Uvicorn) | Synchronous I/O blocks the event loop and degrades throughput under concurrent load <!-- from: adrs/python/async-all-the-way.md --> |
| ORM & migrations | SQLAlchemy 2.0 async engine/sessions with Alembic migrations; asyncpg driver | Mature, battle-tested ORM with first-class async support — the standard Python ORM for PostgreSQL <!-- from: adrs/python/sqlalchemy-async.md --> |
| React component model | Functional components with hooks only; feature-based folder organization | Standard React pattern since 16.8 — simpler, more composable, better ecosystem support <!-- from: adrs/react/functional-components.md --> |
| Packaging | All components shipped as Docker images built with multi-stage builds | Multi-stage builds discard build tooling — smaller images, faster pulls, reduced attack surface <!-- from: adrs/deployment/docker-multi-stage-builds.md --> |
| Configuration | All runtime config via environment variables; external services by connection URL; typed settings validated at startup | Connection URLs decouple the application from its infrastructure topology (twelve-factor) <!-- from: adrs/deployment/env-connection-urls.md --> |
| Process topology | One process type per container (API, worker, frontend); shared-runtime containers reuse one image with command overrides | Independent scaling and restarts per process type, clearer per-process monitoring <!-- from: adrs/deployment/container-per-process.md --> |
| Compose layout | `docker-compose.yml` = dev infrastructure only; `docker-compose.prod.yml` = app services on an external shared network | Clean boundary: dev Compose owns infrastructure lifecycle, prod Compose owns application lifecycle <!-- from: adrs/deployment/local-dev-compose.md --> |
| Primary keys | UUIDs for all primary keys, generated server-side or by the database; never auto-increment | Distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Database naming | snake_case tables and columns; PascalCase entity properties translated automatically | snake_case is the PostgreSQL idiomatic convention and avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Datetime storage | `timestamptz` for all datetime columns; all values stored in UTC | `timestamptz` stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Deletion strategy | Soft deletion via nullable `deleted_at` column; application code never hard-deletes | Soft deletes preserve audit trails and allow recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |
| API response format | Standard `{ data, meta }` envelope on all responses | Uniform envelope — the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Authentication | JWT Bearer tokens via the `Authorization` header; short-lived access + rotated refresh tokens | Stateless token validation — no session store required per request <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination | Offset-based with `page`/`pageSize` query parameters and `sortBy`/`sortDir` sorting | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

---

## 2. Technology Stack

<!-- TODO: Frontend/Backend/Data Storage/Infrastructure tables with versions — project-specific. -->

## 3. Component Architecture

<!-- TODO: High-level component diagram and component descriptions — project-specific. -->

## 4. Data Flow

<!-- TODO: Primary user flows — project-specific. -->

## 5. Integration Points

<!-- TODO: External services and internal communication tables — project-specific. -->

## 6. Security & Observability

<!-- TODO: Authentication/authorization details, data protection, observability tooling — project-specific. -->

## 7. Scalability Considerations

<!-- TODO: Capacity and scaling strategy — project-specific. -->

## 8. Development & Deployment

<!-- TODO: Repository structure and environment strategy — project-specific. -->
