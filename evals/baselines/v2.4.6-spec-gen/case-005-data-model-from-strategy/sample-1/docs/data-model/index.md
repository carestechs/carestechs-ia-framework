# Data Model — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

## 1. Overview

### 1.1 Model Summary

TaskFlow models dependable core task tracking for teams: a **Project** is a team's shared workspace, an explicit **ProjectMember** list controls who can see and touch it, **Tasks** carry structured state (status, day-precision due date, single optional assignee), and **Comments** keep discussion attached to the task it concerns. A single module (`Core`) owns all four entities. Users are never modeled locally — the external auth service issues opaque user UUIDs that appear only in `*_id` columns. The per-project activity feed is derived on read from task and comment records; V1 stores no event log.

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary key strategy | UUID v4 in a column named `id` on every table | CLAUDE.md database convention |
| Soft vs hard deletes | Hard deletes — no `deleted_at` columns in V1 | CLAUDE.md convention; deleting a project removes everything inside it via cascades |
| User identity | No local User entity; opaque auth-service user UUIDs stored in `*_id` columns with no DB-level FK | Architecture: external auth service owns identity; app stores nothing else about users |
| Timestamp handling | `created_at` + `updated_at` `timestamptz` (always UTC) on every table | CLAUDE.md convention |
| Due dates | `date` column — day precision, no time of day | Stakeholder flow: due dates are calendar dates |
| Activity feed | Derived on read from task and comment records — no event/log entity | "Derive, don't duplicate" principle; V1 stores no separate event log |
| Membership modeling | First-class `ProjectMember` entity, not an M:N join to a users table | Users are external, so no local table to join; the record carries the owner/member role and drives access scoping |
| Module ownership | Single `Core` module owns every entity | Architecture: the only module in V1; every reference is same-module |

---

## 2. Module Ownership

> *Every entity belongs to exactly one module. This table doubles as the shard directory: every entity listed here has a shard at `entities/<entity>.md`.*

| Module | Entities Owned | Persistence Unit |
|--------|---------------|------------------|
| Core | [Project](entities/project.md), [Task](entities/task.md), [ProjectMember](entities/project-member.md), [Comment](entities/comment.md) | One repository module per entity in `src/db/`: `project.ts`, `task.ts`, `project-member.ts`, `comment.ts` |

---

## 3. Database Conventions

> *Conventions applied uniformly across all entities (from CLAUDE.md).*

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | snake_case, plural | `tasks`, `project_members` |
| Column naming | snake_case | `due_date`, `created_at` |
| Primary keys | UUID v4, column named `id` | `id uuid PK` |
| Timestamps | `created_at` + `updated_at` `timestamptz` (always UTC) on every table | `created_at timestamptz NOT NULL` |
| Deletes | Hard deletes — no `deleted_at` columns in V1 | `ON DELETE CASCADE` |
| String lengths | Explicit varchar limits, never bare `varchar` | `name varchar(200)` |
| External user references | Opaque auth-service user UUIDs in `*_id` columns; no local User table, no DB-level FK | `assignee_id uuid NULL` |
| Migrations | Plain SQL, numbered `NNN-description.sql` | `migrations/001-init.sql` |

---

## 4. Relationships Overview

> *The full-model view. Each entity shard also lists its own relationships so it can be loaded standalone — keep the two in sync.*

### 4.1 One-to-Many Relationships

| Parent Entity | Child Entity | Foreign Key | Cascade Behavior |
|---------------|-------------|-------------|-----------------|
| Project | Task | `project_id` on `tasks` | Cascade delete |
| Project | ProjectMember | `project_id` on `project_members` | Cascade delete |
| Task | Comment | `task_id` on `comments` | Cascade delete |

### 4.2 Many-to-Many Relationships

None in V1. The only association that could be M:N — users ↔ projects — is modeled as the first-class [ProjectMember](entities/project-member.md) entity instead, because users are external to the database and the membership record carries data (the role).

### 4.3 Cross-Module References

None — V1 has a single module (`Core`), so every entity reference is same-module. The only ID-only references are **external** (to the auth service, not to another module):

| Source Entity (Module) | Target | Field | Purpose |
|----------------------|--------|-------|---------|
| ProjectMember (Core) | Auth-service user (external) | `user_id` | Who holds the membership |
| Task (Core) | Auth-service user (external) | `assignee_id` | The single optional assignee |
| Comment (Core) | Auth-service user (external) | `author_id` | Comment attribution |

### 4.4 Entity-Relationship Diagram

```
┌─────────────────────┐
│ Project             │
│ (projects)          │
│ - id                │
│ - name              │
└──────┬──────────┬───┘
       │ 1:N      │ 1:N
       ▼          └──────────────────┐
┌─────────────────────┐              ▼
│ ProjectMember       │   ┌──────────────────────┐
│ (project_members)   │   │ Task                 │
│ - id                │   │ (tasks)              │
│ - project_id (FK)   │   │ - id                 │
│ - user_id (ext)     │   │ - project_id (FK)    │
│ - role              │   │ - title, description │
└─────────────────────┘   │ - status             │
                          │ - due_date           │
                          │ - assignee_id (ext)  │
                          └──────────┬───────────┘
                                     │ 1:N
                                     ▼
                          ┌──────────────────────┐
                          │ Comment              │
                          │ (comments)           │
                          │ - id                 │
                          │ - task_id (FK)       │
                          │ - author_id (ext)    │
                          │ - body               │
                          └──────────────────────┘

(ext) = opaque auth-service user UUID — ID-only, no users table, no DB-level FK.
Cascades: deleting a project deletes its tasks and memberships; deleting a task
deletes its comments. The activity feed is derived on read from tasks + comments.
```

---

## 5. Shared Enums and Value Types

### 5.1 Shared Enums

None in V1 — no enum is used by more than one entity. Entity-specific enums live in their shards:

- `TaskStatus` — [entities/task.md](entities/task.md)
- `MemberRole` — [entities/project-member.md](entities/project-member.md)

### 5.2 Value Objects

None in V1. The day-precision due date is a plain `date` column, not a value object.

---

## Usage Notes for AI Task Generation

When generating tasks from this document set:

1. **Shard loading**: Read `index.md` plus ONLY the entity shards named by the work item's impact tables — do not read the whole `entities/` directory
2. **Data access**: SQL lives only in `src/db/` repository modules, one per entity (e.g. `src/db/task.ts`) — routers never touch `pg` directly
3. **Field completeness**: Generated migrations and repository code must include every field defined in the entity's shard with the exact types and constraints
4. **Relationship integrity**: Apply the cascade behaviors from the shard tables (`ON DELETE CASCADE` on same-module FKs); external user-id columns get **no** foreign key
5. **Enum consistency**: `TaskStatus` and `MemberRole` values are defined in their entity shards — do not invent new values without updating the owning shard
6. **Index awareness**: Create the indexes listed in each shard's Indexes section in the same migration as the table
7. **Naming conventions**: Tables and columns follow Section 3; JSON payloads use camelCase keys and never expose raw database rows
8. **Membership scoping**: Every read and write is scoped to projects the caller is a member of — queries join through `project_members` for the calling user
9. **No derived-data tables**: The activity feed is computed on read from `tasks` and `comments` — never generate an event/log table for it
10. **New entities**: Create a new shard at `entities/<entity>.md`, add a Module Ownership row (Section 2), add its relationships to Section 4, and record the change in the Changelog

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | spec-generation (Step 1) | Initial sharded data model: Project, Task, ProjectMember, Comment | Derived from stakeholder definition, architecture, and CLAUDE.md at the strategy stage |
