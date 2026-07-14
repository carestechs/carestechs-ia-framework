# Bug Fix Task Generation Prompt

---

## Purpose

Generate investigation and fix tasks for reported bugs. This prompt helps structure bug analysis and produces actionable tasks for resolution.

Bugs should be described in a **Bug Report** (`docs/work-items/BUG-XXX-short-title.md`) before task generation. An inline description (`<inline-request>`) is supported as a fallback for quick/ad-hoc usage.

This prompt uses the **canonical task schema defined in `prompts/base-template.md`** (field list, order, enums, grouping). Deltas declared here: the `Type` enum adds **`Investigation`**; tasks are organized into the three-phase structure below with phase-preset `Workflow` values.

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the context files listed in your project CLAUDE.md's routing table for "Bug fix", read the Bug Report from `docs/work-items/BUG-XXX-short-title.md` (if none exists, gather the bug details from the user as an inline request), follow the sections below, and **write** the task list to `tasks/BUG-XXX-tasks.md` (or `tasks/adhoc-short-title-tasks.md` for inline requests with no work item).
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the [Chat Workflow Template (XML)](#chat-workflow-template-xml) appendix. Include this prompt's Output Format and Constraints sections alongside the skeleton so the assistant knows the expected schema.

---

## Required Context

Context selection lives in the **canonical matrix**: `guides/context-compilation.md` (humans) or the CLAUDE.md routing table (agents).

For bug fixes: **required** = Bug Report + CLAUDE.md; **optional** = Architecture, Data Model, API Spec, UI Specification (per bug type — e.g., data-model for data integrity/calculation bugs, api-spec for API response bugs, ui-specification for display bugs).

Spec docs are **sharded**: when a spec is needed, read that spec's index (`docs/data-model/index.md`, `docs/api-spec/index.md`, `docs/ui-specification/index.md`) plus **only** the shards named by the Bug Report's Affected Entities / impact tables, mapped via the kebab-case naming rule (entity `TaskLabel` → `docs/data-model/entities/task-label.md`; resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md`; screen "Project Board" → `docs/ui-specification/screens/project-board.md`). Do not read whole spec directories.

Prompt-specific notes:

- **Bug Report** (preferred): `docs/work-items/BUG-XXX-short-title.md` provides structured impact assessment, traceability, entity mapping, and severity justification. Generates more targeted investigation tasks.
- **Inline `<inline-request>`** (fallback): use for quick/ad-hoc bug fixes when a full Bug Report hasn't been written yet. Faster but less structured.

---

## Guidance

Generate tasks to investigate and fix the bug. Tasks should:

1. Start with investigation/diagnosis tasks
2. Identify root cause before proposing solutions
3. Include fix implementation tasks
4. Include regression tests to prevent recurrence
5. Consider related areas that might have the same issue
6. Include verification steps

Do not:

- Jump to solutions without investigation
- Over-engineer the fix
- Scope creep into refactoring unrelated code

### Three-Phase Structure

Organize tasks into three phases. The `Workflow` field is pre-set by phase:

- **Phase 1 — Investigation:** `Type: Investigation`, `Workflow: investigation-first` — complete investigation steps and document findings before any fix tasks begin.
- **Phase 2 — Implementation:** `Workflow: standard` — investigation is complete, proceed with the fix.
- **Phase 3 — Verification & Prevention:** `Type: Testing`, `Workflow: standard` — implement tests and verify.

(The full `Workflow` enum — including `mockup-first` — remains valid; it is simply rarely needed for bug fixes.)

---

## Output Format

**Output file:** `tasks/BUG-XXX-tasks.md` (matching the Bug Report's ID; `tasks/adhoc-short-title-tasks.md` for inline requests). AI agents write this file — the task list is not just chat output.

**Task blocks:** use the canonical task schema from `prompts/base-template.md`, all fields in canonical order — Task ID, Title, Type, Workflow, Description, Rationale, Acceptance Criteria, Dependencies, Complexity (`S | M | L | XL`), Files to Modify/Create, Technical Notes (optional). `Type` enum delta: adds `Investigation`. Every task block in every phase includes Description and Acceptance Criteria. In **Files to Modify/Create**, suffix files that don't exist yet with `(new)` — example: `- src/services/label-service.ts (new) - label CRUD logic`.

Phase presets:

> **Cross-system / contract bugs — first investigation step.** When the bug crosses a system boundary (an external API, a protocol, an NDJSON / JSON schema, a file format, an executor's response shape, a message queue payload, an SDK), the first investigation step MUST be **"verify the contract empirically against the producer."** Read the producer's authoritative source (its schema definitions, its own serialization tests, its OpenAPI doc), capture a real sample of the on-the-wire payload, and confirm the code-under-test's reader matches. The whole class of "silent shape mismatch" bugs — where both sides are wrong consistently and existing tests pass against a self-consistent fiction — is invisible without this step. Don't trust comments, type names, or harness fixtures that claim to mirror the producer; verify against the producer itself.

### Phase 1: Investigation

```
### T-[XXX]: [Verb-first investigation task title]

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
[What question this investigation answers and what will be examined]

**Rationale:**
[1-2 sentences: why this investigation is needed — what symptom or report triggered it]

**Acceptance Criteria:**
- [ ] Root cause identified, or hypothesis documented with supporting evidence
- [ ] Findings documented: what was confirmed, what was ruled out
- [ ] [Additional criteria specific to this investigation]

**Dependencies:** None
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [files or code areas to examine] - [what to look for]
- [where findings are recorded, e.g., the Bug Report's Root Cause section]

**Technical Notes:**
- Investigation steps: [ordered steps to perform]
- Expected findings: [what you expect to discover or rule out]
```

### Phase 2: Implementation

```
### T-[XXX]: [Verb-first fix task title]

**Type:** [Backend | Frontend | Database]
**Workflow:** standard

**Description:**
[What fix will be implemented]

**Rationale:**
[1-2 sentences: why this fix is needed — which root cause or investigation finding it addresses]

**Acceptance Criteria:**
- [ ] Bug no longer reproducible with original steps
- [ ] [Additional criteria]

**Dependencies:** [T-XXX, T-YYY — investigation task IDs]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [file/path] - [what changes]

**Technical Notes:**
- Root cause addressed: [how this fix addresses the root cause]
- Implementation approach: [high-level approach to the fix]
- Regression risk: [what could break, how to verify it doesn't]
```

### Phase 3: Verification & Prevention

```
### T-[XXX]: [Verb-first test/verification task title]

**Type:** Testing
**Workflow:** standard

**Description:**
[What testing will be done]

**Rationale:**
[1-2 sentences: why this verification is needed — what regression risk or edge case it guards against]

**Acceptance Criteria:**
- [ ] Test covering the exact bug scenario exists and passes
- [ ] Related scenarios and edge cases (incl. boundary values) are covered
- [ ] Full test suite passes — no regressions introduced by the fix

**Dependencies:** [T-XXX, T-YYY — fix task IDs]
**Complexity:** [S | M | L | XL]

**Files to Modify/Create:**
- [test/file/path] - [test cases added]

**Technical Notes:**
- Test cases: [the exact bug scenario, related scenarios, edge cases]
- Verification steps: [how to verify the fix works and nothing else broke]
```

### Summary Section

After all tasks, provide:

- Most likely root cause hypothesis
- Confidence level in diagnosis
- Risk assessment of proposed fix
- Monitoring recommendations post-fix
- Related areas to audit for similar issues

### Acceptance Criteria Coverage (recommended)

When the Bug Report defines acceptance criteria, end the task list with:

```markdown
## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: [text] | T-003, T-007 |
```

---

## Constraints

- Fix must not break existing functionality
- Must include a test that would have caught this bug
- Must update error handling if the error was unclear
- Investigation tasks precede fix tasks; fix tasks precede verification tasks (enforced via Dependencies)
- One `Type` per task; Dependencies are plain task ID lists (or `None`)
- Add project-specific constraints in the request

---

## Post-Generation Checklist

After Claude generates tasks, verify:

- [ ] Run `python .ai-framework/tools/validate-tasks.py tasks/BUG-XXX-tasks.md` and fix every error
- [ ] Investigation tasks come before fix tasks
- [ ] Root cause is identified, not just symptoms treated
- [ ] For cross-system / contract bugs: the investigation includes an explicit "verify the contract against the producer's authoritative source" step (schema, OpenAPI, producer-side tests, or a captured real payload) — not just an inspection of the consumer side
- [ ] If the bug involves a test harness or fake/mock of an external system: the investigation verifies the harness matches the real producer's output shape, not just the consumer's expected input shape
- [ ] Fix addresses root cause, not workaround
- [ ] Test would catch this bug if it regressed
- [ ] Boundary conditions are tested
- [ ] Related code areas are audited
- [ ] Error messages improved if they were unclear
- [ ] Monitoring/alerting considered for future detection
- [ ] Every task block (all three phases) has Description and Acceptance Criteria
- [ ] Complexity uses the full `S | M | L | XL` scale; dependencies are plain ID lists
- [ ] Task list saved to `tasks/BUG-XXX-tasks.md` (agents)

---

## Chat Workflow Template (XML)

```xml
<task-generation-request>

<context>

<code-conventions>
<!-- REQUIRED: Include CLAUDE.md for understanding code structure -->
[Paste CLAUDE.md content]
</code-conventions>

<architecture>
<!-- RECOMMENDED: Include if bug spans multiple components -->
[Paste relevant architecture sections]
</architecture>

<stakeholder-definition>
<!-- OPTIONAL: Include if scope clarification is needed -->
[Paste scope lock and principles if relevant]
</stakeholder-definition>

</context>

<task-type>Bug Fix</task-type>

<bug-report>
<!-- PREFERRED: Paste the full Bug Report document (from docs/work-items/BUG-XXX-short-title.md).
     The Bug Report template provides structured fields for reproduction steps, evidence,
     impact assessment, affected entities, and traceability.
     See .ai-framework/templates/bug-report.md for the full template. -->
[Paste full Bug Report content]
</bug-report>

<!-- FALLBACK: If no Bug Report document exists, use this inline request instead.
     Remove the <bug-report> block above and uncomment this block. -->
<!--
<inline-request>
**Bug ID:** [BUG-XXX]
**Severity:** [Critical | High | Medium | Low]
**Reported Date:** [Date]
**Reported By:** [Source - user, QA, monitoring, etc.]

**Summary:**
[One-line description of the bug]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Observe: unexpected behavior]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Environment:**
- Version: [App version]
- Platform: [Browser, OS, device]
- User context: [Relevant user state]

**Error Messages/Logs:**
[Any error messages, stack traces, or relevant log output]

**Additional Context:**
- Frequency: [Always | Sometimes | Rarely]
- First occurrence: [Date if known]
- Workaround exists: [Yes/No, describe if yes]
- Related bugs: [Links to related issues]

**Affected Entities/Data:**
- [Entity 1]: [Relevant attributes and business rules]
- [Entity 2]: [Relevant attributes]

**Known Error Patterns:**
- [Error code/pattern seen in logs]
- [Related error handling behavior]
</inline-request>
-->

<request>
Generate tasks to investigate and fix this bug.
[Add any bug-specific focus, e.g., which behavior to zero in on.]
</request>

<constraints>
- Fix must not break existing functionality
- Must include test that would have caught this bug
- Must update error handling if error was unclear
- [Add project-specific constraints]
</constraints>

</task-generation-request>
```

---

## Example

Order calculation bug.

> **Note:** This example uses the inline `<inline-request>` fallback for brevity. For more targeted investigation tasks, use a full Bug Report document via `<bug-report>` as described above.

```xml
<task-generation-request>

<context>

<code-conventions>
## Project Structure
- Services: /src/services/
- Models: /src/models/
- Tests: /src/tests/ (mirrors src structure)

## Error Handling
- Custom AppError class with error codes
- All errors logged with context
- User-facing messages sanitized
</code-conventions>

<architecture>
## Order Service
- Handles order creation, modification, totals
- Connects to Menu Service for pricing
- Persists to PostgreSQL via Prisma

## Data Flow
Cart → Order Service (calculate totals) → Database
                   ↓
          Menu Service (get prices)
</architecture>

</context>

<task-type>Bug Fix</task-type>

<inline-request>
**Bug ID:** BUG-234
**Severity:** High
**Reported Date:** 2024-01-15
**Reported By:** Customer complaint

**Summary:**
Order total shows incorrect amount when delivery fee should be waived

**Steps to Reproduce:**
1. Add items totaling $55 to cart
2. Proceed to checkout
3. Select delivery option
4. Observe total amount

**Expected Behavior:**
Total should be $55 (delivery fee waived for orders over $50)

**Actual Behavior:**
Total shows $60 ($55 + $5 delivery fee)

**Environment:**
- Version: 2.3.1
- Platform: WhatsApp (all devices)

**Error Messages/Logs:**
No errors - calculation completes but with wrong value

**Additional Context:**
- Frequency: Always when order is $50.01 - $54.99
- First noticed: After v2.3.0 release
- Workaround: Add more items to get over $55

**Affected Entities/Data:**
- Order: items (OrderItem[]), subtotal (computed), deliveryFee (fixed/calculated), total (subtotal + deliveryFee)
- Business Rules: Subtotal = sum of (item.price * quantity), Delivery fee waived if subtotal > $50, Total = subtotal + deliveryFee
</inline-request>

<request>
Generate tasks to investigate and fix the delivery fee calculation bug.
Focus on finding why the $50 threshold isn't being applied correctly.
</request>

<constraints>
- Fix must not affect orders already placed
- Must add test covering this exact scenario
- Must verify threshold works at boundary values ($50.00, $50.01)
</constraints>

</task-generation-request>
```
