<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->
<!-- Compiled CLAUDE.md sections — python-react-modular-monolith-docker-compose profile, via prompts/compile-adrs.md.
     Paste into the project CLAUDE.md and fill the TODO scaffolds with project-specific content. -->

## Project Overview

<!-- TODO: 1-2 sentences describing the project, its tech stack summary, and repository type — project-specific. -->

## Quick Reference

### Common Commands

<!-- TODO: dev/test/build/lint/migration commands — project-specific. -->

### Key Directories

<!-- TODO: directory tree with purposes — project-specific. -->

## Code Style & Conventions

### General Principles

<!-- TODO: project-specific principles. -->

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Database tables | snake_case | `order_items` <!-- from: adrs/database/snake-case-naming.md --> |
| Database columns | snake_case | `created_at`, `user_id` <!-- from: adrs/database/snake-case-naming.md --> |
| Entity properties (C#) | PascalCase, auto-translated to snake_case via `UseSnakeCaseNamingConvention()` | `CreatedAt`, `UserId` <!-- from: adrs/database/snake-case-naming.md --> |
| Soft-delete column | nullable `deleted_at`, type `timestamptz` | `deleted_at TIMESTAMPTZ NULL` <!-- from: adrs/database/soft-deletes.md --> |
| Module package files | fixed per-module file set: `router.py`, `service.py`, `models.py`, `schemas.py`, `dependencies.py` | `src/app/modules/catalog/router.py` <!-- from: adrs/python/modular-packages.md --> |
| Custom hooks (React) | `use` prefix, in a `hooks/` directory | `useProjects` <!-- from: adrs/react/functional-components.md --> |
| Service-connection env vars | URL-style environment variables | `DATABASE_URL`, `REDIS_URL` <!-- from: adrs/deployment/env-connection-urls.md --> |
| Response wrapper classes | `ApiResponse<T>` (single item) / `ApiListResponse<T>` (list) | `ApiListResponse<ProductDto>` <!-- from: adrs/api/rest-envelope.md --> |

### File Organization

<!-- TODO: project-specific file structure conventions. -->

## Patterns & Anti-Patterns

### Patterns to Follow

- **Route definitions:** All HTTP endpoints MUST be defined as FastAPI route functions using `@router.get()`, `@router.post()`, etc. <!-- from: adrs/python/fastapi-framework.md -->
- **Use APIRouter:** Always define routes on an `APIRouter` instance <!-- from: adrs/python/fastapi-framework.md -->
- **Pydantic at the boundary:** Every endpoint MUST use Pydantic schemas for request body validation and response serialization <!-- from: adrs/python/fastapi-framework.md --> <!-- from: adrs/python/pydantic-at-boundary.md -->
- **Dependency injection:** Services, database sessions, and auth dependencies MUST be injected into route functions via FastAPI `Depends()` <!-- from: adrs/python/fastapi-framework.md --> <!-- from: adrs/python/service-layer-logic.md -->
- **Async routes:** Route functions MUST be `async def` for any endpoint that performs I/O <!-- from: adrs/python/fastapi-framework.md --> <!-- from: adrs/python/async-all-the-way.md -->
- **One router per module file:** Every router MUST be organized in its own module file and included via `app.include_router()` <!-- from: adrs/python/fastapi-framework.md -->
- **OpenAPI docs in development:** The OpenAPI docs MUST remain enabled in development (production may disable them via configuration) <!-- from: adrs/python/fastapi-framework.md -->
- **Module packages:** Every feature module MUST be its own Python package under `src/app/modules/<module_name>/` <!-- from: adrs/python/modular-packages.md -->
- **Standard module files:** A module MUST contain `router.py`, `service.py`, `models.py`, `schemas.py`, and `dependencies.py` <!-- from: adrs/python/modular-packages.md -->
- **Cross-module via contracts:** Cross-module communication goes through interfaces defined in the shared `src/app/contracts/` package <!-- from: adrs/python/modular-packages.md -->
- **Single registration point:** The application entrypoint (`src/app/main.py`) is the only place that imports and registers module routers <!-- from: adrs/python/modular-packages.md -->
- **Router exposure:** Each module MUST expose a `create_router()` function or a router instance for registration in the main app <!-- from: adrs/python/modular-packages.md -->
- **Thin route handlers:** Route handlers MUST only extract/validate the request, call one or more service functions, and return an HTTP response <!-- from: adrs/python/service-layer-logic.md -->
- **Business logic in services:** All business rules, validations beyond input format, orchestration, and data transformation MUST live in service functions or classes <!-- from: adrs/python/service-layer-logic.md -->
- **Async services:** Service functions that perform I/O MUST be `async def` <!-- from: adrs/python/service-layer-logic.md --> <!-- from: adrs/python/async-all-the-way.md -->
- **Schemas in schemas.py:** Each module MUST define its Pydantic schemas in `schemas.py` within the module package <!-- from: adrs/python/pydantic-at-boundary.md -->
- **Separate request/response schemas:** Request and response schemas MUST be separate classes (e.g., `CreateProductRequest`, `ProductResponse`) <!-- from: adrs/python/pydantic-at-boundary.md -->
- **from_attributes config:** Schemas constructed from ORM instances MUST use `model_config = ConfigDict(from_attributes=True)` <!-- from: adrs/python/pydantic-at-boundary.md -->
- **ORM-to-schema mapping in services:** Mapping from ORM models to Pydantic schemas MUST happen in the service layer, not in route handlers <!-- from: adrs/python/pydantic-at-boundary.md -->
- **Async DB operations:** All SQLAlchemy operations MUST use `AsyncSession` with awaited methods (`await session.execute()`, `await session.commit()`, `await session.refresh()`) <!-- from: adrs/python/async-all-the-way.md --> <!-- from: adrs/python/sqlalchemy-async.md -->
- **ASGI server:** The application MUST run on an ASGI server (Uvicorn or Hypercorn) <!-- from: adrs/python/async-all-the-way.md -->
- **SQLAlchemy 2.0 style:** All models MUST use the 2.0 declarative style with `mapped_column()` and type annotations <!-- from: adrs/python/sqlalchemy-async.md -->
- **Shared declarative Base:** All models MUST inherit from a shared `Base` importable by all modules; models live in each module's `models.py` <!-- from: adrs/python/sqlalchemy-async.md -->
- **Session factory dependency:** Sessions are `AsyncSession` instances created from `async_sessionmaker`, injected into services via a `Depends()` dependency that yields the session and handles commit/rollback <!-- from: adrs/python/sqlalchemy-async.md -->
- **Alembic migrations:** All database migrations MUST be managed by Alembic <!-- from: adrs/python/sqlalchemy-async.md -->
- **Async engine + asyncpg:** The database engine MUST use `create_async_engine` with the `asyncpg` driver (connection string `postgresql+asyncpg://...`) <!-- from: adrs/python/sqlalchemy-async.md -->
- **Functional components:** All components MUST be functional components (`function ComponentName()` or `const ComponentName = () =>`) <!-- from: adrs/react/functional-components.md -->
- **Hook-based state:** State MUST be managed with `useState` or `useReducer` <!-- from: adrs/react/functional-components.md -->
- **Effects via useEffect:** Side effects MUST use `useEffect` <!-- from: adrs/react/functional-components.md -->
- **Feature folders:** Feature components MUST live in `src/features/<feature>/`; shared reusable components in `src/components/` (or `src/shared/`) <!-- from: adrs/react/functional-components.md -->
- **Named exports:** Components MUST be exported as named exports — default exports are reserved for route-level page components only <!-- from: adrs/react/functional-components.md -->
- **Custom hook placement:** Custom hooks MUST be prefixed with `use` and live in a `hooks/` directory within their feature or in a shared `src/hooks/` directory <!-- from: adrs/react/functional-components.md -->
- **Dockerfile per component:** Every deployable component (backend, frontend, worker) MUST have its own Dockerfile <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **Multi-stage builds:** All Dockerfiles MUST use multi-stage builds — a build stage for installing/compiling and a final stage with only the runtime base and production artifacts <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **Slim final stages:** Backend Dockerfiles MUST use a slim or alpine base image for the final stage (e.g., `python:3.12-slim`) <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **Frontend build to nginx:** Frontend Dockerfiles MUST use a Node build stage and an `nginx:alpine` final stage, copying the build output (e.g., `dist/`) to nginx's serving directory <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **.dockerignore:** A `.dockerignore` MUST exist at the build context root excluding at minimum `.venv`, `node_modules`, `.git`, `__pycache__`, `.env`, `tests/`, `docs/`, and IDE configuration files <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **Env-var configuration:** All runtime configuration MUST be read from environment variables <!-- from: adrs/deployment/env-connection-urls.md -->
- **Connection URLs:** External services (database, Redis, LLM providers, search APIs) MUST be configured via URL-style environment variables (e.g., `DATABASE_URL`, `REDIS_URL`) <!-- from: adrs/deployment/env-connection-urls.md -->
- **Typed settings singleton:** A typed settings class (e.g., Pydantic `BaseSettings`) MUST load and validate all environment variables at startup, as a singleton loaded once <!-- from: adrs/deployment/env-connection-urls.md -->
- **.env examples:** The repository MUST contain `.env.example` documenting all required variables with placeholder values; a `.env.production.example` SHOULD show production-specific expectations <!-- from: adrs/deployment/env-connection-urls.md -->
- **Fail fast on missing secrets:** The application MUST fail to start if required secrets are missing <!-- from: adrs/deployment/env-connection-urls.md -->
- **One process type per container:** The API server, background workers, and frontend MUST run as separate containers <!-- from: adrs/deployment/container-per-process.md -->
- **Shared image, command override:** Containers sharing the same codebase (e.g., API and worker) MUST use the same Docker image with different `command` overrides in the Compose file <!-- from: adrs/deployment/container-per-process.md -->
- **Health checks everywhere:** Every container MUST define a `healthcheck` — API containers via an HTTP endpoint (e.g., `GET /health`), database/cache containers via native CLI checks (`pg_isready`, `redis-cli ping`) <!-- from: adrs/deployment/container-per-process.md -->
- **Restart policy:** All containers MUST set `restart: unless-stopped` (or the orchestrator equivalent) <!-- from: adrs/deployment/container-per-process.md -->
- **Explicit worker concurrency:** Worker containers MUST set concurrency explicitly via command-line flags (e.g., `celery worker -c 4`) <!-- from: adrs/deployment/container-per-process.md -->
- **Dev Compose = infra only:** `docker-compose.yml` MUST contain only infrastructure services (database, Redis, message brokers) <!-- from: adrs/deployment/local-dev-compose.md -->
- **Prod Compose = apps only:** `docker-compose.prod.yml` MUST contain only application services, connecting to shared infrastructure via environment variables <!-- from: adrs/deployment/local-dev-compose.md -->
- **External infra network:** Production Compose MUST declare an external network; application services reach databases and caches through it using Docker DNS names <!-- from: adrs/deployment/local-dev-compose.md -->
- **Dev infra readiness:** All dev infrastructure services MUST define health checks and expose ports to the host (e.g., `5432:5432`, `6379:6379`) <!-- from: adrs/deployment/local-dev-compose.md -->
- **Prod env loading:** The prod Compose MUST load environment variables from a `.env` file or receive them from the orchestrator <!-- from: adrs/deployment/local-dev-compose.md -->
- **Named volumes for data:** Infrastructure data MUST use named Docker volumes for persistence across container restarts in dev <!-- from: adrs/deployment/local-dev-compose.md -->
- **UUID primary keys:** All PK columns use `uuid` in PostgreSQL (`Guid` in C#); foreign keys referencing them MUST also be `uuid`/`Guid` <!-- from: adrs/database/uuid-primary-keys.md -->
- **Server-side ID generation:** Generate IDs server-side with `Guid.NewGuid()` or the database default `gen_random_uuid()`; EF Core configurations specify `.ValueGeneratedOnAdd()` for database-generated UUID PKs <!-- from: adrs/database/uuid-primary-keys.md -->
- **Snake-case translation:** Configure `UseSnakeCaseNamingConvention()` on the DbContext (Npgsql EF Core package); entity properties stay PascalCase and are translated automatically <!-- from: adrs/database/snake-case-naming.md -->
- **snake_case in raw SQL:** Raw SQL queries must use snake_case identifiers (e.g., `created_at`, `user_id`) <!-- from: adrs/database/snake-case-naming.md -->
- **Migrations reflect snake_case:** Migration files will reflect snake_case names — this is expected and correct <!-- from: adrs/database/snake-case-naming.md -->
- **timestamptz columns:** All datetime columns in migrations must use `timestamptz` <!-- from: adrs/database/timestamptz-always.md -->
- **DateTimeOffset in code:** Datetime properties use `DateTimeOffset`; the column type is explicitly configured as `timestamptz` when not inferred <!-- from: adrs/database/timestamptz-always.md -->
- **UTC always:** All stored datetime values are UTC — use `DateTimeOffset.UtcNow` <!-- from: adrs/database/timestamptz-always.md -->
- **Frontend-only timezone conversion:** Timezone conversion to local display time is a frontend-only concern <!-- from: adrs/database/timestamptz-always.md -->
- **Soft-delete column:** All soft-deletable entities carry a nullable `DeletedAt` property mapping to a `deleted_at` column of type `timestamptz` <!-- from: adrs/database/soft-deletes.md -->
- **Global query filter:** Configure global query filters so soft-deleted rows are invisible by default (`.HasQueryFilter(e => e.DeletedAt == null)`) <!-- from: adrs/database/soft-deletes.md -->
- **Soft-delete by timestamp:** To soft-delete, set `DeletedAt = DateTimeOffset.UtcNow` <!-- from: adrs/database/soft-deletes.md -->
- **Explicit opt-in for deleted rows:** Use `.IgnoreQueryFilters()` explicitly to query soft-deleted records <!-- from: adrs/database/soft-deletes.md -->
- **Response envelope:** Single-item responses are `{ "data": { ... } }`; list responses are `{ "data": [ ... ], "meta": { "totalCount": N, "page": N, "pageSize": N } }` <!-- from: adrs/api/rest-envelope.md -->
- **Envelope wrapper classes:** Use generic wrappers — `ApiResponse<T>` for single items, `ApiListResponse<T>` for lists — and always wrap controller return values in the envelope <!-- from: adrs/api/rest-envelope.md -->
- **Bearer tokens:** Tokens are sent in the `Authorization: Bearer <token>` header on every authenticated request <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Token claims and lifetime:** Access tokens contain `sub` (user ID), role(s), issued-at, and expiration claims, with a 15-60 minute configurable lifetime <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Refresh token rotation:** Refresh tokens are long-lived, stored securely (httpOnly cookie or secure storage), and rotated on every use <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Full token validation:** Token validation must check signature, expiration, issuer, and audience <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Guarded endpoints:** Protect endpoints with `[Authorize]`; role-based access via `[Authorize(Roles = "...")]` <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Pagination parameters:** `page` is 1-based; `pageSize` defaults to 20 with a maximum of 100 (reject larger requests with a 400 error) <!-- from: adrs/api/offset-pagination.md -->
- **Pagination meta:** List response `meta` must include `totalCount`, `page`, and `pageSize` <!-- from: adrs/api/offset-pagination.md --> <!-- from: adrs/api/rest-envelope.md -->
- **Sorting parameters:** `sortBy` (column name) and `sortDir` (`asc` or `desc`, default `asc`) <!-- from: adrs/api/offset-pagination.md -->
- **Sort allowlist:** Validate `sortBy` against an allowlist of sortable columns <!-- from: adrs/api/offset-pagination.md -->
- **Shared pagination binding:** Create a shared `PaginationParams` class for query parameters; use `.Skip((page - 1) * pageSize).Take(pageSize)` for EF Core queries <!-- from: adrs/api/offset-pagination.md -->

### Anti-Patterns to Avoid

- **No routes on the app instance:** NEVER define routes directly on the main `FastAPI()` app instance <!-- from: adrs/python/fastapi-framework.md -->
- **No cross-module imports:** Modules MUST NOT import models or services from other module packages directly <!-- from: adrs/python/modular-packages.md -->
- **No circular module dependencies:** No circular dependencies between modules — if two modules need each other, extract the shared concept into the contracts package <!-- from: adrs/python/modular-packages.md -->
- **No business logic in routes:** NEVER place business logic in route handlers — route handlers are thin wrappers only <!-- from: adrs/python/service-layer-logic.md -->
- **No raw queries in routes:** NEVER perform raw database queries in route handlers — all data access goes through services <!-- from: adrs/python/service-layer-logic.md -->
- **No ORM models in responses:** NEVER return SQLAlchemy model instances directly from route handlers or services that feed into responses <!-- from: adrs/python/pydantic-at-boundary.md -->
- **No shared input/output schema:** NEVER reuse the same schema class for both input and output <!-- from: adrs/python/pydantic-at-boundary.md -->
- **No sync sessions in async paths:** NEVER use synchronous SQLAlchemy sessions (`Session`) in async code paths <!-- from: adrs/python/async-all-the-way.md -->
- **No blocking I/O in async functions:** NEVER call blocking I/O (synchronous HTTP requests, file reads, `time.sleep()`) directly in async functions — use `asyncio.to_thread()` to wrap unavoidable sync libraries <!-- from: adrs/python/async-all-the-way.md -->
- **No WSGI server:** NEVER use a WSGI server — the application runs on ASGI <!-- from: adrs/python/async-all-the-way.md -->
- **No asyncio.run() in handlers:** NEVER use `asyncio.run()` inside route handlers or services — the event loop is already running <!-- from: adrs/python/async-all-the-way.md -->
- **No out-of-band schema changes:** NEVER modify the database schema outside of Alembic migrations <!-- from: adrs/python/sqlalchemy-async.md -->
- **No class components:** NEVER use class components, `this.state`/`this.setState`, or lifecycle methods (`componentDidMount`, etc.) <!-- from: adrs/react/functional-components.md -->
- **No SDK images in final stage:** NEVER use full SDK or build images as the final Docker stage <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **No dev dependencies in production images:** NEVER install dev dependencies in the final stage — use `--no-dev`, `--only=production`, or equivalent flags <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **No full source in final stage:** NEVER copy the entire source tree into the final stage when only a build artifact is needed <!-- from: adrs/deployment/docker-multi-stage-builds.md -->
- **No hardcoded config:** NEVER hardcode connection strings, API keys, or environment-specific values in source code <!-- from: adrs/deployment/env-connection-urls.md -->
- **No committed secrets:** NEVER commit a real `.env` file with actual secrets <!-- from: adrs/deployment/env-connection-urls.md -->
- **No default secret values:** API keys and secrets MUST NOT have default values in the settings class <!-- from: adrs/deployment/env-connection-urls.md -->
- **No scattered env reads:** NEVER re-read environment variables scattered across the codebase — the settings singleton is loaded once at startup <!-- from: adrs/deployment/env-connection-urls.md -->
- **No multi-process containers:** NEVER run multiple process types inside a single container <!-- from: adrs/deployment/container-per-process.md -->
- **No duplicate Dockerfiles:** NEVER maintain separate Dockerfiles for the same codebase <!-- from: adrs/deployment/container-per-process.md -->
- **No `restart: always`:** NEVER use `restart: always` (prevents intentional stops) or omit the restart policy <!-- from: adrs/deployment/container-per-process.md -->
- **No default worker concurrency:** NEVER rely on library defaults for production worker concurrency <!-- from: adrs/deployment/container-per-process.md -->
- **No app services in dev Compose:** NEVER define application services (API, worker, frontend) in the dev Compose file <!-- from: adrs/deployment/local-dev-compose.md -->
- **No infra in prod Compose:** NEVER define database or cache services in the prod Compose file <!-- from: adrs/deployment/local-dev-compose.md -->
- **No hardcoded Compose connections:** NEVER hardcode connection strings in the Compose file <!-- from: adrs/deployment/local-dev-compose.md -->
- **No bind mounts for database data:** NEVER use bind mounts for database data directories — use named Docker volumes <!-- from: adrs/deployment/local-dev-compose.md -->
- **No integer primary keys:** Never define a primary key as `int`, `long`, or `serial` <!-- from: adrs/database/uuid-primary-keys.md -->
- **No manual column attributes:** Never manually specify `[Column("...")]` or `[Table("...")]` attributes for snake_case translation — the convention handles it <!-- from: adrs/database/snake-case-naming.md -->
- **No timestamp-without-timezone:** Never use `timestamp` (without time zone) for datetime columns <!-- from: adrs/database/timestamptz-always.md -->
- **No DateTime.Now:** Never call `DateTime.Now` or use `DateTime` — always `DateTimeOffset.UtcNow` <!-- from: adrs/database/timestamptz-always.md -->
- **No hard deletes from app code:** Never call `Remove()` or `DELETE` to delete — hard deletes (`DELETE FROM`) are only permitted in background compaction/cleanup jobs <!-- from: adrs/database/soft-deletes.md -->
- **No raw top-level responses:** Never return a raw array or raw object at the top level — always use the envelope <!-- from: adrs/api/rest-envelope.md -->
- **No JWTs in localStorage:** Never store JWTs in localStorage — use httpOnly cookies or in-memory storage on the frontend <!-- from: adrs/api/jwt-bearer-auth.md -->
- **No raw input in ORDER BY:** Never pass raw user input to ORDER BY — `sortBy` is validated against the allowlist <!-- from: adrs/api/offset-pagination.md -->

## Error Handling

<!-- TODO: error handling strategy, standard error pattern, error types — project-specific (no frozen ADR covers error format). -->

## Testing Conventions

<!-- TODO: test locations, structure, priorities — project-specific. -->

## API Conventions (if applicable)

<!-- TODO: endpoint naming and project-specific request/response examples — see docs/api-spec/index.md compiled sections for the envelope, auth, and pagination conventions. -->

## Database Conventions (if applicable)

<!-- TODO: project-specific index/FK naming and migration guidelines — see docs/data-model/index.md compiled sections for the compiled database conventions. -->

## Environment & Configuration

<!-- TODO: concrete environment variable table and configuration files — project-specific (the env-var conventions above define the rules). -->

## Git Conventions

<!-- TODO: branch naming and commit message conventions — project-specific. -->

## Performance Considerations

<!-- TODO: project-specific. -->

## Security Checklist

<!-- TODO: project-specific. -->

## Common Gotchas

<!-- TODO: project-specific. -->

## Related Documentation

<!-- TODO: project-specific links. -->
