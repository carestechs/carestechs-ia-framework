# Data Model — [Product Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

> *Sharded document set: cross-cutting content lives in this index; every entity has its own shard at `entities/<entity>.md` (kebab-case, **singular** — e.g., entity `TaskLabel` → `entities/task-label.md`). Copy `entities/TEMPLATE-entity.md` to add one. Work items name entities as retrieval keys — task generation loads this index plus only the named shards.*

## 1. Overview

### 1.1 Model Summary

<!-- TODO: Describe the domain at a high level — what the system models, how many modules own data, and any key modeling decisions -->

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Primary key strategy --> | <!-- e.g., UUIDs --> | <!-- e.g., No sequential ID leaks --> |
| <!-- e.g., Soft vs hard deletes --> | <!-- e.g., Soft deletes with `deleted_at` --> | <!-- e.g., Audit trail --> |
| <!-- e.g., Timestamp handling --> | <!-- e.g., TIMESTAMPTZ, always UTC --> | <!-- e.g., Timezone consistency --> |

## 2. Module Ownership

<!-- TODO: Every entity belongs to exactly one module. This table doubles as the shard directory — every entity listed here must have a shard at entities/<entity>.md -->

| Module | Entities Owned | Persistence Unit [e.g., EF Core DbContext / Prisma schema] |
|--------|---------------|-------------------------------------------------------------|
| <!-- e.g., Users --> | <!-- e.g., User, Role --> | <!-- e.g., UsersDbContext --> |
| <!-- e.g., Projects --> | <!-- e.g., Project, ProjectMember --> | <!-- e.g., ProjectsDbContext --> |

## 3. Database Conventions

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | <!-- e.g., snake_case, plural --> | <!-- e.g., task_items --> |
| Column naming | <!-- e.g., snake_case --> | <!-- e.g., due_date --> |
| Primary keys | <!-- e.g., UUID, column named `id` --> | <!-- e.g., id UUID PK --> |
| Timestamps | <!-- e.g., TIMESTAMPTZ, always present --> | <!-- e.g., created_at, updated_at --> |

## 4. Relationships Overview

<!-- The full-model view. Each entity shard also lists its own relationships so it can be loaded standalone — keep the two in sync. -->

### 4.1 One-to-Many Relationships

| Parent Entity | Child Entity | Foreign Key | Cascade Behavior |
|---------------|-------------|-------------|-----------------|
| <!-- e.g., Project --> | <!-- e.g., Task --> | <!-- e.g., project_id on Task --> | <!-- e.g., Cascade delete --> |

### 4.2 Many-to-Many Relationships

| Entity A | Entity B | Join Table | Additional Fields |
|----------|----------|-----------|-------------------|
| <!-- e.g., Task --> | <!-- e.g., Label --> | <!-- e.g., task_labels --> | <!-- e.g., assigned_at --> |

### 4.3 Cross-Module References

<!-- These are ID-only references — no navigation properties across module boundaries -->

| Source Entity (Module) | Target Entity (Module) | Field | Purpose |
|----------------------|----------------------|-------|---------|
| <!-- e.g., Task (Tasks) --> | <!-- e.g., User (Users) --> | <!-- e.g., assignee_id --> | <!-- e.g., Task assignment --> |

### 4.4 Entity-Relationship Diagram

```
<!-- TODO: ASCII or text-based overview of the full data model -->
```

## 5. Shared Enums and Value Types

### 5.1 Shared Enums

<!-- TODO: Only enums used by MORE than one entity belong here — an enum used by a single entity lives in that entity's shard -->

#### [EnumName]

> *Used by: [EntityA.field, EntityB.field]*

| Value | Description |
|-------|-------------|
| <!-- e.g., Active --> | <!-- e.g., Currently active --> |
| <!-- e.g., Archived --> | <!-- e.g., Soft-archived, hidden from default views --> |

### 5.2 Value Objects

<!-- TODO: Complex types without their own identity (not separate tables), shared across entities — e.g., Money, Address. DELETE this subsection if you have none. -->

#### [ValueObjectName]

| Property | Type | Description |
|----------|------|-------------|
| <!-- e.g., amount --> | <!-- e.g., decimal --> | <!-- e.g., Always in minor units --> |

## Usage Notes for AI Task Generation

- **Shard loading**: Read this `index.md` plus ONLY the entity shards named by the work item's impact tables — do not read the whole `entities/` directory
- **Module boundaries**: Every data-access task must target the correct module's persistence unit [e.g., DbContext / Prisma client / repository]
- **Field completeness**: Generated entity classes must include all fields defined in the entity's shard
- **Relationship integrity**: Ensure cascade behaviors and cross-module ID-only references are respected
- **Naming conventions**: Table and column names must follow the conventions in Section 3
- **New entities**: Create a new shard at `entities/<entity>.md` (copy `entities/TEMPLATE-entity.md`), add a Module Ownership row (Section 2), add its relationships to Section 4, and record the change in the Changelog

## Changelog

<!-- Records changes across the whole docs/data-model/ set — shard edits included. Update the freshness stamp on every file touched. -->

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |
