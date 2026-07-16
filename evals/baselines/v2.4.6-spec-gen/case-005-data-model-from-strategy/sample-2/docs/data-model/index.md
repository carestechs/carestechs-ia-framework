# Data Model — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

## 1. Overview

### 1.1 Model Summary

TaskFlow models a small team task tracker as four entities — Project, ProjectMember, Task, Comment — all owned by the single `Core` module and persisted in one PostgreSQL 16 database. Projects are the access boundary: membership records scope every read and write, tasks live inside projects, and comments live on tasks. Users are **not** modeled locally — the external auth service issues opaque user UUIDs, which appear only in `*_id` columns. The project activity feed is derived on read from task and comment records; no event or log entity exists.

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary key strategy | UUID v4 in a column named `id` on every table | CLAUDE.md database convention |
| Deletes | Hard deletes; `ON DELETE CASCADE` down the containment chain (project → memberships/tasks → comments) | CLAUDE.md forbids `deleted_at` in V1; stakeholder: "deleting a project removes everything inside it" |
| User identity | Opaque auth-service user UUIDs stored in `user_id` / `assignee_id` / `author_id`; **no local User entity** | CLAUDE.md: never model users as a table |
| Activity feed | Computed on read from `tasks` + `comments`; no event table | Stakeholder principle "Derive, don't duplicate" |
| Timestamps | `created_at` + `updated_at` `timestamptz` (always UTC) on every table | CLAUDE.md database convention |
| Due dates | `date` column — day precision, no time of day | Stakeholder flow: "a calendar date; no time of day" |
| Project ownership | Represented by `role = owner` on ProjectMember; no `owner_id` column on Project | The (project, user) membership record already carries the role; avoids duplicated state |
| Enum storage | `varchar(20)` with a `CHECK` constraint | Plain SQL migrations, no ORM; adding a value is a plain `ALTER TABLE` |
| Cross-module references | None — the single `Core` module owns everything | Architecture defines `Core` as the only V1 module |

---

## 2. Module Ownership

> *Every entity belongs to exactly one module. V1 has a single module, `Core`, so every reference is same-module. This table doubles as the shard directory.*

| Module | Entity | Table | Shard | Persistence Unit (repository module) |
|--------|--------|-------|-------|--------------------------------------|
| Core | Project | `projects` | `entities/project.md` | `src/db/project.ts` |
| Core | ProjectMember | `project_members` | `entities/project-member.md` | `src/db/project-member.ts` |
| Core | Task | `tasks` | `entities/task.md` | `src/db/task.ts` |
| Core | Comment | `comments` | `entities/comment.md` | `src/db/comment.ts` |

---

## 3. Database Conventions

> *Applied uniformly across all entities (from CLAUDE.md).*

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | snake_case, plural | `project_members` |
| Column naming | snake_case | `due_date`, `created_at` |
| Primary keys | UUID v4, column named `id` | `id uuid PRIMARY KEY` |
| Timestamps | `created_at` + `updated_at` `timestamptz` (always UTC) on every table | `created_at timestamptz NOT NULL` |
| Deletes | Hard deletes — no `deleted_at` columns in V1 | `DELETE FROM projects WHERE id = $1` |
| String lengths | Explicit varchar limits, never bare `varchar`; long-form content uses `text` | `name varchar(200)` |
| Enum storage | `varchar(20)` + `CHECK` constraint listing the enum values | `status varchar(20) NOT NULL CHECK (status IN ('todo', 'in_progress', 'done'))` |
| User references | Opaque auth-service UUIDs in `*_id` columns; no `users` table, no DB-level FK | `assignee_id uuid NULL` |
| Migrations | Plain SQL, numbered `NNN-description.sql` | `migrations/001-init.sql` |

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

None between owned entities. ProjectMember relates projects to **external** auth-service users and carries data (`role`, audit columns), so it is modeled as a first-class entity — not a bare join table.

### 4.3 Cross-Module References

