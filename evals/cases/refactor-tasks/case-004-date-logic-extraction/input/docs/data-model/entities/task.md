---
kind: entity
name: Task
module: Projects
endpoints: [tasks]
screens: [project-board, task-detail-panel]
---

# Entity: Task

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

> *Module: Projects — a unit of work shown as a card on the project board. Repository: `src/db/task.ts`; exposed via `src/api/tasks.ts`.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| project_id | UUID | Required, FK → Project | Owning project |
| title | varchar(200) | Required | Card title shown on the board |
| description | text | Optional | Markdown body shown in the task detail panel |
| status | enum: TaskStatus | Required, Default: `todo` | Board column the task sits in |
| position | integer | Required | Ordering within the `(project_id, status)` column, 0-based |
| assignee_id | UUID | Optional | Opaque user id from the auth service |
| due_date | timestamptz | Optional | Due date — the calendar date picked in the detail panel, stored as 00:00:00 UTC of that date (date-only semantics) |
| created_at | timestamptz | Required, Auto | Record creation timestamp |
| updated_at | timestamptz | Required, Auto | Last modification timestamp |

## Indexes

- Composite index on `(project_id, status, position)` — board column queries

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Projects) | N:1 — Task belongs to Project | `project_id` on `tasks` | Deleting a project deletes its tasks | — |

## Entity-Specific Enums & Rules

### TaskStatus

| Value | Description |
|-------|-------------|
| todo | Task sits in the To Do column |
| in_progress | Task is being worked on |
| done | Task is finished |

### Business Rules

- `title` must be 1–200 characters after trimming
- `position` values are contiguous within a `(project_id, status)` pair; moving a task renumbers the affected columns in one transaction
- A task is **overdue** only when its due date has fully passed in the viewing user's timezone — i.e., from 00:00 local time of the day *after* the due date. The board's Overdue filter applies this rule server-side (see `docs/api-spec/endpoints/tasks.md`, `filter`/`tz` parameters)
