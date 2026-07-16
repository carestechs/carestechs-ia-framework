<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# CLAUDE.md

> This file provides guidance to Claude Code (or any AI assistant) when working with this codebase.

<!-- TODO: Pre-Work Checklist and AI-Assisted Development Framework sections are static template content — copy verbatim from the claude-md.md template. -->

---

## Project Overview

<!-- TODO: 1-2 sentences describing what this project does and its primary purpose. -->

**Tech Stack**: <!-- TODO: primary technologies -->

**Repository Type**: <!-- TODO: Monorepo / Single application / Library / etc. -->

---

## Quick Reference

### Common Commands

<!-- TODO: development, testing, building, linting/formatting, and database commands. -->

### Key Directories

<!-- TODO: directory tree with the purpose of each directory. -->

---

## Code Style & Conventions

### General Principles

<!-- TODO: project-wide coding principles. -->

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Database tables | snake_case | `order_items` <!-- from: adrs/database/snake-case-naming.md --> |
| Database columns | snake_case | `created_at`, `user_id` <!-- from: adrs/database/snake-case-naming.md --> |
| C# entity properties | PascalCase (the EF Core naming convention package translates to snake_case) | `CreatedAt`, `UserId` <!-- from: adrs/database/snake-case-naming.md --> |
| Raw SQL identifiers | snake_case | `created_at`, `user_id` <!-- from: adrs/database/snake-case-naming.md --> |
| Soft-delete column | Nullable `deleted_at` of type `timestamptz` | `deleted_at TIMESTAMPTZ NULL` <!-- from: adrs/database/soft-deletes.md --> |
| Feature module packages | Python package under `src/app/modules/<module_name>/` | `src/app/modules/catalog/` <!-- from: adrs/python/modular-packages.md --> |
| Module files | Fixed file names per module: `router.py`, `service.py`, `models.py`, `schemas.py`, `dependencies.py` | `src/app/modules/catalog/router.py` <!-- from: adrs/python/modular-packages.md --> |
| Request/response schema classes | Separate classes for input and output | `CreateProductRequest`, `ProductResponse` <!-- from: adrs/python/pydantic-at-boundary.md --> |
| Custom hooks (React) | Prefixed with `use`, in a `hooks/` directory | `useCatalog` <!-- from: adrs/react/functional-components.md --> |
| Response wrapper classes | `ApiResponse<T>` for single items, `ApiListResponse<T>` for lists | `ApiResponse<T>` <!-- from: adrs/api/rest-envelope.md --> |
| Pagination/sorting query parameters | Exact names: `page`, `pageSize`, `sortBy`, `sortDir` | `?page=1&pageSize=20&sortBy=created_at&sortDir=asc` <!-- from: adrs/api/offset-pagination.md --> |

### File Organization

<!-- TODO: component and service/utility file internal structure. -->

---

## Patterns & Anti-Patterns

### Patterns to Follow

