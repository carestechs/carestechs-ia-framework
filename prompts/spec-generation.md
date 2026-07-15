# Spec Generation Prompt

## Purpose

Generate a Data Model or API Specification document from existing strategic documentation. Use this prompt when you have stakeholder definitions, architecture docs, and code conventions, and need to derive the data model or API endpoints before generating implementation tasks.

**When to use**: After completing the strategic documents (Stakeholder Definition, Architecture, CLAUDE.md) and before generating feature tasks. This fills the gap between "what we're building" and "how to break it into tasks."

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the context files listed in the project CLAUDE.md routing table for "Spec generation", follow the **Guidance**, **Output Format**, and **Constraints** sections below, and **write the output files** (sharded): for a Data Model, `docs/data-model/index.md` plus one `docs/data-model/entities/<entity>.md` per entity; for an API Specification, `docs/api-spec/index.md` plus one `docs/api-spec/endpoints/<resource>.md` per resource.
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the **Chat Workflow Template (XML)** appendix — paste your documentation into the `<context>` sections and include the Guidance, Output Format, and Constraints sections of this prompt alongside it.

---

## Required Context

Context selection follows the canonical matrix — see `guides/context-compilation.md` (for manual assembly) or the project CLAUDE.md routing table (for agents).

Prompt-specific notes:

- **All three required documents (Stakeholder Definition, Architecture, CLAUDE.md) should be included in full.** Unlike feature task generation where you excerpt relevant sections, spec generation needs the complete picture to derive a comprehensive model.
- **Persona** is optional — include it for user-facing entity/endpoint decisions.
- When generating the **API Specification**, also include the generated Data Model as context — `docs/data-model/index.md` plus the entity shards (see Guidance below).
- Read the output format template from `.ai-framework/templates/` for the target spec type (`data-model.md` or `api-spec.md`).

---

## Guidance

### For Data Model Generation

When deriving entities:
1. Read the Scope Lock — every in-scope feature implies at least one entity
2. Read the User Flow — each phase implies data that must be persisted
3. Read Backend Responsibilities — these map to service operations on entities (if the document has no Backend Responsibilities section, derive service operations from the User Flow and Scope Lock)
4. Read the Architecture — module boundaries determine entity ownership
5. Read CLAUDE.md — database conventions dictate naming, types, and patterns

For each entity, determine:
- Which module owns it (from Architecture module list)
- What fields it needs (from user flow steps and feature descriptions)
- What relationships it has (from flow transitions and cross-references)
- What constraints apply (from business rules in stakeholder definition)
- What indexes are needed (from query patterns implied by the UI)

Cross-module references:
- Use ID-only references (no navigation properties across modules)
- Note which module owns the reference and which module owns the target
- Document the purpose of each cross-module reference

### For API Specification Generation

When deriving endpoints:
1. Start with entities — each entity typically needs CRUD endpoints
2. Read the User Flow — each user action implies an API call
3. Map endpoints to modules — the owning module exposes the endpoint
4. Read CLAUDE.md — API conventions dictate route patterns, response format, and auth
5. Consider the frontend — what data does each page/view need?

For each endpoint, determine:
- HTTP method and path (from REST conventions + entity name)
- Auth requirements (from architecture security section)
- Request DTO fields (from entity fields that are user-editable)
- Response DTO fields (from what the frontend needs to display)
- Status codes (from error handling patterns in CLAUDE.md)
- Pagination (for list endpoints)

Endpoint grouping:
- Group by module, then by resource within the module
- Order: List → Create → Get → Update → Delete (standard CRUD order)
- Add non-CRUD actions as sub-resources (e.g., POST /api/tasks/{id}/assign)

### Workflow Order

**Step 1 — Generate the Data Model first.** Write `docs/data-model/index.md` plus one `docs/data-model/entities/<entity>.md` per entity. Entities inform endpoint structure (CRUD per entity), field definitions inform request/response DTOs, and relationships inform nested routes and query parameters.

**Step 2 — Generate the API Spec second.** Write `docs/api-spec/index.md` plus one `docs/api-spec/endpoints/<resource>.md` per resource. With the data model in hand, add `docs/data-model/index.md` + the entity shards as extra context and use them as the source of truth for entities, fields, and relationships.

**Step 3 — Review and validate** each generated document against the source docs:
- Does every scope-lock item have representation?
- Are module boundaries consistent with the architecture?
- Do naming conventions match CLAUDE.md?

---

## Output Format

Write the generated spec as a **sharded document set** at the canonical locations:

- Data Model → **`docs/data-model/index.md`** + one **`docs/data-model/entities/<entity>.md`** per entity
- API Specification → **`docs/api-spec/index.md`** + one **`docs/api-spec/endpoints/<resource>.md`** per resource

