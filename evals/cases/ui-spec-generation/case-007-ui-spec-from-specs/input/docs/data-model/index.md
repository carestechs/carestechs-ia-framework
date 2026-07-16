# Data Model — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

## 1. Overview

### 1.1 Model Summary

TaskFlow V1 models projects whose explicit members work on tasks and discuss them in comments. A single Core module owns all four entities: Project, Task, ProjectMember, Comment. User identity is external — the auth service issues opaque user UUIDs — so there is no local User entity. The project activity feed is derived on read from task and comment records; V1 stores no event table.

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary keys | UUID v4, column `id` | Safe client-side generation; no sequence coupling |
| Deletes | Hard deletes, cascading down the ownership chain | Small data set; no audit requirement in V1 |
| Timestamps | `timestamptz`, always UTC | Unambiguous ordering across time zones |
| Due dates | `date` (day precision, no time component) | Stakeholder flow specifies calendar-date deadlines |
| User identity | Opaque `*_id` UUIDs from the external auth service; no local User entity | Authentication is out of scope for the app database |
| Membership | Explicit ProjectMember entity, not a bare join table | Carries a role and anchors all access control |
| Activity feed | Derived on read from `tasks` and `comments` | Stakeholder decision: no dedicated event table in V1 |

---

## 2. Module Ownership

> *Every entity belongs to exactly one module. This table doubles as the shard directory: every entity listed here has a shard at `entities/<entity>.md` (kebab-case, singular).*

| Module | Entities Owned (shard) | Persistence Unit |
|--------|------------------------|------------------|
| Core | Project (`entities/project.md`), Task (`entities/task.md`), ProjectMember (`entities/project-member.md`), Comment (`entities/comment.md`) | Repository modules in `src/db/` — one per entity (`src/db/project.ts`, `src/db/task.ts`, `src/db/project-member.ts`, `src/db/comment.ts`) |

---

## 3. Database Conventions

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | snake_case, plural | `project_members` |
| Column naming | snake_case | `due_date`, `created_at` |
| Primary keys | UUID v4, column named `id` | `id UUID PK` |
| Timestamps | `created_at` + `updated_at` timestamptz (UTC) on every table | `created_at TIMESTAMPTZ NOT NULL` |
| String lengths | Explicit varchar limits | `title VARCHAR(200)` |
| Deletes | Hard deletes — no `deleted_at` columns in V1 | `DELETE FROM comments WHERE id = $1` |
| Migrations | Plain SQL in `migrations/NNN-description.sql` | `migrations/001-init.sql` |

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

None. Project-to-user membership is modeled as the explicit ProjectMember entity because it carries a role and anchors access control — and users are external to the database, so there is no user table to join against.

### 4.3 Cross-Module References

None — Core is the only module in V1. Columns holding auth-service user ids (`owner_id`, `user_id`, `assignee_id`, `author_id`) are opaque external references, not foreign keys.

### 4.4 Entity-Relationship Diagram

```
┌───────────────┐    1:N (cascade)    ┌──────────────────┐
│    Project    │────────────────────→│  ProjectMember   │
│               │                     │  - project_id    │
│  - id         │                     │  - user_id       │
│  - name       │                     │  - role          │
│  - owner_id   │                     └──────────────────┘
└──────┬────────┘
       │ 1:N (cascade)
       ▼
┌───────────────┐    1:N (cascade)    ┌──────────────────┐
│     Task      │────────────────────→│     Comment      │
│  - project_id │                     │  - task_id       │
│  - status     │                     │  - author_id     │
│  - due_date   │                     │  - body          │
│  - assignee_id│                     └──────────────────┘
└───────────────┘
```

---

## 5. Shared Enums and Value Types

None shared — each enum is used by exactly one entity and lives in its shard: `TaskStatus` in `entities/task.md`, `MemberRole` in `entities/project-member.md`.

---

## Usage Notes for AI Task Generation

1. **Shard loading**: Read this index plus ONLY the entity shards named by the work item's impact tables — kebab-case, singular (e.g., entity `ProjectMember` → `entities/project-member.md`). Do not read the whole `entities/` directory.
2. **Data access**: SQL goes in the owning entity's repository module in `src/db/` — routers never query the database directly.
3. **Access control**: every project-scoped query filters through `project_members` — a caller must hold a membership row for the target project.
4. **Naming conventions**: tables and columns must follow Section 3; migration tasks create `migrations/NNN-description.sql` files.
5. **Activity feed**: derive it on read from `tasks` and `comments` (`created_at`/`updated_at` ordering) — do not add an event table without a scope change.
6. **New entities**: create a new shard at `entities/<entity>.md`, add its Module Ownership row (Section 2) and Relationships Overview entries (Section 4), and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | spec-generation | Initial data model (Project, Task, ProjectMember, Comment) | Derived from stakeholder Scope Lock V1 |
