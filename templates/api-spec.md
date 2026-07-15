# API Specification Template

> **Purpose**: Document all REST API endpoints with their routes, methods, request/response shapes, authentication requirements, and status codes. This provides AI with the contract definitions needed to generate consistent backend controllers, frontend services, and integration tests.
> **Applicability**: If applicable — skip this document for CLI tools, libraries, and headless services with no HTTP API. The framework assumes a web app + REST API shape; if your product exposes a different contract surface (e.g., a CLI command set or a public library API), document that contract elsewhere instead.

> **Context budget note:** This document is loaded into AI context. Keep it contract-style —
> tables, schemas, rules, one example each. Move narrative and history to `docs/rationale/`
> and link it; rationale files are never loaded by default.

---

## Directory Layout

The API specification is a **sharded document set**, not a single file. Cross-cutting contracts (envelope, errors, auth, pagination, shared DTOs) live in `index.md`; every resource group lives in its own shard. Work items name endpoints in their impact tables, and task generation loads `index.md` plus only the named resource shards — shard boundaries are retrieval boundaries.

```
docs/api-spec/
  index.md                  # Key API Decisions, response envelope, Error Catalog,
                            # Authentication Endpoints, Pagination, Usage Notes, Changelog
  endpoints/<resource>.md   # ONE resource group per file: all endpoint blocks for that resource
                            # (route, method, auth, request/response DTOs, status codes)
```

Rules:

- **One resource group per shard.** All endpoints operating on the same resource (e.g., every `/api/task-labels*` endpoint) live together in one file. Never split a resource across shards, and never put endpoint blocks in `index.md`.
- **Shards are self-sufficient with the index.** A shard does not restate the envelope/error/pagination conventions — it relies on `index.md` for those — but it contains every endpoint block for its resource in full.
- **Cross-cutting only in the index.** Shared DTOs, error catalog rows, and auth conventions go in `index.md`; DTOs used by a single resource stay in that resource's shard.

---

## Index File (`docs/api-spec/index.md`)

Everything from here down to "Resource Shard" defines the contents of `index.md`. Start the file with its own H1 and the freshness stamp directly beneath it:

```
# API Specification — [Product Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->
```

## 1. Overview

### 1.1 API Summary

[One paragraph describing the API surface — how many modules expose endpoints, the authentication model, and the general response format.]

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Base path] | [e.g., `/api/`] | [Why] |
| [Versioning strategy] | [e.g., URL prefix `/api/v1/`] | [Why] |
| [Auth mechanism] | [e.g., JWT Bearer tokens] | [Why] |
| [Response envelope] | [e.g., `{ data, meta }`] | [Why] |
| [Error format] | [e.g., RFC 7807 Problem Details] | [Why] |
| [Pagination style] | [e.g., Offset with `page` + `pageSize`] | [Why] |

---

## 2. Common Conventions

### 2.1 Response Envelope

**Success Response:**
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

<!-- TODO: Adjust envelope format to match your project conventions -->

**Single-item responses** omit the `meta` field unless pagination or extra metadata is relevant.

### 2.2 Error Response (RFC 7807)

```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "[Error Title]",
  "status": 400,
  "detail": "[Human-readable explanation]",
  "errors": {
    "[field]": ["[Validation message 1]", "[Validation message 2]"]
  }
}
```

### 2.3 Authentication

- **Mechanism**: [e.g., JWT Bearer token in `Authorization` header]
- **Token format**: `Authorization: Bearer <token>`
- **Unauthenticated endpoints**: [List any public endpoints]

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| [page] | [int] | [1] | [Page number (1-based)] |
| [pageSize] | [int] | [20] | [Items per page (max 100)] |
| [sortBy] | [string] | [created_at] | [Field to sort by] |
| [sortDir] | [string] | [desc] | [Sort direction: asc or desc] |

### 2.5 Error Catalog

> *Enumerate the stable, machine-readable error identifiers clients can rely on — the RFC 7807 `type` values (or error codes if you use a code-based format). Endpoints reference these instead of inventing ad-hoc errors. Add rows as new error conditions appear; never repurpose an existing identifier.*

| Error Code / `type` | HTTP Status | When Used | Notes |
|---------------------|-------------|-----------|-------|
| [validation-error] | [400] | [Request body or query fails validation] | [`errors` object lists per-field messages] |
| [unauthorized] | [401] | [Missing, expired, or invalid auth token] | [Client should redirect to login / refresh token] |
| [forbidden] | [403] | [Authenticated but lacks the required role] | — |
| [not-found] | [404] | [Resource does not exist or is soft-deleted] | — |
| [conflict] | [409] | [Uniqueness or state conflict — e.g., duplicate name] | [`detail` names the conflicting field] |
| [rate-limited] | [429] | [Client exceeded request quota] | [Include `Retry-After` header] |

