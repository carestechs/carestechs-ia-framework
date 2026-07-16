<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# Data Model — <!-- TODO: [Product Name] -->

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 Model Summary

<!-- TODO: One paragraph describing the domain — what the system models, how many modules own data. -->

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary key strategy | UUIDs generated server-side or by the database; never auto-increment integers | Distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Naming convention | snake_case tables and columns; code properties stay PascalCase with automatic translation | PostgreSQL idiomatic convention; avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Timestamp handling | `timestamptz` (TIMESTAMP WITH TIME ZONE) columns, all values stored in UTC | Stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Soft vs hard deletes | Soft deletion via nullable `deleted_at` column; application code never hard-deletes | Preserves audit trails and allows recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |

---

## 2. Module Ownership

<!-- TODO: Project-specific — list each module, the entities it owns, and its persistence unit. -->

---

## 3. Database Conventions

- All PK columns use `uuid` type in PostgreSQL and `Guid` in C#; foreign keys referencing PKs are also `uuid`/`Guid` <!-- from: adrs/database/uuid-primary-keys.md -->
- IDs are generated server-side with `Guid.NewGuid()` or via database default `gen_random_uuid()`; entity configurations specify `.ValueGeneratedOnAdd()` for UUID PKs when using database defaults <!-- from: adrs/database/uuid-primary-keys.md -->
- `UseSnakeCaseNamingConvention()` is configured on the DbContext (via the Npgsql EF Core package); entity properties use PascalCase as normal (e.g., `CreatedAt`, `UserId`) <!-- from: adrs/database/snake-case-naming.md -->
- Raw SQL queries use snake_case identifiers (e.g., `created_at`, `user_id`) <!-- from: adrs/database/snake-case-naming.md -->
- Migration files reflect snake_case names — this is expected and correct <!-- from: adrs/database/snake-case-naming.md -->
- All datetime columns in migrations use `timestamptz`, with the column type explicitly configured as `timestamptz` if not inferred <!-- from: adrs/database/timestamptz-always.md -->
- Datetime properties use `DateTimeOffset`; all stored values are in UTC (`DateTimeOffset.UtcNow`) <!-- from: adrs/database/timestamptz-always.md -->
- Timezone conversion to local display time is a frontend-only concern <!-- from: adrs/database/timestamptz-always.md -->
- All soft-deletable entities carry a nullable `DateTimeOffset? DeletedAt` property, mapped to a `deleted_at` column of type `timestamptz` <!-- from: adrs/database/soft-deletes.md -->
- Global query filters (`.HasQueryFilter(e => e.DeletedAt == null)`) hide soft-deleted records by default; querying including soft-deleted records uses `.IgnoreQueryFilters()` explicitly <!-- from: adrs/database/soft-deletes.md -->
- Soft-deleting sets `DeletedAt = DateTimeOffset.UtcNow` <!-- from: adrs/database/soft-deletes.md -->

---

## 4. Relationships Overview

### 4.1 One-to-Many Relationships

<!-- TODO: Project-specific — add parent/child relationships with foreign keys and cascade behavior. -->

### 4.2 Many-to-Many Relationships

<!-- TODO: Project-specific — add join tables and their additional fields. -->

### 4.3 Cross-Module References

<!-- TODO: Project-specific — add ID-only references across module boundaries. -->

### 4.4 Entity-Relationship Diagram

<!-- TODO: Project-specific — add the full-model ER diagram. -->

---

## 5. Shared Enums and Value Types

### 5.1 Shared Enums

<!-- TODO: Project-specific — add enums used by more than one entity. -->

### 5.2 Value Objects

<!-- TODO: Project-specific — add complex types without their own identity. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: Framework boilerplate from the data-model.md template — copy when assembling the project docs/data-model/index.md. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version compiled from ADRs | — |
