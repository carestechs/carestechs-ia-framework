---
kind: entity
name: ProjectMember
module: Core
endpoints: []
screens: []
---

# Entity: ProjectMember

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — one row per (project, user): the explicit membership record that anchors all access control.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key (UUID v4) |
| project_id | UUID | Required, FK → Project | Project the membership belongs to |
| user_id | UUID | Required | Opaque auth-service user id of the member |
| role | enum: MemberRole | Required, Default: `member` | Membership role |
| created_at | timestamptz | Required, Auto | When the user joined the project |
| updated_at | timestamptz | Required, Auto | Last modification timestamp (e.g., role change) |

## Indexes

- Unique composite index on `(project_id, user_id)` — a user appears at most once per project
- Index on `(user_id)` — "my projects" lookup

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — ProjectMember belongs to Project | `project_id` on `project_members` | Deleting a project deletes its membership rows | — |

## Entity-Specific Enums & Rules

### MemberRole

> *Used only by this entity — enums shared across entities would live in `index.md` Section 5.*

| Value | Description |
|-------|-------------|
| owner | Full control: manage membership, rename or delete the project |
| member | Create and edit tasks and comments within the project |

### Business Rules

- Exactly one row per `(project_id, user_id)` (unique index)
- The project's `owner_id` always holds a row with role `owner`; that row cannot be removed or demoted while the project exists
- Removing a member sets `assignee_id` to NULL on that project's tasks assigned to them, in the same transaction (see `entities/task.md`)
- `user_id` is an opaque auth-service UUID — membership is the app's only notion of user existence; there is no local User entity
