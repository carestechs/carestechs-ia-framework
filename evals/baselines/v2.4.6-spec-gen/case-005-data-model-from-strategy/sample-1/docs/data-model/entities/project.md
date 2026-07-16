---
kind: entity
name: Project
module: Core
endpoints: []
screens: []
---

# Entity: Project

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — a team's shared workspace; owns the task list and the explicit member list.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| name | varchar(200) | Required | Project name; rename is the only V1 update |
| created_at | timestamptz | Required, Auto | Record creation timestamp (UTC) |
| updated_at | timestamptz | Required, Auto | Last modification timestamp (UTC) |

Table: `projects`.

## Indexes

- None beyond the primary key — projects are looked up by `id`, and "projects for the calling user" is served by the `user_id` index on `project_members`.

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Task (Core) | 1:N — this entity is parent | `project_id` on `tasks` | Cascade delete | Deleting a project removes its tasks (and, transitively, their comments) |
| ProjectMember (Core) | 1:N — this entity is parent | `project_id` on `project_members` | Cascade delete | Memberships are removed with the project |

## Entity-Specific Enums & Rules

### Business Rules

- Creating a project also creates a `ProjectMember` record for the creating user with role `owner` — the creator is the project's first member.
- Deleting a project hard-deletes everything inside it: tasks, their comments, and membership records (cascade; no soft delete in V1).
- Only members can see or touch a project's data — every read and write on a project and its children is scoped through `project_members`.
