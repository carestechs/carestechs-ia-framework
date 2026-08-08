# Task Implementation Plan Prompt

---

## Purpose

Generate a per-task implementation plan that bridges "what to do" (task definition) and "how to do it" (exact code changes). Plans are developer-facing workflow artifacts — not stakeholder documents. They live in `plans/` and are consumed by the implementing developer or AI agent.

**When to use:** After picking a task (T-XXX) from a generated task list in `tasks/<WORK-ITEM-ID>-tasks.md` (e.g., `tasks/FEAT-012-tasks.md`) and completing any workflow prerequisites (mockup approval, investigation). Use before starting implementation — for every task, regardless of complexity.

**When to skip:** Only skip for trivial single-line fixes where the task definition already contains all necessary implementation detail (e.g., "change constant X from 5 to 10 in file Y").

Task definitions follow the canonical task schema in `prompts/base-template.md`, so every task is guaranteed to carry the fields this prompt relies on — in particular **Files to Modify/Create** and **Acceptance Criteria**.

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the task definition (T-XXX) from the task list file `tasks/<WORK-ITEM-ID>-tasks.md`, read `CLAUDE.md` for conventions, read the files listed in the task's "Files to Modify/Create" to understand current code state, add relevant specs per Required Context below, follow the sections below, and **write** the plan to `plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md`.
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the [Chat Workflow Template (XML)](#chat-workflow-template-xml) appendix. Include this prompt's Guidance and Output Format sections alongside the skeleton so the assistant knows the rules and plan structure.

---

## Required Context

Plan generation has its own context recipe (it operates on a single task, not a work item — the canonical task-generation matrix in `guides/context-compilation.md` does not apply here):

| Task Origin | Required Context | Conditional Context |
|-------------|-----------------|---------------------|
| All tasks | `CLAUDE.md`, task definition (from `tasks/<WORK-ITEM-ID>-tasks.md`), files listed in "Files to Modify/Create" | — |
| Feature tasks | — | The entity/endpoint/screen shards referenced by the task — `docs/data-model/entities/<entity>.md`, `docs/api-spec/endpoints/<resource>.md`, `docs/ui-specification/screens/<screen>.md` — plus each loaded spec's `index.md` for conventions (based on which layers the task touches) |
| Bugfix tasks | — | `docs/ARCHITECTURE.md` (for understanding system structure) |
| Refactoring tasks | — | `docs/ARCHITECTURE.md` (for understanding module boundaries) |
| Frontend tasks | — | `docs/ui-specification/screens/<screen>.md` (target screen shard) + the Design System sections from `docs/ui-specification/index.md` |

### What NOT to Include

- Whole spec directories or full documents — load only the shards the task references and the sections relevant to the task's files and domain
- Stakeholder definition — plans are implementation-level, not strategic
- Persona documents — plans deal with code, not user experience
- Other task definitions — each plan addresses one task only

---

## Guidance

### Plan Generation Rules

1. **One plan per task** — each plan addresses exactly one task (T-XXX)
2. **Steps are ordered** — implementation steps follow a logical dependency order (e.g., create types before services that use them)
3. **File-level specificity** — every step names the exact file and action (Create / Modify / Delete)
4. **Reference conventions** — cite patterns from CLAUDE.md when a step must follow a specific convention
5. **No ambiguity** — each step should be specific enough for a developer to implement without further questions
6. **Edge cases surfaced** — identify boundary conditions, error states, and integration risks
7. **Acceptance-linked verification** — map each acceptance criterion from the task to a concrete verification step

### Workflow

**Step 1: Pick a Task.** Select the next task from the task list (`tasks/<WORK-ITEM-ID>-tasks.md`), respecting dependency order. Verify all blocking tasks are complete.

**Step 2: Complete Workflow Prerequisites.** Check the task's **Workflow** field and complete any prerequisites before planning:
- `standard` — proceed directly to Step 3
- `mockup-first` — ensure mockup is generated and approved
- `investigation-first` — ensure investigation is complete and findings are documented

**Step 3: Assemble Context.** Read the task definition, `CLAUDE.md`, and the files listed in "Files to Modify/Create". Add conditional context based on which layers the task touches (see Required Context).

**Step 4: Generate Plan.** Run the prompt. The AI produces the plan file.

**Step 5: Review the Plan.** Verify the plan covers all acceptance criteria, steps are in dependency order, and file references are accurate.

**Step 6: Implement.** Follow the plan's implementation steps in order. Mark each acceptance verification item as complete.

---

## Output Format

**Output file:** `plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md` — uppercase `T-XXX`, kebab-case short title. Example: `plans/plan-FEAT-012-T-035-delivery-fee-service.md`. AI agents write this file.

> **Work-item-qualified filename.** Task IDs restart at `T-001` in every task list, so an
> unqualified artifact name does not say which work item owns it. Include the work-item id
> (e.g. `FEAT-002-T-001-...`): `next-step.py` refuses to use an unqualified artifact as
> evidence when another task list declares the same ID, because crediting another work
> item's artifact skips real work. Legacy unqualified names still work while the ID is unique.


**Plan budget** (the output budget for plans — a plan is the implementing developer's or agent's context, so verbosity degrades implementation precision): a plan is ≤ ~150 lines and ≤ 10 implementation steps, and each step names concrete files and changes. If a plan wants more, the task is too big — send it back to the task list for splitting.

Generate a markdown file with this structure:

```markdown
# Implementation Plan: T-XXX — [Task Title]

## Task Reference
- **Task ID:** T-XXX
- **Type:** [from task]
- **Workflow:** [from task]
- **Complexity:** [from task]
- **Rationale:** [from task]

## Overview
[2-3 sentences: what this task accomplishes and why, in plain language]

## Implementation Steps

### Step 1: [Action verb — e.g., "Create the delivery fee service"]
**File:** `path/to/file.ts`
**Action:** [Create | Modify | Delete]
[Detailed description of what to do — specific enough for a developer
to implement without ambiguity. Reference patterns from CLAUDE.md.]

### Step 2: [Action]
**File:** `path/to/file.ts`
**Action:** [Create | Modify | Delete]
[Detailed description]

## Files Affected
| File | Action | Summary |
|------|--------|---------|
| `path/to/file.ts` | Modify | [one-line description] |

## Edge Cases & Risks
- [Edge case and how to handle it]
- [Risk and mitigation]

## Acceptance Verification
- [ ] [How to verify AC-1 from the task]
- [ ] [How to verify AC-2]
```

---

## Constraints

- One plan covers exactly one task — do not merge tasks or plan ahead for future tasks
- The plan must not expand the task's scope: no steps beyond the task definition's Description and Acceptance Criteria
- Every file listed in the task's "Files to Modify/Create" must be covered by at least one step
- Respect the plan budget: ≤ ~150 lines and ≤ 10 implementation steps, each step naming concrete files and changes — a plan that needs more means the task is too big; send it back for splitting
- Do not generate a plan for a task whose Workflow prerequisites (mockup approval, investigation) are incomplete

---

## Post-Generation Checklist

After the AI generates a plan file, verify:

- [ ] Plan file is saved to `plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md` with correct naming (uppercase `T-XXX`, kebab-case title)
- [ ] Task Reference section matches the task definition exactly
- [ ] Overview clearly explains what and why in plain language
- [ ] Every file in the task's "Files to Modify/Create" is covered by at least one step
- [ ] Steps are in dependency order (types before services, services before components)
- [ ] Each step names an exact file path and action (Create / Modify / Delete)
- [ ] Steps reference CLAUDE.md conventions where applicable
- [ ] Files Affected table is complete and consistent with the steps
- [ ] Every acceptance criterion from the task maps to at least one verification item
- [ ] Plan respects the plan budget (≤ ~150 lines, ≤ 10 steps, concrete files per step) — an oversized plan means the task goes back for splitting
- [ ] Edge cases and risks are identified (not just a placeholder section)

---

## Chat Workflow Template (XML)

```xml
<plan-generation-request>

<context>

<task-definition>
<!-- REQUIRED: The full task block (T-XXX) from the task list file
     (tasks/<WORK-ITEM-ID>-tasks.md), including all canonical schema fields:
     Title, Type, Workflow, Description, Rationale, Acceptance Criteria,
     Dependencies, Complexity, Files to Modify/Create. -->
[Paste the complete task definition block]
</task-definition>

<code-conventions>
<!-- REQUIRED: Project conventions, patterns, and anti-patterns from CLAUDE.md.
     Ensures the plan follows established codebase patterns. -->
[Paste relevant sections from CLAUDE.md]
</code-conventions>

<current-code>
<!-- REQUIRED: The current content of files listed in the task's
     "Files to Modify/Create" section. Enables step-level specificity. -->
[Paste the current content of each file the task touches]
</current-code>

<data-model>
<!-- CONDITIONAL: Include for tasks that touch entities, database, or data flow.
     Provides entity shapes, relationships, and constraints. -->
[Paste the entity shards the task references (docs/data-model/entities/<entity>.md)
 + conventions from docs/data-model/index.md]
</data-model>

<api-spec>
<!-- CONDITIONAL: Include for tasks that touch API endpoints or DTOs.
     Provides endpoint contracts and response shapes. -->
[Paste the endpoint shards the task references (docs/api-spec/endpoints/<resource>.md)
 + conventions from docs/api-spec/index.md]
</api-spec>

<ui-specification>
<!-- CONDITIONAL: Include for frontend tasks that touch screens or components.
     Provides component hierarchy, states, and layout. -->
[Paste the target screen shard (docs/ui-specification/screens/<screen>.md)
 + the Design System sections from docs/ui-specification/index.md]
</ui-specification>

<architecture>
<!-- CONDITIONAL: Include for tasks that add new components, services, or
     cross-cutting concerns. Provides system structure and module boundaries. -->
[Paste relevant sections from docs/ARCHITECTURE.md]
</architecture>

</context>

<plan-scope>
<!-- Identifies the target task only — the full block lives in <task-definition> above. -->
Task ID: [T-XXX]
Task Title: [from task definition]
</plan-scope>

</plan-generation-request>
```

---

## Example

Feature task plan.

```xml
<plan-generation-request>

<context>

<task-definition>
### T-035: Add delivery fee calculation to order summary

**Type:** Backend
**Workflow:** standard

**Description:**
Calculate a delivery fee based on distance and display it in the order
summary. Fee = base rate + per-km charge. Free delivery over $50.

**Rationale:**
Orders currently omit delivery costs, so totals shown at checkout are
inaccurate and support receives pricing complaints.

**Acceptance Criteria:**
- [ ] AC-1: Delivery fee appears as a line item in the order summary
- [ ] AC-2: Fee is $0 when subtotal exceeds $50
- [ ] AC-3: Fee calculation uses base rate + per-km charge from config

**Dependencies:** T-034
**Complexity:** M

**Files to Modify/Create:**
- Create: `src/services/delivery-fee.service.ts`
- Modify: `src/components/OrderSummary.tsx`
- Modify: `src/types/order.ts`
</task-definition>

<code-conventions>
- Use TypeScript strict mode
- Services follow the repository pattern
- All monetary values in cents (integer)
- Prefer named exports
</code-conventions>

<current-code>
// src/components/OrderSummary.tsx — current version
// src/types/order.ts — current version
[Paste current file contents]
</current-code>

</context>

<plan-scope>
Task ID: T-035
Task Title: Add delivery fee calculation to order summary
</plan-scope>

</plan-generation-request>
```

**Output:** `plans/plan-FEAT-012-T-035-delivery-fee-service.md`
