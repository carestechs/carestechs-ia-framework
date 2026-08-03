# Bug Report Template

> **Purpose**: Provide a structured description of a bug before generating investigation and fix tasks. This document ensures bugs are reported with sufficient context for AI to generate targeted investigation steps rather than guessing at root causes.
> **When to use**: Before running the bug fix task generation prompt. One Bug Report per bug.

> **Context budget note:** This document is loaded into AI context. Keep it contract-style —
> tables, schemas, rules, one example each. Move narrative and history to `docs/rationale/`
> and link it; rationale files are never loaded by default.

---

## 1. Identity

> *Unique identifier and severity classification for tracking and triage.*

| Field | Value |
|-------|-------|
| **ID** | BUG-[XXX] |
| **Summary** | [One-line description of the bug] |
| **Severity** | [Critical · High · Medium · Low] |
| **Status** | [Reported · Investigating · Fix In Progress · Resolved · Won't Fix] |
| **Reported By** | [Source — user complaint, QA, monitoring alert, developer, etc.] |
| **Date Reported** | [YYYY-MM-DD] |
| **Date First Observed** | [YYYY-MM-DD or "Unknown"] |

<!-- TODO: Fill in all identity fields. Use a sequential ID (BUG-001, BUG-002, etc.). Severity guide: Critical = system down/data loss, High = core feature broken, Medium = feature degraded, Low = cosmetic/minor. -->

### Severity Justification

[1-2 sentences explaining why this severity level — who is affected, how badly, how often]

---

## 2. Steps to Reproduce

> *Exact sequence to trigger the bug. Numbered steps that anyone can follow.*

**Preconditions:** [Required state before starting — logged in as X, data Y exists, etc.]

1. [Step 1 — specific action]
2. [Step 2 — specific action]
3. [Step 3 — specific action]
4. **Observe:** [What goes wrong]

**Reproducibility:** [Always · Sometimes (~X%) · Rarely · Only once]

<!-- TODO: Be as specific as possible. "Click the button" is worse than "Click the 'Submit Order' button on the checkout screen". Include exact input values when relevant. -->

---

## 3. Expected vs Actual Behavior

> *Clear contrast between what should happen and what does happen.*

### Expected Behavior

[What the system should do according to specs, acceptance criteria, or reasonable user expectation]

### Actual Behavior

[What the system actually does — be specific about the observable difference]

<!-- TODO: Reference the relevant spec if possible — e.g., "Per AC-3 in FEAT-012, the total should exclude delivery fee for orders over $50". -->

---

## 4. Environment

> *Where the bug was observed. Helps narrow down platform-specific vs universal issues.*

| Field | Value |
|-------|-------|
| **App Version** | [Version number or commit hash] |
| **Platform** | [Browser + version, OS, device, API client] |
| **User Context** | [Relevant user state — role, account type, specific data] |
| **Deployment** | [Production · Staging · Development · Local] |

---

## 5. Error Evidence

> *Logs, stack traces, screenshots, or network traces that provide diagnostic clues.*

### Error Messages / Logs

```
[Paste error messages, stack traces, or relevant log output]
```

### Network / API Evidence

```
[Paste relevant request/response data if applicable — sanitize sensitive data]
```

### Screenshots / Recordings

[Link to or describe visual evidence of the bug]

<!-- TODO: Include as much raw evidence as possible. Stack traces are especially valuable for investigation task generation. Sanitize PII and credentials. -->

---

## 6. Additional Context

> *Patterns, workarounds, and related observations that help narrow the investigation.*

| Field | Value |
|-------|-------|
| **Frequency** | [Always · Sometimes · Rarely · Once] |
| **First occurrence** | [Date, version, or event that correlates — e.g., "After v2.3.0 release"] |
| **Workaround exists** | [Yes/No — describe if yes] |
| **Related bugs** | [BUG-XXX IDs or external issue links] |
| **Regression** | [Yes (worked before) · No (never worked) · Unknown] |

### Observations

- [Any pattern you've noticed — e.g., "only happens with orders containing 3+ items"]
- [Any hypothesis about what might be wrong — clearly labeled as hypothesis]

---

## 7. Affected Entities and Components

> *Which parts of the system are involved? Reference `docs/data-model/`, `docs/api-spec/`, `docs/ui-specification/` (index + shards) and `docs/ARCHITECTURE.md` for full definitions.*

| Entity / Component | How Affected | Reference |
|--------------------|-------------|-----------|
| [Entity or component name] | [What aspect is broken — data integrity, calculation, display, etc.] | [Shard path or section — e.g., `docs/data-model/entities/task.md`, `docs/api-spec/endpoints/tasks.md`, `docs/ARCHITECTURE.md` §3.2] |

<!-- Retrieval key: Names in this table map mechanically to spec shards — entity `Task` → `docs/data-model/entities/task.md`; resource `/api/tasks` → `docs/api-spec/endpoints/tasks.md`; screen "Project Board" → `docs/ui-specification/screens/project-board.md`. Task generation reads each spec's `index.md` plus ONLY the shards named here, so list every entity, endpoint, and screen visibly involved in the symptoms. (HTML comment so the example paths never trip validate-specs reference checks in a filled report.) -->

<!-- TODO: Even if you're not sure of the root cause, list the entities and components that are visibly involved in the bug's symptoms. -->

---

## 8. Impact Assessment

> *Who and what is affected by this bug? Helps prioritize and scope the fix.*

| Dimension | Assessment |
|-----------|------------|
| **Users affected** | [All users · Subset (describe) · Single user] |
| **Feature affected** | [Which feature(s) — reference FEAT-XXX if applicable] |
| **Data impact** | [None · Incorrect data created · Data loss risk · Data corruption] |
| **Business impact** | [Revenue loss · User trust · Compliance risk · Operational overhead · None significant] |

---

## 9. Traceability

> *Links this bug back to the feature, spec, or acceptance criterion it violates.*

| Reference | Link |
|-----------|------|
| **Related Feature** | [FEAT-XXX if this bug is in a known feature] |
| **Violated AC** | [Which acceptance criterion the bug contradicts — e.g., "FEAT-012 AC-3"] |
| **Spec Reference** | [Which spec shard or index section defines the correct behavior — e.g., `docs/data-model/entities/<entity>.md`, `docs/api-spec/endpoints/<resource>.md`, `docs/ui-specification/screens/<screen>.md`] |
| **Related Work Items** | [Other FEAT/BUG/IMP IDs that relate to this bug] |

---

## 10. Root Cause & Resolution

> *Fill this section when the Status moves to Resolved. It closes the loop: future investigations of similar symptoms start here, and it feeds regression-test generation.*

| Field | Value |
|-------|-------|
| **Root Cause** | [The actual underlying defect — code path, wrong assumption, missing validation. Be specific: "X did Y because Z", not "fixed the bug"] |
| **Fix Summary** | [What was changed to fix it — files/components touched and the nature of the change] |
| **Fixed In** | [Version, commit hash, or PR reference where the fix shipped] |

<!-- TODO: Leave this section with placeholder values until the bug is actually resolved. Do not guess the root cause here while Status is Reported/Investigating — hypotheses belong in Section 6 (Observations). -->

---

## 11. Usage Notes for AI Task Generation

When generating investigation and fix tasks from this Bug Report:

1. **Investigation first**: Always generate investigation tasks before fix tasks. Do not assume the root cause based on symptoms alone.
2. **Evidence-driven**: Use Section 5 (Error Evidence) to guide investigation steps. Stack traces point to specific code paths; error messages point to specific error handling.
3. **Scope awareness**: Use Section 7 (Affected Entities) to determine which spec shards to read for understanding correct behavior — each spec's `index.md` plus only the shards named there.
4. **Reproduction**: The first investigation task should verify reproducibility using Section 2 (Steps to Reproduce).
5. **Regression context**: If Section 6 indicates regression, investigation should include checking recent changes (git log) to the affected area.
6. **Impact-proportionate response**: Use Section 8 (Impact Assessment) to calibrate fix scope. A data-loss bug requires more thorough testing than a cosmetic issue.
7. **Traceability**: Include the Bug Report ID (BUG-XXX) in the task generation output summary for cross-referencing.
8. **Fix verification**: Generated fix tasks must include a test case that reproduces the exact bug scenario from Section 2.
9. **Resolution capture**: The final generated task should include filling Section 10 (Root Cause & Resolution) and setting Status to Resolved once the fix is verified.
