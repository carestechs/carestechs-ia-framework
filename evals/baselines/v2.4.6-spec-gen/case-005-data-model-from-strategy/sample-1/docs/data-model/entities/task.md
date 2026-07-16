---
kind: entity
name: Task
module: Core
endpoints: []
screens: []
---

# Entity: Task

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — a unit of work inside a project, with explicit status, an optional day-precision due date, and at most one assignee.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| project_id | uuid | Required, FK → Project (cascade delete) | Owning project |
| title | varchar(200) | Required | Task title |
| description | text | Optional | Longer free-form description |
| status | enum: TaskStatus | Required, Default: `todo` | Explicit workflow state — a structured field, never a prose convention |
| due_date | date | Optional | Day-precision calendar date; no time of day |
| assignee_id | uuid | Optional | Opaque auth-service user UUID of the single assignee; NULL = unassigned. No DB-level FK (users are external) |
| created_at | timestamptz | Required, Auto | Record creation timestamp (UTC) |
| updated_at | timestamptz | Required, Auto | Last modification timestamp (UTC) |

Table: `tasks`.

## Indexes

- Composite index on `(project_id, status)` — the project task list filters by status
- Composite index on `(project_id, updated_at)` — the activity feed derives "recent task changes, newest first" on read

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — this entity is child | `project_id` on `tasks` | Cascade delete (removed with parent project) | Every task belongs to exactly one project |
| Comment (Core) | 1:N — this entity is parent | `task_id` on `comments` | Cascade delete | Discussion stays attached to the task |
| Auth-service user (external) | N:1 | `assignee_id` — ID only, no DB-level FK, no navigation property | — | The single optional assignee; users are not modeled locally |

## Entity-Specific Enums & Rules

### TaskStatus

> *Used only by this entity.*

| Value | Description |
|-------|-------------|
| todo | Not started |
| in_progress | Actively being worked on |
| done | Completed |

### Business Rules

- Status, due date, and assignee are structured fields — task state is never encoded as prose conventions in comments ("state over chat").
- A task is assigned to **exactly one current project member or left unassigned**: when `assignee_id` is set, the backend must verify the user is a current member of the task's project (no DB constraint can enforce this — users are external).
- When a member is removed from a project, tasks assigned to them in that project are unassigned (`assignee_id` set to NULL) to keep the current-member invariant.
- `due_date` carries no time of day — comparisons and displays are calendar-based.
- Task creation and updates are member-only operations, scoped through the project's membership.
