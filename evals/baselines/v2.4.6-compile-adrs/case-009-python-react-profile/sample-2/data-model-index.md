<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# Data Model — <!-- TODO: [Product Name] -->

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 Model Summary

<!-- TODO: One paragraph describing the domain at a high level — what the system models, how many modules own data. -->

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary key strategy | UUIDs for all primary keys, generated server-side or by the database; no auto-increment integers | UUIDs enable distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Database naming | snake_case tables and columns; PascalCase C# properties translated automatically by the EF Core naming convention package | snake_case is the PostgreSQL idiomatic convention and avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Timestamp handling | All datetime columns use `timestamptz` (`DateTimeOffset` in C#); all values stored in UTC | `timestamptz` stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Soft vs hard deletes | Soft deletion via a nullable `deleted_at` (`timestamptz`) column; application code never performs hard deletes | Soft deletes preserve audit trails and allow recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |

<!-- TODO: add project-specific modeling decisions (e.g., multi-tenancy approach, cross-module references) as rows. -->

---

## 2. Module Ownership

<!-- TODO: module ownership table — every entity belongs to exactly one module; this table doubles as the shard directory. -->

---

## 3. Database Conventions

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | snake_case | `order_items` <!-- from: adrs/database/snake-case-naming.md --> |
| Column naming | snake_case | `created_at`, `user_id` <!-- from: adrs/database/snake-case-naming.md --> |
| Naming translation | Configure `UseSnakeCaseNamingConvention()` on the DbContext (via Npgsql EF Core package); C# entity properties use PascalCase as normal | `CreatedAt` → `created_at` <!-- from: adrs/database/snake-case-naming.md --> |
| Raw SQL identifiers | Raw SQL queries must use snake_case identifiers | `created_at`, `user_id` <!-- from: adrs/database/snake-case-naming.md --> |
| Migration naming | Migration files will reflect snake_case names — this is expected and correct | — <!-- from: adrs/database/snake-case-naming.md --> |
| Primary keys | All PK columns use `uuid` type in PostgreSQL and `Guid` in C# | `id uuid PK` <!-- from: adrs/database/uuid-primary-keys.md --> |
| PK generation | Generate IDs server-side with `Guid.NewGuid()` or use database default `gen_random_uuid()` | `gen_random_uuid()` <!-- from: adrs/database/uuid-primary-keys.md --> |
| Foreign keys | Foreign keys referencing PKs must also be `uuid`/`Guid` | `user_id uuid FK` <!-- from: adrs/database/uuid-primary-keys.md --> |
| PK value generation config | EF Core entity configurations must specify `.ValueGeneratedOnAdd()` for UUID PKs when using database defaults | `.ValueGeneratedOnAdd()` <!-- from: adrs/database/uuid-primary-keys.md --> |
| Datetime columns | All datetime columns in migrations must use `timestamptz`; EF Core column type explicitly configured as `timestamptz` if not inferred | `created_at TIMESTAMPTZ` <!-- from: adrs/database/timestamptz-always.md --> |
| Datetime properties | C# properties must use `DateTimeOffset`; all stored values must be in UTC (`DateTimeOffset.UtcNow`) | `DateTimeOffset CreatedAt` <!-- from: adrs/database/timestamptz-always.md --> |
| Timezone display | Timezone conversion to local display time is a frontend-only concern | — <!-- from: adrs/database/timestamptz-always.md --> |
| Soft deletes | Add a nullable `DateTimeOffset? DeletedAt` property to all soft-deletable entities, mapping to a `deleted_at` column of type `timestamptz` | `deleted_at TIMESTAMPTZ NULL` <!-- from: adrs/database/soft-deletes.md --> |
| Soft-delete filtering | Configure EF Core global query filters so soft-deleted records are invisible by default | `.HasQueryFilter(e => e.DeletedAt == null)` <!-- from: adrs/database/soft-deletes.md --> |
| Soft-delete operation | To soft-delete, set `DeletedAt = DateTimeOffset.UtcNow` | `entity.DeletedAt = DateTimeOffset.UtcNow` <!-- from: adrs/database/soft-deletes.md --> |
| Querying deleted records | To query including soft-deleted records, use `.IgnoreQueryFilters()` explicitly | `.IgnoreQueryFilters()` <!-- from: adrs/database/soft-deletes.md --> |

---

## 4. Relationships Overview

### 4.1 One-to-Many Relationships

<!-- TODO: parent/child relationships table. -->

### 4.2 Many-to-Many Relationships

<!-- TODO: join table relationships. -->

### 4.3 Cross-Module References

<!-- TODO: ID-only cross-module references table. -->

### 4.4 Entity-Relationship Diagram

<!-- TODO: entity-relationship diagram. -->

---

## 5. Shared Enums and Value Types

### 5.1 Shared Enums

<!-- TODO: enums used by more than one entity. -->

### 5.2 Value Objects

<!-- TODO: complex types without their own identity. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: static template content — copy verbatim from the data-model.md template. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version (compiled from ADRs) | — |
