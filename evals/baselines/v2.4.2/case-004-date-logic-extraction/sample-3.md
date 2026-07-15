# IMP-001 — Extract Shared Date Logic: Refactoring Tasks

> **Source work item:** docs/work-items/IMP-001-extract-date-logic.md (Improvement Proposal IMP-001, Approved)
> **Prompts:** prompts/refactor-tasks.md + canonical task schema from prompts/base-template.md
> **Binding constraints (Section 8):** no behavior changes; no new external dependencies (plain `Date`/`Intl` only); every task leaves the system releasable.

---

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue/date-comparison logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current test coverage for the two inline copies of the overdue rule — the `filter=overdue` predicate in `src/api/tasks.ts` and the due-date chip check in `src/ui/project-board.tsx`. Record the proposal's Section 10 gaps as the checklist to close: no DST-transition cases on the API side, no tests at all for the UI chip. Run the full existing suite to confirm it is green before any refactoring begins.

**Rationale:**
Refactoring must not start without a documented safety-net baseline; the v1.2.4 incident proves this exact logic drifts silently when untested.

**Acceptance Criteria:**
- [ ] Current coverage for both call sites measured and documented in the baseline notes
- [ ] Coverage gaps listed (API DST-transition scenarios; all UI chip scenarios)
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - baseline coverage notes and gap list

### T-002: Add DST-transition and offset edge-case tests for the API overdue filter

**Type:** Testing
**Workflow:** standard

**Description:**
Extend the existing Supertest suite with characterization tests for GET /api/v1/projects/{projectId}/tasks with `filter=overdue` + `tz`: day boundaries (23:59 vs 00:00 local), DST spring-forward and fall-back transition days, and UTC-8 / UTC / UTC+13 offsets. The tests lock in the current server-side behavior without modifying `src/api/tasks.ts`.

**Rationale:**
Section 10 marks API coverage as partial (no DST-transition cases); Section 7 requires the edge-case matrix to be written against current behavior before the shared module exists.

**Acceptance Criteria:**
- [ ] Day-boundary, DST-transition, and negative/zero/positive offset scenarios have passing tests
- [ ] Tests exercise current (pre-refactoring) behavior; `src/api/tasks.ts` is unchanged
- [ ] Existing happy-path and v1.2.4 regression tests still pass unchanged

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add DST/day-boundary/offset characterization cases

### T-003: Add characterization tests for the Project Board due-date chip overdue check

**Type:** Testing
**Workflow:** standard

**Description:**
Create UI tests for `src/ui/project-board.tsx` covering the client-side check that switches the TaskCard due-date chip to the `error` color. Cover due dates in the past, today, and in the future in the browser's local zone, plus the day-boundary case, locking in the current pre-refactoring behavior.

**Rationale:**
Section 10 calls the untested chip logic the biggest gap before refactoring; without these tests the UI migration in Phase 2 has no safety net.

**Acceptance Criteria:**
- [ ] Chip renders `error` color for overdue tasks and default color otherwise, per the components.md contract
- [ ] Day-boundary behavior in the browser-local zone is covered
- [ ] Tests exercise current (pre-refactoring) behavior; `src/ui/project-board.tsx` is unchanged

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/project-board.test.tsx (new) - chip overdue-styling characterization tests

## Phase 1: Safe Parallel Implementation

