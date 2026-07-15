---
kind: entity
name: Project
module: Projects
endpoints: [tasks]
screens: [project-board]
---

# Entity: Project

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

> *Module: Projects — a workspace that owns a board of tasks. Repository: `src/db/project.ts`. Its tasks are exposed through the nested route in `src/api/tasks.ts`.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| name | varchar(120) | Required, Unique (case-insensitive) | Project name shown in the app header |
| description | text | Optional | Short summary shown on hover |
| owner_id | UUID | Required | Opaque user id of the project owner (auth service) |
| created_at | timestamptz | Required, Auto | Record creation timestamp |
| updated_at | timestamptz | Required, Auto | Last modification timestamp |

## Indexes

- Unique index on `lower(name)`

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Task (Projects) | 1:N — Project is parent | `project_id` on `tasks` | Cascade delete | Board contents die with the project |

## Entity-Specific Enums & Rules

### Business Rules

- `name` must be 1–120 characters after trimming, unique case-insensitively across all projects
- Members with edit rights are resolved by the auth service; the database stores only opaque user ids
