---
kind: entity
name: Project
module: Core
endpoints: []
screens: []
---

# Entity: Project

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — a workspace with an explicit member list that owns tasks. Repository: `src/db/project.ts` (planned).*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key (UUID v4) |
| name | varchar(120) | Required, Unique (case-insensitive) | Project name shown in the app header |
| description | text | Optional | Short summary of the project |
| owner_id | UUID | Required | Opaque auth-service user id of the project owner |
| created_at | timestamptz | Required, Auto | Record creation timestamp |
| updated_at | timestamptz | Required, Auto | Last modification timestamp |

## Indexes

- Unique index on `lower(name)`

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Task (Core) | 1:N — Project is parent | `project_id` on `tasks` | Cascade delete | A project's tasks (and, transitively, their comments) die with it |
| ProjectMember (Core) | 1:N — Project is parent | `project_id` on `project_members` | Cascade delete | Membership rows die with the project |

## Entity-Specific Enums & Rules

### Business Rules

- `name` must be 1–120 characters after trimming, unique case-insensitively across all projects
- Creating a project also creates a ProjectMember row for `owner_id` with role `owner`, in the same transaction
- `owner_id` is an opaque auth-service UUID — never joined to a local user table (none exists)
