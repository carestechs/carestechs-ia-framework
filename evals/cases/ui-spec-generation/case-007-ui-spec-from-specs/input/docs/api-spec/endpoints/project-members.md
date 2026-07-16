---
kind: resource
resource: project-members
routes: [/api/v1/projects/{projectId}/members, /api/v1/projects/{projectId}/members/{userId}]
entities: [project-member, project, task]
---

# Resource: Project Members (`/api/v1/projects/{projectId}/members`, `/api/v1/projects/{projectId}/members/{userId}`)

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Module: Core — the explicit membership list that anchors all access control. Router: `src/api/project-members.ts`; repository: `src/db/project-member.ts` (planned). Removing a member also unassigns that user's tasks in the project — hence `task` in `entities`. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*

## ProjectMemberDto

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | string (UUID) | No | Membership row id |
| projectId | string (UUID) | No | Project the membership belongs to |
| userId | string (UUID) | No | Opaque auth-service user id — never resolved to a name or profile |
| role | string | No | `owner` \| `member` |
| createdAt | string (ISO 8601) | No | When the user joined the project |
| updatedAt | string (ISO 8601) | No | — |

---

## GET /api/v1/projects/{projectId}/members

> *List the project's members, sorted by `createdAt` ascending (owner first — the owner row is created with the project).*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Any project member |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| projectId | UUID | Project whose members are requested |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | int | No | 1 | See index Section 2.4 |
| pageSize | int | No | 50 | Max 100 |

**Response (200 OK):**

```json
{
  "data": [ { "id": "…", "projectId": "…", "userId": "…", "role": "owner" } ],
  "meta": { "totalCount": 4, "page": 1, "pageSize": 50 }
}
```

`data` items are full `ProjectMemberDto` objects.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Invalid query parameters (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not a member (`forbidden`) |
| 404 | Project does not exist (`not-found`) |

---

## POST /api/v1/projects/{projectId}/members

> *Add a member by their auth-service user id. Added rows always get role `member` — the single `owner` row is created with the project and never granted here.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Project owner |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| projectId | UUID | Project to add the member to |

**Request Body:**

```json
{
  "userId": "string (UUID) — required, the auth-service user id"
}
```

**Response (201 Created):** `{ "data": ProjectMemberDto }`

**Status Codes:**

| Code | Condition |
|------|-----------|
| 201 | Created |
| 400 | `userId` missing or not a UUID (`validation-error`) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not the owner (`forbidden`) |
| 404 | Project does not exist (`not-found`) |
| 409 | User is already a member (`conflict`) |

---

## DELETE /api/v1/projects/{projectId}/members/{userId}

> *Remove a member. In the same transaction, sets `assigneeId` to null on this project's tasks assigned to them (no dangling assignments). The owner's row cannot be removed while the project exists.*

| Attribute | Value |
|-----------|-------|
| **Auth** | Required |
| **Roles** | Project owner |

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| projectId | UUID | Project to remove the member from |
| userId | UUID | Auth-service user id of the member to remove |

**Response (204 No Content):** no body.

**Status Codes:**

| Code | Condition |
|------|-----------|
| 204 | Removed (their assigned tasks in this project are now unassigned) |
| 401 | Missing or invalid token (`unauthorized`) |
| 403 | Caller is not the owner (`forbidden`) |
| 404 | Project or membership row does not exist (`not-found`) |
| 409 | Target is the owner's membership row (`conflict`) |
