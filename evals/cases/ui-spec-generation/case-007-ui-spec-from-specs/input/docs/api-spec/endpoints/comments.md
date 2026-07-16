---
kind: resource
resource: comments
routes: [/api/v1/tasks/{taskId}/comments, /api/v1/comments/{id}]
entities: [comment, task, project-member]
---

# Resource: Comments (`/api/v1/tasks/{taskId}/comments`, `/api/v1/comments/{id}`)

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Module: Core — task discussion threads. Router: `src/api/comments.ts`; repository: `src/db/comment.ts` (planned). The author must hold a membership row for the task's project at posting time — hence `project-member` in `entities`. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*

## CommentDto

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string (UUID) | No | Comment id |
| taskId | string (UUID) | No | Task the comment is attached to |
| authorId | string (UUID) | No | Opaque auth-service user id of the author |
| body | string | No | 1–5000 chars, plain text |
| createdAt | string (ISO 8601) | No | Post time — orders the thread |
| updatedAt | string (ISO 8601) | No | Last edit time |

---

## GET /api/v1/tasks/{taskId}/comments

> *List a task's comments, sorted by `createdAt` ascending (thread order).*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any member of the owning project |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| taskId | UUID | Task whose comments are requested |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | int | No | 1 | See index Section 2.4 |
| pageSize | int | No | 50 | Max 100 |

**Response (200 OK):**

```json
{
  "data": [ { "id": "…", "taskId": "…", "authorId": "…", "body": "…" } ],
  "meta": { "totalCount": 7, "page": 1, "pageSize": 50 }
}
```

`data` items are full `CommentDto` objects.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Invalid query parameters (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member of the owning project (`forbidden`) |
| 404 | Task does not exist (`not-found`) |

---

## POST /api/v1/tasks/{taskId}/comments

> *Add a comment to a task. `authorId` is taken from the bearer token, never from the body.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any member of the owning project |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| taskId | UUID | Task to comment on |

**Request Body:**

```json
{
  "body": "string — required, 1-5000 chars after trimming"
}
```

**Response (201 Created):** `{ "data": CommentDto }`

**Status Codes:**

| Code | Condition |
|------|-----------|
| 201 | Created |
| 400 | Body fails validation (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member of the owning project (`forbidden`) |
| 404 | Task does not exist (`not-found`) |

---

## PATCH /api/v1/comments/{id}

> *Edit a comment's body. Author only; edits update `updatedAt`.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Comment author |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | UUID | Comment id |

**Request Body:**

```json
{
  "body": "string — required, 1-5000 chars after trimming"
}
```

**Response (200 OK):** `{ "data": CommentDto }` — the updated comment.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Body fails validation (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not the author (`forbidden`) |
| 404 | Comment does not exist (`not-found`) |
