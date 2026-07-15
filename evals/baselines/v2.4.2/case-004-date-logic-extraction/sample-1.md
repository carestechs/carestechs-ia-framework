# Refactoring Tasks — IMP-001: Extract Shared Date Logic

> **Source work item:** `docs/work-items/IMP-001-extract-date-logic.md` (Improvement Proposal IMP-001, Approved)
> **Generated:** 2026-07-15
> **Binding constraints (proposal Section 8):** no behavior changes — the overdue rule, API responses, and chip styling stay byte-for-byte identical; no new external dependencies — plain `Date`/`Intl` only; incrementally deployable — every task leaves the system releasable.

---

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue/date logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current test coverage for the two inline copies of the overdue rule: the `filter=overdue` predicate in `src/api/tasks.ts` and the due-date chip check in `src/ui/project-board.tsx`. Record the proposal's Section 10 baseline (API filter: happy path and v1.2.4 regression covered, DST transitions missing; UI chip: no tests at all) and confirm the existing suite is green.

**Rationale:**
Tests must be verified before refactoring begins; the documented baseline defines exactly which gaps Phase 0 must close before any restructuring task starts.

**Acceptance Criteria:**
- [ ] Current coverage for the `src/api/tasks.ts` overdue filter and the `src/ui/project-board.tsx` chip check is measured and documented
- [ ] Coverage gaps are listed (DST-transition cases for the API filter; all chip-styling scenarios for the UI)
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - baseline notes: current coverage, gap list, suite status

### T-002: Add timezone edge-case characterization tests for the API overdue filter

**Type:** Testing
**Workflow:** standard

**Description:**
Extend `tests/api/tasks.test.ts` with characterization tests that lock in the current behavior of the `filter=overdue` + `tz` predicate across the proposal's edge-case matrix: day boundaries (just before/after 00:00 local time of the day after the due date), DST transition days, and negative/zero/positive UTC offsets (UTC-8, UTC, UTC+13). Route code stays untouched.

**Rationale:**
Section 10 flags DST-transition cases as untested on the server copy; these tests pin current behavior so the Phase 2 migration can be verified as behavior-preserving (Section 7 drift mitigation).

**Acceptance Criteria:**
- [ ] Day-boundary cases around 00:00 local time in the requesting `tz` have passing tests
- [ ] DST-transition-day cases have passing tests
- [ ] UTC-8, UTC, and UTC+13 offsets each have passing tests
- [ ] Tests exercise current (pre-refactoring) behavior with `src/api/tasks.ts` unchanged

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add overdue-filter edge-case characterization tests

**Technical Notes:**
- Test through the route with Supertest per CLAUDE.md convention 6 — the inline helper is not exported, so behavior can only be locked in black-box
- Fix the reference instant per case so day-boundary expectations are deterministic

### T-003: Add characterization tests for the Project Board due-date chip overdue check

**Type:** Testing
**Workflow:** standard

**Description:**
Create UI tests for the client-side overdue check in `src/ui/project-board.tsx` that drives the TaskCard due-date chip's `error` styling, covering the same edge-case matrix (day boundaries, DST transition days, UTC-8/UTC/UTC+13) against the browser-local date derivation. Board and TaskCard code stay untouched.

**Rationale:**
Section 10 identifies the chip logic as having no tests — the biggest gap before refactoring; its current behavior must be locked in before the migration touches this call site.

**Acceptance Criteria:**
- [ ] Chip renders `error` styling exactly when the due date has fully passed in the browser's local timezone, default styling otherwise (contract in `docs/ui-specification/components.md`)
- [ ] Day-boundary and DST-transition-day cases have passing tests
- [ ] Negative, zero, and positive UTC-offset cases have passing tests
- [ ] Tests exercise current (pre-refactoring) behavior with `src/ui/project-board.tsx` unchanged

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/project-board.test.tsx (new) - chip overdue-styling characterization tests

**Technical Notes:**
- Pin the clock and zone (e.g. Vitest fake timers + `TZ`) so date cases are deterministic in CI

## Phase 1: Safe Parallel Implementation

