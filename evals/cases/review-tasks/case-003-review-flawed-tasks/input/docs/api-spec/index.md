# API Specification — TaskFlow

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

## 1. Overview

### 1.1 API Summary

A single Express API under `/api/v1`, JSON only. Every endpoint requires a JWT bearer token issued by the external auth service. All responses use the shared envelope; all errors use stable codes from the Error Catalog.

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Base path | `/api/v1` | Room for breaking changes behind a new prefix |
| Auth mechanism | JWT Bearer tokens (external auth service) | No local credential storage |
| Response envelope | `{ "data": ... }` (+ `"meta"` on lists) | Uniform client parsing |
| Error format | `{ "error": { "code", "message", "fields?" } }` | Stable machine-readable codes |
| Pagination style | Offset with `page` + `pageSize` | Simple; data volumes are small |

---

## 2. Common Conventions

### 2.1 Response Envelope

**Success (list):**

```json
{
  "data": [],
  "meta": { "totalCount": 0, "page": 1, "pageSize": 50 }
}
```

**Single-item responses** are `{ "data": { ... } }` — no `meta`.

### 2.2 Error Response

```json
{
  "error": {
    "code": "validation-error",
    "message": "title must be 1-200 characters",
    "fields": { "title": ["must be 1-200 characters"] }
  }
}
```

`fields` is present only for `validation-error`. Routers throw `ApiError`; `src/api/errors.ts` serializes it.

### 2.3 Authentication

- **Mechanism**: JWT Bearer token in the `Authorization` header — `Authorization: Bearer <token>`
- **Unauthenticated endpoints**: none

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-based) |
| pageSize | int | 50 | Items per page (max 100) |

List responses always include `meta` with `totalCount`, `page`, `pageSize`. Default sort is documented per endpoint.

### 2.5 Error Catalog

> *Stable, machine-readable error codes. Endpoints reference these instead of inventing ad-hoc errors. Add a row before introducing a new code; never repurpose one.*

| Error Code | HTTP Status | When Used | Notes |
|------------|-------------|-----------|-------|
| validation-error | 400 | Request body or query fails Zod validation | `fields` maps field → messages |
| unauthorized | 401 | Missing, expired, or invalid bearer token | Client redirects to login |
| not-found | 404 | Resource does not exist | — |
| conflict | 409 | Uniqueness or state conflict (e.g., duplicate name) | `message` names the conflicting field |

---

## 3. Shared DTOs

None yet — DTOs used by a single resource live in that resource's shard.

---

## 4. Endpoint Summary

> *Quick reference of ALL endpoints across all shards — this table doubles as the shard directory. Add a row here whenever a resource shard gains an endpoint.*

| Method | Path | Module | Auth | Shard | Description |
|--------|------|--------|------|-------|-------------|
| GET | /api/v1/projects/{projectId}/tasks | Projects | Required | `endpoints/tasks.md` | List tasks for the project board |
| GET | /api/v1/tasks/{id} | Projects | Required | `endpoints/tasks.md` | Get a single task |
| PATCH | /api/v1/tasks/{id} | Projects | Required | `endpoints/tasks.md` | Partially update a task |

---

## Usage Notes for AI Task Generation

1. **Shard loading**: Read this index plus ONLY the resource shards named by the work item's impact tables — kebab-case, plural, matching the route segment (e.g., `/api/v1/tasks/{id}` operates on tasks → `endpoints/tasks.md`; nested routes group under the resource being operated on, so `/api/v1/projects/{id}/labels` maps to a `labels` shard). Do not read the whole `endpoints/` directory.
2. **Envelope discipline**: All responses use the envelope in Section 2.1 — never return raw rows.
3. **Error catalog discipline**: Error responses use codes from Section 2.5 — add a catalog row before introducing a new code.
4. **Pagination**: List endpoints must support Section 2.4 parameters and return `meta` totals.
5. **New resources**: Create a new shard at `endpoints/<resource>.md`, add its endpoints to the Endpoint Summary (Section 4), and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-01 | TaskFlow team | Initial version (tasks resource) | v1.0 baseline |
