---
kind: entity
name: Task
module: Core
endpoints: []
screens: []
---

# Entity: Task

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — a unit of work inside a project, with an explicit status, an optional day-precision due date, and at most one assignee.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key (UUID v4) |
| project_id | UUID | Required, FK → Project | Owning project |
| title | varchar(200) | Required | Task title |
| description | text | Optional | Longer body text |
| status | enum: TaskStatus | Required, Default: `todo` | Workflow state |
| due_date | date | Optional | Day-precision deadline (calendar date, no time component) |
| assignee_id | UUID | Optional | Opaque auth-service user id; must belong to a current member of the owning project |
| created_at | timestamptz | Required, Auto | Record creation timestamp |
| updated_at | timestamptz | Required, Auto | Last modification timestamp |

## Indexes

- Composite index on `(project_id, status)` — status filtering per project
- Composite index on `(project_id, due_date)` — due-date views per project
- Composite index on `(project_id, updated_at)` — activity-feed derivation

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — Task belongs to Project | `project_id` on `tasks` | Deleting a project deletes its tasks | — |
| Comment (Core) | 1:N — Task is parent | `task_id` on `comments` | Cascade delete | A task's comments die with it |

## Entity-Specific Enums & Rules

### TaskStatus

> *Used only by this entity — enums shared across entities would live in `index.md` Section 5.*

| Value | Description |
|-------|-------------|
| todo | Not started |
| in_progress | Being worked on |
| done | Finished |

### Business Rules

- `title` must be 1–200 characters after trimming
- `assignee_id`, when set, must match the `user_id` of a ProjectMember row of the owning project — enforced in the service layer (the id is an external auth UUID, so there is no DB-level FK)
- When a member is removed from a project, `assignee_id` is set to NULL on that project's tasks assigned to them, in the same transaction (no dangling assignments)
