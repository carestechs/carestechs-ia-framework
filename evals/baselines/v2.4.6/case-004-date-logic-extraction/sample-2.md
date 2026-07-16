# IMP-001 — Extract Shared Date Logic: Refactoring Tasks

> Source: `docs/work-items/IMP-001-extract-date-logic.md` (Improvement Proposal, Approved).
> Schema: canonical task schema from `prompts/base-template.md`; `Type` enum delta adds `Cleanup`.
> Binding constraints (proposal Section 8): no behavior changes — API responses and chip styling byte-for-byte identical; no new external dependencies (plain `Date`/`Intl` only); incrementally deployable — every task leaves the system releasable.

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue/date logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current test coverage for the two inline copies of the overdue rule: the `filter=overdue` predicate in `src/api/tasks.ts` and the due-date chip check in `src/ui/project-board.tsx`. Record the gaps from proposal Section 10: the API filter lacks DST-transition cases, and the chip check has no tests at all.

**Rationale:**
Refactoring may not begin without a documented safety net; the v1.2.4 incident shows exactly this logic drifting undetected, so the baseline defines what "behavior unchanged" means for every later task.

**Acceptance Criteria:**
- [ ] Current coverage for `src/api/tasks.ts` (overdue filter) and `src/ui/project-board.tsx` (chip check) measured and documented
- [ ] Coverage gaps listed: DST-transition scenarios for the API; all chip-styling scenarios for the UI
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - baseline notes: measured coverage plus gap list

### T-002: Add DST and offset edge-case tests for the API overdue filter

**Type:** Testing
**Workflow:** standard

**Description:**
Extend `tests/api/tasks.test.ts` with characterization tests for `GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=...` covering day boundaries, DST-transition days, and negative/zero/positive UTC offsets. The tests lock in the current (pre-refactoring) server behavior without touching production code.

**Rationale:**
Proposal Section 10 marks DST-transition cases as untested on the API copy, and the Section 7 mitigation requires the edge-case matrix to exist against current behavior before the shared implementation must reproduce it.

**Acceptance Criteria:**
- [ ] Day-boundary cases pass: task due today in `tz` is not returned; task due yesterday in `tz` is returned
- [ ] DST spring-forward and fall-back transition days covered in a DST-observing zone (e.g. `America/Los_Angeles`)
- [ ] Negative (UTC-8), zero (UTC), and positive (UTC+13) offsets covered
- [ ] Tests exercise current behavior — no production code changes in this task

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add overdue-filter edge-case characterization tests (Supertest, per CLAUDE.md)

### T-003: Add characterization tests for the Project Board due-date chip

**Type:** Testing
**Workflow:** standard

**Description:**
Create component tests for `src/ui/project-board.tsx` locking in the TaskCard due-date chip behavior: the chip switches to `error` color once the due date has fully passed in the browser's local timezone. Cover the same edge matrix as T-002 (day boundary, DST transitions, offsets) by controlling the test clock and timezone.

**Rationale:**
Proposal Section 10 flags the chip logic as fully untested — the biggest gap before refactoring; without these tests the Phase 2 UI migration has no regression signal.

**Acceptance Criteria:**
- [ ] Chip shows `error` styling for a task due yesterday (local) and default styling for one due today
- [ ] Day-boundary case covered: chip flips to overdue at 00:00 local time of the day after `dueDate`
- [ ] DST-transition and non-UTC offset cases covered via a controlled clock/timezone
- [ ] Tests exercise current (pre-refactoring) behavior — no production code changes in this task

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/project-board.test.tsx (new) - chip overdue-styling characterization tests

**Technical Notes:**
- Vitest per CLAUDE.md; make local-date cases deterministic with fake timers (`vi.setSystemTime`) and a pinned timezone (`TZ` env) rather than the machine clock

## Phase 1: Safe Parallel Implementation

