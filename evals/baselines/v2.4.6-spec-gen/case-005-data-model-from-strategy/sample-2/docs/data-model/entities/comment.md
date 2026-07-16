---
kind: entity
name: Comment
module: Core
endpoints: []
screens: []
---

# Entity: Comment

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — A member's remark on a task, attributed to its author and ordered by time.*

Table: `comments`

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| task_id | uuid | Required, FK → tasks.id, ON DELETE CASCADE | Task the comment is attached to |
| author_id | uuid | Required; opaque auth-service user UUID — no DB-level FK | Comment author; retained even if the author later leaves the project |
| body | text | Required, non-empty | Comment text |
| created_at | timestamptz | Required, auto (UTC) | Posting time — ordering key for the thread and the derived activity feed |
| updated_at | timestamptz | Required, auto (UTC) | Last modification timestamp |

## Indexes

- Composite index on `(task_id, created_at)` — per-task comment thread ordered by time; also drives the comment side of the derived activity feed (comments joined to `tasks` to scope by `project_id`)

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Task (Core) | N:1 — this entity is child | `task_id` on `comments` | Deleted with its task (cascade) | Project deletion cascades here through `tasks` |
| Auth-service user (external) | N:1 — ID-only reference | `author_id` — no DB-level FK, no local User table | — | Attribution survives membership removal |

## Entity-Specific Enums & Rules

### Business Rules

- The author must be a current member of the task's project at posting time (application-enforced).
- Per-task comments are returned ordered by `created_at`; the project activity feed lists comment activity newest first.
- Comment records appear in the derived activity feed read from this table — no separate event rows are written.
- Comments are hard-deleted with their task (and transitively with the project); no soft-delete marker.
