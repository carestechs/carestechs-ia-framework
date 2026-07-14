# Data Model Template

> **Purpose**: Document the domain entities, their fields, relationships, and module ownership. This provides AI with the structural understanding needed to generate data-layer tasks, validate feature scope, and ensure cross-module boundaries are respected.

> **Context budget note:** This document is loaded into AI context. Keep it contract-style —
> tables, schemas, rules, one example each. Move narrative and history to `docs/rationale/`
> and link it; rationale files are never loaded by default.

---

## Directory Layout

The data model is a **sharded document set**, not a single file. Cross-cutting content lives in `index.md`; every entity lives in its own shard. Work items name entities in their impact tables, and task generation loads `index.md` plus only the named shards — shard boundaries are retrieval boundaries.

```
docs/data-model/
  index.md                  # Key Modeling Decisions, Module Ownership, Database Conventions,
                            # Relationships Overview (ER diagram), shared Enums/Value Types,
                            # Usage Notes for AI Task Generation, Changelog
  entities/<entity>.md      # ONE entity per file: owning module, fields table, relationships,
                            # entity-specific enums & rules
```

Rules:

- **One entity per shard.** Never fold two entities into one file, and never define an entity inside `index.md`.
- **Shards are self-sufficient with the index.** Loading `index.md` + one shard must give everything needed to work on that entity — each shard lists its own relationships even though the index carries the overview.
- **Cross-cutting only in the index.** A decision, convention, or enum used by more than one entity belongs in `index.md`; anything specific to a single entity belongs in that entity's shard.

---

## Index File (`docs/data-model/index.md`)

Everything from here down to "Entity Shard" defines the contents of `index.md`. Start the file with its own H1 and the freshness stamp directly beneath it:

```
# Data Model — [Product Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->
```

## 1. Overview

### 1.1 Model Summary

[One paragraph describing the domain at a high level — what the system models, how many modules own data, and any key modeling decisions (soft deletes, UUIDs, multi-tenancy, etc.)]

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Primary key strategy] | [e.g., UUIDs] | [Why] |
| [Soft vs hard deletes] | [e.g., Soft deletes with `deleted_at`] | [Why] |
| [Multi-tenancy approach] | [e.g., Shared DB with tenant column] | [Why] |
| [Timestamp handling] | [e.g., TIMESTAMPTZ, always UTC] | [Why] |
| [Cross-module references] | [e.g., Foreign IDs only, no navigation properties] | [Why] |

---

## 2. Module Ownership

> *Every entity belongs to exactly one module. Cross-module references use IDs only — no shared tables, no cross-module foreign keys at the ORM level.*
>
> *This table doubles as the shard directory: every entity listed here must have a shard at `entities/<entity>.md` (see Naming Rule at the bottom of this template).*

| Module | Entities Owned | Persistence Unit [e.g., EF Core DbContext / Prisma schema / repository module] |
|--------|---------------|--------------------------------------------------------------------------------|
| [Module A] | [Entity1, Entity2] | [e.g., ModuleADbContext] |
| [Module B] | [Entity3, Entity4] | [e.g., ModuleBDbContext] |
| [Module C] | [Entity5, Entity6, Entity7] | [e.g., ModuleCDbContext] |

---

## 3. Database Conventions

> *Conventions applied uniformly across all entities and modules.*

| Convention | Rule | Example |
|------------|------|---------|
| [Table naming] | [e.g., snake_case, plural] | [task_items] |
| [Column naming] | [e.g., snake_case] | [due_date, created_at] |
| [Primary keys] | [e.g., UUID, column named `id`] | [id UUID PK] |
| [Timestamps] | [e.g., TIMESTAMPTZ, always present] | [created_at, updated_at] |
| [Soft deletes] | [e.g., nullable `deleted_at`] | [deleted_at TIMESTAMPTZ NULL] |
| [String lengths] | [e.g., explicit max lengths] | [name VARCHAR(200)] |

---

## 4. Relationships Overview

> *The full-model view. Each entity shard also lists its own relationships so it can be loaded standalone — keep the two in sync.*

### 4.1 One-to-Many Relationships

| Parent Entity | Child Entity | Foreign Key | Cascade Behavior |
|---------------|-------------|-------------|-----------------|
| [Entity A] | [Entity B] | [entity_a_id on Entity B] | [Cascade delete / Restrict / Set null] |
| [Entity C] | [Entity D] | [entity_c_id on Entity D] | [Cascade / Restrict] |

### 4.2 Many-to-Many Relationships

| Entity A | Entity B | Join Table | Additional Fields |
|----------|----------|-----------|-------------------|
| [Entity X] | [Entity Y] | [entity_x_entity_y] | [role, assigned_at, etc.] |

<!-- TODO: Define join table fields if the relationship carries data (e.g., a role or timestamp) -->

### 4.3 Cross-Module References

> *These are ID-only references — no ORM-level navigation properties or relations [e.g., EF Core navigation properties / Prisma relation fields], no database-level foreign keys across module boundaries.*

| Source Entity (Module) | Target Entity (Module) | Field | Purpose |
|----------------------|----------------------|-------|---------|
| [EntityB (Module A)] | [EntityX (Module B)] | [entity_x_id] | [Why this reference exists] |

### 4.4 Entity-Relationship Diagram

> *ASCII or text-based overview of the full data model.*

