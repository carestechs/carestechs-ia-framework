---
kind: resource
resource: projects
routes: [/api/v1/projects, /api/v1/projects/{id}, /api/v1/projects/{projectId}/feed]
entities: [project, project-member, task, comment]
---

# Resource: Projects (`/api/v1/projects`, `/api/v1/projects/{id}`, `/api/v1/projects/{projectId}/feed`)

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Module: Core — project CRUD plus the derived activity feed. Router: `src/api/projects.ts`; repository: `src/db/project.ts` (planned). Creating a project also writes the owner's `project_members` row; the feed reads `tasks` and `comments` — hence the wide `entities` list. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*

## ProjectDto

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string (UUID) | No | Project id |
| name | string | No | 1–120 chars, unique case-insensitively |
| description | string | Yes | Short summary |
| ownerId | string (UUID) | No | Opaque auth-service user id of the owner |
| createdAt | string (ISO 8601) | No | — |
| updatedAt | string (ISO 8601) | No | — |

## ActivityEventDto

> *Derived on read from `tasks` and `comments` — never stored. Task events carry no actor: tasks do not record who changed them.*

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| type | string | No | `task_created` \| `task_updated` \| `comment_added` |
| occurredAt | string (ISO 8601) | No | `created_at` / `updated_at` of the underlying record |
| taskId | string (UUID) | No | Task the event concerns |
| taskTitle | string | No | Task title at read time |
| commentId | string (UUID) | Yes | Set only for `comment_added` |
| actorId | string (UUID) | Yes | Comment author for `comment_added`; null for task events |

---

## GET /api/v1/projects

> *List the projects the caller holds a membership row in, sorted by `name` ascending.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any authenticated user (results scoped to own memberships) |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | int | No | 1 | See index Section 2.4 |
| pageSize | int | No | 50 | Max 100 |

**Response (200 OK):**

```json
{
  "data": [ { "id": "…", "name": "…", "description": null, "ownerId": "…" } ],
  "meta": { "totalCount": 3, "page": 1, "pageSize": 50 }
}
```

`data` items are full `ProjectDto` objects.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Invalid query parameters (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |

---

## POST /api/v1/projects

> *Create a project. The caller becomes `ownerId` and gets a `project_members` row with role `owner` in the same transaction.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any authenticated user |

**Request Body:**

```json
{
  "name": "string — required, 1-120 chars after trimming",
  "description": "string | null — optional"
}
```

**Response (201 Created):** `{ "data": ProjectDto }`

**Status Codes:**

| Code | Condition |
|------|-----------|
| 201 | Created |
| 400 | Body fails validation (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 409 | Name already taken, case-insensitively (`conflict`) |

---

## GET /api/v1/projects/{id}

> *Fetch one project (header data for the board and member screens).*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any project member |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Project id |

**Response (200 OK):** `{ "data": ProjectDto }`

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member (`forbidden`) |
| 404 | Project does not exist (`not-found`) |

---

## PATCH /api/v1/projects/{id}

> *Rename a project or edit its description.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Project owner |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Project id |

**Request Body** (all fields optional; at least one required):

```json
{
  "name": "string — 1-120 chars",
  "description": "string | null"
}
```

**Response (200 OK):** `{ "data": ProjectDto }` — the updated project.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Body fails validation or is empty (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not the owner (`forbidden`) |
| 404 | Project does not exist (`not-found`) |
| 409 | Name already taken (`conflict`) |

---

## DELETE /api/v1/projects/{id}

> *Hard-delete a project. Cascades to its tasks, those tasks' comments, and its membership rows — "deleting a project removes everything inside it".*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Project owner |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Project id |

**Response (204 No Content):** no body.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 204 | Deleted |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not the owner (`forbidden`) |
| 404 | Project does not exist (`not-found`) |

---

## GET /api/v1/projects/{projectId}/feed

> *The project activity feed: recent task and comment changes, newest first. Computed on read from `tasks` and `comments` (`created_at`/`updated_at` ordering) — V1 stores no event table.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any project member |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| projectId | UUID | Project whose feed is requested |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | int | No | 1 | See index Section 2.4 |
| pageSize | int | No | 50 | Max 100 |

**Response (200 OK):**

```json
{
  "data": [ { "type": "comment_added", "occurredAt": "…", "taskId": "…", "taskTitle": "…", "commentId": "…", "actorId": "…" } ],
  "meta": { "totalCount": 12, "page": 1, "pageSize": 50 }
}
```

`data` items are `ActivityEventDto` objects ordered by `occurredAt` descending.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Invalid query parameters (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member (`forbidden`) |
| 404 | Project does not exist (`not-found`) |