- **FastAPI routes:** All HTTP endpoints MUST be defined as FastAPI route functions using `@router.get()`, `@router.post()`, etc. <!-- from: adrs/python/fastapi-framework.md -->
- **APIRouter always:** Always use `APIRouter` — every router MUST be organized in its own module file and included via `app.include_router()` <!-- from: adrs/python/fastapi-framework.md -->
- **Pydantic at the boundary:** Every endpoint MUST use Pydantic schemas for request body validation and response serialization <!-- from: adrs/python/fastapi-framework.md --> <!-- from: adrs/python/pydantic-at-boundary.md -->
- **Dependency injection:** Services, database sessions, and auth dependencies MUST be injected into route functions via FastAPI's `Depends()` <!-- from: adrs/python/fastapi-framework.md --> <!-- from: adrs/python/service-layer-logic.md -->
- **Async route handlers:** Route functions MUST be `async def` for any endpoint that performs I/O <!-- from: adrs/python/fastapi-framework.md --> <!-- from: adrs/python/async-all-the-way.md -->
- **OpenAPI docs in dev:** The OpenAPI docs MUST remain enabled in development (production may disable them via configuration) <!-- from: adrs/python/fastapi-framework.md -->
- **Module packages:** Every feature module MUST be its own Python package under `src/app/modules/<module_name>/` <!-- from: adrs/python/modular-packages.md -->
- **Module contents:** A module MUST contain: `router.py` (API routes), `service.py` (business logic), `models.py` (SQLAlchemy entities), `schemas.py` (Pydantic DTOs), and `dependencies.py` (FastAPI dependencies) <!-- from: adrs/python/modular-packages.md -->
- **Cross-module contracts:** Cross-module communication goes through interfaces defined in a shared `src/app/contracts/` package <!-- from: adrs/python/modular-packages.md -->
- **Single registration point:** The application entrypoint (`src/app/main.py`) is the only place that imports and registers module routers <!-- from: adrs/python/modular-packages.md -->
- **Router exposure:** Each module MUST expose a `create_router()` function or a router instance for registration in the main app <!-- from: adrs/python/modular-packages.md -->
- **Thin route handlers:** Route handlers MUST only: extract/validate the request (Pydantic handles this), call one or more service functions, and return an HTTP response <!-- from: adrs/python/service-layer-logic.md -->
- **Service-layer logic:** All business rules, validations beyond input format, orchestration, and data transformation MUST live in service functions or classes <!-- from: adrs/python/service-layer-logic.md -->
- **Async services:** Service functions that perform I/O MUST be `async def` <!-- from: adrs/python/service-layer-logic.md --> <!-- from: adrs/python/async-all-the-way.md -->
- **Separate request/response schemas:** Request schemas and response schemas MUST be separate classes (e.g., `CreateProductRequest`, `ProductResponse`) <!-- from: adrs/python/pydantic-at-boundary.md -->
- **Schemas in schemas.py:** Each module MUST define its schemas in `schemas.py` within the module package <!-- from: adrs/python/pydantic-at-boundary.md -->
- **from_attributes for ORM mapping:** Schemas MUST use `model_config = ConfigDict(from_attributes=True)` when they need to be constructed from ORM model instances <!-- from: adrs/python/pydantic-at-boundary.md -->
- **ORM-to-schema mapping in services:** Mapping from ORM models to Pydantic schemas MUST happen in the service layer, not in route handlers <!-- from: adrs/python/pydantic-at-boundary.md -->
- **Async database access:** All SQLAlchemy database operations MUST use `AsyncSession` instances (created from `async_sessionmaker`) with awaited async methods: `await session.execute()`, `await session.commit()`, `await session.refresh()`, etc. <!-- from: adrs/python/async-all-the-way.md --> <!-- from: adrs/python/sqlalchemy-async.md -->
- **ASGI server:** The application MUST run on an ASGI server (Uvicorn or Hypercorn) <!-- from: adrs/python/async-all-the-way.md -->
- **SQLAlchemy 2.0 style:** All SQLAlchemy models MUST use the 2.0 declarative style with `mapped_column()` and type annotations <!-- from: adrs/python/sqlalchemy-async.md -->
- **Shared declarative Base:** All models MUST inherit from a shared `Base` class (declarative base) importable by all modules; models live in each module's `models.py` <!-- from: adrs/python/sqlalchemy-async.md -->
- **Session dependency:** Sessions MUST be injected into services via FastAPI `Depends()`, using a dependency that yields a session and handles commit/rollback <!-- from: adrs/python/sqlalchemy-async.md -->
- **Alembic migrations:** Migrations MUST be managed by Alembic <!-- from: adrs/python/sqlalchemy-async.md -->
- **asyncpg engine:** The database engine MUST use `create_async_engine` with the `asyncpg` driver (connection string: `postgresql+asyncpg://...`) <!-- from: adrs/python/sqlalchemy-async.md -->
- **Functional components:** All components MUST be functional components (`function ComponentName()` or `const ComponentName = () =>`) <!-- from: adrs/react/functional-components.md -->
- **Hook-based state:** State MUST be managed with `useState` or `useReducer` <!-- from: adrs/react/functional-components.md -->
- **useEffect for side effects:** Side effects MUST use `useEffect` <!-- from: adrs/react/functional-components.md -->
- **Feature folders:** Feature components MUST live in `src/features/<feature>/` directories <!-- from: adrs/react/functional-components.md -->
- **Shared components location:** Shared reusable components MUST live in `src/components/` (or `src/shared/`) <!-- from: adrs/react/functional-components.md -->
- **Named exports:** Components MUST be exported as named exports (default exports are reserved for route-level page components only) <!-- from: adrs/react/functional-components.md -->
- **Custom hook naming:** Custom hooks MUST be prefixed with `use` and live in a `hooks/` directory within their feature or in a shared `src/hooks/` directory <!-- from: adrs/react/functional-components.md -->
- **UUID primary keys:** All PK columns use `uuid` type in PostgreSQL and `Guid` in C# <!-- from: adrs/database/uuid-primary-keys.md -->
- **Server-side ID generation:** Generate IDs server-side with `Guid.NewGuid()` or use database default `gen_random_uuid()` <!-- from: adrs/database/uuid-primary-keys.md -->
- **UUID foreign keys:** Foreign keys referencing PKs must also be `uuid`/`Guid` <!-- from: adrs/database/uuid-primary-keys.md -->
- **ValueGeneratedOnAdd for DB defaults:** EF Core entity configurations must specify `.ValueGeneratedOnAdd()` for UUID PKs when using database defaults <!-- from: adrs/database/uuid-primary-keys.md -->
- **Snake-case naming convention:** Configure `UseSnakeCaseNamingConvention()` on the DbContext (via Npgsql EF Core package) <!-- from: adrs/database/snake-case-naming.md -->
- **PascalCase entity properties:** C# entity properties use PascalCase as normal (e.g., `CreatedAt`, `UserId`) <!-- from: adrs/database/snake-case-naming.md -->
- **snake_case in raw SQL:** Raw SQL queries must use snake_case identifiers (e.g., `created_at`, `user_id`) <!-- from: adrs/database/snake-case-naming.md -->
- **snake_case migrations expected:** Migration files will reflect snake_case names — this is expected and correct <!-- from: adrs/database/snake-case-naming.md -->
- **timestamptz columns:** All datetime columns in migrations must use `timestamptz` <!-- from: adrs/database/timestamptz-always.md -->
- **DateTimeOffset properties:** C# properties must use `DateTimeOffset` <!-- from: adrs/database/timestamptz-always.md -->
- **UTC always:** All values stored must be in UTC — always use `DateTimeOffset.UtcNow` <!-- from: adrs/database/timestamptz-always.md -->
- **Frontend-only timezone conversion:** Timezone conversion to local display time is a frontend-only concern <!-- from: adrs/database/timestamptz-always.md -->
- **Explicit timestamptz config:** EF Core column type should be explicitly configured as `timestamptz` if not inferred <!-- from: adrs/database/timestamptz-always.md -->
- **Soft-delete property:** Add a nullable `DateTimeOffset? DeletedAt` property to all soft-deletable entities, mapping to a `deleted_at` column of type `timestamptz` <!-- from: adrs/database/soft-deletes.md -->
- **Global query filters:** Configure EF Core global query filters: `.HasQueryFilter(e => e.DeletedAt == null)` <!-- from: adrs/database/soft-deletes.md -->
- **Soft-delete by timestamp:** To soft-delete, set `DeletedAt = DateTimeOffset.UtcNow` <!-- from: adrs/database/soft-deletes.md -->
- **Explicit inclusion of deleted records:** To query including soft-deleted records, use `.IgnoreQueryFilters()` explicitly <!-- from: adrs/database/soft-deletes.md -->
- **Response envelope:** Single item responses: `{ "data": { ... } }`; list responses: `{ "data": [ ... ], "meta": { ... } }` <!-- from: adrs/api/rest-envelope.md -->
- **Envelope wrapper classes:** Create generic response wrapper classes: `ApiResponse<T>` for single items, `ApiListResponse<T>` for lists <!-- from: adrs/api/rest-envelope.md -->
- **Always wrap responses:** Controllers must always wrap return values in the envelope <!-- from: adrs/api/rest-envelope.md -->
- **Pagination metadata:** List response `meta` must include `totalCount`, `page`, `pageSize` <!-- from: adrs/api/rest-envelope.md --> <!-- from: adrs/api/offset-pagination.md -->
- **Bearer tokens:** Tokens are sent in the `Authorization: Bearer <token>` header on every authenticated request <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Token claims:** Access tokens contain claims: user ID (`sub`), role(s), issued-at, expiration <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Short-lived access tokens:** Access token lifetime is 15-60 minutes (configurable) <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Refresh token rotation:** Refresh tokens are long-lived, stored securely (httpOnly cookie or secure storage), and rotated on every use <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Full token validation:** Token validation must check signature, expiration, issuer, and audience <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Authorize attributes:** Protect endpoints with `[Authorize]`; role-based access with `[Authorize(Roles = "...")]` <!-- from: adrs/api/jwt-bearer-auth.md -->
- **1-based pages:** The `page` parameter is 1-based (first page is `page=1`) <!-- from: adrs/api/offset-pagination.md -->
- **Page size limits:** `pageSize` defaults to 20 if not provided; maximum is 100 — reject requests exceeding this with a 400 error <!-- from: adrs/api/offset-pagination.md -->
- **Sorting parameters:** Sorting uses `sortBy` (column name) and `sortDir` (`asc` or `desc`, default `asc`) <!-- from: adrs/api/offset-pagination.md -->
- **sortBy allowlist:** Validate `sortBy` against an allowlist of sortable columns <!-- from: adrs/api/offset-pagination.md -->
- **Shared PaginationParams:** Create a shared `PaginationParams` class for binding query parameters <!-- from: adrs/api/offset-pagination.md -->
- **Skip/Take pagination:** Use `.Skip((page - 1) * pageSize).Take(pageSize)` for EF Core queries <!-- from: adrs/api/offset-pagination.md -->
- **Dockerfile per component:** Every deployable component (backend, frontend, worker) MUST have its own Dockerfile <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **Multi-stage builds:** All Dockerfiles MUST use multi-stage builds: a build stage for installing/compiling and a final stage with only the runtime base and production artifacts <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **Slim final stages:** Backend Dockerfiles MUST use a slim or alpine base image for the final stage (e.g., `python:3.12-slim`) <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **nginx frontend images:** Frontend Dockerfiles MUST use a Node image for the build stage and an `nginx:alpine` image for the final stage, copying the build output (e.g., `dist/`) to nginx's serving directory <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **.dockerignore required:** A `.dockerignore` file MUST exist at the build context root, excluding at minimum: `.venv`, `node_modules`, `.git`, `__pycache__`, `.env`, `tests/`, `docs/`, and IDE configuration files <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **Env-var configuration:** All runtime configuration MUST be read from environment variables <!-- from: adrs/deployment/env-connection-urls.md -->
- **Connection URLs:** External service connections (database, Redis, LLM providers, search APIs) MUST be configured via URL-style environment variables (e.g., `DATABASE_URL`, `REDIS_URL`) <!-- from: adrs/deployment/env-connection-urls.md -->
- **Typed settings singleton:** The project MUST include a typed settings/configuration class (e.g., Pydantic `BaseSettings`) that loads and validates all environment variables at application startup, loaded once as a singleton <!-- from: adrs/deployment/env-connection-urls.md -->
- **.env examples:** The repository MUST contain `.env.example` with all required variables documented with placeholder values; a `.env.production.example` SHOULD exist showing production-specific variable expectations <!-- from: adrs/deployment/env-connection-urls.md -->
- **Fail fast on missing secrets:** The application MUST fail to start if required secrets are missing <!-- from: adrs/deployment/env-connection-urls.md -->
- **Container per process type:** The API server, background workers, and frontend MUST run as separate containers <!-- from: adrs/deployment/container-per-process.md -->
- **Shared image, different command:** Containers sharing the same codebase (e.g., API and worker) MUST use the same Docker image with different `command` overrides in the Compose file <!-- from: adrs/deployment/container-per-process.md -->
- **Health checks everywhere:** Every container MUST define a `healthcheck` in the Compose file or orchestrator manifest; dev-Compose infrastructure services included, so application processes can wait for readiness <!-- from: adrs/deployment/container-per-process.md --> <!-- from: adrs/deployment/local-dev-compose.md -->
- **HTTP health endpoints:** API containers MUST use an HTTP health endpoint (e.g., `GET /health`) for their health check <!-- from: adrs/deployment/container-per-process.md -->
- **Native infra health checks:** Database and cache containers MUST use native CLI health checks (e.g., `pg_isready`, `redis-cli ping`) <!-- from: adrs/deployment/container-per-process.md -->
- **restart: unless-stopped:** All containers MUST set `restart: unless-stopped` (Compose) or equivalent restart policy <!-- from: adrs/deployment/container-per-process.md -->
- **Explicit worker concurrency:** Worker containers MUST set concurrency explicitly via command-line flags (e.g., `celery worker -c 4`) <!-- from: adrs/deployment/container-per-process.md -->
- **Dev Compose is infra only:** `docker-compose.yml` MUST contain only infrastructure services (database, Redis, message brokers) <!-- from: adrs/deployment/local-dev-compose.md -->
- **Prod Compose is app only:** `docker-compose.prod.yml` MUST contain only application services <!-- from: adrs/deployment/local-dev-compose.md -->
- **External infra network:** Production Compose MUST declare an external network for infrastructure connectivity; application services connect to databases and caches through this shared network using Docker DNS names <!-- from: adrs/deployment/local-dev-compose.md -->
- **Host-exposed dev ports:** Dev infrastructure services MUST expose ports to the host (e.g., `5432:5432`, `6379:6379`) so developers can run application processes directly on the host <!-- from: adrs/deployment/local-dev-compose.md -->
- **Env-loaded prod Compose:** The prod Compose MUST load environment variables from a `.env` file or receive them from the orchestrator <!-- from: adrs/deployment/local-dev-compose.md -->
- **Named volumes for data:** Infrastructure data MUST use named Docker volumes for persistence across container restarts in dev <!-- from: adrs/deployment/local-dev-compose.md -->

