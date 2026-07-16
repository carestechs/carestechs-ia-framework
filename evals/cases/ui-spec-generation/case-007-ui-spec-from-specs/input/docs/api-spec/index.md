# API Specification — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

## 1. Overview

### 1.1 API Summary

A single Express API under `/api/v1`, JSON only, owned entirely by the `Core` module. Every endpoint requires a JWT bearer token issued by the external auth service — the API stores only the opaque user UUIDs the token carries. All responses use the shared envelope; all errors use stable codes from the Error Catalog. The project activity feed is **derived on read** from task and comment records — there is no event table and no feed-write endpoint.

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Base path | `/api/v1` | Room for breaking changes behind a new prefix |
| Auth mechanism | JWT Bearer tokens (external auth service) | No local credential or user-profile storage |
| Response envelope | `{ "data": ... }` (+ `"meta"` on lists) | Uniform client parsing |
| Error format | `{ "error": { "code", "message", "fields?" } }` | Stable machine-readable codes |
| Pagination style | Offset with `page` + `pageSize` | Simple; data volumes are small |
| Access model | Every project-scoped route requires a membership row for the caller | Stakeholder principle: explicit membership anchors all access |
| Activity feed | `GET .../feed` computed from `tasks` + `comments` on read | Stakeholder decision: no dedicated event table in V1 |

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

**Single-item responses** are `{ "data": { ... } }` — no `meta`. **204 No Content** responses (deletes) carry no body — the envelope applies to responses that have one.

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
- **Caller identity**: the token's subject is the opaque auth-service user UUID; it is never resolved to a name or profile (the app has no local User entity)
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
| unauthorized | 401 | Missing, expired, or invalid bearer token | Client redirects to the external auth service |
| forbidden | 403 | Caller is not a member of the target project, not the comment author, or not the owner on an owner-only action | — |
| not-found | 404 | Resource does not exist | — |
| conflict | 409 | Uniqueness or state conflict (duplicate project name, duplicate member, removing the owner's membership) | `message` names the conflict |

---

## 3. Shared DTOs

None — every DTO is used by a single resource and lives in that resource's shard.

---

## 4. Endpoint Summary

> *Quick reference of ALL endpoints across all shards — this table doubles as the shard directory. Add a row here whenever a resource shard gains an endpoint.*

| Method | Path | Module | Auth | Shard | Description |
|--------|------|--------|------|-------|-------------|
| GET | /api/v1/projects | Core | Required | `endpoints/projects.md` | List the caller's projects |
| POST | /api/v1/projects | Core | Required | `endpoints/projects.md` | Create a project (caller becomes owner) |
| GET | /api/v1/projects/{id} | Core | Required | `endpoints/projects.md` | Get one project |
| PATCH | /api/v1/projects/{id} | Core | Required | `endpoints/projects.md` | Rename / update a project (owner) |
| DELETE | /api/v1/projects/{id} | Core | Required | `endpoints/projects.md` | Delete a project and everything inside it (owner) |
| GET | /api/v1/projects/{projectId}/feed | Core | Required | `endpoints/projects.md` | Activity feed, derived on read, newest first |
| GET | /api/v1/projects/{projectId}/members | Core | Required | `endpoints/project-members.md` | List project members |
| POST | /api/v1/projects/{projectId}/members | Core | Required | `endpoints/project-members.md` | Add a member by auth user id (owner) |
| DELETE | /api/v1/projects/{projectId}/members/{userId} | Core | Required | `endpoints/project-members.md` | Remove a member (owner); unassigns their tasks |
| GET | /api/v1/projects/{projectId}/tasks | Core | Required | `endpoints/tasks.md` | List tasks (status/assignee filters, paginated) |
| POST | /api/v1/projects/{projectId}/tasks | Core | Required | `endpoints/tasks.md` | Create a task |
| GET | /api/v1/tasks/{id} | Core | Required | `endpoints/tasks.md` | Get one task |
| PATCH | /api/v1/tasks/{id} | Core | Required | `endpoints/tasks.md` | Partially update a task (status, assignee, due date, …) |
| GET | /api/v1/tasks/{taskId}/comments | Core | Required | `endpoints/comments.md` | List a task's comments, oldest first |
| POST | /api/v1/tasks/{taskId}/comments | Core | Required | `endpoints/comments.md` | Add a comment to a task |
| PATCH | /api/v1/comments/{id} | Core | Required | `endpoints/comments.md` | Edit a comment (author only) |

---

## Usage Notes for AI Task Generation

1. **Shard loading**: Read this index plus ONLY the resource shards named by the work item's impact tables. The Shard column of the Endpoint Summary (Section 4) is the authoritative route → shard mapping: sub-resources are documented in the shard of the resource being operated on (`.../members` → `endpoints/project-members.md`, `.../comments` → `endpoints/comments.md`, `.../feed` → `endpoints/projects.md`). Do not read the whole `endpoints/` directory.
2. **Envelope discipline**: All responses use the envelope in Section 2.1 — never return raw rows.
3. **Error catalog discipline**: Error responses use codes from Section 2.5 — add a catalog row before introducing a new code.
4. **Pagination**: List endpoints must support Section 2.4 parameters and return `meta` totals.
5. **User identity**: user ids are opaque auth-service UUIDs. No endpoint returns names, emails, or avatars, and there is no user search or profile endpoint — do not invent one.
6. **New resources**: Create a new shard at `endpoints/<resource>.md`, add its endpoints to the Endpoint Summary (Section 4), and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | spec-generation | Initial version (projects, project-members, tasks, comments) | Derived from the data model and stakeholder Scope Lock V1 |
