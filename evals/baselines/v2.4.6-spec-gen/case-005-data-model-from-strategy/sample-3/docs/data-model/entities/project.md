---
kind: entity
name: Project
module: Core
endpoints: []
screens: []
---

# Entity: Project

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — A team's shared workspace: the container for membership, tasks, and the derived activity feed.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid | PK (UUID v4) | Primary key |
| name | varchar(200) | Required | Project name; editable (rename is a backend responsibility) |
| created_at | timestamptz | Required, Auto (UTC) | Record creation timestamp |
| updated_at | timestamptz | Required, Auto (UTC) | Last modification timestamp |

Table: `projects`

## Indexes

- None beyond the primary key — projects are listed per user via membership (see the `user_id` index on ProjectMember).

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| ProjectMember (Core) | 1:N — this entity is parent | `project_id` on `project_members` | Cascade delete | Deleting a project removes its membership records |
| Task (Core) | 1:N — this entity is parent | `project_id` on `tasks` | Cascade delete | Deleting a project removes its tasks (and, via tasks, their comments) |

## Entity-Specific Enums & Rules

### Business Rules

- Creating a project atomically creates its first ProjectMember record: the creator with role `owner`.
- The project owner is the single membership record with role `owner` — there is no `owner_id` column on `projects` (derive, don't duplicate).
- Deleting a project hard-deletes everything inside it: memberships, tasks, and comments (cascade).
- Only members can see or touch a project's data — every read and write is scoped to projects the caller is a member of.
- The project activity feed (recent task and comment changes, newest first) is computed on read from this project's `tasks` and `comments` records — no event data is stored on this entity or anywhere else in V1.
