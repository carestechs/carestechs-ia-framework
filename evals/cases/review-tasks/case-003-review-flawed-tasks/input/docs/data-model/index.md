# Data Model — TaskFlow

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

## 1. Overview

### 1.1 Model Summary

TaskFlow models projects containing tasks arranged on a kanban board. A single Projects module owns both entities. User identity is external — the auth service issues opaque user UUIDs — so there is no local User entity.

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary keys | UUID v4, column `id` | Safe client-side generation; no sequence coupling |
| Deletes | Hard deletes | Small data set; no audit requirement yet |
| Timestamps | `timestamptz`, always UTC | Unambiguous ordering across time zones |
| User identity | Opaque `*_id` UUIDs from the external auth service; no local User entity | Authentication is out of scope for the app database |

---

## 2. Module Ownership

> *Every entity belongs to exactly one module. This table doubles as the shard directory: every entity listed here has a shard at `entities/<entity>.md` (kebab-case, singular).*

| Module | Entities Owned (shard) | Persistence Unit |
|--------|------------------------|------------------|
| Projects | Project (`entities/project.md`), Task (`entities/task.md`) | Repository modules in `src/db/` — one per entity (`src/db/project.ts`, `src/db/task.ts`) |

---

## 3. Database Conventions

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | snake_case, plural | `tasks` |
| Column naming | snake_case | `due_date`, `created_at` |
| Primary keys | UUID, column named `id` | `id UUID PK` |
| Timestamps | `created_at` + `updated_at` timestamptz on every table | `created_at TIMESTAMPTZ NOT NULL` |
| String lengths | Explicit varchar limits | `title VARCHAR(200)` |
| Migrations | Plain SQL in `migrations/NNN-description.sql` | `migrations/001-init.sql` |

---

## 4. Relationships Overview

> *The full-model view. Each entity shard also lists its own relationships so it can be loaded standalone — keep the two in sync.*

### 4.1 One-to-Many Relationships

| Parent Entity | Child Entity | Foreign Key | Cascade Behavior |
|---------------|-------------|-------------|-----------------|
| Project | Task | `project_id` on `tasks` | Cascade delete |

### 4.2 Many-to-Many Relationships

None yet.

### 4.3 Entity-Relationship Diagram

```
┌──────────────┐       1:N        ┌──────────────┐
│   Project    │─────────────────→│     Task     │
│              │  cascade delete  │              │
│  - id        │                  │  - id        │
│  - name      │                  │  - project_id│
└──────────────┘                  │  - status    │
                                  └──────────────┘
```

---

## 5. Shared Enums and Value Types

None yet — `TaskStatus` is used only by Task and lives in `entities/task.md`.

---

## Usage Notes for AI Task Generation

1. **Shard loading**: Read this index plus ONLY the entity shards named by the work item's impact tables — kebab-case, singular (e.g., entity `Project` → `entities/project.md`; a multi-word entity like `TaskLabel` maps to kebab-case `task-label`). Do not read the whole `entities/` directory.
2. **Data access**: SQL goes in the owning entity's repository module in `src/db/` — routers never query the database directly.
3. **Naming conventions**: Tables and columns must follow Section 3; migration tasks create `migrations/NNN-description.sql` files.
4. **New entities**: Create a new shard at `entities/<entity>.md`, add its Module Ownership row (Section 2) and Relationships Overview entries (Section 4), and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-01 | TaskFlow team | Initial version (Project, Task) | v1.0 baseline |
