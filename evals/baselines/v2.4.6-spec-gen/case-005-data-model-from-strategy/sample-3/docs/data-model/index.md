# Data Model — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

## 1. Overview

### 1.1 Model Summary

TaskFlow models dependable core task tracking for teams: shared **projects** with an explicit **member** list, **tasks** carrying structured state (status, day-precision due date, single optional assignee), and **comments** attached to the task they discuss. All four entities are owned by the single `Core` module and persisted in one PostgreSQL 16 database. Users are **not** modeled locally — the external auth service issues opaque user UUIDs that are stored in `*_id` columns. The project activity feed is **derived on read** from task and comment records; V1 stores no event log.

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary key strategy | UUID v4 in a column named `id` on every table | CLAUDE.md database convention |
| Soft vs hard deletes | **Hard deletes** — no `deleted_at` columns; deleting a project cascades to everything inside it | CLAUDE.md convention; stakeholder rule "deleting a project removes everything inside it" |
| User identity | Opaque auth-service UUIDs stored in `*_id` columns (`user_id`, `assignee_id`, `author_id`); **no local User entity** | CLAUDE.md convention; the app stores nothing about users beyond their id |
| Timestamp handling | `created_at` + `updated_at` `timestamptz` (always UTC) on every table | CLAUDE.md convention |
| Due dates | `date` column (calendar day, no time of day) | Stakeholder flow specifies day-precision due dates |
| Project ownership | A `role` on the membership record (`owner`/`member`), not an `owner_id` on `projects` | One source of truth for "who can do what in this project" (derive, don't duplicate) |
| Activity feed | Computed on read from `tasks` + `comments`; **no event/log table** | Stakeholder principle "derive, don't duplicate" — V1 stores no separate event log |
| String columns | Explicit varchar limits everywhere (never bare `varchar`) | CLAUDE.md convention |

---

## 2. Module Ownership

> *Every entity belongs to exactly one module. V1 defines a single module, `Core`, so every entity is same-module — there are no cross-module references.*
>
> *This table doubles as the shard directory: every entity listed here has a shard at `entities/<entity>.md`.*

| Module | Entity | Shard | Persistence Unit (repository module) |
|--------|--------|-------|--------------------------------------|
| Core | Project | `entities/project.md` | `src/db/project.ts` |
| Core | ProjectMember | `entities/project-member.md` | `src/db/project-member.ts` |
| Core | Task | `entities/task.md` | `src/db/task.ts` |
| Core | Comment | `entities/comment.md` | `src/db/comment.ts` |

---

## 3. Database Conventions

> *Conventions applied uniformly across all entities (from CLAUDE.md).*

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | snake_case, **plural** | `tasks`, `project_members` |
| Column naming | snake_case | `due_date`, `assignee_id` |
| Primary keys | UUID v4, column named `id` | `id uuid PK` |
| Timestamps | `created_at` + `updated_at` `timestamptz` (always UTC) on every table | `created_at timestamptz NOT NULL` |
| Deletes | **Hard deletes** — no `deleted_at` columns in V1 | `DELETE FROM projects ...` cascades |
| String lengths | Explicit varchar limits, never bare `varchar` | `title varchar(200)` |
| User references | Opaque auth-service UUIDs in `*_id` columns; no `users` table, no FK target | `user_id uuid NOT NULL` |
| Migrations | Plain SQL, numbered `NNN-description.sql` in `migrations/` | `migrations/001-init.sql` |

---

## 4. Relationships Overview

> *The full-model view. Each entity shard also lists its own relationships so it can be loaded standalone — keep the two in sync.*

### 4.1 One-to-Many Relationships

| Parent Entity | Child Entity | Foreign Key | Cascade Behavior |
|---------------|-------------|-------------|-----------------|
| Project | ProjectMember | `project_id` on `project_members` | Cascade delete |
| Project | Task | `project_id` on `tasks` | Cascade delete |
| Task | Comment | `task_id` on `comments` | Cascade delete |

### 4.2 Many-to-Many Relationships

None. Project↔user membership is modeled as the first-class entity **ProjectMember** (it carries a `role`), and users are external to the database — there is no join between two local tables.

### 4.3 Cross-Module References

None — V1 has a single `Core` module, so every reference is same-module.

**External identity references** (ID-only, no database FK — the auth service is the system of record for users):

| Source Entity | Field | Purpose |
|---------------|-------|---------|
| ProjectMember | `user_id` | Which auth-service user this membership belongs to |
| Task | `assignee_id` | The auth-service user the task is assigned to (nullable — unassigned) |
| Comment | `author_id` | The auth-service user who wrote the comment |

### 4.4 Entity-Relationship Diagram

```
                        ┌──────────────────────┐
                        │       projects       │
                        │  - id (PK)           │
                        │  - name              │
                        └──────────┬───────────┘
             1:N (cascade delete)  │  1:N (cascade delete)
            ┌──────────────────────┴──────────────────────┐
            ▼                                             ▼
┌────────────────────────────┐              ┌────────────────────────────┐
│      project_members       │              │           tasks            │
│  - id (PK)                 │              │  - id (PK)                 │
│  - project_id (FK)         │              │  - project_id (FK)         │
│  - user_id  (auth UUID)    │              │  - title, description      │
│  - role (owner|member)     │              │  - status, due_date        │
└────────────────────────────┘              │  - assignee_id (auth UUID) │
                                            └──────────────┬─────────────┘
                                          1:N (cascade delete)
                                                           ▼
                                            ┌────────────────────────────┐
                                            │          comments          │
                                            │  - id (PK)                 │
                                            │  - task_id (FK)            │
                                            │  - author_id (auth UUID)   │
                                            │  - body                    │
                                            └────────────────────────────┘

user_id / assignee_id / author_id hold opaque UUIDs issued by the external
auth service — ID-only references with no local users table and no FK.

The per-project activity feed is DERIVED ON READ from tasks + comments
(newest first) — it has no table of its own.
```

---

## 5. Shared Enums and Value Types

> *Only types used by MORE than one entity belong here.*

### 5.1 Shared Enums

None — every enum in this model is used by exactly one entity and lives in that entity's shard:

- **TaskStatus** → `entities/task.md`
- **MemberRole** → `entities/project-member.md`

### 5.2 Value Objects

None. Due dates are plain `date` columns (day precision); no complex value types exist in V1.

---

## Usage Notes for AI Task Generation

When generating tasks from this document set:

1. **Shard loading**: Read `index.md` plus ONLY the entity shards named by the work item's impact tables — do not read the whole `entities/` directory
2. **Data access**: SQL lives only in `src/db/` repository modules, one per entity (see Section 2) — routers never touch `pg` directly
3. **Field completeness**: Generated repositories and migrations must include all fields defined in the entity's shard with correct types and constraints
4. **Relationship integrity**: Migrations must declare the cascade deletes from Section 4.1 — deleting a project removes its members, tasks, and (via tasks) comments
5. **Enum consistency**: Use the enum values defined in the entity shards — do not invent new values without updating the owning shard
6. **Index awareness**: Include index creation in migration tasks for every index listed in the entity shards
7. **Naming conventions**: Table and column names must follow Section 3; JSON payloads use camelCase keys (mapping happens in the repository layer — never return raw rows)
8. **No local users**: Never create a `users` table or User entity — user UUIDs are opaque `*_id` columns, and membership checks go through `project_members`
9. **Derived activity feed**: The feed is computed on read from `tasks` and `comments` — never add an event/log table for it in V1
10. **New entities**: Create a new shard at `entities/<entity>.md`, add a Module Ownership row (Section 2), add its relationships to Section 4, and record the change in the Changelog

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | spec-generation (Step 1) | Initial data model: Project, ProjectMember, Task, Comment | Derived from stakeholder definition (Scope Lock), ARCHITECTURE.md, and CLAUDE.md conventions |
