# IMP-001 — Extract Shared Date Logic: Refactoring Tasks

> **Source work item:** `docs/work-items/IMP-001-extract-date-logic.md` (Improvement Proposal, Approved)
> **Workflow classification:** standard — refactoring maintains existing functionality; current behavior is well documented in the proposal and spec shards.
> **Binding constraints (proposal Section 8), applying to every task below:** no behavior changes (overdue rule, API responses, and chip styling byte-for-byte identical); no new external dependencies (plain `Date`/`Intl` only); each task leaves the system releasable.

The rule being preserved is defined in `docs/data-model/entities/task.md`: a task is **overdue** only when its due date has fully passed in the viewing user's timezone — from 00:00 local time of the day *after* the due date; `due_date` is stored as 00:00:00 UTC of the picked calendar date (date-only semantics).

---

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue/date-comparison logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current test coverage for the two inline copies of the overdue rule: the `filter=overdue` predicate in `src/api/tasks.ts` and the due-date chip check in `src/ui/project-board.tsx`. Record the proposal's Section 10 baseline (API filter: happy path and v1.2.4 regression covered, no DST-transition cases; UI chip: no tests at all) and list every untested scenario. Confirm the full existing suite passes before any refactoring begins.

**Rationale:**
Refactoring may not start without a documented safety net (proposal Section 12.1); the baseline defines exactly which gaps Phase 0 must close before restructuring.

**Acceptance Criteria:**
- [ ] Current coverage for `src/api/tasks.ts` (overdue filter) and `src/ui/project-board.tsx` (chip check) measured and documented
- [ ] Coverage gaps listed: DST-transition and offset edge cases for the API filter; all chip-styling scenarios for the UI
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - baseline coverage notes and gap list

### T-002: Add DST and offset edge-case tests for the API overdue filter

**Type:** Testing
**Workflow:** standard

**Description:**
Extend `tests/api/tasks.test.ts` with characterization tests locking in the current behavior of `GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=…`: day boundaries (due date not yet passed vs. fully passed in `tz`), DST transition days, and negative/zero/positive offsets (UTC-8, UTC, UTC+13). Tests must assert today's actual responses — response envelope and `meta` totals included — not the desired post-refactoring behavior.

**Rationale:**
The proposal's Section 7 mitigation requires the edge-case matrix to be written against current behavior first, so the shared module can later be required to pass it unchanged (Section 3, problem 2: drift already shipped the v1.2.4 incident).

**Acceptance Criteria:**
- [ ] Day-boundary cases pass against current `src/api/tasks.ts` behavior (due today vs. fully passed in `tz`)
- [ ] DST-transition-day cases pass against current behavior
- [ ] UTC-8 / UTC / UTC+13 offset cases pass against current behavior
- [ ] Tasks with status `done` are excluded from `filter=overdue` results (per `docs/api-spec/endpoints/tasks.md`)

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add DST-transition and offset characterization tests for filter=overdue

### T-003: Add characterization tests for the Project Board due-date chip

**Type:** Testing
**Workflow:** standard

**Description:**
Create UI tests for `src/ui/project-board.tsx` covering the TaskCard due-date chip: the chip switches to `error` color once the due date has fully passed in the browser's local timezone and keeps default styling otherwise. Cover day boundaries and DST transition days; this closes the proposal's biggest gap (Section 10: no UI tests exist for the chip).

**Rationale:**
The client-side copy of the rule has zero coverage (Section 10); restructuring it without locking current behavior in first would make a recurrence of the v1.2.4 defect class (Section 3, problem 2) undetectable.

**Acceptance Criteria:**
- [ ] Chip renders `error` color for a task whose due date has fully passed in the browser zone
- [ ] Chip renders default styling for tasks due today or later
- [ ] Day-boundary and DST-transition-day cases pass against the current inline check
- [ ] Tests exercise current (pre-refactoring) behavior; the TaskCard chip contract in `docs/ui-specification/components.md` is asserted unchanged

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/project-board.test.tsx (new) - characterization tests for the due-date chip overdue styling

## Phase 1: Safe Parallel Implementation

