---
kind: resource
resource: tasks
routes: [/api/v1/projects/{projectId}/tasks, /api/v1/tasks/{id}]
entities: [task, project]
---

# Resource: Tasks (`/api/v1/projects/{projectId}/tasks`, `/api/v1/tasks/{id}`)

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

> *Module: Projects — board task listing and task editing. Router: `src/api/tasks.ts`; repository: `src/db/task.ts`. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*

## TaskDto

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string (UUID) | No | Task id |
| projectId | string (UUID) | No | Owning project |
| title | string | No | 1–200 chars |
| description | string | Yes | Markdown body |
| status | string | No | `todo` \| `in_progress` \| `done` |
| position | number | No | 0-based order within the status column |
| assigneeId | string (UUID) | Yes | Opaque user id |
| dueDate | string (ISO 8601) | Yes | UTC |
| createdAt | string (ISO 8601) | No | — |
| updatedAt | string (ISO 8601) | No | — |

---

## GET /api/v1/projects/{projectId}/tasks

> *List the project's tasks for the board, ordered by `status`, then `position`.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any project member |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| projectId | UUID | Project whose board is requested |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| status | string | No | null | Filter to one `TaskStatus` value |
| filter | string | No | null | `overdue` — only tasks whose due date has fully passed **in the requesting user's timezone** and whose status is not `done` |
| tz | string | No | `UTC` | IANA timezone (e.g. `America/Los_Angeles`) used to interpret date-only comparisons for `filter=overdue`; the SPA always sends the browser zone |
| page | int | No | 1 | See index Section 2.4 |
| pageSize | int | No | 50 | Max 100 |

**Response (200 OK):**

```json
{
  "data": [ { "id": "…", "projectId": "…", "title": "…", "status": "todo", "position": 0 } ],
  "meta": { "totalCount": 42, "page": 1, "pageSize": 50 }
}
```

`data` items are full `TaskDto` objects.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Invalid query parameters (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 404 | Project does not exist (`not-found`) |

---

## GET /api/v1/tasks/{id}

> *Fetch one task for the detail panel.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any project member |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task id |

**Response (200 OK):**

```json
{ "data": { "id": "…", "projectId": "…", "title": "…", "description": "…", "status": "todo" } }
```

`data` is a full `TaskDto`.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 401 | Missing or invalid token (`unauthorized`) |
| 404 | Task does not exist (`not-found`) |

---

## PATCH /api/v1/tasks/{id}

> *Partially update a task — used by the detail panel (fields) and the board (drag: status + position).*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Project member with edit rights |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task id |

**Request Body** (all fields optional; at least one required):

```json
{
  "title": "string — 1-200 chars",
  "description": "string | null",
  "status": "todo | in_progress | done",
  "position": "number — 0-based",
  "assigneeId": "string (UUID) | null",
  "dueDate": "string (ISO 8601) | null"
}
```

**Response (200 OK):** `{ "data": TaskDto }` — the updated task.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Body fails validation or is empty (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 404 | Task does not exist (`not-found`) |