```
<!-- TODO: Replace with actual entity-relationship diagram -->

┌──────────────┐       1:N       ┌──────────────┐
│  [Entity A]  │────────────────→│  [Entity B]  │
│              │                 │              │
│  - field_1   │                 │  - field_1   │
│  - field_2   │                 │  - entity_a_id│
└──────────────┘                 └──────┬───────┘
                                        │
                                        │ N:M (via join table)
                                        │
                                 ┌──────┴───────┐
                                 │  [Entity C]  │
                                 │              │
                                 │  - field_1   │
                                 └──────────────┘
```

---

## 5. Shared Enums and Value Types

> *Only types used by MORE than one entity belong here. An enum used by a single entity lives in that entity's shard (Entity-Specific Enums & Rules).*

### 5.1 Shared Enums

#### [EnumName]

> *Used by: [EntityA.field, EntityB.field]*

| Value | Description |
|-------|-------------|
| [Value1] | [What it means] |
| [Value2] | [What it means] |
| [Value3] | [What it means] |

<!-- TODO: Repeat for each enum shared across entities -->

### 5.2 Value Objects

> *Complex types that don't have their own identity (not separate tables).*

#### [ValueObjectName]

| Property | Type | Description |
|----------|------|-------------|
| [property_1] | [type] | [Description] |
| [property_2] | [type] | [Description] |

---

## Usage Notes for AI Task Generation

When generating tasks from this document set:

1. **Shard loading**: Read `index.md` plus ONLY the entity shards named by the work item's impact tables (mapped via the Naming Rule) — do not read the whole `entities/` directory
2. **Module boundaries**: Every data-access task must target the correct module's persistence unit [e.g., DbContext / Prisma client / repository] — never query across module boundaries
3. **Field completeness**: Generated entity classes must include all fields defined in the entity's shard with correct types and constraints
4. **Relationship integrity**: Ensure cascade behaviors and cross-module ID-only references are respected in migrations
5. **Enum consistency**: Use the enum values defined in Section 5 (shared) or the entity shard (entity-specific) — do not invent new values without updating the owning file
6. **Index awareness**: Include index creation in migration tasks for fields marked with indexes in the entity shard
7. **Naming conventions**: Table and column names must follow the conventions in Section 3
8. **Cross-module lookups**: When a task needs data from another module, generate a call through that module's public interface [e.g., a service interface in a shared contracts project / the module's exported API] — not a direct DB query
9. **New entities**: Create a new shard at `entities/<entity>.md`, add a Module Ownership row (Section 2), add its relationships to Section 4, and record the change in the Changelog

---

## Changelog

> *Lives at the very bottom of `index.md` and records changes across the whole `docs/data-model/` set — shard edits included. Every edited or verified file also gets its freshness stamp updated.*

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |

---

## Entity Shard (`docs/data-model/entities/<entity>.md`)

One file per entity. Every shard follows this skeleton — reuse it verbatim when adding a new entity:

````markdown
# Entity: [Entity Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> *Module: [Owning Module] — [One-sentence description of what this entity represents]*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| [id] | [UUID] | [PK] | [Primary key] |
| [field_1] | [string(100)] | [Required, Unique] | [What this field represents] |
| [field_2] | [string(500)] | [Optional] | [What this field represents] |
| [field_3] | [enum: ValueType] | [Required, Default: X] | [What this field represents] |
| [foreign_id] | [UUID] | [Required, FK → OtherEntity] | [Cross-module or same-module reference] |
| [created_at] | [timestamptz] | [Required, Auto] | [Record creation timestamp] |
| [updated_at] | [timestamptz] | [Required, Auto] | [Last modification timestamp] |
| [deleted_at] | [timestamptz] | [Optional] | [Soft delete marker] |

## Indexes

- [Unique index on `field_1`]
- [Composite index on `(foreign_id, created_at)`]

## Relationships

<!-- This entity's slice of the Relationships Overview in index.md — keep the two in sync. -->

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| [EntityB (same module)] | [1:N — this entity is parent] | [entity_a_id on EntityB] | [Cascade delete / Restrict / Set null] | [—] |
| [EntityX (Module B)] | [N:1 — cross-module] | [entity_x_id — ID only, no navigation property or DB-level FK] | [—] | [Why this reference exists] |
| [EntityY] | [N:M] | [entity_a_entity_y join table] | [Join rows removed with either side] | [Join carries: role, assigned_at] |

## Entity-Specific Enums & Rules

### [EnumName]

> *Used only by this entity — enums shared across entities live in `index.md` Section 5.*

| Value | Description |
|-------|-------------|
| [Value1] | [What it means] |
| [Value2] | [What it means] |

### Business Rules

- [Rule 1: e.g., "field_1 must be unique within the scope of foreign_id"]
- [Rule 2: e.g., "Cannot be deleted if referenced by active EntityB records"]
````

---

## Naming Rule

Shard names derive **mechanically** from entity names — kebab-case, **singular**:

| Entity Name | Shard Path |
|-------------|-----------|
| `Task` | `docs/data-model/entities/task.md` |
| `TaskLabel` | `docs/data-model/entities/task-label.md` |
| `NotificationOutbox` | `docs/data-model/entities/notification-outbox.md` |

Never deviate from this mapping: work-item impact tables use entity names as retrieval keys, and task generation resolves `entity name → shard path` without guessing.
