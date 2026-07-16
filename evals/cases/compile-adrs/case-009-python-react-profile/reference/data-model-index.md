<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->
<!-- Compiled docs/data-model/index.md sections — database-category ADRs of the python-react-modular-monolith-docker-compose
     profile, via prompts/compile-adrs.md (Rule 5). Paste into docs/data-model/index.md and fill the TODO scaffolds. -->

## 1. Overview

### 1.1 Model Summary

<!-- TODO: One paragraph describing the domain — project-specific. -->

### 1.2 Key Modeling Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary keys | UUIDs for all primary keys, generated server-side or by the database; never auto-increment | Distributed ID generation without coordination between services or database nodes <!-- from: adrs/database/uuid-primary-keys.md --> |
| Table/column naming | snake_case tables and columns; PascalCase entity properties translated automatically | snake_case is the PostgreSQL idiomatic convention and avoids quoting issues with mixed-case identifiers <!-- from: adrs/database/snake-case-naming.md --> |
| Timestamp handling | `timestamptz` for all datetime columns; all values stored in UTC | `timestamptz` stores an absolute point in time, eliminating timezone ambiguity <!-- from: adrs/database/timestamptz-always.md --> |
| Soft vs hard deletes | Soft deletion via nullable `deleted_at` column; application code never hard-deletes | Soft deletes preserve audit trails and allow recovery of accidentally deleted data <!-- from: adrs/database/soft-deletes.md --> |

---

## 2. Module Ownership

<!-- TODO: one row per module with the entities it owns — project-specific. -->

---

## 3. Database Conventions

- All PK columns use the `uuid` type in PostgreSQL (`Guid` in C#) <!-- from: adrs/database/uuid-primary-keys.md -->
- IDs are generated server-side with `Guid.NewGuid()` or the database default `gen_random_uuid()` <!-- from: adrs/database/uuid-primary-keys.md -->
- Foreign keys referencing PKs are also `uuid`/`Guid` <!-- from: adrs/database/uuid-primary-keys.md -->
- EF Core entity configurations specify `.ValueGeneratedOnAdd()` for UUID PKs when using database defaults <!-- from: adrs/database/uuid-primary-keys.md -->
- `UseSnakeCaseNamingConvention()` is configured on the DbContext (Npgsql EF Core package); entity properties stay PascalCase (e.g., `CreatedAt`, `UserId`) <!-- from: adrs/database/snake-case-naming.md -->
- Raw SQL queries use snake_case identifiers (e.g., `created_at`, `user_id`) <!-- from: adrs/database/snake-case-naming.md -->
- Migration files reflect snake_case names — expected and correct <!-- from: adrs/database/snake-case-naming.md -->
- All datetime columns in migrations use `timestamptz`; datetime properties use `DateTimeOffset`, with the column type explicitly configured as `timestamptz` when not inferred <!-- from: adrs/database/timestamptz-always.md -->
- All stored datetime values are UTC (`DateTimeOffset.UtcNow`); timezone conversion to local display time is a frontend-only concern <!-- from: adrs/database/timestamptz-always.md -->
- Soft-deletable entities carry a nullable `DeletedAt` property mapping to a `deleted_at` column of type `timestamptz` <!-- from: adrs/database/soft-deletes.md -->
- Global query filters hide soft-deleted rows by default (`.HasQueryFilter(e => e.DeletedAt == null)`); soft-delete by setting `DeletedAt = DateTimeOffset.UtcNow` <!-- from: adrs/database/soft-deletes.md -->
- Querying soft-deleted records requires an explicit `.IgnoreQueryFilters()` <!-- from: adrs/database/soft-deletes.md -->

---

## 4. Relationships Overview

<!-- TODO: one-to-many / many-to-many / cross-module reference tables and ER diagram — project-specific. -->

---

## 5. Shared Enums and Value Types

<!-- TODO: enums and value objects shared by 2+ entities — project-specific. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: retain the template's usage notes when pasting into the real index — not filled by ADR compilation. -->

---

## Changelog

<!-- TODO: changelog table — maintained by the project. -->