**Shard naming (mechanical, kebab-case):** entity `TaskLabel` → `entities/task-label.md` (singular); resource `/api/task-labels` → `endpoints/task-labels.md` (matches the route segment, plural).

**Frontmatter (required on every generated shard):** every shard begins with a frontmatter block — **before the H1** — carrying its machine-readable retrieval keys. **Index files get no frontmatter.** Constraint: the frontmatter is parsed by a stdlib mini-parser — **flat keys only**; values are scalars or inline arrays `[a, b, c]`. No nesting, no multiline values, no quotes needed for kebab-case/path values.

Entity shard (`docs/data-model/entities/<entity>.md`):

```
---
kind: entity
name: TaskLabel            # PascalCase; kebab-case of it MUST equal the filename
module: Projects
endpoints: [task-labels]   # api-spec/endpoints/<x>.md shards that expose this entity (may be [])
screens: [project-board]   # ui-specification/screens/<x>.md shards that render it (may be [])
---
```

Resource shard (`docs/api-spec/endpoints/<resource>.md`):

```
---
kind: resource
resource: task-labels      # MUST equal the filename
routes: [/api/task-labels]
entities: [task-label]     # entity shard names this resource reads/writes
---
```

**Freshness stamp:** every generated file (index and every shard) starts with this line directly under its H1 — fill in today's date and the current commit hash:

```
> **Last verified against code:** YYYY-MM-DD (commit `abc1234`)
```

**File order in every shard:** frontmatter block → H1 → freshness stamp. The stamp lives only as the blockquote under the H1 — it is never duplicated into the frontmatter.

**Index files hold cross-cutting content only** — anything specific to one entity or one resource lives in its shard.

Derive all content from the context documents provided:
- Entities/endpoints from the stakeholder scope and user flows
- Module ownership from the architecture doc
- Naming and conventions from CLAUDE.md
- Field types and constraints from domain rules in the stakeholder definition

### For Data Model

Use the section structure from `.ai-framework/templates/data-model.md` for the index and shard formats.

`docs/data-model/index.md` (cross-cutting only):
1. Overview with Key Modeling Decisions table
2. Module Ownership table
3. Database Conventions summary
4. Relationships Overview — entity-relationship diagram (ASCII)
5. Shared Enums and Value Types (used by 2+ entities)
6. Usage Notes for AI Task Generation
7. Changelog

`docs/data-model/entities/<entity>.md` — **one entity per file**:
- `kind: entity` frontmatter (retrieval keys — see above)
- Owning module
- Fields table (types, constraints, indexes)
- Relationships (1:N, M:N, cross-module — with cascade behaviors)
- Entity-specific enums and business rules

### For API Specification

Use the section structure from `.ai-framework/templates/api-spec.md` for the index and shard formats.

`docs/api-spec/index.md` (cross-cutting only):
1. Overview with Key API Decisions table
2. Common conventions — response envelope, Error Catalog, Authentication Endpoints, Pagination
3. Shared DTOs
4. Endpoint summary table
5. Usage Notes for AI Task Generation
6. Changelog

`docs/api-spec/endpoints/<resource>.md` — **one resource group per file**: `kind: resource` frontmatter (retrieval keys — see above), then all endpoint blocks for that resource, each with route, method, auth, request/response DTOs, and status codes.

---

## Constraints

- Follow all naming conventions from CLAUDE.md exactly
- Respect module boundaries from the architecture document
- Only include entities/endpoints for features within the scope lock — do not invent features or entities beyond the defined scope
- Use the response envelope format defined in CLAUDE.md or architecture docs
- Apply the database conventions declared in CLAUDE.md [e.g., snake_case tables, UUID PKs, TIMESTAMPTZ]
- Include all standard audit fields (created_at, updated_at) on every entity

---

## Post-Generation Checklist

After the AI generates a spec document set, verify:

### For Both:
- [ ] Run `python .ai-framework/tools/validate-specs.py --root .` and fix every error
- [ ] Every generated shard begins with its frontmatter block (`kind: entity` / `kind: resource`, flat keys only, name/resource key matches the filename); index files have none
- [ ] Every generated file (index and every shard) starts with the freshness stamp directly under its H1 (after the frontmatter in shards), filled with today's date and the current commit
- [ ] Index files hold cross-cutting content only — every entity/resource lives in its own shard
- [ ] Shard filenames follow the kebab-case naming rule (entity singular; resource matches the route segment)