### T-004: Create shared date module src/lib/dates.ts

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`, implementing the overdue rule from `docs/data-model/entities/task.md` (overdue from 00:00 local time of the day after the due date). The module is plain TypeScript using only `Date`/`Intl` — no framework, DOM, or server dependencies — and is added alongside the existing inline copies, which stay untouched.

**Rationale:**
A single dependency-free implementation is the target state (Section 4), resolving Section 3, problem 1 (duplicated business rule) while remaining consumable by both the Express backend and the React frontend.

**Acceptance Criteria:**
- [ ] `src/lib/dates.ts` exports `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`
- [ ] Module has no framework, DOM, or server-only imports and adds no external dependencies (Section 8)
- [ ] Backend and frontend builds both compile the module
- [ ] Inline copies in `src/api/tasks.ts` and `src/ui/project-board.tsx` are unchanged and all existing tests still pass

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared toUserLocalDate/isOverdue helpers

**Technical Notes:**
- Approach: extract-and-delegate / parallel change — build the new module alongside the old inline copies without touching them
- Coexistence strategy: the inline helpers keep serving both call sites until Phase 2 migrates them one at a time
- Honor `due_date` date-only semantics: stored as 00:00:00 UTC of the picked calendar date (entity shard)
- Derive "today in tz" via `Intl.DateTimeFormat` with `timeZone` — avoids both historical drift sources (DB session date vs. browser `Date`)

### T-005: Add unit tests for the shared date module

**Type:** Testing
**Workflow:** standard

**Description:**
Write unit tests for `src/lib/dates.ts` covering the full edge-case matrix: day boundaries, DST transitions, and negative/zero/positive UTC offsets (UTC-8, UTC, UTC+13). Expected values must match the behavior characterized in T-002 and T-003, so later migration cannot change observable behavior.

**Rationale:**
Section 3, problem 3 — the date logic was untestable in isolation; fast direct unit tests are a stated benefit (Section 4) and an explicit success criterion (Section 9).

**Acceptance Criteria:**
- [ ] Day-boundary cases (due yesterday / today / tomorrow relative to `tz`) covered and passing
- [ ] DST-transition-day cases covered and passing
- [ ] UTC-8 / UTC / UTC+13 offset cases covered and passing
- [ ] Expected values agree with the characterization tests from T-002 and T-003

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/lib/dates.test.ts (new) - edge-case matrix unit tests for the shared module

## Phase 2: Migration

### T-006: Migrate the API overdue filter to the shared module

**Type:** Backend
**Workflow:** standard

**Description:**
Switch the `filter=overdue` predicate in `src/api/tasks.ts` to derive the user-local "today" via `toUserLocalDate`/`isOverdue` imported from `src/lib/dates.ts`, replacing the route's inline derivation at the call site. The now-unused inline helper stays in the file until Phase 3 cleanup, per the proposal's rollback strategy.

**Rationale:**
First of the two call-site migrations toward the single source of truth (Section 4); migrating one call site per task bounds the drift window flagged as the top risk in Section 7.

**Acceptance Criteria:**
- [ ] `src/api/tasks.ts` uses `src/lib/dates.ts` for the overdue predicate; no inline date derivation is executed
- [ ] All API tests pass unchanged, including the T-002 characterization matrix and the v1.2.4 regression test
- [ ] `filter=overdue` responses are byte-for-byte identical (envelope, `meta` totals, ordering)
- [ ] System is releasable with the UI call site still on its inline copy

**Dependencies:** T-004, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - switch the overdue predicate call site to src/lib/dates.ts imports

**Technical Notes:**
- Migration steps: import the module → replace the call-site computation → run the full API suite → confirm the characterization matrix passes unchanged
- Rollback plan: `git revert` of this single commit restores the inline behavior without touching the other consumer (proposal Section 7)

### T-007: Migrate the Project Board chip check to the shared module

**Type:** Frontend
**Workflow:** standard

**Description:**
Switch the due-date chip overdue check in `src/ui/project-board.tsx` to `isOverdue` imported from `src/lib/dates.ts`, passing the browser zone, replacing the screen's inline comparison at the call site. The now-unused inline helper stays until Phase 3 cleanup, per the proposal's rollback strategy.

**Rationale:**
Second call-site migration (Section 4); once merged, the Overdue filter and the chip share one implementation and cannot disagree by construction.

**Acceptance Criteria:**
- [ ] `src/ui/project-board.tsx` uses `src/lib/dates.ts` for the chip check; no inline comparison is executed
- [ ] T-003 characterization tests pass unchanged; the chip styling contract in `docs/ui-specification/components.md` is unaffected
- [ ] Frontend build compiles with the shared module (no server-only dependency leaked)
- [ ] System is releasable independently of T-006

**Dependencies:** T-004, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - switch the chip overdue check call site to the src/lib/dates.ts import

**Technical Notes:**
- Migration steps: import the module → replace the call-site computation → run the UI suite → verify the chip on a board containing overdue and non-overdue tasks
- Rollback plan: `git revert` of this single commit restores the inline chip behavior without touching the other consumer (proposal Section 7)

## Phase 3: Cleanup

### T-008: Remove old inline date helpers from both call sites

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unused inline date parsing, "today in timezone" derivation, and comparison helpers from `src/api/tasks.ts` and `src/ui/project-board.tsx`, leaving the `src/lib/dates.ts` imports as the only implementation. Leave no dead or commented-out code behind.

**Rationale:**
Both call sites are migrated and verified (T-006, T-007), so per the proposal's rollback strategy the coexistence window can close; this completes Section 9's "no inline date-comparison helper remains in either file".

**Acceptance Criteria:**
- [ ] No inline date-comparison helper remains in `src/api/tasks.ts` or `src/ui/project-board.tsx`
- [ ] No references to the old implementations remain; no dead code left behind
- [ ] Backend and frontend builds succeed
- [ ] Full test suite passes

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - delete the unused inline date helper
- src/ui/project-board.tsx - delete the unused inline date helper

## Phase 4: Verification

### T-009: Update CLAUDE.md project structure for src/lib/

**Type:** Documentation
**Workflow:** standard

**Description:**
Add a `src/lib/` row to CLAUDE.md's Project Structure table describing it as dependency-free shared TypeScript consumed by both backend and frontend (proposal Section 11: shared code under `src/lib/` is new to the architecture). No spec shards change — this improvement moves code, not contracts (Section 6).

**Rationale:**
The refactoring introduces a new top-level source directory; documenting it keeps CLAUDE.md's structure table authoritative so future work routes shared logic correctly.

**Acceptance Criteria:**
- [ ] CLAUDE.md Project Structure table documents `src/lib/` and its dependency-free constraint
- [ ] No spec shards under `docs/` are modified (Section 6: contracts unchanged)

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- CLAUDE.md - add a src/lib/ row to the Project Structure table

### T-010: Verify IMP-001 success criteria end-to-end

**Type:** Testing
**Workflow:** standard

**Description:**
Run the full verification pass across the refactored area: the complete original suite, the T-002/T-003 characterization matrices, the T-005 module unit tests, type/lint checks, and both builds. Verify every Section 9 success criterion and record the results against the T-001 baseline.

**Rationale:**
Final confirmation that the refactoring preserved behavior end-to-end (proposal Section 12.5) before IMP-001 is closed.

**Acceptance Criteria:**
- [ ] All original tests pass with no changes to existing test expectations (Section 9)
- [ ] Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts`, imported by both `src/api/tasks.ts` and `src/ui/project-board.tsx` (Section 9)
- [ ] Module unit tests cover day boundaries, DST transitions, and negative/zero/positive UTC offsets (Section 9)
- [ ] No type or lint errors; backend and frontend builds both compile the shared module
- [ ] Verification results recorded against the T-001 baseline

