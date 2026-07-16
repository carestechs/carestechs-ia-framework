---
kind: resource
resource: tasks
routes: [/api/v1/projects/{projectId}/tasks, /api/v1/tasks/{id}]
entities: [task, project, project-member]
---

# Resource: Tasks (`/api/v1/projects/{projectId}/tasks`, `/api/v1/tasks/{id}`)

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Module: Core — task listing, creation, and editing. Router: `src/api/tasks.ts`; repository: `src/db/task.ts` (planned). `assigneeId` is validated against `project_members` — hence `project-member` in `entities`. Tasks have **no ordering/position field**: board columns group by `status`; ordering within a column is presentation-side. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*

## TaskDto

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string (UUID) | No | Task id |
| projectId | string (UUID) | No | Owning project |
| title | string | No | 1–200 chars |
| description | string | Yes | Longer body text (plain text) |
| status | string | No | `todo` \| `in_progress` \| `done` |
| dueDate | string (`YYYY-MM-DD`) | Yes | **Day-precision calendar date — no time component, no timezone** |
| assigneeId | string (UUID) | Yes | Opaque user id; must be a current member of the owning project |
| createdAt | string (ISO 8601) | No | — |
| updatedAt | string (ISO 8601) | No | — |

---

## GET /api/v1/projects/{projectId}/tasks

> *List the project's tasks, sorted by `createdAt` descending. The board loads all statuses and groups client-side; the filters serve assignee and status views.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any project member |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| projectId | UUID | Project whose tasks are requested |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| status | string | No | null | Filter to one `TaskStatus` value (`todo` \| `in_progress` \| `done`) |
| assigneeId | UUID | No | null | Filter to tasks assigned to this user |
| page | int | No | 1 | See index Section 2.4 |
| pageSize | int | No | 50 | Max 100 |

**Response (200 OK):**

```json
{
  "data": [ { "id": "…", "projectId": "…", "title": "…", "status": "todo", "dueDate": "2026-07-20", "assigneeId": null } ],
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
| 403 | Caller is not a member (`forbidden`) |
| 404 | Project does not exist (`not-found`) |

---

## POST /api/v1/projects/{projectId}/tasks

> *Create a task in the project.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any project member |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| projectId | UUID | Project to create the task in |

**Request Body:**

```json
{
  "title": "string — required, 1-200 chars after trimming",
  "description": "string | null — optional",
  "status": "todo | in_progress | done — optional, default todo",
  "dueDate": "string (YYYY-MM-DD) | null — optional, calendar date",
  "assigneeId": "string (UUID) | null — optional, must be a current project member"
}
```

**Response (201 Created):** `{ "data": TaskDto }`

**Status Codes:**

| Code | Condition |
|------|-----------|
| 201 | Created |
| 400 | Body fails validation, incl. `assigneeId` not a current member (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member (`forbidden`) |
| 404 | Project does not exist (`not-found`) |

---

## GET /api/v1/tasks/{id}

> *Fetch one task for the detail panel.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any member of the owning project |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Task id |

**Response (200 OK):** `{ "data": TaskDto }`

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member of the owning project (`forbidden`) |
| 404 | Task does not exist (`not-found`) |

---

## PATCH /api/v1/tasks/{id}

> *Partially update a task — used by the detail panel (fields) and the board (drag between columns: `status` only).*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any member of the owning project |

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
  "dueDate": "string (YYYY-MM-DD) | null — null clears the due date",
  "assigneeId": "string (UUID) | null — null unassigns; must be a current member when set"
}
```

**Response (200 OK):** `{ "data": TaskDto }` — the updated task.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Body fails validation or is empty, incl. `assigneeId` not a current member (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member of the owning project (`forbidden`) |
| 404 | Task does not exist (`not-found`) |
