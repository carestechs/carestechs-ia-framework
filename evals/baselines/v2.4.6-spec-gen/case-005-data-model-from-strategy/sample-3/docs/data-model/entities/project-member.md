---
kind: entity
name: ProjectMember
module: Core
endpoints: []
screens: []
---

# Entity: ProjectMember

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — One record per (project, user) pair: grants project access and carries the member's role.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid | PK (UUID v4) | Primary key |
| project_id | uuid | Required, FK → Project (cascade delete) | The project this membership belongs to |
| user_id | uuid | Required | Opaque auth-service user UUID — ID-only, no local users table, no FK |
| role | enum: MemberRole | Required, Default: `member` | The member's role in this project |
| created_at | timestamptz | Required, Auto (UTC) | Record creation timestamp (when the member was added) |
| updated_at | timestamptz | Required, Auto (UTC) | Last modification timestamp |

Table: `project_members`

## Indexes

- Unique composite index on `(project_id, user_id)` — enforces one membership record per (project, user) pair
- Partial unique index on `(project_id)` where `role = 'owner'` — enforces exactly one owner per project
- Index on `user_id` — lists the projects a user is a member of

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — this entity is child | `project_id` on `project_members` | Cascade delete (removed with the project) | Grants the user access to the project |

External identity: `user_id` references an auth-service user — ID-only, no navigation property, no database-level FK.

## Entity-Specific Enums & Rules

### MemberRole

> *Used only by this entity.*

| Value | Description |
|-------|-------------|
| owner | Project owner — manages membership (add/remove members); every project has exactly one |
| member | Regular member — full access to the project's tasks, comments, and feed |

### Business Rules

- One membership record per (project, user) pair (unique index).
- Every project has exactly one `owner` membership (partial unique index); the creator becomes the owner when the project is created.
- Only the owner adds or removes members; members are added by their auth user id.
- The owner's membership cannot be removed — V1 has no ownership transfer.
- Removing a member unassigns their tasks in that project (`tasks.assignee_id` → NULL) — enforced by the application, since auth user ids have no FK target.
- Membership gates all access: every read and write in the system is scoped to projects where the caller has a membership record.