**Dependencies:** T-008, T-009
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - record final verification results against the baseline

## Summary

Generated from Improvement Proposal **IMP-001** (Extract Shared Date Logic), triggered by the v1.2.4 overdue-filter timezone incident post-mortem.

### Total Tasks by Phase

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 0: Preparation (Safety Net) | T-001, T-002, T-003 | 3 |
| Phase 1: Safe Parallel Implementation | T-004, T-005 | 2 |
| Phase 2: Migration | T-006, T-007 | 2 |
| Phase 3: Cleanup | T-008 | 1 |
| Phase 4: Verification | T-009, T-010 | 2 |
| **Total** | | **10** |

### Critical Path and Estimated Sequence

T-001 → T-002 → T-004 → T-005 → T-006 → T-008 → T-009 → T-010 (8 sequential steps). Two pairs can run in parallel: T-002 with T-003 (independent test suites) and T-006 with T-007 (independent call sites, each releasable on its own). Everything else is strictly sequential — no restructuring before the safety net is green, no migration before the module passes its matrix, no cleanup before both migrations are verified.

### Risk Assessment

| Risk (proposal Section 7) | Mitigating tasks |
|---------------------------|------------------|
| Behavior drift between the two copies during migration (Medium/High) | T-002, T-003 lock current behavior before restructuring; T-006 and T-007 migrate one call site each; old and new coexist until T-008 |
| Timezone/DST edge cases behave differently in the shared implementation (Medium/Medium) | Edge-case matrix written against current behavior first (T-002, T-003), then required to pass unchanged against the module (T-005) |
| Shared module grows server-only or DOM dependencies (Low/Medium) | Dependency-free constraint asserted in T-004, re-verified by the frontend build in T-007 and both builds in T-010 |

Performance implications: none expected — the refactoring extracts pure functions with no new dependencies; T-006's byte-for-byte response check and the unchanged test suite guard against regressions.

### Recommended Review Points

1. **After T-003** — safety net complete and green; approve before any restructuring starts.
2. **After T-005** — the module's edge-case matrix matches characterized behavior; approve before any call site migrates.
3. **After each of T-006 and T-007** — system releasable; each migration commit independently revertible.
4. **Before T-008** — confirm both call sites are migrated and verified; cleanup permanently closes the rollback window.

### Rollback Strategy Summary

Per proposal Section 7: the old inline helpers stay in place until Phase 3, so each migration commit is independently revertible with `git revert` — reverting a single call-site migration restores its previous inline behavior without touching the other consumer. Cleanup (T-008) runs only after both call sites are migrated and verified.

## Acceptance Criteria Coverage

| Work Item AC (Section 9 success criteria) | Covered By |
|-------------------------------------------|------------|
| AC-1: Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` (new) | T-004, T-008, T-010 |
| AC-2: `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; no inline date-comparison helper remains in either file | T-006, T-007, T-008, T-010 |
| AC-3: The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets | T-005, T-010 |
| AC-4: Full test suite passes with no changes to existing test expectations | T-002, T-003, T-010 |