### T-004: Create shared date module src/lib/dates.ts

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`, implementing the overdue rule from `docs/data-model/entities/task.md`: a task is overdue from 00:00 local time of the day after its due date. Do not modify either existing call site — both inline copies keep running unchanged.

**Rationale:**
Resolves proposal problem 1 (duplicated business rule with no shared source of truth) by giving the rule a single importable implementation that both the Express backend and the React frontend can consume.

**Acceptance Criteria:**
- [ ] `src/lib/dates.ts` exports `toUserLocalDate` and `isOverdue` as specified in proposal Section 4
- [ ] Module is dependency-free plain TypeScript — no framework, DOM, or Node-only APIs; plain `Date`/`Intl` only
- [ ] `src/api/tasks.ts` and `src/ui/project-board.tsx` are untouched and all existing tests still pass
- [ ] Both the backend and frontend builds compile the module

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared `toUserLocalDate` / `isOverdue` helpers

**Technical Notes:**
- Approach: Strangler Fig — build the new module alongside the old inline copies without touching them
- Coexistence strategy: the module has no consumers until the Phase 2 migrations import it; each call site keeps its inline copy until Phase 3
- Derive the user-local calendar date with `Intl.DateTimeFormat(..., { timeZone: tz })`; no date libraries (Section 8 constraint)

### T-005: Add unit tests for the shared date module

**Type:** Testing
**Workflow:** standard

**Description:**
Create `tests/lib/dates.test.ts` covering `toUserLocalDate` and `isOverdue` against the full edge matrix: day boundaries, DST spring-forward/fall-back transition days, and negative/zero/positive UTC offsets (UTC-8, UTC, UTC+13). Expected values must match the behavior locked in by the T-002 and T-003 characterization tests.

**Rationale:**
Resolves proposal problem 3 (date logic untestable in isolation): edge cases get fast unit tests against the module instead of full API or component round-trips, and Section 9 requires exactly this coverage.

**Acceptance Criteria:**
- [ ] Day-boundary cases pass: not overdue on the due date itself, overdue from 00:00 local time the next day
- [ ] DST transition days pass in a DST-observing zone (e.g. `America/Los_Angeles`)
- [ ] Negative, zero, and positive UTC offsets pass
- [ ] Expected results agree with the T-002/T-003 characterization tests

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/lib/dates.test.ts (new) - unit tests for the shared date helpers

## Phase 2: Migration

### T-006: Migrate the API overdue filter to the shared module

**Type:** Backend
**Workflow:** standard

**Description:**
Switch `src/api/tasks.ts` to compute the `filter=overdue` predicate parameters via `toUserLocalDate`/`isOverdue` from `src/lib/dates.ts` instead of its inline derivation. Leave the now-unused inline helper in place until Phase 3 so this commit stays independently revertible.

**Rationale:**
First of the two call-site migrations (proposal Section 12, note 3); moving the server copy onto the shared module retires the side of the duplication that shipped wrong in v1.2.4.

**Acceptance Criteria:**
- [ ] The route imports the shared module and uses it for the overdue predicate
- [ ] All API tests — including the T-002 edge cases and the existing v1.2.4 timezone regression test — pass unchanged
- [ ] `filter=overdue` responses are byte-for-byte identical (no test expectation changes)

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - replace inline date derivation with `src/lib/dates.ts` imports; inline helper stays until Phase 3

**Technical Notes:**
- Migration steps: import the module → swap the predicate computation → run the full API suite → confirm zero expectation changes
- Rollback plan (proposal Section 7): single-commit change; `git revert` restores the inline behavior without touching the UI call site

### T-007: Migrate the board due-date chip to the shared module

**Type:** Frontend
**Workflow:** standard

**Description:**
Switch the overdue check in `src/ui/project-board.tsx` that drives the TaskCard due-date chip styling to `isOverdue` from `src/lib/dates.ts`, evaluated in the browser's timezone. Leave the now-unused inline helper in place until Phase 3 so this commit stays independently revertible.

**Rationale:**
Second call-site migration (proposal Section 12, note 3); once both sites import the module, the Overdue filter and the chip cannot disagree by construction.

**Acceptance Criteria:**
- [ ] The board screen imports the shared module and uses it for the chip's overdue check
- [ ] T-003 chip characterization tests pass unchanged
- [ ] Chip styling contract from `docs/ui-specification/components.md` is unchanged: `error` color once the due date has passed in browser-local time

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - replace inline overdue check with `src/lib/dates.ts` import; inline helper stays until Phase 3

**Technical Notes:**
- Migration steps: import the module → swap the chip predicate → run the UI suite → visually verify a board containing overdue and non-overdue tasks
- Rollback plan (proposal Section 7): single-commit change; `git revert` restores the inline chip check independently of the API migration

## Phase 3: Cleanup

### T-008: Remove old inline date helpers from both call sites

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unused inline date parsing, "today in timezone" derivation, and comparison code from `src/api/tasks.ts` and `src/ui/project-board.tsx`, leaving `src/lib/dates.ts` as the single implementation.

**Rationale:**
Both call sites are migrated and verified (T-006, T-007), so the inline copies are provably dead; removing them completes Section 9's "no inline date-comparison helper remains in either file".

**Acceptance Criteria:**
- [ ] No inline date-comparison or local-date-derivation helper remains in `src/api/tasks.ts` or `src/ui/project-board.tsx`
- [ ] No dead code or commented-out old code left behind
- [ ] Build succeeds for backend and frontend
- [ ] All tests pass

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - delete the unused inline date helper and any orphaned imports
- src/ui/project-board.tsx - delete the unused inline date helper and any orphaned imports

## Phase 4: Verification

### T-009: Run final verification against the proposal success criteria

**Type:** Testing
**Workflow:** standard

**Description:**
Run the full verification pass: complete test suite (API, UI, and shared-module tests), type check and lint, and both builds compiling `src/lib/dates.ts`. Confirm every proposal Section 9 success criterion and update the CLAUDE.md Project Structure table to document the new `src/lib/` location.

**Rationale:**
Confirms end-to-end that the refactoring preserved behavior (Section 8: byte-for-byte identical) and closes IMP-001 with the project documentation reflecting the new structure.

**Acceptance Criteria:**
- [ ] Full test suite passes with no changes to existing test expectations (Section 9)
- [ ] Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` — verified by searching both former call sites
- [ ] No type or lint errors; backend and frontend builds both compile the shared module
- [ ] CLAUDE.md Project Structure table documents shared code under `src/lib/`

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- CLAUDE.md - add a `src/lib/` row to the Project Structure table

## Summary

**Improvement Proposal:** IMP-001 — Extract Shared Date Logic.

**Total tasks by phase:**

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 0 — Preparation (Safety Net) | T-001, T-002, T-003 | 3 |
| Phase 1 — Safe Parallel Implementation | T-004, T-005 | 2 |
| Phase 2 — Migration | T-006, T-007 | 2 |
| Phase 3 — Cleanup | T-008 | 1 |
| Phase 4 — Verification | T-009 | 1 |
| **Total** | | **9** |

**Critical path and sequence:** T-001 → (T-002 ∥ T-003) → T-004 → T-005 → (T-006 ∥ T-007) → T-008 → T-009. The two gap-closing test tasks can run in parallel after the baseline, and the two call-site migrations can run in parallel after the module is unit-tested; everything else is sequential.

**Risk assessment (from proposal Section 7):**
- *Behavior drift during migration* (Medium/High) — characterization tests (T-002, T-003) lock current behavior in before any restructuring; each call site migrates in its own task; old and new coexist until both are verified.
- *Timezone/DST divergence in the shared implementation* (Medium/Medium) — the edge matrix (day boundaries, DST transitions, UTC-8/UTC/UTC+13) is written against current behavior first (T-002, T-003) and must pass unchanged against the module (T-005).
- *Shared module grows server-only or DOM dependencies* (Low/Medium) — T-004 and T-009 require the module to stay dependency-free and to compile in both builds.

**Recommended review points:**
1. After Phase 0 (T-003) — confirm the safety net covers both call sites before any restructuring starts.
2. After T-005 — confirm the module reproduces the characterization behavior before any consumer migrates.
3. After each migration (T-006, T-007) — confirm zero test-expectation changes before proceeding.
4. Before T-008 — confirm both migrations are deployed and verified before deleting the old copies.

**Rollback strategy summary:** Old inline helpers stay in place until Phase 3, so each migration commit is independently revertible with `git revert` — reverting one call-site migration restores its previous inline behavior without touching the other consumer. Cleanup (T-008) happens only after both call sites are migrated and verified (proposal Section 7).

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| SC-1: Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` (new) | T-004, T-008, T-009 |
| SC-2: `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; no inline date-comparison helper remains in either file | T-006, T-007, T-008 |
| SC-3: The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets | T-005 |
| SC-4: Full test suite passes with no changes to existing test expectations | T-002, T-003, T-009 |
