---
kind: entity
name: Task
module: Core
endpoints: []
screens: []
---

# Entity: Task

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — A unit of tracked work inside a project, with explicit status, an optional day-precision due date, and at most one assignee.*

Table: `tasks`

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| project_id | uuid | Required, FK → projects.id, ON DELETE CASCADE | Project the task belongs to |
| title | varchar(200) | Required, non-empty | Task title |
| description | text | Optional (nullable) | Long-form task details |
| status | enum: TaskStatus | Required, default `todo` | Explicit task state — a structured field, never a prose convention |
| due_date | date | Optional (nullable) | Day-precision calendar date; no time of day, no timezone |
| assignee_id | uuid | Optional (nullable); opaque auth-service user UUID — no DB-level FK | Current assignee; must be a current member of `project_id`, or NULL for unassigned |
| created_at | timestamptz | Required, auto (UTC) | Record creation timestamp |
| updated_at | timestamptz | Required, auto (UTC) | Last modification timestamp — ordering key for the derived activity feed |

## Indexes

- Composite index on `(project_id, updated_at)` — project task list and the derived activity feed ("recent task changes, newest first")
- Composite index on `(project_id, due_date)` — due-date ordering ("who owns this and when is it due?" from the task list alone)
- Composite index on `(project_id, assignee_id)` — assignee filters and bulk unassignment when a member is removed

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — this entity is child | `project_id` on `tasks` | Deleted with its project (cascade) | — |
| Comment (Core) | 1:N — this entity is parent | `task_id` on `comments` | Cascade delete | Discussion stays attached to the task it concerns |
| Auth-service user (external) | N:1 — ID-only reference | `assignee_id` — no DB-level FK, no local User table | Set NULL on membership removal (application-enforced) | A task is assigned to exactly one current project member, or left unassigned |

## Entity-Specific Enums & Rules

### TaskStatus

> *Used only by this entity — enums shared across entities would live in `index.md` Section 5. The stakeholder definition mandates an explicit status field without enumerating values; these are the minimal V1 lifecycle. Adding a value is a data-model change: update this table and the index Changelog.*

| Value | Description |
|-------|-------------|
| todo | Created, work not started |
| in_progress | Actively being worked on |
| done | Completed |

### Business Rules

- `assignee_id` is either NULL or the auth user UUID of a **current** member of the task's project — validated by the application on every assignment (no FK exists for the database to enforce it).
- When a membership is removed, the backend sets `assignee_id = NULL` on that user's tasks in the project, keeping "assigned to a current member" true.
- All status transitions are permitted in V1 — no transition matrix.
- `due_date` carries no time or timezone; comparisons ("due today") are plain calendar-date comparisons.
- Task creates and updates surface in the project activity feed, which is derived on read — no event rows are written.
