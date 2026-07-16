---
kind: entity
name: ProjectMember
module: Core
endpoints: []
screens: []
---

# Entity: ProjectMember

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — One membership record per (project, user) pair, carrying the member's role; the unit of access control for everything in a project.*

Table: `project_members`

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| project_id | uuid | Required, FK → projects.id, ON DELETE CASCADE | Project this membership belongs to |
| user_id | uuid | Required; opaque auth-service user UUID — no DB-level FK | The member's identity as issued by the external auth service; nothing else about the user is stored |
| role | enum: MemberRole | Required, default `member` | The member's role in the project |
| created_at | timestamptz | Required, auto (UTC) | When the member was added |
| updated_at | timestamptz | Required, auto (UTC) | Last modification timestamp |

## Indexes

- Unique composite index on `(project_id, user_id)` — enforces one record per (project, user) pair
- Index on `user_id` — "projects the caller is a member of" lookups and per-request membership checks

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — this entity is child | `project_id` on `project_members` | Deleted with its project (cascade) | — |
| Auth-service user (external) | N:1 — ID-only reference | `user_id` — no DB-level FK, no local User table | — | The app stores nothing about the user beyond this UUID |

## Entity-Specific Enums & Rules

### MemberRole

> *Used only by this entity — enums shared across entities would live in `index.md` Section 5.*

| Value | Description |
|-------|-------------|
| owner | The project creator and its first member; adds and removes members |
| member | A regular member: sees project data, creates/updates/assigns tasks, comments |

### Business Rules

- Exactly one membership per (project, user) pair — enforced by the unique index.
- Each project has exactly one `owner` membership in V1: its creator, added in the same transaction as the project. Ownership transfer is out of scope, so the owner membership cannot be removed or downgraded.
- Members are added and removed by the project owner, identified by their auth user id.
- Removing a member unassigns their tasks in that project (the application sets `tasks.assignee_id = NULL` — no FK exists to enforce this in the database).
- Removing a member does not delete their comments: `comments.author_id` retains the UUID for attribution.
- Only members can see or touch a project's data — every read and write is checked against this table.
