---
kind: entity
name: ProjectMember
module: Core
endpoints: []
screens: []
---

# Entity: ProjectMember

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Module: Core — one record per (project, user) pair; grants access to the project and carries the member's role.*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid (v4) | PK | Primary key |
| project_id | uuid | Required, FK → Project (cascade delete) | The project this membership belongs to |
| user_id | uuid | Required | Opaque auth-service user UUID; the app stores nothing else about the user. No DB-level FK (no local User table) |
| role | enum: MemberRole | Required, Default: `member` | Owner/member role carried by the membership |
| created_at | timestamptz | Required, Auto | Record creation timestamp (UTC) |
| updated_at | timestamptz | Required, Auto | Last modification timestamp (UTC) |

Table: `project_members`.

## Indexes

- Unique composite index on `(project_id, user_id)` — exactly one membership record per (project, user) pair
- Index on `user_id` — lists the calling user's projects; membership scoping runs on every read and write

## Relationships

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| Project (Core) | N:1 — this entity is child | `project_id` on `project_members` | Cascade delete (removed with parent project) | Membership never outlives its project |
| Auth-service user (external) | N:1 | `user_id` — ID only, no DB-level FK, no navigation property | — | Identifies who holds the membership |

## Entity-Specific Enums & Rules

### MemberRole

> *Used only by this entity.*

| Value | Description |
|-------|-------------|
| owner | Full control: manages membership, renames and deletes the project (the creator's role) |
| member | Creates and updates tasks, comments, and views the project |

### Business Rules

- Project creation inserts the creator's membership with role `owner` — every project starts with its owner as the first member.
- Only the owner adds or removes members; members are added by their auth-service user id.
- One record per (project, user) pair — enforced by the unique `(project_id, user_id)` index.
- Every read and write in the system is scoped to projects the caller is a member of; non-members get no access to a project's data.
- Removing a member unassigns any tasks assigned to them in that project (see Task business rules).