### T-004: Create shared date module with toUserLocalDate and isOverdue

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`, implementing the overdue rule from `docs/data-model/entities/task.md` (overdue from 00:00 local time of the day after the due date). Plain TypeScript using only `Date`/`Intl` — no framework, DOM, or external dependencies. Neither call site is touched; both inline copies keep running unchanged.

**Rationale:**
Resolves Section 3 problems 1 and 3 — creates the single, directly testable source of truth while strangler-fig coexistence keeps both consumers on their old code until migration.

**Acceptance Criteria:**
- [ ] Module exports both helpers and implements the documented overdue rule
- [ ] No new external dependencies; no framework or DOM imports
- [ ] Module compiles in both the backend and frontend builds
- [ ] Old inline copies are untouched and the full existing suite still passes

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared date-only helpers (single source of truth)

**Technical Notes:**
- Approach: strangler fig — build the new module alongside the old inline copies without removing them
- Coexistence strategy: the module stays unreferenced until Phase 2; each call site migrates in its own task
- Keep the file dependency-free per Section 7 risk 3 so both builds compile it in CI

### T-005: Add unit tests for the shared date module edge-case matrix

**Type:** Testing
**Workflow:** standard

**Description:**
Unit-test `src/lib/dates.ts` directly against the edge-case matrix: day boundaries, DST spring-forward and fall-back transitions, and UTC-8 / UTC / UTC+13 offsets. Expectations mirror the behavior locked in by the Phase 0 characterization tests (T-002, T-003), proving the module equivalent before any consumer migrates.

**Rationale:**
Section 4 requires the date logic to be testable in isolation; Section 7 requires the matrix to pass unchanged against the module to rule out drift.

**Acceptance Criteria:**
- [ ] Day-boundary cases pass (task becomes overdue exactly at 00:00 local of the day after the due date)
- [ ] DST-transition cases pass for both spring-forward and fall-back days
- [ ] Negative/zero/positive UTC offsets (UTC-8, UTC, UTC+13) pass
- [ ] Module results agree with the Phase 0 characterization expectations

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/lib/dates.test.ts (new) - unit tests for toUserLocalDate and isOverdue

## Phase 2: Migration

### T-006: Migrate the API overdue filter to the shared module

**Type:** Backend
**Workflow:** standard

**Description:**
Switch the `filter=overdue` predicate in `src/api/tasks.ts` to import `toUserLocalDate`/`isOverdue` from `src/lib/dates.ts` instead of its inline derivation. The old inline helper stays in the file, unreferenced, until Phase 3 cleanup.

**Rationale:**
First of the two per-call-site migrations required by Section 7's drift mitigation — the API consumer moves alone so the UI copy keeps its known behavior meanwhile.

**Acceptance Criteria:**
- [ ] Route derives the overdue predicate exclusively via the shared module
- [ ] All API tests pass unchanged, including the v1.2.4 regression scenario and the T-002 DST cases
- [ ] GET /api/v1/projects/{projectId}/tasks responses are byte-for-byte identical (no behavior change)

**Dependencies:** T-002, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - replace inline date derivation with shared-module imports

**Technical Notes:**
- Migration steps: swap the predicate inputs to the shared helpers, run tests/api/tasks.test.ts, verify identical responses
- Rollback plan: single-commit change — `git revert` restores the inline behavior without touching the UI consumer (Section 7 rollback strategy)

### T-007: Migrate the Project Board chip overdue check to the shared module

**Type:** Frontend
**Workflow:** standard

**Description:**
Switch the TaskCard due-date chip overdue check in `src/ui/project-board.tsx` to `isOverdue` from `src/lib/dates.ts`, passing the browser zone. The old inline check stays in the file, unreferenced, until Phase 3 cleanup.

**Rationale:**
Second per-call-site migration (Section 7): once both consumers read the same module, the Overdue filter and the chip cannot disagree by construction (Section 4 benefit 1).

**Acceptance Criteria:**
- [ ] Chip styling decision comes exclusively from the shared module
- [ ] TaskCard chip styling contract is unchanged per docs/ui-specification/components.md
- [ ] T-003 characterization tests pass unchanged (no visual or behavior change)

**Dependencies:** T-003, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - replace inline overdue check with shared-module import

**Technical Notes:**
- Migration steps: import the helper, feed it the browser zone, run tests/ui/project-board.test.tsx
- Rollback plan: single-commit change — `git revert` restores the inline check without touching the API consumer (Section 7 rollback strategy)

## Phase 3: Cleanup

### T-008: Remove old inline date helpers from both call sites

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unreferenced inline date parsing, "today in timezone" derivation, and comparison code from `src/api/tasks.ts` and `src/ui/project-board.tsx`. Both call sites have migrated (T-006, T-007) and been verified, so the old copies are dead code.

**Rationale:**
Completes the Section 9 criterion "no inline date-comparison helper remains in either file"; cleanup is safe only now that both migrations are verified (Section 7 rollback strategy).

**Acceptance Criteria:**
- [ ] No inline date-comparison helper or reference to the old implementations remains in either file
- [ ] No dead or commented-out code left behind
- [ ] Build succeeds and the full test suite passes

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - remove unused inline date helper
- src/ui/project-board.tsx - remove unused inline overdue check

## Phase 4: Verification

### T-009: Document the new src/lib directory in CLAUDE.md

**Type:** Documentation
**Workflow:** standard

**Description:**
Add a `src/lib/` row to the CLAUDE.md Project Structure table describing shared framework-free modules (currently `src/lib/dates.ts`), including the mirrored `tests/lib/` test location. Spec shards stay untouched — Section 6 states this improvement moves code, not contracts.

**Rationale:**
Section 11 notes shared code under `src/lib/` is new to the architecture reference; leaving it undocumented invites the next date helper to be inlined again.

**Acceptance Criteria:**
- [ ] Project Structure table documents `src/lib/` and its purpose
- [ ] No spec shard (data-model, api-spec, ui-specification) is modified

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- CLAUDE.md - add src/lib/ row to the Project Structure table

### T-010: Final verification of IMP-001 success criteria

**Type:** Testing
**Workflow:** standard

**Description:**
Run the full verification pass: complete test suite (original plus the T-002/T-003/T-005 additions), type and lint checks, and both backend and frontend builds compiling `src/lib/dates.ts`. Verify each Section 9 success criterion and record the outcome in the proposal.

**Rationale:**
Confirms end-to-end that the refactoring preserved behavior under the Section 8 constraints before IMP-001 is closed.

**Acceptance Criteria:**
- [ ] All original tests pass with no changes to existing test expectations
- [ ] New unit and characterization tests pass
- [ ] Exactly one overdue/date-only implementation exists (src/lib/dates.ts) and both consumers import it
- [ ] No type or lint errors; both builds compile the shared module
- [ ] Section 9 verification outcome recorded in the proposal

**Dependencies:** T-008, T-009
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-extract-date-logic.md - record Section 9 verification outcome and status update

## Summary

Task generation output for Improvement Proposal **IMP-001 — Extract Shared Date Logic** (refactoring; no behavior changes).

**Total tasks by phase:**

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 0 — Preparation (Safety Net) | T-001, T-002, T-003 | 3 |
| Phase 1 — Safe Parallel Implementation | T-004, T-005 | 2 |
| Phase 2 — Migration | T-006, T-007 | 2 |
| Phase 3 — Cleanup | T-008 | 1 |
| Phase 4 — Verification | T-009, T-010 | 2 |
| **Total** | | **10** |

**Critical path and estimated sequence:**
T-001 → T-003 → T-004 → T-005 → T-007 → T-008 → T-009 → T-010 (8 sequential steps). T-002 and T-003 can run in parallel after T-001; T-006 and T-007 can run in parallel after T-005. Estimated effort matches the proposal's M sizing: two M-complexity safety-net tasks, two M-complexity build tasks, and six S/M incremental steps.

**Risk assessment (mapped to Section 7):**
- *Mid-migration drift between the two copies*: bounded by characterization tests written first (T-002, T-003) and by migrating exactly one call site per task (T-006, T-007) while the other keeps its verified inline copy.
- *DST/offset divergence in the shared implementation*: the edge-case matrix is locked against current behavior in Phase 0 and must pass unchanged against the module (T-005) before any migration.
- *Shared module growing server-only or DOM dependencies*: forbidden by T-004 acceptance criteria and re-verified in T-010 (both builds compile the module).

**Recommended review points:**
1. After Phase 0 (T-001–T-003): baseline documented, suite green, gaps closed — approve the start of restructuring.
2. After T-005: module proven equivalent on the edge-case matrix — approve migrations.
3. After each migration (T-006, T-007): confirm identical behavior before proceeding.
4. Before T-008 cleanup: confirm both call sites are migrated and verified — the last point where per-call-site `git revert` is trivial.

**Rollback strategy summary:**
Per Section 7, the old inline helpers remain in place until Phase 3, so each migration commit is independently revertible with `git revert` — reverting one call-site migration restores its previous inline behavior without touching the other consumer. Cleanup (T-008) runs only after both call sites are migrated and verified; after cleanup, rollback means reverting the cleanup commit itself.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Exactly one implementation of the overdue/date-only comparison exists, in src/lib/dates.ts (new) | T-004, T-008, T-010 |
| AC-2: src/api/tasks.ts and src/ui/project-board.tsx both import it; no inline date-comparison helper remains in either file | T-006, T-007, T-008 |
| AC-3: The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets | T-005 |
| AC-4: Full test suite passes with no changes to existing test expectations | T-002, T-003, T-010 |
