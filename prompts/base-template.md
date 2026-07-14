# Base Prompt Template for Claude

> The foundational structure for all Claude task generation prompts — and the **single canonical definition of the task schema**. Task-specific prompts (feature-tasks.md, bugfix-tasks.md, refactor-tasks.md) build on this file.

---

## Purpose

Use this template to generate task lists for any development work. It serves two roles:

1. **Canonical schema.** The task block schema below (field list, field order, enums, grouping scheme) is defined **only here**. Task-specific prompts declare deltas (extra `Type` values, phase presets) — never a competing schema.
2. **Direct use for task types without a dedicated prompt.** Testing, Integration, and Prioritization work has no dedicated prompt — use this base template with the context recipe for that task type from the canonical matrix (see Required Context).

**Precedence:** For features, bug fixes, and refactoring, use the corresponding task-specific prompt (feature-tasks.md, bugfix-tasks.md, refactor-tasks.md) — it defines the procedure, phase presets, and `Type`-enum deltas. The task schema itself always lives here; if a task prompt appears to conflict with this schema, this file wins.

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the context files listed in your project CLAUDE.md's routing table for the task type, follow the sections below (Guidance → Output Format → Constraints → Post-Generation Checklist), and **write** the resulting task list to a file: `tasks/FEAT-XXX-tasks.md` / `tasks/BUG-XXX-tasks.md` / `tasks/IMP-XXX-tasks.md` (matching the work item), or `tasks/adhoc-short-title-tasks.md` for inline requests with no work item.
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the [Chat Workflow Template (XML)](#chat-workflow-template-xml) appendix — paste your documentation into the `<context>` placeholders and submit. Include this prompt's Output Format and Constraints sections alongside the skeleton so the assistant knows the expected schema.

---

## Required Context

Context selection per task type lives in the **canonical matrix**: `guides/context-compilation.md` (for humans assembling context) or the routing table in your project's `CLAUDE.md` (for agents). Do not maintain a separate list here.

Prompt-specific notes:

- **Rule of thumb:** Work item documents (Feature Brief, Bug Report, Improvement Proposal) are the primary input for task generation — they describe *what* to do. CLAUDE.md is almost always required for *how* to do it. Add Data Model + API Spec for work involving entities/endpoints, UI Spec for user-facing work, Architecture for structural work, Stakeholder for scope questions, Persona for user-facing decisions.
- **Testing / Integration / Prioritization:** no dedicated prompt exists — use this base template with the context recipe for that task type from the canonical matrix.

---

## Guidance

### Request Clarity

**Be specific about:**
- The exact outcome you want
- What "done" looks like
- Any decisions already made
- What you DON'T want

**Example - Vague Request:**
```
Add user authentication to the app
```

**Example - Clear Request:**
```
Implement email/password authentication with the following:
- Registration endpoint with email verification
- Login endpoint returning JWT tokens
- Password reset flow via email
- Middleware for protecting routes
- Following patterns in CLAUDE.md for error handling
```

### Specifying Constraints

**Always specify:**
- Technology constraints (must use X, cannot use Y)
- Time/complexity constraints (MVP only, full implementation)
- Compatibility requirements (must work with existing X)
- Security requirements (must validate X, must not expose Y)

### Shaping the Output

**Be explicit about:**
- Task granularity (how detailed?)
- Grouping preferences
- Priority indicators needed
- Dependency mapping requirements

### Prompting Tips

**Ask for clarification:**
```
If any requirements are ambiguous or you need more information
to generate accurate tasks, list your questions before proceeding.
```

**Request alternatives:**
```
For any task where multiple approaches are viable, briefly note
the alternatives and which you recommend.
```

**Include rationale:**
```
For each major task, include a brief rationale explaining why
this task is necessary and how it contributes to the goal.
```

---

## Output Format

### Canonical Task Schema

Every task block, in every task list, in every prompt, uses these fields **in this order**:

```
### T-[XXX]: [Verb-first task title]

**Type:** [Backend | Frontend | Database | Testing | DevOps | Documentation]
**Workflow:** [standard | mockup-first | investigation-first]

**Description:**
[2-3 sentences describing what needs to be done]

**Rationale:**
[1-2 sentences: why this task exists — which requirement, business rule,
or architectural need it addresses]

**Acceptance Criteria:**
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]

**Dependencies:** [T-XXX, T-YYY — or "None"]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [file/path/example.ts] - [what changes]

**Technical Notes:** (optional)
[Implementation guidance, patterns to follow, or gotchas to avoid]
```

Field rules:

1. **Task ID** — sequential within one task list (T-001, T-002, ...)
2. **Title** — short, verb-first, action-oriented
3. **Type** — exactly **one** value per task. If a task spans types (e.g., Backend + Frontend), split it into separate tasks. Deltas: bugfix-tasks adds `Investigation`; refactor-tasks adds `Cleanup`.
4. **Workflow** — all three values are valid for **all** task types:
   - **`standard`** — implement directly, no prerequisite artifacts.
   - **`mockup-first`** — generate an HTML mockup for stakeholder approval before implementing. Use for tasks that add or significantly change a user-facing screen.
   - **`investigation-first`** — investigate and document root cause before proposing a fix. Use for bug investigation tasks or any task with ambiguous requirements.
5. **Description** — what needs to be done
6. **Rationale** — 1-2 sentences linking to a requirement, business rule, or architectural need
7. **Acceptance Criteria** — a checklist of testable criteria. **Every task block in every phase gets this field** — no exceptions.
8. **Dependencies** — comma-separated task IDs (`T-001, T-002`) or `None`. No free-text annotations.
9. **Complexity** — `S | M | L | XL` (full scale, always)
10. **Files to Modify/Create** — exact field name everywhere; list likely files and what changes
11. **Technical Notes** — optional

**No nested sub-task lists inside a task block.** If a task needs sub-tasks, split it into separate T-XXX tasks.

### Task Grouping

Group tasks using the canonical grouping scheme, in this order (omit empty groups):

1. **Foundation** — database, models, types, setup
2. **Backend** — services, API endpoints
3. **Frontend** — components, pages, state
4. **Integration** — connecting pieces
5. **Testing** — unit, integration, e2e tests
6. **Documentation & Polish** — docs, error handling refinement, edge cases, logging

---

## Constraints

- One `Type` per task — split tasks that span types
- Dependencies must form a valid DAG (no cycles) and reference only task IDs
- No tasks outside the stakeholder scope lock
- No over-engineered solutions beyond the stated requirements
- Respect the project-specific constraints supplied in the request (technology, compatibility, security)

---

## Post-Generation Checklist

After generating tasks, verify:

- [ ] Every task block contains all schema fields, in the canonical order
- [ ] Every task has Acceptance Criteria (no exceptions, in any phase)
- [ ] Each `Type` is a single value; tasks spanning types were split
- [ ] `Complexity` uses the full `S | M | L | XL` scale
- [ ] Dependencies are plain task ID lists (or `None`) and form a valid DAG
- [ ] Tasks are grouped per the canonical grouping scheme
- [ ] No tasks violate the stakeholder scope lock
- [ ] The task list is saved to the correct `tasks/` file (agents)

---

## Chat Workflow Template (XML)

Copy this skeleton, paste your documentation into the placeholders, and submit. The skeleton carries only context and input placeholders — the schema and rules live in the sections above.

```xml
<task-generation-request>

<context>
<!-- Include relevant documentation here using XML tags.
     See Required Context above for which documents to include. -->

<feature-brief>
<!-- Work item document (preferred). Use <bug-report> for bugs,
     <improvement-proposal> for improvements. -->
[Paste Feature Brief content from docs/work-items/FEAT-XXX-short-title.md]
</feature-brief>

<inline-request>
<!-- Fallback when no work item document exists: describe the work inline. -->
[Describe the work item inline — goal, acceptance criteria, known constraints]
</inline-request>

<stakeholder-definition>
[Paste stakeholder definition content - philosophy, scope lock, success metrics]
</stakeholder-definition>

<architecture>
[Paste architecture sections relevant to this task]
</architecture>

<code-conventions>
[Paste CLAUDE.md content]
</code-conventions>

<persona>
[Paste persona details if task is user-facing or needs prioritization context]
</persona>

<data-model>
[Paste relevant entity definitions from data-model.md]
</data-model>

<api-spec>
[Paste relevant endpoint definitions from api-spec.md]
</api-spec>

<ui-specification>
[Paste relevant screen specs from ui-specification.md]
</ui-specification>

</context>

<task-type>[New Feature | Bug Fix | Refactoring | Testing | Integration | Prioritization]</task-type>
<!-- Testing, Integration, and Prioritization have no dedicated prompt —
     use this base template with the context recipe from the canonical matrix. -->

<request>
[Describe what you need - be specific about the desired outcome]
</request>

<constraints>
- [Constraint 1: e.g., "Must be completed within existing architecture"]
- [Constraint 2: e.g., "No new dependencies allowed"]
- [Constraint 3: e.g., "Must maintain backward compatibility"]
</constraints>

</task-generation-request>
```

---

## Example

```xml
<task-generation-request>

<context>
<stakeholder-definition>
## Product Philosophy
- Conversation-first: Feels like chat, not a form
- Keyboard-last: Typing only when unavoidable

## Scope Lock (V1)
Included: Pizza ordering, Multi-pizza cart, Visual guidance
Excluded: Discounts, User accounts, Loyalty programs
</stakeholder-definition>

<code-conventions>
## File Structure
- Components in /src/components/
- Services in /src/services/
- Types in /src/types/

## Patterns
- Zod for validation
- Custom hooks for business logic
</code-conventions>
</context>

<task-type>New Feature</task-type>

<request>
Generate implementation tasks for adding a "reorder previous order"
feature. Users should be able to see their last 3 orders and
reorder any of them with a single tap.
</request>

<constraints>
- Must work within existing WhatsApp Flows framework
- Cannot require user authentication (use phone number from WhatsApp)
- Must respect current menu/pricing (no historical prices)
- Order history limited to last 30 days
</constraints>

</task-generation-request>
```

The output is a task list using the canonical task schema above, grouped per the canonical grouping scheme, with `Complexity` on the `S | M | L | XL` scale.
