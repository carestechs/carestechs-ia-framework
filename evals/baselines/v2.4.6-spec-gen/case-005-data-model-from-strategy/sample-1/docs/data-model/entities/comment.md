---
kind: entity
name: Comment
module: Core
endpoints: []
screens: []
---

# Entity: Comment

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — a member's remark attached to a task, attributed to its author and ordered by time.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| task_id | uuid | Required, FK → Task (cascade delete) | The task this comment is attached to |
| author_id | uuid | Required | Opaque auth-service user UUID of the authoring member. No DB-level FK (users are external) |
| body | text | Required | Comment text |
| created_at | timestamptz | Required, Auto | Record creation timestamp (UTC); comments are ordered by this |
| updated_at | timestamptz | Required, Auto | Last modification timestamp (UTC) |

Table: `comments`.

## Indexes

- Composite index on `(task_id, created_at)` — serves the time-ordered comment list per task and the per-project activity feed's join through `tasks`

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Task (Core) | N:1 — this entity is child | `task_id` on `comments` | Cascade delete (removed with parent task) | Also removed transitively when a project is deleted |
| Auth-service user (external) | N:1 | `author_id` — ID only, no DB-level FK, no navigation property | — | Attributes the comment to its author |

## Entity-Specific Enums & Rules

### Business Rules

- The author must be a current member of the task's project at write time — enforced by the backend (no DB constraint; users are external).
- Comments are listed in time order (`created_at`), and the activity feed shows recent comment changes newest first.
- Comment records are one of the two sources (with tasks) from which the per-project activity feed is **derived on read** — there is no separate event entity.
- Hard deletes only (V1): comments disappear with their task, and with the project via the task cascade.
