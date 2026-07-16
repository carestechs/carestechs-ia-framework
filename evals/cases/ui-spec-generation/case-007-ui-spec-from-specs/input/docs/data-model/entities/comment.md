---
kind: entity
name: Comment
module: Core
endpoints: []
screens: []
---

# Entity: Comment

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — a discussion entry attached to a task, attributed to its author and ordered by time.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key (UUID v4) |
| task_id | UUID | Required, FK → Task | Task the comment is attached to |
| author_id | UUID | Required | Opaque auth-service user id of the comment author |
| body | varchar(5000) | Required | Comment text (plain text in V1) |
| created_at | timestamptz | Required, Auto | Post time — orders the thread and feeds the derived activity feed |
| updated_at | timestamptz | Required, Auto | Last edit time |

## Indexes

- Composite index on `(task_id, created_at)` — thread ordering per task and activity-feed derivation

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Task (Core) | N:1 — Comment belongs to Task | `task_id` on `comments` | Deleting a task deletes its comments | Project deletes cascade transitively via tasks |

## Entity-Specific Enums & Rules

### Business Rules

- `body` must be 1–5000 characters after trimming
- `author_id` must hold a ProjectMember row for the task's project at posting time — enforced in the service layer (external auth UUID, no DB-level FK)
- Only the author may edit a comment; edits update `updated_at`. Deletes are hard deletes, per the model-wide decision
