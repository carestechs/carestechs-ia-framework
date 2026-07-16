---
kind: entity
name: Project
module: Core
endpoints: []
screens: []
---

# Entity: Project

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — A team's shared workspace: the container and access boundary for tasks, membership, and comments.*

Table: `projects`

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| name | varchar(200) | Required, non-empty | Project name; changed by the rename operation |
| created_at | timestamptz | Required, auto (UTC) | Record creation timestamp |
| updated_at | timestamptz | Required, auto (UTC) | Last modification timestamp |

## Indexes

- None beyond the primary key — projects are fetched by `id`; "projects the caller belongs to" resolves through the `user_id` index on `project_members` (see `entities/project-member.md`).

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| ProjectMember (Core) | 1:N — this entity is parent | `project_id` on `project_members` | Cascade delete | The creator's `owner` membership is created in the same transaction as the project |
| Task (Core) | 1:N — this entity is parent | `project_id` on `tasks` | Cascade delete | Deleting a project deletes its tasks and, via tasks, their comments |

## Entity-Specific Enums & Rules

### Business Rules

- Creating a project inserts the creator's ProjectMember record with role `owner` in the same transaction — a project never exists without an owner.
- There is no `owner_id` column: ownership is read from the `owner` role on `project_members` ("derive, don't duplicate").
- Every read and write of project data is scoped to callers holding a membership record for the project.
- Deleting a project hard-deletes all of its memberships, tasks, and comments via `ON DELETE CASCADE` — no soft-delete marker exists.
