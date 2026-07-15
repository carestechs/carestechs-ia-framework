# Improvement Proposal: Extract Shared Date Logic

> **Product**: TaskFlow — a small web-based task tracker (projects, kanban boards, tasks) with an Express REST API backend and a React SPA frontend.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | IMP-001 |
| **Name** | Extract Shared Date Logic |
| **Type** | Refactoring |
| **Status** | Approved |
| **Priority** | Medium |
| **Estimated Effort** | M |
| **Proposed By** | Tech lead — action item from the v1.2.4 overdue-filter timezone incident post-mortem |
| **Date Created** | 2026-07-14 |

---

## 2. Target Area

**Component / Module:** Overdue/date-comparison logic in the tasks API route and the Project Board screen

**Affected Files / Directories:**
- `src/api/tasks.ts` — server-side copy: computes the user-local "today" for the board list's `filter=overdue` predicate parameters
- `src/ui/project-board.tsx` — client-side copy: computes "is this task overdue" for the TaskCard due-date chip styling
- `src/lib/dates.ts` (new) — target location for the single shared implementation

---

## 3. Current State

### How It Works Today

The rule "a task is overdue once its due date has fully passed in the user's timezone" is implemented twice: `src/api/tasks.ts` derives the user-local date from the `tz` query parameter to build the overdue predicate, and `src/ui/project-board.tsx` re-derives the same comparison from the browser's local date to color the due-date chip. Neither copy is exported or shared; each inlines its own date parsing, "today in timezone" derivation, and comparison.

### Problems

1. **Duplicated business rule**: the same overdue comparison exists in two files with no shared source of truth; every change must be made twice
2. **Drift risk is proven, not theoretical**: the two copies already disagreed once — the server-side copy compared against the UTC day while the chip used the local day, shipping the v1.2.4 overdue-filter timezone bug that the filter and the chip displayed contradictory answers for
3. **Untestable in isolation**: the date logic is inlined in a route handler and a React component, so its edge cases (day boundaries, DST transitions, positive/negative offsets) can only be exercised through full API or component tests

### Evidence

- v1.2.4 shipped a fix for the overdue-filter timezone incident — root cause was exactly this duplication drifting (server copy wrong, client copy right, same screen showing both answers)
- The two copies currently differ in DST handling: the API derives the local date via the database session, the UI via the browser `Date` — nothing guarantees they agree on transition days

---

## 4. Desired State

### Target Implementation

A single `src/lib/dates.ts` module owns the date-only helpers — `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)` — implementing the overdue rule from `docs/data-model/entities/task.md`. `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; neither keeps a private copy. The module is plain TypeScript with no framework or DOM dependencies so both the Express backend and the React frontend can consume it.

### Benefits

1. **Single source of truth**: the overdue rule changes in one file; filter and chip cannot disagree by construction
2. **Directly testable**: date edge cases (day boundaries, DST, offsets) get fast unit tests against the module instead of full API round-trips
3. **Safer future work**: upcoming date-based features (reminders, aging indicators) build on one audited helper instead of adding a third copy

---

## 5. Trigger and Motivation

**Trigger:** Post-mortem action item from the v1.2.4 overdue-filter timezone incident — the review concluded the defect class ("two copies of the same date rule drifting") survives the fix and will recur.

**Impact if deferred:** Every future change to due-date semantics must be hand-synchronized across the two copies; the next drift ships another contradictory-board incident.

**Dependencies on this improvement:** None yet — no open FEAT/BUG items are blocked by it.

---

## 6. Affected Entities and Components

| Entity / Component | What Changes | Spec Reference |
|--------------------|-------------|----------------|
| Task (`due_date` semantics) | Nothing — the overdue business rule is unchanged; its implementation moves | `docs/data-model/entities/task.md` |
| GET /api/v1/projects/{projectId}/tasks (`filter=overdue`, `tz`) | Behavior unchanged; the route's inline date derivation is replaced by the shared module | `docs/api-spec/endpoints/tasks.md` |
| Project Board (due-date chip + Overdue filter display) | Behavior unchanged; the screen's inline overdue check is replaced by the shared module | `docs/ui-specification/screens/project-board.md` |
| TaskCard (shared component) | Behavior unchanged — chip styling contract stays as documented | `docs/ui-specification/components.md` |

> **Retrieval key:** Names in this table map mechanically to spec shards — task generation reads each spec's `index.md` plus ONLY the shards named here. No spec shard changes: this improvement moves code, not contracts.

---

## 7. Risk Assessment

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Behavior drift between the two copies during migration — one call site on the new module while the other still runs its old inline copy | Medium | High | Characterization tests lock current behavior in before any restructuring; migrate one call site per task; old and new implementations coexist until both call sites are verified |
| Timezone/DST edge cases behave differently in the shared implementation than in either original copy | Medium | Medium | Edge-case test matrix (day boundaries, DST transitions, UTC-8/UTC/UTC+13) written against the current behavior first, then required to pass unchanged against the module |
| Shared module accidentally grows server-only or DOM dependencies, breaking one consumer's build | Low | Medium | Keep `src/lib/dates.ts` dependency-free plain TypeScript; both builds compile it in CI |

### Rollback Strategy

Old inline helpers stay in place until the cleanup phase, so each migration commit is independently revertible with `git revert` — reverting a single call-site migration restores its previous inline behavior without touching the other consumer. Cleanup happens only after both call sites are migrated and verified.

---

## 8. Constraints

- No behavior changes — the overdue rule, API responses, and chip styling must be byte-for-byte identical before and after
- No new external dependencies — no date libraries; plain `Date`/`Intl` only
- Must be deployable incrementally — each task leaves the system releasable

---

## 9. Success Criteria

- Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` (new)
- `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; no inline date-comparison helper remains in either file
- The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets
- Full test suite passes with no changes to existing test expectations

---

## 10. Current Test Coverage

| Area | Coverage | Notes |
|------|----------|-------|
| `src/api/tasks.ts` (overdue filter) | Partial | `tests/api/tasks.test.ts` covers the filter happy path and the v1.2.4 timezone regression scenario; no DST-transition cases |
| `src/ui/project-board.tsx` (chip overdue check) | None | No UI tests exist for the due-date chip styling — this is the biggest gap before refactoring |

---

## 11. Traceability

| Reference | Link |
|-----------|------|
| **Triggered By** | v1.2.4 overdue-filter timezone incident post-mortem |
| **Stakeholder Alignment** | This project keeps no stakeholder definition; CLAUDE.md conventions are the authority |
| **Architecture Reference** | CLAUDE.md Project Structure table (`src/api/`, `src/ui/`, shared code under `src/lib/` is new) |
| **Related Work Items** | None |
| **Blocked Features** | None |

---

## 12. Usage Notes for AI Task Generation

When generating refactoring tasks from this Improvement Proposal:

1. **Safety-first phasing**: Section 10 shows a real coverage gap (UI chip logic untested) — Phase 0 must establish the baseline and close the gaps before any restructuring.
2. **Problem-driven**: Each task should map to a Section 3 problem; do not generate tasks that don't.
3. **Incremental approach**: Per Section 7, old and new implementations coexist; migrate the API call site and the UI call site as separate tasks.
4. **Constraint respect**: No behavior changes, no new dependencies, incrementally deployable (Section 8).
5. **Success verification**: Verify all Section 9 criteria before cleanup is considered done.
6. **No feature creep**: This is an improvement, not a feature — no new date-based capabilities.
7. **Rollback awareness**: Reference the Section 7 rollback strategy in migration tasks.
8. **Traceability**: Include the Improvement Proposal ID (IMP-001) in the task generation output summary.