None — V1 has a single `Core` module, so every entity reference is same-module. The only outward references are to the external auth service (not a module), and they are ID-only by definition:

| Source Entity | Field | Target | Purpose |
|---------------|-------|--------|---------|
| ProjectMember | `user_id` | Auth-service user (external) | The member's identity |
| Task | `assignee_id` | Auth-service user (external) | Current assignee (nullable) |
| Comment | `author_id` | Auth-service user (external) | Attribution, retained after membership removal |

These columns hold opaque UUIDs: no `users` table exists, and no DB-level FK can be declared for them.

### 4.4 Entity-Relationship Diagram

```
                      ┌───────────────────────────┐
                      │         projects          │
                      │ id (uuid PK)              │
                      │ name varchar(200)         │
                      └───────┬───────────┬───────┘
               1:N, cascade   │           │   1:N, cascade
           ┌──────────────────┘           └──────────────────┐
           ▼                                                 ▼
┌───────────────────────────┐               ┌───────────────────────────┐
│      project_members      │               │           tasks           │
│ id (uuid PK)              │               │ id (uuid PK)              │
│ project_id (FK, cascade)  │               │ project_id (FK, cascade)  │
│ user_id (auth user UUID)  │               │ title varchar(200)        │
│ role (MemberRole)         │               │ description text          │
│ UNIQUE(project_id,        │               │ status (TaskStatus)       │
│        user_id)           │               │ due_date date             │
└───────────────────────────┘               │ assignee_id (auth UUID)   │
                                            └─────────────┬─────────────┘
                                                          │ 1:N, cascade
                                                          ▼
                                            ┌───────────────────────────┐
                                            │         comments          │
                                            │ id (uuid PK)              │
                                            │ task_id (FK, cascade)     │
                                            │ author_id (auth UUID)     │
                                            │ body text                 │
                                            └───────────────────────────┘

External identity: user_id / assignee_id / author_id hold opaque auth-service
user UUIDs — there is no users table and no DB-level FK on these columns.
```

---

## 5. Shared Enums and Value Types

> *Only types used by MORE than one entity belong here. V1 has none:*

- **TaskStatus** is used only by Task — defined in `entities/task.md`.
- **MemberRole** is used only by ProjectMember — defined in `entities/project-member.md`.

No shared value objects are defined in V1.

---

## Usage Notes for AI Task Generation

When generating tasks from this document set:

1. **Shard loading**: Read `index.md` plus ONLY the entity shards named by the work item's impact tables — do not read the whole `entities/` directory.
2. **Data access**: SQL lives only in the entity's repository module in `src/db/` (one module per entity — see Module Ownership); routers never touch `pg` directly.
3. **Field completeness**: Generated repositories and migrations must include every field defined in the entity's shard with the exact type and constraints (explicit varchar limits, `timestamptz`, nullability).
4. **Migrations**: Plain SQL in `migrations/NNN-description.sql`; include the `ON DELETE CASCADE` foreign keys, the unique constraint on `project_members (project_id, user_id)`, the enum `CHECK` constraints, and every index listed in the shards.
5. **No User table**: `user_id` / `assignee_id` / `author_id` are opaque auth-service UUIDs — never create a `users` table, never join to one, never add a foreign key on these columns.
6. **Derived feed**: The project activity feed is computed on read from `tasks` and `comments` — never introduce an event/log table or write feed rows.
7. **Membership scoping**: Every generated query must be scoped to projects the caller is a member of, via `project_members`.
8. **Hard deletes**: Use `DELETE`; never add `deleted_at` columns or soft-delete filters.
9. **Enum consistency**: Use the values defined in the owning shard (`TaskStatus`, `MemberRole`) — adding a value means updating that shard and the Changelog below.
10. **New entities**: Create a new shard at `entities/<entity>.md`, add a Module Ownership row (Section 2), add its relationships to Section 4, and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | spec-generation (Step 1) | Initial data model: Project, ProjectMember, Task, Comment (index + 4 entity shards) | Derived from stakeholder definition, architecture, and CLAUDE.md conventions |