### For Data Model:
- [ ] Every feature in the scope lock maps to at least one entity
- [ ] No entities exist for out-of-scope features
- [ ] Each entity has an explicit module owner (exactly one module)
- [ ] All field types are specific (not vague — `string(200)` not just `string`)
- [ ] Relationships are fully defined with cascade behaviors
- [ ] Cross-module references are ID-only (no navigation properties)
- [ ] Enums are defined with all values listed
- [ ] Standard audit fields (id, created_at, updated_at) are on every entity
- [ ] Indexes are defined for fields used in lookups and filters
- [ ] Business rules are documented per entity
- [ ] Naming follows CLAUDE.md conventions throughout
- [ ] Entity-relationship diagram matches the field/relationship definitions

### For API Specification:
- [ ] Every entity has appropriate CRUD endpoints
- [ ] No endpoints exist for out-of-scope features
- [ ] Non-CRUD actions (assign, move, upload) are covered
- [ ] Auth requirements are specified for every endpoint
- [ ] Request DTOs only include user-editable fields (not id, created_at, etc.)
- [ ] Response DTOs include all fields the frontend needs
- [ ] List endpoints support pagination
- [ ] Error status codes are comprehensive (400, 401, 403, 404, 409 as applicable)
- [ ] Response envelope format is consistent across all endpoints
- [ ] Naming follows CLAUDE.md conventions throughout
- [ ] Endpoint summary table is complete and matches detailed definitions

---

## Chat Workflow Template (XML)

Copy this skeleton, paste your documentation into the `<context>` sections, and submit together with the Guidance, Output Format, and Constraints sections above.

```xml
<spec-generation-request>

<context>

<stakeholder-definition>
<!-- REQUIRED: Include full stakeholder definition — scope lock, user flows,
     backend responsibilities, and success metrics are critical for deriving entities -->
[Paste full stakeholder-definition.md content]
</stakeholder-definition>

<architecture>
<!-- REQUIRED: Include full architecture doc — module boundaries, tech stack,
     and data flow inform entity ownership and API structure -->
[Paste full ARCHITECTURE.md content]
</architecture>

<code-conventions>
<!-- REQUIRED: Include full CLAUDE.md — naming conventions, database conventions,
     and patterns directly constrain how entities and endpoints are defined -->
[Paste full CLAUDE.md content]
</code-conventions>

<persona>
<!-- OPTIONAL: Include if user-facing features need persona context -->
[Paste persona details]
</persona>

<data-model>
<!-- ONLY when generating the API Specification (Step 2):
     paste the Data Model generated in Step 1 -->
[Paste docs/data-model/index.md + docs/data-model/entities/*.md content]
</data-model>

</context>

<spec-type>[Data Model | API Specification]</spec-type>

<request>
Generate a complete [Data Model | API Specification] document for this project,
following the Guidance, Output Format, and Constraints from prompts/spec-generation.md.
</request>

</spec-generation-request>
```

---

## Example

Generating a Data Model:

```xml
<spec-generation-request>

<context>

<stakeholder-definition>
## Executive Summary
The product is an internal project management web application.

## Scope Lock (V1)
Included: Projects, Tasks with Kanban/List/Gantt views, Team members, Labels, Comments
Excluded: Time tracking, Billing, External integrations, Mobile app

## User Flow
Phase 1: Login via Google OAuth
Phase 2: Select or create project, manage members
Phase 3: Create tasks, assign to members, set status/priority/dates
Phase 4: View tasks in Kanban (drag columns), List (sortable table), Gantt (timeline)
Phase 5: Collaborate via comments and file attachments on tasks
</stakeholder-definition>

<architecture>
## Modules
- TecherPlannr.Auth → handles Google OAuth, JWT
- TecherPlannr.Users → user profiles, roles
- TecherPlannr.Projects → projects, membership
- TecherPlannr.Tasks → tasks, labels, comments, attachments
- TecherPlannr.Shared → common interfaces, base entity
</architecture>

<code-conventions>
## Database Conventions
- snake_case for tables (plural) and columns
- UUID primary keys
- TIMESTAMPTZ for all date/time columns
- Soft deletes with deleted_at where appropriate
## Naming
- Entity class: PascalCase (TaskItem, not Task)
- Persistence unit: {Module}DbContext
</code-conventions>

</context>

<spec-type>Data Model</spec-type>

<request>
Generate a complete Data Model document for this project management application.
Derive all entities from the scope lock and user flows.
Assign each entity to the correct module per the architecture.
</request>

</spec-generation-request>
```

**Output:** `docs/data-model/index.md` + one `docs/data-model/entities/<entity>.md` per entity (e.g., `entities/task-item.md`, `entities/project.md`) — a complete sharded data model following the `data-model.md` template structure, every shard opening with its `kind: entity` frontmatter and every file stamped `> **Last verified against code:** ...` directly under its H1.
