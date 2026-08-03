<!-- Copy this file to docs/work-items/BUG-XXX-short-title.md (next free ID) before filling. -->

# Bug Report: BUG-XXX — [One-line Summary]

> **Purpose**: Structured bug description before generating investigation and fix tasks.
> **Template reference**: `.ai-framework/templates/bug-report.md`

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | BUG-XXX |
| **Summary** | <!-- TODO: One-line description of the bug --> |
| **Severity** | <!-- TODO: Critical · High · Medium · Low --> |
| **Status** | Reported |
| **Reported By** | <!-- TODO: Source — user, QA, monitoring, developer --> |
| **Date Reported** | <!-- TODO: YYYY-MM-DD --> |
| **Date First Observed** | <!-- TODO: YYYY-MM-DD or "Unknown" --> |

### Severity Justification

<!-- TODO: 1-2 sentences explaining severity — who is affected, how badly, how often -->

---

## 2. Steps to Reproduce

**Preconditions:** <!-- TODO: Required state before starting -->

1. <!-- TODO: Step 1 -->
2. <!-- TODO: Step 2 -->
3. <!-- TODO: Step 3 -->
4. **Observe:** <!-- TODO: What goes wrong -->

**Reproducibility:** <!-- TODO: Always · Sometimes (~X%) · Rarely · Only once -->

---

## 3. Expected vs Actual Behavior

### Expected Behavior

<!-- TODO: What the system should do — reference a spec or AC if possible -->

### Actual Behavior

<!-- TODO: What the system actually does -->

---

## 4. Environment

| Field | Value |
|-------|-------|
| **App Version** | <!-- TODO: Version or commit hash --> |
| **Platform** | <!-- TODO: Browser + version, OS, device --> |
| **User Context** | <!-- TODO: Role, account type, specific data --> |
| **Deployment** | <!-- TODO: Production · Staging · Development · Local --> |

---

## 5. Error Evidence

### Error Messages / Logs

```
<!-- TODO: Paste error messages, stack traces, or relevant log output. Sanitize PII. -->
```

### Network / API Evidence

```
<!-- TODO: Paste relevant request/response data if applicable -->
```

### Screenshots / Recordings

<!-- TODO: Link to or describe visual evidence -->

---

## 6. Additional Context

| Field | Value |
|-------|-------|
| **Frequency** | <!-- TODO: Always · Sometimes · Rarely · Once --> |
| **First occurrence** | <!-- TODO: Date, version, or correlating event --> |
| **Workaround exists** | <!-- TODO: Yes (describe) / No --> |
| **Related bugs** | <!-- TODO: BUG-XXX IDs or external issue links --> |
| **Regression** | <!-- TODO: Yes (worked before) · No (never worked) · Unknown --> |

### Observations

<!-- TODO: Patterns, hypotheses, anything else relevant -->
-

---

## 7. Affected Entities and Components

<!-- TODO: Which parts of the system are involved? Reference docs/data-model/, docs/api-spec/, docs/ui-specification/ (index + shards) and docs/ARCHITECTURE.md -->

| Entity / Component | How Affected | Reference |
|--------------------|-------------|-----------|
| <!-- TODO --> | | |

<!-- Retrieval key: Names in this table map mechanically to spec shards — entity `Task` → `docs/data-model/entities/task.md`; resource `/api/tasks` → `docs/api-spec/endpoints/tasks.md`; screen "Project Board" → `docs/ui-specification/screens/project-board.md`. Task generation reads each spec's `index.md` plus ONLY the shards named here, so list every entity, endpoint, and screen visibly involved in the symptoms. (HTML comment so the example paths never trip validate-specs reference checks in a filled report.) -->

---

## 8. Impact Assessment

| Dimension | Assessment |
|-----------|------------|
| **Users affected** | <!-- TODO: All users · Subset (describe) · Single user --> |
| **Feature affected** | <!-- TODO: Which feature(s) — reference FEAT-XXX --> |
| **Data impact** | <!-- TODO: None · Incorrect data · Data loss risk · Corruption --> |
| **Business impact** | <!-- TODO: Revenue · User trust · Compliance · Operational · None --> |

---

## 9. Traceability

| Reference | Link |
|-----------|------|
| **Related Feature** | <!-- TODO: FEAT-XXX --> |
| **Violated AC** | <!-- TODO: Which acceptance criterion the bug contradicts --> |
| **Spec Reference** | <!-- TODO: Which spec shard or index section defines the correct behavior — e.g., docs/data-model/entities/<entity>.md, docs/api-spec/endpoints/<resource>.md, docs/ui-specification/screens/<screen>.md --> |
| **Related Work Items** | <!-- TODO: FEAT/BUG/IMP IDs --> |

---

## 10. Root Cause & Resolution

<!-- TODO: Fill when Status moves to Resolved — do not guess the root cause while investigating (hypotheses belong in Section 6 Observations) -->

| Field | Value |
|-------|-------|
| **Root Cause** | <!-- TODO: The actual underlying defect — "X did Y because Z", not "fixed the bug" --> |
| **Fix Summary** | <!-- TODO: What was changed — files/components touched and the nature of the change --> |
| **Fixed In** | <!-- TODO: Version, commit hash, or PR reference --> |
