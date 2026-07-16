<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# Data Model — [Product Name] <!-- TODO: replace with the product name -->

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 Model Summary

<!-- TODO: One paragraph describing the domain, module ownership, and key modeling decisions — project-specific content. -->

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary keys | UUIDs, generated server-side or by the database; auto-increment integers never used | UUIDs enable distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Naming convention | snake_case tables and columns; PascalCase properties translated automatically by the naming convention package | snake_case is the PostgreSQL idiomatic convention and avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Timestamp handling | `timestamptz` for all datetime columns, values stored in UTC | `timestamptz` stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Deletion strategy | Soft deletes via nullable `deleted_at` column; application code never hard-deletes | Soft deletes preserve audit trails and allow recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |

---

## 2. Module Ownership

<!-- TODO: One row per module listing its owned entities and persistence unit — project-specific content. -->

---

## 3. Database Conventions

- All PK columns use `uuid` type in PostgreSQL and `Guid` in C#; foreign keys referencing PKs must also be `uuid`/`Guid` <!-- from: adrs/database/uuid-primary-keys.md -->
- Generate IDs server-side with `Guid.NewGuid()` or use the database default `gen_random_uuid()`; entity configurations must specify `.ValueGeneratedOnAdd()` for UUID PKs when using database defaults <!-- from: adrs/database/uuid-primary-keys.md -->
- Configure `UseSnakeCaseNamingConvention()` on the DbContext (via the Npgsql EF Core package); entity properties use PascalCase as normal (e.g., `CreatedAt`, `UserId`) <!-- from: adrs/database/snake-case-naming.md -->
- Raw SQL queries must use snake_case identifiers (e.g., `created_at`, `user_id`); migration files will reflect snake_case names — this is expected and correct <!-- from: adrs/database/snake-case-naming.md -->
- All datetime columns in migrations must use `timestamptz`; the column type should be explicitly configured as `timestamptz` if not inferred <!-- from: adrs/database/timestamptz-always.md -->
- Datetime properties must use `DateTimeOffset`, and all stored values must be in UTC (`DateTimeOffset.UtcNow`); timezone conversion to local display time is a frontend-only concern <!-- from: adrs/database/timestamptz-always.md -->
- Add a nullable `DateTimeOffset? DeletedAt` property to all soft-deletable entities, mapping to a `deleted_at` column of type `timestamptz` <!-- from: adrs/database/soft-deletes.md -->
- Configure global query filters so soft-deleted records are invisible by default (`.HasQueryFilter(e => e.DeletedAt == null)`); to soft-delete, set `DeletedAt = DateTimeOffset.UtcNow`; to query including soft-deleted records, use `.IgnoreQueryFilters()` explicitly <!-- from: adrs/database/soft-deletes.md -->

---

## 4. Relationships Overview

### 4.1 One-to-Many Relationships

<!-- TODO: Parent/child relationship table — project-specific content. -->

### 4.2 Many-to-Many Relationships

<!-- TODO: Join table relationships — project-specific content. -->

### 4.3 Cross-Module References

<!-- TODO: ID-only cross-module reference table — project-specific content. -->

### 4.4 Entity-Relationship Diagram

<!-- TODO: Entity-relationship diagram — project-specific content. -->

---

## 5. Shared Enums and Value Types

### 5.1 Shared Enums

<!-- TODO: Enums used by more than one entity — project-specific content. -->

### 5.2 Value Objects

<!-- TODO: Value object definitions — project-specific content. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: Copy from the data-model.md template — static framework content, not derived from ADRs. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version — modeling decisions and conventions compiled from database ADRs | — |
