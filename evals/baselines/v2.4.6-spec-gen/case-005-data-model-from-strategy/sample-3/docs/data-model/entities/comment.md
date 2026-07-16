---
kind: entity
name: Comment
module: Core
endpoints: []
screens: []
---

# Entity: Comment

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — Discussion attached to the task it concerns, attributed to its author and ordered by time.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid | PK (UUID v4) | Primary key |
| task_id | uuid | Required, FK → Task (cascade delete) | The task this comment belongs to |
| author_id | uuid | Required | Opaque auth-service user UUID of the comment author — ID-only, no FK |
| body | varchar(2000) | Required | Comment text |
| created_at | timestamptz | Required, Auto (UTC) | Record creation timestamp — orders the task's comment thread and feeds the activity feed |
| updated_at | timestamptz | Required, Auto (UTC) | Last modification timestamp |

Table: `comments`

## Indexes

- Composite index on `(task_id, created_at)` — a task's comment thread in time order

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Task (Core) | N:1 — this entity is child | `task_id` on `comments` | Cascade delete (removed with the task, and transitively with the project) | Comments exist only on a task |

External identity: `author_id` references an auth-service user — ID-only, no navigation property, no database-level FK.

## Entity-Specific Enums & Rules

### Business Rules

- The author must be a current member of the task's project at creation time — enforced by the application (membership gates every write).
- Comments are ordered by `created_at` within their task.
- Comments contribute to the derived project activity feed (scoped to the project by joining through `tasks` on `task_id`) — no separate event record is written.
- Comments are hard-deleted with their task (cascade); V1 has no soft delete.
