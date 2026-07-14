# Feature Task Generation Prompt

---

## Purpose

Generate implementation tasks for a new feature. Use this prompt when you have a Feature Brief (or feature idea) and need to break it down into actionable development tasks.

Features should be described in a **Feature Brief** (`docs/work-items/FEAT-XXX-short-title.md`) before task generation. An inline description (`<inline-request>`) is supported as a fallback for quick/ad-hoc usage.

This prompt uses the **canonical task schema defined in `prompts/base-template.md`** (field list, order, enums, grouping). Deltas declared here: none to the `Type` enum — only the workflow-classification rules and summary section below.

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the context files listed in your project CLAUDE.md's routing table for "New feature", read the Feature Brief from `docs/work-items/FEAT-XXX-short-title.md` (if none exists, gather the feature details from the user as an inline request), follow the sections below, and **write** the task list to `tasks/FEAT-XXX-tasks.md` (or `tasks/adhoc-short-title-tasks.md` for inline requests with no work item).
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the [Chat Workflow Template (XML)](#chat-workflow-template-xml) appendix. Include this prompt's Output Format and Constraints sections alongside the skeleton so the assistant knows the expected schema.

---

## Required Context

Context selection lives in the **canonical matrix**: `guides/context-compilation.md` (humans) or the CLAUDE.md routing table (agents).

For features: **required** = Feature Brief + Stakeholder Definition + CLAUDE.md; **recommended** = Data Model, API Spec, UI Specification (include when the feature touches data/API/UI — typical), Architecture, Persona.

Spec docs are **sharded** — load the index plus referenced shards only:

- Read `docs/data-model/index.md`, `docs/api-spec/index.md`, and `docs/ui-specification/index.md` for cross-cutting conventions.
- Read **only** the shards named by the Feature Brief's impact tables (Entities / API / UI), mapped via the kebab-case naming rule: entity `TaskLabel` → `docs/data-model/entities/task-label.md` (singular); resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md` (matches the route segment); screen "Project Board" → `docs/ui-specification/screens/project-board.md`.
- Do not read whole spec directories.

Prompt-specific notes:

- **Feature Brief** (preferred): `docs/work-items/FEAT-XXX-short-title.md` provides structured scope, traceability, entity/API/UI impact assessment, and constraint documentation. Generates higher-quality tasks.
- **Inline `<inline-request>`** (fallback): use for quick/ad-hoc features when a full Feature Brief hasn't been written yet. Faster but less structured.

---

## Guidance

Generate a complete task breakdown for the feature. Tasks should:

1. Cover all acceptance criteria
2. Include necessary database/data model changes
3. Include API endpoints if applicable
4. Include frontend/UI implementation
5. Include error handling and edge cases
6. Include testing at all levels (unit, integration, e2e)
7. Consider monitoring/logging requirements

Do not include:

- Tasks outside the defined scope (see stakeholder scope lock)
- Over-engineered solutions beyond the requirements

### Workflow Classification

Set the **Workflow** field on each task using these rules (all three values from the canonical schema are valid):

- **`mockup-first`** — Type is Frontend AND the task adds a new user-facing screen or significantly changes an existing screen layout. **Exception:** standard CRUD screens (list/detail/form) or screens that follow an already-approved mockup pattern.
- **`investigation-first`** — the task's requirements are ambiguous or depend on unknowns in the existing system; investigate and document findings before implementing.
- **`standard`** — all other tasks.

When a task is marked `mockup-first`, its description should note which screen needs a mockup and reference `.ai-framework/prompts/mockup-generation.md`.

---

## Output Format

**Output file:** `tasks/FEAT-XXX-tasks.md` (matching the Feature Brief's ID; `tasks/adhoc-short-title-tasks.md` for inline requests). AI agents write this file — the task list is not just chat output.

**Task blocks:** use the canonical task schema from `prompts/base-template.md`, all fields in canonical order — Task ID, Title, Type, Workflow, Description, Rationale, Acceptance Criteria, Dependencies, Complexity (`S | M | L | XL`), Files to Modify/Create, Technical Notes (optional). `Type` uses the base enum (Backend | Frontend | Database | Testing | DevOps | Documentation) — no deltas for features. In **Files to Modify/Create**, suffix files that don't exist yet with `(new)` — example: `- src/services/label-service.ts (new) - label CRUD logic`.

**Grouping:** the canonical scheme — Foundation → Backend → Frontend → Integration → Testing → Documentation & Polish (omit empty groups).

**Summary section** — after all tasks, provide:

- Total task count by type
- Estimated complexity distribution
- Critical path (longest dependency chain)
- Risks or open questions discovered during analysis

**Acceptance Criteria Coverage** (mandatory) — the task list ends with this section; the validator cross-checks it against the work item via `--work-item`:

```markdown
## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: [text] | T-003, T-007 |
```

Every acceptance criterion from the Feature Brief gets one row; `Covered By` lists the task IDs that implement and verify it.

---

## Constraints

- No tasks outside the stakeholder scope lock
- No over-engineered solutions beyond the requirements
- One `Type` per task — split tasks that span types
- Dependencies are plain task ID lists (or `None`) forming a valid DAG
- Apply the project-specific constraints supplied in the request, e.g.:
  - Technology stack: [technologies that must be used]
  - Timeline constraint: [if any]
  - Dependency constraints: [external factors]
  - Security requirements: [specific security needs]

---

## Post-Generation Checklist

After Claude generates tasks, verify:

- [ ] Run `python .ai-framework/tools/validate-tasks.py tasks/FEAT-XXX-tasks.md --work-item docs/work-items/FEAT-XXX-short-title.md` and fix every error
- [ ] All acceptance criteria have corresponding tasks (the `## Acceptance Criteria Coverage` table is present and complete)
- [ ] Database/model changes come before code that uses them
- [ ] API endpoints are defined before frontend integration
- [ ] Error handling tasks exist for important error scenarios
- [ ] Testing tasks cover happy path and edge cases
- [ ] No tasks violate stakeholder scope lock
- [ ] Complexity estimates seem reasonable (full `S | M | L | XL` scale)
- [ ] Every task block has Acceptance Criteria and all canonical schema fields
- [ ] Dependencies form a valid DAG (no cycles)
- [ ] Critical path is identified and sensible
- [ ] Task list saved to `tasks/FEAT-XXX-tasks.md` (agents)

---

## Chat Workflow Template (XML)

```xml
<task-generation-request>

<context>

<stakeholder-definition>
<!-- REQUIRED: Include product philosophy, guiding principles, and scope lock -->
[Paste relevant sections from stakeholder definition]
</stakeholder-definition>

<code-conventions>
<!-- REQUIRED: Include CLAUDE.md for coding standards -->
[Paste CLAUDE.md content]
</code-conventions>

<architecture>
<!-- RECOMMENDED: Include if feature touches multiple components -->
[Paste relevant architecture sections]
</architecture>

<data-model>
<!-- RECOMMENDED: Include relevant entity definitions for the feature -->
[Paste docs/data-model/index.md conventions + the entity shards
 (docs/data-model/entities/) named in the Feature Brief's impact tables]
</data-model>

<api-spec>
<!-- RECOMMENDED: Include relevant endpoint definitions for the feature -->
[Paste docs/api-spec/index.md conventions + the endpoint shards
 (docs/api-spec/endpoints/) named in the Feature Brief's impact tables]
</api-spec>

<ui-specification>
<!-- RECOMMENDED: Include for user-facing features — screen specs, component hierarchy, interactions, states -->
[Paste docs/ui-specification/index.md Design System + the screen shards
 (docs/ui-specification/screens/) named in the Feature Brief's impact tables]
</ui-specification>

<persona>
<!-- OPTIONAL: Include if feature is user-facing -->
[Paste persona details]
</persona>

</context>

<task-type>New Feature</task-type>

<feature-brief>
<!-- PREFERRED: Paste the full Feature Brief document (from docs/work-items/FEAT-XXX-short-title.md).
     The Feature Brief template provides structured fields for scope, acceptance criteria,
     entity/API/UI impact, edge cases, constraints, and traceability.
     See .ai-framework/templates/feature-brief.md for the full template. -->
[Paste full Feature Brief content]
</feature-brief>

<!-- FALLBACK: If no Feature Brief exists, use this inline request instead.
     Remove the <feature-brief> block above and uncomment this block. -->
<!--
<inline-request>
Feature Name: [Name]
User Story: As a [persona], I want to [action], so that [benefit]
Primary Goal: [One sentence describing success]

Acceptance Criteria:
- [AC-1: Testable criterion]
- [AC-2: Testable criterion]
- [AC-3: Testable criterion]

Key Entities Involved:
- [Entity 1]: [Brief description of attributes and rules]
- [Entity 2]: [Brief description]

Edge Cases:
- [Edge case 1]
- [Edge case 2]
</inline-request>
-->

<request>
Generate a complete task breakdown for implementing this feature.
[Add any feature-specific focus or emphasis here.]
</request>

<constraints>
<!-- Add project-specific constraints -->
- Technology stack: [List technologies that must be used]
- Timeline constraint: [If any]
- Dependency constraints: [External factors]
- Security requirements: [Specific security needs]
</constraints>

</task-generation-request>
```

---

## Example

Pizza ordering feature.

> **Note:** This example uses the inline `<inline-request>` fallback for brevity. For higher-quality task generation, use a full Feature Brief document via `<feature-brief>` as described above.

```xml
<task-generation-request>

<context>

<stakeholder-definition>
## Product Philosophy
- Conversation-first: Feels like chat, not a form
- Keyboard-last: Typing only when unavoidable
- Progressive disclosure: Show only what's needed next

## Scope Lock (V1)
Included: Pizza ordering, Multi-pizza cart, Visual guidance
Excluded: Discounts, User accounts, Loyalty programs
</stakeholder-definition>

<code-conventions>
## File Structure
- Components in /src/components/{FeatureName}/
- Services in /src/services/
- Types in /src/types/

## Patterns
- Use Zod for validation
- Custom hooks for business logic
- Error boundaries for component errors
</code-conventions>

<architecture>
## Relevant Components
- Order Service: Handles order lifecycle
- Menu Service: Provides available items and pricing
- WhatsApp Flows: UI layer for all interactions

## Data Flow
User → WhatsApp → Flow Engine → Order Service → Database
</architecture>

</context>

<task-type>New Feature</task-type>

<inline-request>
Feature Name: Half-and-Half Pizza Selection
User Story: As a pizza customer, I want to select two different flavors for my pizza (half-and-half), so that I can enjoy variety in one order.
Primary Goal: Enable two-flavor pizza orders without keyboard input

Acceptance Criteria:
- AC-1: User can select "Half & Half" option after choosing size
- AC-2: System shows two flavor selection steps sequentially
- AC-3: Both flavors displayed in order review
- AC-4: Price is average of both flavors + half-half surcharge
- AC-5: Option only available for Medium and Large sizes

Key Entities Involved:
- Pizza: size (enum), flavors (Flavor[], 1-3 based on size), base (enum)
- Business Rules: Personal=1 flavor, Standard=1-2, Party=1-3

Edge Cases:
- Same flavor selected for both halves (allow, no surcharge)
- User changes size after selecting flavors (reset selections)
</inline-request>

<request>
Generate implementation tasks for the half-and-half pizza feature.
Ensure all acceptance criteria are covered and follow the existing
WhatsApp Flows pattern used for single-flavor selection.
</request>

<constraints>
- Must work within WhatsApp Flows JSON structure
- Cannot add new external dependencies
- Must maintain existing cart functionality
- Pricing calculation must be server-side
</constraints>

</task-generation-request>
```