<!-- TODO: Replace with your real catalog. Use full URIs for RFC 7807 `type` values if your convention requires them (e.g., https://yourapp.example/errors/validation-error). -->

### 2.6 Authentication Endpoints

> *Model authentication endpoints (login, token refresh, logout, password reset) like any other endpoints — full endpoint blocks in their own resource shard with request/response shapes and status codes. Do not leave auth as prose-only.*

Guidance:

- Give auth endpoints their own resource shard (`docs/api-spec/endpoints/auth.md`) so controller/service tasks are generated for them like any other resource.
- Document token lifetimes, refresh semantics, and where tokens are stored/sent as part of the endpoint blocks or Section 2.3.
- Mark which auth endpoints are public (login, refresh) vs authenticated (logout, change password) in the **Auth** attribute.
- Failed authentication uses the same error format as everything else — reference the Error Catalog (Section 2.5) entries [unauthorized] / [validation-error] rather than a custom shape.

---

## 3. Shared DTOs

> *DTOs referenced by multiple resources or modules. DTOs used by a single resource live in that resource's shard.*

### 3.1 [DTOName]

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| [field_1] | [string] | [No] | [Description] |
| [field_2] | [int] | [Yes] | [Description] |

<!-- TODO: Define shared DTOs used across modules — e.g., PaginationMeta, UserSummaryDto -->

---

## 4. Endpoint Summary

> *Quick reference table of ALL endpoints across all shards — this doubles as the shard directory. Add a row here whenever a resource shard gains an endpoint.*

| Method | Path | Module | Auth | Shard | Description |
|--------|------|--------|------|-------|-------------|
| [GET] | [/api/resources] | [Module A] | [Required] | [`endpoints/resources.md`] | [List resources] |
| [POST] | [/api/resources] | [Module A] | [Required] | [`endpoints/resources.md`] | [Create resource] |
| [GET] | [/api/resources/{id}] | [Module A] | [Required] | [`endpoints/resources.md`] | [Get resource by ID] |
| [PUT] | [/api/resources/{id}] | [Module A] | [Required] | [`endpoints/resources.md`] | [Update resource] |
| [DELETE] | [/api/resources/{id}] | [Module A] | [Required] | [`endpoints/resources.md`] | [Delete resource] |

<!-- TODO: Add all endpoints here for a complete at-a-glance reference -->

---

## Usage Notes for AI Task Generation

When generating tasks from this document set:

1. **Shard loading**: Read `index.md` plus ONLY the resource shards named by the work item's impact tables (mapped via the Naming Rule) — do not read the whole `endpoints/` directory
2. **Controller structure**: Each resource shard maps to a controller / route group — generate controller tasks per resource, not per endpoint
3. **DTO generation**: Request and response JSON shapes map directly to DTO classes — generate DTOs in the owning module
4. **Status codes**: Every endpoint must handle all listed status codes — include error-path tasks
5. **Auth requirements**: Respect the auth/roles attributes — generate middleware or attribute decorations accordingly
6. **Response envelope**: All responses must use the shared envelope format (Section 2.1) — never return raw entities
7. **Pagination**: Endpoints returning lists must support pagination parameters and return meta with totals
8. **Frontend alignment**: Frontend service tasks should mirror the endpoint signatures defined in the resource shards — same paths, same request/response shapes
9. **Error catalog discipline**: Error responses must use identifiers from the Error Catalog (Section 2.5) — add a new catalog row before introducing a new error condition
10. **New resources**: Create a new shard at `endpoints/<resource>.md`, add its endpoints to the Endpoint Summary (Section 4), and record the change in the Changelog

---

## Changelog

> *Lives at the very bottom of `index.md` and records changes across the whole `docs/api-spec/` set — shard edits included. Every edited or verified file also gets its freshness stamp updated.*

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |

---

## Resource Shard (`docs/api-spec/endpoints/<resource>.md`)

One file per resource group, containing ALL endpoint blocks for that resource. Every shard follows this skeleton — reuse it verbatim when adding a new resource:

> **Frontmatter note:** Flat keys only — values are scalars or inline `[a, b, c]` arrays (no nesting, no multiline values; parsed by `.ai-framework/tools/validate-specs.py`), and `resource` MUST match the filename. Shards only — `index.md` gets NO frontmatter.

````markdown
---
kind: resource
resource: [resource-name]      # kebab-case; MUST equal the filename
routes: [/api/resource-name]
entities: [entity-a]           # entity shard names this resource reads/writes (may be [])
---

# Resource: [Resource Name] (`/api/[resource]`)

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> *Module: [Owning Module] — [One-sentence description of this resource group]. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*

## [METHOD] [/api/path/{param}]

> *[One-sentence description of what this endpoint does]*

| Attribute | Value |
|-----------|-------|
| **Auth** | [Required / Public] |
| **Roles** | [Any / Admin / Owner] |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| [param] | [UUID] | [Description] |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| [filter] | [string] | [No] | [null] | [Description] |

**Request Body:**

```json
{
  "[field_1]": "[type — description]",
  "[field_2]": "[type — description]"
}
```

**Response (200 OK):**

```json
{
  "data": {
    "[field_1]": "[type]",
    "[field_2]": "[type]"
  }
}
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| [200] | [Success] |
| [400] | [Validation error — see Error Catalog] |
| [401] | [Missing or invalid auth token] |
| [404] | [Resource not found] |

---

## [METHOD] [/api/path]

> *[Description]*

| Attribute | Value |
|-----------|-------|
| **Auth** | [Required / Public] |
| **Roles** | [Any / Admin] |

**Request Body:**

```json
{
  "[field]": "[type — description]"
}
```

**Response (201 Created):**

```json
{
  "data": {
    "[field]": "[type]"
  }
}
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| [201] | [Resource created] |
| [400] | [Validation error] |
| [401] | [Unauthorized] |
| [409] | [Conflict — resource already exists] |

---

<!-- TODO: Repeat one ## endpoint block per endpoint in this resource group -->
````

---

## Naming Rule

Shard names derive **mechanically** from the resource route segment — kebab-case, **plural**, matching the route:

| Resource / Route | Shard Path |
|------------------|-----------|
| `/api/tasks` | `docs/api-spec/endpoints/tasks.md` |
| `/api/task-labels` | `docs/api-spec/endpoints/task-labels.md` |
| Auth endpoints (login, refresh, logout) | `docs/api-spec/endpoints/auth.md` |

Nested routes group under the resource being operated on: `/api/projects/{id}/labels` operates on labels → `docs/api-spec/endpoints/labels.md`.

Never deviate from this mapping: work-item impact tables use endpoint paths as retrieval keys, and task generation resolves `route → shard path` without guessing.
