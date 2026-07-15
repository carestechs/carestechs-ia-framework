<!-- Copy this file to docs/data-model/entities/<entity-kebab-singular>.md — one entity per file. -->
<!-- Frontmatter: flat keys only — values are scalars or inline [a, b, c] arrays (no nesting, no multiline values); the kebab-case of `name` MUST equal the filename. -->

---
kind: entity
name: [EntityName]         # PascalCase; kebab-case of it MUST equal the filename
module: [OwningModule]
endpoints: [resource-a]    # api-spec/endpoints/<x>.md shards that expose this entity (may be [])
screens: [screen-a]        # ui-specification/screens/<x>.md shards that render it (may be [])
---

# Entity: [Entity Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> *Module: [Owning Module] — <!-- TODO: One-sentence description of what this entity represents -->*

## Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| <!-- field --> | <!-- type --> | <!-- constraints --> | <!-- description --> |
| created_at | timestamptz | Required, Auto | Record creation timestamp |
| updated_at | timestamptz | Required, Auto | Last modification timestamp |

## Indexes

<!-- TODO: e.g., Unique index on `name` -->
-

## Relationships

<!-- This entity's slice of the Relationships Overview in index.md — keep the two in sync. Cross-module references are ID-only. -->

| Related Entity (Module) | Cardinality | Foreign Key / Join Table | Cascade Behavior | Notes |
|-------------------------|-------------|--------------------------|------------------|-------|
| <!-- e.g., Task (same module) --> | <!-- e.g., 1:N — this entity is parent --> | <!-- e.g., project_id on Task --> | <!-- e.g., Cascade delete --> | <!-- --> |

## Entity-Specific Enums & Rules

### [EnumName]

<!-- TODO: Enums used only by this entity — enums shared across entities live in index.md Section 5 -->

| Value | Description |
|-------|-------------|
| <!-- e.g., Active --> | <!-- e.g., Currently active --> |

### Business Rules

<!-- TODO: e.g., "Name must be unique within the project" -->
-