### Anti-Patterns to Avoid

- **No routes on the app instance:** NEVER define routes directly on the main `FastAPI()` app instance — always use `APIRouter` <!-- from: adrs/python/fastapi-framework.md -->
- **No direct cross-module imports:** Modules MUST NOT import models or services from other module packages directly <!-- from: adrs/python/modular-packages.md -->
- **No circular module dependencies:** No circular dependencies between modules — if two modules need each other, extract the shared concept into the contracts package <!-- from: adrs/python/modular-packages.md -->
- **No logic in route handlers:** NEVER place business logic in route handlers — route handlers are thin wrappers only <!-- from: adrs/python/service-layer-logic.md -->
- **No raw queries in routes:** NEVER perform raw database queries in route handlers — all data access goes through services <!-- from: adrs/python/service-layer-logic.md -->
- **No ORM models in responses:** NEVER return SQLAlchemy model instances directly from route handlers or services that feed into responses <!-- from: adrs/python/pydantic-at-boundary.md -->
- **No shared input/output schemas:** NEVER reuse the same schema for input and output <!-- from: adrs/python/pydantic-at-boundary.md -->
- **No sync sessions in async paths:** NEVER use synchronous SQLAlchemy sessions (`Session`) in async code paths <!-- from: adrs/python/async-all-the-way.md -->
- **No blocking I/O in async functions:** NEVER call blocking I/O (synchronous HTTP requests, file reads, `time.sleep()`) directly in async functions — use `asyncio.to_thread()` if wrapping unavoidable sync libraries <!-- from: adrs/python/async-all-the-way.md -->
- **No WSGI server:** NEVER use a WSGI server — the application runs on ASGI (Uvicorn or Hypercorn) <!-- from: adrs/python/async-all-the-way.md -->
- **No asyncio.run() in handlers:** NEVER use `asyncio.run()` inside route handlers or services — the event loop is already running <!-- from: adrs/python/async-all-the-way.md -->
- **No out-of-band schema changes:** NEVER modify database schema outside of Alembic migrations <!-- from: adrs/python/sqlalchemy-async.md -->
- **No class components:** NEVER use class components <!-- from: adrs/react/functional-components.md -->
- **No this.state:** NEVER use `this.state` or `this.setState` <!-- from: adrs/react/functional-components.md -->
- **No lifecycle methods:** NEVER use lifecycle methods (`componentDidMount`, etc.) — side effects use `useEffect` <!-- from: adrs/react/functional-components.md -->
- **No integer primary keys:** Never define a primary key as `int`, `long`, or `serial` <!-- from: adrs/database/uuid-primary-keys.md -->
- **No manual column mapping:** Never manually specify `[Column("...")]` or `[Table("...")]` attributes for snake_case translation — the convention handles it <!-- from: adrs/database/snake-case-naming.md -->
- **No timestamp without timezone:** Never use `timestamp` (without time zone) for datetime columns — always `timestamptz` <!-- from: adrs/database/timestamptz-always.md -->
- **No DateTime.Now:** Never call `DateTime.Now` and never use `DateTime` properties — always `DateTimeOffset` with `DateTimeOffset.UtcNow` <!-- from: adrs/database/timestamptz-always.md -->
- **No hard deletes from app code:** To delete, never call `Remove()` or `DELETE` — hard deletes (`DELETE FROM`) are only permitted in background data compaction/cleanup jobs, never from application code <!-- from: adrs/database/soft-deletes.md -->
- **No raw top-level responses:** Never return a raw array or raw object at the top level — always use the envelope <!-- from: adrs/api/rest-envelope.md -->
- **No JWTs in localStorage:** Never store JWTs in localStorage — use httpOnly cookies or in-memory storage on the frontend <!-- from: adrs/api/jwt-bearer-auth.md -->
- **No raw ORDER BY input:** Never pass raw user input to ORDER BY — validate `sortBy` against an allowlist of sortable columns <!-- from: adrs/api/offset-pagination.md -->
- **No SDK images in final stage:** NEVER use full SDK or build images as the final stage <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **No dev dependencies in production images:** NEVER install dev dependencies in the final stage — use `--no-dev`, `--only=production`, or equivalent flags <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **No full source in final stage:** NEVER copy the entire source tree into the final stage if only a build artifact (e.g., compiled output, static files) is needed <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **No hardcoded config:** NEVER hardcode connection strings, API keys, or environment-specific values — not in source code and not in Compose files <!-- from: adrs/deployment/env-connection-urls.md --> <!-- from: adrs/deployment/local-dev-compose.md -->
- **No committed secrets:** NEVER commit a real `.env` file with actual secrets <!-- from: adrs/deployment/env-connection-urls.md -->
- **No default secret values:** API keys and secrets MUST NOT have default values in the settings class <!-- from: adrs/deployment/env-connection-urls.md -->
- **No scattered env reads:** NEVER re-read environment variables scattered across the codebase — the settings class is a singleton loaded once at startup <!-- from: adrs/deployment/env-connection-urls.md -->
- **No multi-process containers:** NEVER run multiple process types inside a single container <!-- from: adrs/deployment/container-per-process.md -->
- **No duplicate Dockerfiles per codebase:** NEVER maintain separate Dockerfiles for the same codebase — reuse the image with `command` overrides <!-- from: adrs/deployment/container-per-process.md -->
- **No restart: always:** NEVER use `restart: always` (prevents intentional stops) or omit the restart policy <!-- from: adrs/deployment/container-per-process.md -->
- **No default worker concurrency:** NEVER rely on library defaults for production concurrency — set it explicitly via command-line flags <!-- from: adrs/deployment/container-per-process.md -->
- **No app services in dev Compose:** NEVER define application services (API, worker, frontend) in the dev Compose file <!-- from: adrs/deployment/local-dev-compose.md -->
- **No infra services in prod Compose:** NEVER define database or cache services in the prod Compose file — these connect to shared infrastructure via environment variables <!-- from: adrs/deployment/local-dev-compose.md -->
- **No bind mounts for database data:** NEVER use bind mounts for database data directories — use named Docker volumes <!-- from: adrs/deployment/local-dev-compose.md -->

### Design Patterns

<!-- TODO: filled by DDR compilation (compile-ddrs.md), not ADR compilation. -->

---

## Error Handling

<!-- TODO: error handling strategy, standard error pattern, and error types table. -->

---

## Testing Conventions

<!-- TODO: test file locations, test structure, testing priorities, and what NOT to test. -->

---

## API Conventions (if applicable)

<!-- TODO: endpoint naming, request/response format, and validation approach — see the compiled docs/api-spec/index.md sections for ADR-derived API conventions. -->

---

## Database Conventions (if applicable)

<!-- TODO: naming, migration guidelines — see the compiled docs/data-model/index.md sections for ADR-derived database conventions. -->

---

## Environment & Configuration

<!-- TODO: environment variables table and configuration files table. -->

---

## Git Conventions

<!-- TODO: branch naming and commit message conventions. -->

---

## Performance Considerations

<!-- TODO: project-specific performance guidance. -->

---

## Security Checklist

<!-- TODO: project-specific security checklist items. -->

---

## Common Gotchas

<!-- TODO: things that often trip people up in this codebase. -->

---

## Related Documentation

<!-- TODO: links to architecture, API, deployment, and contributing docs. -->
