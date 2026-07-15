# Refactoring Task Generation Prompt

---

## Purpose

Generate tasks for refactoring code while maintaining functionality. Use this when improving code quality, architecture, or preparing for new features.

Improvements should be described in an **Improvement Proposal** (`docs/work-items/IMP-XXX-short-title.md`) before task generation. An inline description (`<inline-request>`) is supported as a fallback for quick/ad-hoc usage.

This prompt uses the **canonical task schema defined in `prompts/base-template.md`** (field list, order, enums, grouping). Deltas declared here: the `Type` enum adds **`Cleanup`**; tasks are organized into the five-phase safety structure below with phase-preset `Workflow` values.

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the context files listed in your project CLAUDE.md's routing table for "Refactoring", read the Improvement Proposal from `docs/work-items/IMP-XXX-short-title.md` (if none exists, gather the refactoring scope from the user as an inline request), follow the sections below, and **write** the task list to `tasks/IMP-XXX-tasks.md` (or `tasks/adhoc-short-title-tasks.md` for inline requests with no work item).
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the [Chat Workflow Template (XML)](#chat-workflow-template-xml) appendix. Include this prompt's Output Format and Constraints sections alongside the skeleton so the assistant knows the expected schema.

---

## Required Context

Context selection lives in the **canonical matrix**: `guides/context-compilation.md` (humans) or the CLAUDE.md routing table (agents).

For refactoring: **required** = Improvement Proposal + CLAUDE.md + Architecture (current and target structure); **optional** = Data Model (data layer refactoring), Stakeholder Definition (large-scale refactoring that affects product scope).

Spec docs are **sharded**: when data-layer context is needed, read `docs/data-model/index.md` plus **only** the entity shards named by the Improvement Proposal's scope (Affected Entities), mapped via the kebab-case naming rule (entity `TaskLabel` → `docs/data-model/entities/task-label.md`, singular). Do not read whole spec directories.

Prompt-specific notes:

- **Improvement Proposal** (preferred): `docs/work-items/IMP-XXX-short-title.md` provides structured risk assessment, success criteria, test coverage baseline, and traceability. Generates safer, better-phased refactoring tasks.
- **Inline `<inline-request>`** (fallback): use for quick/ad-hoc refactoring when a full Improvement Proposal hasn't been written yet. Faster but less structured.

---

## Guidance

Generate tasks to refactor the identified area. Tasks should:

1. Start with test coverage verification/improvement
2. Proceed in small, safe increments
3. Maintain functionality at every step (no broken intermediate states)
4. Include migration steps if data/API changes needed
5. End with cleanup of old code
6. Verify no regression after each major change

Do not:

- Change functionality (this is refactoring, not enhancement)
- Introduce new features during refactoring
- Leave dead code or commented-out old code
- Skip test updates for changed code

### Workflow Classification

Refactoring tasks default to **`standard`** — refactoring maintains existing functionality. The full enum remains valid: use `investigation-first` when the current behavior of the code being refactored is poorly understood and must be documented before restructuring; `mockup-first` applies only in the rare case a refactoring legitimately reworks a user-facing screen.

### Common Refactoring Patterns

When generating refactoring tasks, consider these safe patterns:

**1. Strangler Fig Pattern**
- Build new alongside old
- Gradually migrate consumers
- Delete old when unused

**2. Branch by Abstraction**
- Introduce abstraction layer
- Implement old behavior behind abstraction
- Implement new behavior behind abstraction
- Switch via configuration/flag
- Remove old implementation

**3. Parallel Change**
- Add new field/method alongside old
- Migrate consumers one by one
- Remove old field/method

**4. Extract and Delegate**
- Extract subset of functionality to new module
- Original delegates to new module
- Gradually move more logic to new module

---

## Output Format

**Output file:** `tasks/IMP-XXX-tasks.md` (matching the Improvement Proposal's ID; `tasks/adhoc-short-title-tasks.md` for inline requests). AI agents write this file — the task list is not just chat output.

**Task blocks:** use the canonical task schema from `prompts/base-template.md`, all fields in canonical order — Task ID, Title, Type, Workflow, Description, Rationale, Acceptance Criteria, Dependencies, Complexity (`S | M | L | XL`), Files to Modify/Create, Technical Notes (optional). `Type` enum delta: adds `Cleanup`. Every task block in every phase includes Description and Acceptance Criteria. No nested sub-task lists — one T-XXX block per unit of work. In **Files to Modify/Create**, suffix files that don't exist yet with `(new)` — example: `- src/services/label-service.ts (new) - label CRUD logic`.

**Budgets:** respect the output budgets defined in `prompts/base-template.md` — generated task lists are downstream context.

Generate tasks in phases that ensure safety:

### Phase 0: Preparation (Safety Net)

Create **separate tasks** for the coverage baseline and for each coverage gap — do not nest a sub-task list inside one block.

```
### T-[XXX]: Establish test coverage baseline for [affected area]

**Type:** Testing
**Workflow:** standard

**Description:**
[Measure and document current test coverage for the code being refactored;
list untested scenarios and missing edge cases]

**Rationale:**
[1-2 sentences: why a documented baseline is needed before refactoring begins]

**Acceptance Criteria:**
- [ ] Current coverage for the affected area measured and documented
- [ ] Coverage gaps listed (untested scenarios, missing edge cases)
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [coverage report / baseline notes location]
```

```
### T-[XXX]: Add tests for [uncovered scenario or edge case]

**Type:** Testing
**Workflow:** standard

**Description:**
[Add the missing tests for one specific gap identified in the baseline task —
create one task like this per coverage gap]

**Rationale:**
[1-2 sentences: why this scenario must be covered before the refactoring touches it]

**Acceptance Criteria:**
- [ ] Scenario has passing test coverage
- [ ] Tests exercise current (pre-refactoring) behavior

**Dependencies:** [T-XXX]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [test/file/path] - [tests added]
```

### Phase 1: Safe Parallel Implementation

```
### T-[XXX]: [Create new structure]

**Type:** [Backend | Frontend]
**Workflow:** standard

**Description:**
[Create new implementation alongside old, without removing old]

**Rationale:**
[1-2 sentences: why this new structure is needed — which problem from the current state it resolves]

**Acceptance Criteria:**
- [ ] New structure is complete
- [ ] Old code still works unchanged
- [ ] New structure passes all intended tests

**Dependencies:** [T-XXX, T-YYY]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [new/file/path.ts] - [purpose]

**Technical Notes:**
- Approach: [how to build new structure without breaking old]
- Coexistence strategy: [how old and new will coexist temporarily]
```

### Phase 2: Migration

```
### T-[XXX]: [Migrate component/consumer X]

**Type:** [Backend | Frontend]
**Workflow:** standard

**Description:**
[Switch specific consumer from old to new implementation]

**Rationale:**
[1-2 sentences: why this consumer needs to migrate — what benefit the new implementation provides]

**Acceptance Criteria:**
- [ ] Component uses new implementation
- [ ] All tests still pass
- [ ] No regression in functionality

**Dependencies:** [T-XXX, T-YYY]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [consumer/file/path.ts] - [switch to new implementation]

**Technical Notes:**
- Migration steps: [ordered steps, ending with functional verification]
- Rollback plan: [how to quickly revert if problems found]
```

### Phase 3: Cleanup

```
### T-[XXX]: Remove old implementation

**Type:** Cleanup
**Workflow:** standard

**Description:**
[Remove old code now that migration is complete]

**Rationale:**
[1-2 sentences: why cleanup is safe now — what migration milestones confirm the old code is unused]

**Acceptance Criteria:**
- [ ] No references to old implementation remain
- [ ] No dead code left behind
- [ ] Build succeeds
- [ ] All tests pass

**Dependencies:** [T-XXX, T-YYY — all migration task IDs]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [old/file/path.ts] - DELETE
- [file/with/imports.ts] - remove old imports
```

### Phase 4: Verification

```
### T-[XXX]: Final verification

**Type:** Testing
**Workflow:** standard

**Description:**
[Run the full verification pass across the refactored area — original and new
test suites, static checks, performance benchmarks, and documentation review]

**Rationale:**
[1-2 sentences: why final verification is needed — what confidence it provides that the refactoring preserved behavior]

**Acceptance Criteria:**
- [ ] All original tests pass
- [ ] New tests pass
- [ ] Performance benchmarks met (if applicable)
- [ ] No type/lint errors
- [ ] Documentation updated
- [ ] Team walkthrough completed (if significant change)

**Dependencies:** [T-XXX, T-YYY — cleanup task IDs]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [documentation files to update, if any]
```

### Summary Section

After all tasks, provide:

- Total tasks by phase
- Critical path and estimated sequence
- Risk assessment
- Recommended review points (where to pause and verify)
- Rollback strategy summary

### Acceptance Criteria Coverage (recommended)

When the Improvement Proposal defines success criteria / acceptance criteria, end the task list with:

```markdown
## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: [text] | T-003, T-007 |
```

---

## Constraints

- No functionality changes — this is refactoring, not enhancement
- Every phase must leave the system in a working state
- Old code is removed only after all consumers have migrated and verification passes
- One `Type` per task; Dependencies are plain task ID lists (or `None`)
- Apply the project-specific constraints supplied in the request, e.g.:
  - Must maintain backward compatibility: [Yes/No, details]
  - Can break internal APIs: [Yes/No]
  - Deployment strategy: [All at once | Incremental | Feature flagged]
  - Rollback plan required: [Yes/No]

---

## Post-Generation Checklist

- [ ] Run `python .ai-framework/tools/validate-tasks.py tasks/IMP-XXX-tasks.md` and fix every error
- [ ] Run `python .ai-framework/tools/validate-specs.py` and fix every error — confirms the spec shards the task list relies on are internally consistent and fresh

### Safety Checklist

Before approving generated refactoring tasks:

- [ ] Tests are written/verified BEFORE refactoring begins
- [ ] Each phase leaves system in working state
- [ ] No "big bang" changes that can't be incrementally deployed
- [ ] Rollback strategy exists for each significant change
- [ ] Old code removed only after verification
- [ ] Documentation updates included
- [ ] Team review points identified
- [ ] Performance implications considered
- [ ] No functionality changes hidden in refactoring

### Schema Checklist

- [ ] Every task block (all phases) has Description and Acceptance Criteria
- [ ] Every task respects the output budgets defined in `prompts/base-template.md`
- [ ] No nested sub-task lists — each unit of work is its own T-XXX block
- [ ] Complexity uses the full `S | M | L | XL` scale
- [ ] Dependencies are plain task ID lists (or `None`) forming a valid DAG
- [ ] Task list saved to `tasks/IMP-XXX-tasks.md` (agents)

---

## Chat Workflow Template (XML)

```xml
<task-generation-request>

<context>

<code-conventions>
<!-- REQUIRED: Include CLAUDE.md for target patterns -->
[Paste CLAUDE.md content]
</code-conventions>

<architecture>
<!-- REQUIRED: Include current and target architecture -->
[Paste architecture documentation]
</architecture>

<stakeholder-definition>
<!-- OPTIONAL: Include for large-scale refactoring that affects product scope -->
[Paste principles and scope lock if relevant]
</stakeholder-definition>

</context>

<task-type>Refactoring</task-type>

<improvement-proposal>
<!-- PREFERRED: Paste the full Improvement Proposal document (from docs/work-items/IMP-XXX-short-title.md).
     The Improvement Proposal template provides structured fields for current/desired state,
     risk assessment, success criteria, test coverage, and traceability.
     See .ai-framework/templates/improvement-proposal.md for the full template. -->
[Paste full Improvement Proposal content]
</improvement-proposal>

<!-- FALLBACK: If no Improvement Proposal exists, use this inline request instead.
     Remove the <improvement-proposal> block above and uncomment this block. -->
<!--
<inline-request>
**Refactoring Type:** [Code Quality | Architecture | Performance | Testability | Maintainability]

**Target Area:**
[Specific component, module, or system being refactored]

**Current State:**
[Description of current implementation and its problems]

**Problems with Current State:**
1. [Problem 1 - e.g., "God class with too many responsibilities"]
2. [Problem 2 - e.g., "Difficult to test due to tight coupling"]
3. [Problem 3 - e.g., "Duplicated logic across multiple files"]

**Desired State:**
[Description of what the code should look like after refactoring]

**Benefits of Refactoring:**
1. [Benefit 1 - e.g., "Easier to add new payment methods"]
2. [Benefit 2 - e.g., "Reduced test complexity"]
3. [Benefit 3 - e.g., "Better separation of concerns"]

**Trigger/Motivation:**
[Why now? e.g., "Preparing for new feature X" or "Tech debt sprint"]

**Affected Entities/Data:**
- [Entity 1]: [What changes about how this entity is handled]
- [Entity 2]: [What changes]

**Current Test Coverage:**
- [Current coverage status for affected area]
- [Known gaps or concerns]
</inline-request>
-->

<request>
Generate tasks to refactor the identified area.
[Add any refactoring-specific focus here.]
</request>

<constraints>
<!-- Add project-specific constraints -->
- Must maintain backward compatibility: [Yes/No, details]
- Can break internal APIs: [Yes/No]
- Deployment strategy: [All at once | Incremental | Feature flagged]
- Rollback plan required: [Yes/No]
- [Additional constraints]
</constraints>

</task-generation-request>
```

---

## Example

Service extraction.

> **Note:** This example uses the inline `<inline-request>` fallback for brevity. For safer, better-phased refactoring tasks, use a full Improvement Proposal document via `<improvement-proposal>` as described above.

```xml
<task-generation-request>

<context>

<code-conventions>
## Service Pattern
- One responsibility per service
- Services injected via dependency injection
- All external calls wrapped in services

## Testing
- Services must have unit tests with mocked dependencies
- Integration tests for service interactions
</code-conventions>

<architecture>
## Current Structure
OrderController → OrderService (handles orders, payments, notifications)

## Target Structure
OrderController → OrderService → PaymentService
                              → NotificationService

## Component Details
- OrderService: Currently 1500 lines, handles order CRUD, payments, notifications
- PaymentService (new): Will handle Stripe integration
- NotificationService (new): Will handle WhatsApp and Email
</architecture>

</context>

<task-type>Refactoring</task-type>

<inline-request>
**Refactoring Type:** Architecture

**Target Area:** OrderService

**Current State:**
OrderService is a 1500-line file that handles:
- Order CRUD operations
- Payment processing (Stripe integration)
- Notification sending (WhatsApp, Email)
- Pricing calculations

**Problems with Current State:**
1. God class - too many responsibilities
2. Hard to test - many dependencies
3. Hard to modify - changes risk breaking unrelated features
4. Payment and notification logic duplicated in other services

**Desired State:**
- OrderService: Only order lifecycle management
- PaymentService: All payment logic
- NotificationService: All notification logic

**Benefits:**
1. Easier to test each service in isolation
2. Payment method changes isolated to PaymentService
3. Notification channel changes isolated to NotificationService

**Trigger:** Need to add Apple Pay support, current structure makes this risky

**Affected Entities/Data:**
- Order: processPayment() and sendNotification() methods to be moved
- Payment: Will become its own service boundary
- Notification: Will become its own service boundary

**Current Test Coverage:**
- OrderService has ~60% coverage
- Payment paths well-tested, notification paths have gaps
- No integration tests between payment and notification flows
</inline-request>

<request>
Generate tasks to extract PaymentService and NotificationService from OrderService.
</request>

<constraints>
- Must maintain API compatibility (OrderService public methods unchanged)
- Can be deployed incrementally
- Must have feature flag to rollback payment service extraction
</constraints>

</task-generation-request>
```

### Anti-Example (would fail review)

A big-bang rewrite — do **not** generate blocks like this:

```
### T-001: Rewrite the notification system

**Type:** Backend
**Workflow:** standard

**Description:**
Replace the old notification code everywhere with the new service in one pass. Old code will be deleted in the same change.

**Rationale:**
The current code is messy.

**Acceptance Criteria:**
- [ ] New system in place

**Dependencies:** [all previous tasks]
**Complexity:** XL

**Files to Remove/Modify:**
- src/**/*.ts - everything touching notifications
```

**Why it fails:**

- No Phase 0 coverage-baseline task precedes it — tests must be written/verified BEFORE refactoring begins, so there is no safety net
- Big-bang replace + delete in one task — defeats the phased coexistence/migration structure (parallel implementation → migration → cleanup) and the "no big-bang changes" safety rule
- "New system in place" is not a testable acceptance criterion
- **Dependencies** `[all previous tasks]` is not a plain task ID list (or `None`) — validator error
- **Files to Remove/Modify** is not the canonical field name — the schema requires **Files to Modify/Create** everywhere — validator error
- A glob of everything (`src/**/*.ts`) is not a reviewable file list — name concrete files and what changes in each
- No rollback consideration in Technical Notes — every significant change needs a rollback strategy
