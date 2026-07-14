# Data Model

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

<!-- TODO: Every entity belongs to exactly one module -->

| Module | Entities Owned | Persistence Unit [e.g., EF Core DbContext / Prisma schema] |
|--------|---------------|-------------------------------------------------------------|
| <!-- e.g., Users --> | <!-- e.g., User, Role --> | <!-- e.g., UsersDbContext --> |
| <!-- e.g., Projects --> | <!-- e.g., Project, ProjectMember --> | <!-- e.g., ProjectsDbContext --> |

## 3. Entity Definitions

<!-- TODO: Define each entity with fields, types, and constraints. See .ai-framework/templates/data-model.md for the full template. -->

### 3.1 [Entity Name]

> *Module: [Owning Module] — [One-sentence description]*

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| <!-- field --> | <!-- type --> | <!-- constraints --> | <!-- description --> |
| created_at | timestamptz | Required, Auto | Record creation timestamp |
| updated_at | timestamptz | Required, Auto | Last modification timestamp |

**Indexes:**
- <!-- e.g., Unique index on `name` -->

**Business Rules:**
- <!-- e.g., "Name must be unique within the project" -->

---

<!-- TODO: Repeat entity definition blocks (3.2, 3.3, ...) for each entity -->

## 4. Relationships

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

## 5. Enums and Value Types

### 5.1 Enums

<!-- TODO: Define enums used by entities -->

#### [EnumName]

> *Used by: [Entity.field]*

| Value | Description |
|-------|-------------|
| <!-- e.g., Active --> | <!-- e.g., Currently active --> |
| <!-- e.g., Archived --> | <!-- e.g., Soft-archived, hidden from default views --> |

## 6. Database Conventions

| Convention | Rule | Example |
|------------|------|---------|
| Table naming | <!-- e.g., snake_case, plural --> | <!-- e.g., task_items --> |
| Column naming | <!-- e.g., snake_case --> | <!-- e.g., due_date --> |
| Primary keys | <!-- e.g., UUID, column named `id` --> | <!-- e.g., id UUID PK --> |
| Timestamps | <!-- e.g., TIMESTAMPTZ, always present --> | <!-- e.g., created_at, updated_at --> |

## Usage Notes for AI Task Generation

- **Module boundaries**: Every data-access task must target the correct module's persistence unit [e.g., DbContext / Prisma client / repository]
- **Field completeness**: Generated entity classes must include all fields defined here
- **Relationship integrity**: Ensure cascade behaviors and cross-module ID-only references are respected
- **Naming conventions**: Table and column names must follow the conventions in Section 6

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |
