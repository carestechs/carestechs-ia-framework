# API Specification — [Product Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

> *Sharded document set: cross-cutting conventions live in this index; every resource group has its own shard at `endpoints/<resource>.md` (kebab-case, **plural**, matching the route segment — e.g., `/api/task-labels` → `endpoints/task-labels.md`). Copy `endpoints/TEMPLATE-resource.md` to add one. Work items name endpoints as retrieval keys — task generation loads this index plus only the named shards.*

## 1. Overview

### 1.1 API Summary

<!-- TODO: Describe the API surface — how many modules expose endpoints, the auth model, and the response format -->

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Base path --> | <!-- e.g., `/api/` --> | <!-- e.g., Standard convention --> |
| <!-- e.g., Versioning strategy --> | <!-- e.g., URL prefix `/api/v1/` --> | <!-- e.g., Explicit, cache-friendly --> |
| <!-- e.g., Auth mechanism --> | <!-- e.g., JWT Bearer tokens --> | <!-- e.g., Stateless, scalable --> |
| <!-- e.g., Response envelope --> | <!-- e.g., `{ data, meta }` --> | <!-- e.g., Consistent response shape --> |
| <!-- e.g., Error format --> | <!-- e.g., RFC 7807 --> | <!-- e.g., Standard problem details --> |
| <!-- e.g., Pagination style --> | <!-- e.g., Offset with `page` + `pageSize` --> | <!-- e.g., Simple, widely understood --> |

## 2. Common Conventions

### 2.1 Response Envelope

```json
{
  "data": { },
  "meta": {
    "totalCount": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

<!-- TODO: Adjust to match your project's response format -->

### 2.2 Error Response (RFC 7807)

```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "[Error Title]",
  "status": 400,
  "detail": "[Human-readable explanation]",
  "errors": {
    "[field]": ["[Validation message]"]
  }
}
```

### 2.3 Authentication

- **Mechanism**: <!-- e.g., JWT Bearer token in `Authorization` header -->
- **Token format**: `Authorization: Bearer <token>`

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-based) |
| pageSize | int | 20 | Items per page (max 100) |

### 2.5 Error Catalog

<!-- TODO: Enumerate the stable error identifiers clients can rely on — the RFC 7807 `type` values or error codes. Endpoint shards reference these instead of inventing ad-hoc errors. -->

| Error Code / `type` | HTTP Status | When Used | Notes |
|---------------------|-------------|-----------|-------|
| <!-- e.g., validation-error --> | <!-- e.g., 400 --> | <!-- e.g., Request fails validation --> | <!-- e.g., `errors` lists per-field messages --> |
| <!-- e.g., not-found --> | <!-- e.g., 404 --> | <!-- e.g., Resource does not exist --> | <!-- --> |

### 2.6 Authentication Endpoints

<!-- TODO: Model auth endpoints (login, refresh, logout) as full endpoint blocks in their own resource shard (endpoints/auth.md) — don't leave auth as prose-only. Mark which are public vs authenticated in the Auth attribute, and reference Error Catalog entries for failed auth. -->

## 3. Shared DTOs

<!-- TODO: Define DTOs used across modules — DTOs used by a single resource live in that resource's shard -->

### 3.1 [DTOName]

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| <!-- field --> | <!-- type --> | <!-- Yes/No --> | <!-- description --> |

## 4. Endpoint Summary

<!-- TODO: Quick reference of ALL endpoints across all shards — this doubles as the shard directory. Add a row whenever a resource shard gains an endpoint. -->

| Method | Path | Module | Auth | Shard | Description |
|--------|------|--------|------|-------|-------------|
| <!-- GET --> | <!-- /api/resources --> | <!-- Module --> | <!-- Required --> | <!-- `endpoints/resources.md` --> | <!-- List resources --> |
| <!-- POST --> | <!-- /api/resources --> | <!-- Module --> | <!-- Required --> | <!-- `endpoints/resources.md` --> | <!-- Create resource --> |

## Usage Notes for AI Task Generation

- **Shard loading**: Read this `index.md` plus ONLY the resource shards named by the work item's impact tables — do not read the whole `endpoints/` directory
- **Controller structure**: Each resource shard maps to a controller / route group
- **DTO generation**: Request and response shapes map to DTO classes
- **Status codes**: Every endpoint must handle all listed status codes
- **Auth requirements**: Respect the auth/roles attributes
- **Response envelope**: All responses must use the shared envelope format (Section 2.1)
- **Pagination**: List endpoints must support pagination parameters
- **Error catalog discipline**: Error responses must use identifiers from the Error Catalog (Section 2.5) — add a catalog row before introducing a new error condition
- **New resources**: Create a new shard at `endpoints/<resource>.md` (copy `endpoints/TEMPLATE-resource.md`), add its endpoints to the Endpoint Summary (Section 4), and record the change in the Changelog

## Changelog

<!-- Records changes across the whole docs/api-spec/ set — shard edits included. Update the freshness stamp on every file touched. -->

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |
