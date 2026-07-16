---
kind: entity
name: Task
module: Core
endpoints: []
screens: []
---

# Entity: Task

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — A unit of work inside a project, carrying explicit structured state: status, day-precision due date, and a single optional assignee.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid | PK (UUID v4) | Primary key |
| project_id | uuid | Required, FK → Project (cascade delete) | The project this task belongs to |
| title | varchar(200) | Required | Task title |
| description | varchar(2000) | Optional | Longer free-text description |
| status | enum: TaskStatus | Required, Default: `todo` | Explicit task state — a structured field, never a prose convention |
| due_date | date | Optional | Day-precision due date — a calendar date with no time of day |
| assignee_id | uuid | Optional | Opaque auth-service user UUID of the single assignee; NULL = unassigned. ID-only, no FK |
| created_at | timestamptz | Required, Auto (UTC) | Record creation timestamp |
| updated_at | timestamptz | Required, Auto (UTC) | Last modification timestamp — drives the derived activity feed |

Table: `tasks`

## Indexes

- Composite index on `(project_id, updated_at)` — project task list and the derived activity feed (recent task changes, newest first)
- Composite index on `(project_id, due_date)` — "when is it due?" answered from the task list

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — this entity is child | `project_id` on `tasks` | Cascade delete (removed with the project) | Tasks exist only inside a project |
| Comment (Core) | 1:N — this entity is parent | `task_id` on `comments` | Cascade delete | Deleting a task removes its comments |

External identity: `assignee_id` references an auth-service user — ID-only, no navigation property, no database-level FK.

## Entity-Specific Enums & Rules

### TaskStatus

> *Used only by this entity.*

| Value | Description |
|-------|-------------|
| todo | Not started |
| in_progress | Being worked on |
| done | Completed |

### Business Rules

- A task is assigned to exactly one **current project member** or left unassigned (`assignee_id` NULL) — membership is checked by the application at assignment time, since auth user ids have no FK target.
- When a member is removed from the project, their tasks in that project are unassigned (`assignee_id` → NULL) by the application.
- `due_date` is a calendar date (day precision) — no time of day, no timezone conversion.
- V1 places no restrictions on status transitions — any status may move to any other.
- Any project member may create and update tasks in that project; non-members have no access.
- Task creation and updates surface in the derived project activity feed via `created_at`/`updated_at` — no event record is written.