### T-004: Create shared date module src/lib/dates.ts alongside the inline copies

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`, implementing the overdue rule from `docs/data-model/entities/task.md` (overdue from 00:00 local time of the day after the due date) as dependency-free plain TypeScript. Neither call site changes in this task; both inline copies keep running unchanged.

**Rationale:**
Resolves the duplicated-business-rule problem (Section 3) by building the single source of truth alongside the old copies — the extract-and-delegate pattern's safe first step.

**Acceptance Criteria:**
- [ ] `src/lib/dates.ts` exports `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)` implementing the documented overdue rule
- [ ] Module is plain TypeScript with no framework, DOM, or server-only dependencies and no new external packages
- [ ] `src/api/tasks.ts` and `src/ui/project-board.tsx` are untouched and the full suite still passes

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared toUserLocalDate/isOverdue implementation

**Technical Notes:**
- Approach: derive the user-local calendar date via `Intl.DateTimeFormat` with the `timeZone` option — no date libraries (Section 8)
- Coexistence strategy: the module ships unused; both inline copies remain the live implementations until Phase 2 migrates them one at a time
- `due_date` is stored as 00:00:00 UTC with date-only semantics (entity shard) — compare calendar dates, not instants

### T-005: Add unit tests for the shared date module

**Type:** Testing
**Workflow:** standard

**Description:**
Create `tests/lib/dates.test.ts` unit-testing `toUserLocalDate` and `isOverdue` directly against the same edge-case matrix locked in Phase 0: day boundaries, DST transitions, and negative/zero/positive UTC offsets (UTC-8, UTC, UTC+13). Expected values must agree with the characterization tests' locked-in behavior.

**Rationale:**
Resolves the untestable-in-isolation problem (Section 3) and satisfies the Section 9 criterion that the shared module has direct unit coverage of the date edge cases.

**Acceptance Criteria:**
- [ ] Day-boundary cases (just before/after 00:00 local time of the day after the due date) pass
- [ ] DST-transition-day cases pass
- [ ] Negative (UTC-8), zero (UTC), and positive (UTC+13) offset cases pass
- [ ] Expected values agree with the Phase 0 characterization tests (T-002, T-003)

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/lib/dates.test.ts (new) - unit tests for toUserLocalDate/isOverdue

## Phase 2: Migration

### T-006: Migrate the API overdue filter to the shared module

**Type:** Backend
**Workflow:** standard

**Description:**
Switch the `filter=overdue` predicate in `src/api/tasks.ts` to derive the user-local "today" via `src/lib/dates.ts` instead of its inline copy. The old inline helper stays in the file, unused, until Phase 3 cleanup.

**Rationale:**
First of two independent consumer migrations to the single source of truth; migrating one call site per task keeps each commit independently revertible per the Section 7 rollback strategy.

**Acceptance Criteria:**
- [ ] The route's overdue predicate uses the shared module for the user-local date derivation
- [ ] All API tests pass unchanged, including the v1.2.4 regression scenario and the T-002 edge-case matrix
- [ ] API responses for `filter=overdue` + `tz` are identical to pre-migration behavior

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - replace inline date derivation with shared-module import

**Technical Notes:**
- Migration steps: import the module, swap the predicate's date derivation, run the full API suite, confirm no test expectation changed
- Rollback plan: `git revert` of this commit alone restores the inline behavior (helper still present) without touching the UI consumer

### T-007: Migrate the Project Board chip check to the shared module

**Type:** Frontend
**Workflow:** standard

**Description:**
Switch the due-date chip overdue check in `src/ui/project-board.tsx` to call `isOverdue` from `src/lib/dates.ts` with the browser zone instead of its inline copy. The old inline check stays in the file, unused, until Phase 3 cleanup.

**Rationale:**
Second consumer migration to the single source of truth; after this task the filter and the chip compute overdue from the same implementation, closing the drift class behind the v1.2.4 incident.

**Acceptance Criteria:**
- [ ] The board's chip overdue check uses the shared module with the browser's IANA zone
- [ ] All UI tests pass unchanged, including the T-003 characterization matrix
- [ ] TaskCard chip styling contract in `docs/ui-specification/components.md` is unchanged
- [ ] The frontend (Vite) build compiles the shared module — guards the Section 7 dependency-creep risk

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - replace inline chip overdue check with shared-module import

**Technical Notes:**
- Migration steps: import the module, swap the chip check, run the UI suite, sanity-check chip states on the board
- Rollback plan: `git revert` of this commit alone restores the inline chip check; the API consumer is unaffected

## Phase 3: Cleanup

### T-008: Remove the old inline date helpers from both call sites

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unused inline date parsing, "today in timezone" derivation, and comparison code from `src/api/tasks.ts` and `src/ui/project-board.tsx`. Leave no dead or commented-out code.

**Rationale:**
Both migrations (T-006, T-007) are verified with unchanged test expectations, so the old copies are provably unused; removing them completes the Section 9 single-source-of-truth criterion.

**Acceptance Criteria:**
- [ ] No inline date-comparison helper remains in `src/api/tasks.ts` or `src/ui/project-board.tsx`
- [ ] No references to the removed helpers and no dead code remain
- [ ] Build succeeds and the full test suite passes unchanged

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - delete unused inline date helper
- src/ui/project-board.tsx - delete unused inline date helper

## Phase 4: Verification

### T-009: Update CLAUDE.md project structure for the new shared-code location

**Type:** Documentation
**Workflow:** standard

**Description:**
Add a `src/lib/` row to CLAUDE.md's Project Structure table documenting the new shared, framework-free code location (the proposal's Traceability section notes shared code under `src/lib/` is new). No spec shards change — this improvement moves code, not contracts.

**Rationale:**
Future date-based work (reminders, aging indicators — Section 4 benefits) must be routed to the shared module instead of adding a third copy, so the structure table has to name the location.

**Acceptance Criteria:**
- [ ] CLAUDE.md Project Structure table documents `src/lib/` (shared framework-free modules, e.g. `src/lib/dates.ts`)
- [ ] No spec shard under `docs/` is modified

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- CLAUDE.md - add src/lib/ row to the Project Structure table

### T-010: Final verification of behavior parity and success criteria

**Type:** Testing
**Workflow:** standard

**Description:**
Run the full verification pass: the original suite, the Phase 0 characterization tests, and the module unit tests, with type checks and lint; confirm both backend and frontend builds compile `src/lib/dates.ts`; verify every Section 9 success criterion and record the results against the Phase 0 baseline.

**Rationale:**
Confirms end-to-end that the refactoring preserved behavior — no test expectation changed anywhere — before IMP-001 is considered done.

**Acceptance Criteria:**
- [ ] All original tests pass with no changes to existing test expectations
- [ ] All new tests (T-002, T-003, T-005) pass
- [ ] No type or lint errors; backend and frontend builds both compile the shared module
- [ ] Exactly one overdue/date-only implementation exists (`src/lib/dates.ts`) and both call sites import it
- [ ] Verification results recorded against the T-001 baseline notes

**Dependencies:** T-008, T-009
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - append final verification results

## Summary

**Work item:** IMP-001 — Extract Shared Date Logic (refactoring: no behavior changes, no new dependencies, incrementally deployable).

**Total tasks by phase:**

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 0 — Preparation (Safety Net) | T-001, T-002, T-003 | 3 |
| Phase 1 — Safe Parallel Implementation | T-004, T-005 | 2 |
| Phase 2 — Migration | T-006, T-007 | 2 |
| Phase 3 — Cleanup | T-008 | 1 |
| Phase 4 — Verification | T-009, T-010 | 2 |
| **Total** | | **10** |

**Critical path and estimated sequence:** T-001 → (T-002 and T-003, parallel) → T-004 → T-005 → (T-006 and T-007, parallel, separate commits) → T-008 → T-009 → T-010. Every phase leaves the system releasable; the shared module ships unused after Phase 1, carries one consumer after either migration, and becomes the sole implementation only at T-008.

**Risk assessment:** The highest risk is behavior drift while one call site runs the module and the other still runs its inline copy (Section 7: Medium/High) — mitigated by the Phase 0 characterization matrix locked in before any restructuring and by one-call-site-per-task migration. DST/offset divergence (Medium/Medium) is pinned by reusing the same edge-case matrix (day boundaries, DST transitions, UTC-8/UTC/UTC+13) across T-002, T-003, and T-005. Dependency creep into the shared module (Low/Medium) is guarded by T-004's dependency-free criterion and by both builds compiling the module (T-007, T-010).

**Recommended review points:**

1. After Phase 0 (T-003): baseline documented, characterization matrix green — confirm the safety net before any restructuring.
2. After T-005: module unit-test results agree with the characterization tests — the parity gate before any consumer migrates.
3. After each migration (T-006, T-007): full suite green with zero expectation changes before proceeding.
4. Before T-008: confirm both call sites import the module and the old helpers are unreferenced — cleanup only after both migrations are verified.

**Rollback strategy summary:** Old inline helpers stay in place until T-008, so each migration commit is independently revertible with `git revert` — reverting one call-site migration restores its previous inline behavior without touching the other consumer. Cleanup happens only after both call sites are migrated and verified (proposal Section 7).

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| SC-1: Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` (new) | T-004, T-008 |
| SC-2: `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; no inline date-comparison helper remains in either file | T-006, T-007, T-008 |
| SC-3: The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets | T-005 |
| SC-4: Full test suite passes with no changes to existing test expectations | T-010 |
