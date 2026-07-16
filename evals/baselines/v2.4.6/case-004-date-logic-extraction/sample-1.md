# IMP-001 — Extract Shared Date Logic: Refactoring Tasks

> Generated from Improvement Proposal `docs/work-items/IMP-001-extract-date-logic.md` (IMP-001, Approved). The proposal's Section 8 constraints bind every task: **no behavior changes** (overdue rule, API responses, and chip styling byte-for-byte identical), **no new external dependencies** (plain `Date`/`Intl` only), and **incrementally deployable** (every task leaves the system releasable). File paths are relative to the project root; files that do not exist yet are marked `(new)`.

---

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue date logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current test coverage for the two inline copies of the overdue rule — the `filter=overdue` predicate in `src/api/tasks.ts` and the due-date chip check in `src/ui/project-board.tsx` — starting from the proposal's Section 10 table. List the untested scenarios: no DST-transition or offset-extreme cases for the API filter, and no tests at all for the chip styling. Confirm the full existing suite passes before any refactoring begins.

**Rationale:**
The v1.2.4 incident shipped because the duplicated date logic had no shared safety net; a documented baseline defines exactly which behavior the characterization tests must lock in before restructuring starts.

**Acceptance Criteria:**
- [ ] Current coverage for the `src/api/tasks.ts` overdue filter and the `src/ui/project-board.tsx` chip check is measured and documented
- [ ] Coverage gaps are listed (DST transitions and offset extremes for the API filter; all chip-styling scenarios for the UI)
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - coverage baseline notes and gap list

### T-002: Add edge-case tests for the API overdue filter

**Type:** Testing
**Workflow:** standard

**Description:**
Extend `tests/api/tasks.test.ts` with characterization tests for `GET /api/v1/projects/{projectId}/tasks` with `filter=overdue`, covering day boundaries around 00:00 local, DST transition days, and negative/zero/positive UTC offsets (e.g. `America/Los_Angeles`, `UTC`, `Pacific/Auckland`) via the `tz` parameter. The tests assert the route's current behavior and must pass without touching production code.

**Rationale:**
The proposal's Section 7 mitigation requires the edge-case matrix to be written against current behavior first, so the shared module can later be required to pass it unchanged; today's suite covers only the filter happy path and the v1.2.4 regression scenario.

**Acceptance Criteria:**
- [ ] Overdue filter asserted at day boundaries for negative, zero, and positive UTC offsets
- [ ] Overdue filter asserted across DST spring-forward and fall-back transition days
- [ ] Tasks with status `done` asserted excluded from overdue results
- [ ] All new tests pass against the current (pre-refactoring) implementation

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add day-boundary, DST, and UTC-offset characterization cases for `filter=overdue`

### T-003: Add characterization tests for the due-date chip overdue styling

**Type:** Testing
**Workflow:** standard

**Description:**
Create `tests/ui/project-board.test.tsx` covering the TaskCard due-date chip on the Project Board: the chip switches to `error` color only once the due date has fully passed in the browser's local timezone (from 00:00 local of the day after the due date, per `docs/data-model/entities/task.md`). Pin the test timezone so day boundaries and DST transitions are exercised deterministically.

**Rationale:**
The proposal's Section 10 flags the chip logic as the biggest gap — no UI tests exist for it; these tests lock in the current client-side behavior before the check moves to the shared module.

**Acceptance Criteria:**
- [ ] Chip shows `error` styling for a task whose due date has fully passed in the local timezone
- [ ] Chip shows default styling for a task due today and for future due dates
- [ ] Day-boundary and DST-transition cases pass with a pinned timezone
- [ ] All new tests pass against the current (pre-refactoring) implementation

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/project-board.test.tsx (new) - characterization tests for the chip overdue styling

---

## Phase 1: Safe Parallel Implementation

### T-004: Create shared date module alongside the inline copies

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`, implementing the overdue rule documented in `docs/data-model/entities/task.md` (overdue from 00:00 local time of the day after the due date). Do not touch either call site — both keep running their inline copies unchanged.

**Rationale:**
Gives the duplicated business rule (Section 3 problems 1 and 3) a single, directly unit-testable home, built alongside the old copies per the Strangler Fig pattern.

**Acceptance Criteria:**
- [ ] `src/lib/dates.ts` exports `toUserLocalDate` and `isOverdue` implementing the documented overdue rule
- [ ] Module is plain TypeScript with no framework, DOM, or server-only dependencies and no new external packages (`Date`/`Intl` only)
- [ ] `src/api/tasks.ts` and `src/ui/project-board.tsx` are unmodified and the full existing suite still passes

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared date-only helpers (`toUserLocalDate`, `isOverdue`)

**Technical Notes:**
- Approach: derive the user-local calendar date via `Intl.DateTimeFormat` with the explicit `tz` argument — no database-session or implicit-browser conversions, so both consumers compute identical results
- Coexistence strategy: the module ships unused by production code; both inline copies keep serving traffic until Phase 2 migrates them one at a time
- Both the backend and frontend (Vite) builds must compile the module in CI — Section 7's dependency-creep mitigation

### T-005: Add unit tests for the shared date module

**Type:** Testing
**Workflow:** standard

**Description:**
Create `tests/lib/dates.test.ts` with a unit-test matrix for `toUserLocalDate` and `isOverdue`: day boundaries just before and after 00:00 local, DST spring-forward and fall-back transitions, and negative/zero/positive UTC offsets. Expected values must match the current behavior locked in by the T-002/T-003 characterization tests.

**Rationale:**
The proposal's Section 9 requires the shared module to have unit tests for exactly these edge cases, replacing full API round-trips as the fast primary defense for the date logic (Section 3 problem 3).

**Acceptance Criteria:**
- [ ] Day-boundary cases pass for negative, zero, and positive UTC offsets
- [ ] DST spring-forward and fall-back transition days produce correct results
- [ ] Expected values agree with the T-002/T-003 characterization expectations

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/lib/dates.test.ts (new) - edge-case unit tests for the shared module

---

## Phase 2: Migration

### T-006: Migrate the API overdue filter to the shared module

**Type:** Backend
**Workflow:** standard

**Description:**
Switch the `filter=overdue` predicate in `src/api/tasks.ts` to derive the user-local "today" through the shared module instead of its inline copy, leaving the inline helper in place (unused) for clean revertibility. Responses of `GET /api/v1/projects/{projectId}/tasks` must be identical before and after.

**Rationale:**
The server-side copy is the one that drifted in v1.2.4 (UTC day instead of user-local day); moving it onto the audited shared implementation removes that drift source (Section 3 problem 2).

**Acceptance Criteria:**
- [ ] The overdue predicate uses `toUserLocalDate`/`isOverdue` from `src/lib/dates.ts`
- [ ] `tests/api/tasks.test.ts` passes unchanged, including the v1.2.4 regression scenario and the T-002 edge cases
- [ ] No existing test expectations modified; API behavior unchanged

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - import the shared helpers and route the overdue predicate through them

**Technical Notes:**
- Migration steps: import the module → swap the predicate's date derivation → run the full API suite → functional check of the Overdue filter against a seeded board across several `tz` values
- Rollback plan: single-commit change; `git revert` restores the inline derivation without touching the UI call site (Section 7 rollback strategy)
- The inline helper is deliberately left in the file until Phase 3 (T-008) so the revert stays clean

### T-007: Migrate the Project Board chip check to the shared module

**Type:** Frontend
**Workflow:** standard

**Description:**
Switch the due-date chip overdue check in `src/ui/project-board.tsx` to `isOverdue` from the shared module, passing the browser timezone, and leave the old inline check in place (unused) for clean revertibility. The TaskCard chip styling contract in `docs/ui-specification/components.md` must be unchanged.

**Rationale:**
Migrates the second copy of the duplicated rule (Section 3 problem 1); after this task the Overdue filter and the chip derive "overdue" from the same implementation and cannot disagree by construction.

**Acceptance Criteria:**
- [ ] The chip check calls `isOverdue` from `src/lib/dates.ts` with the browser zone
- [ ] `tests/ui/project-board.test.tsx` passes unchanged
- [ ] Chip styling behavior unchanged: `error` color exactly when the due date has fully passed locally

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - import the shared helper and route the chip check through it

**Technical Notes:**
- Migration steps: import the module → swap the chip predicate → run the UI suite → visually verify chips for overdue/today/future due dates on a board
- Rollback plan: single-commit change; `git revert` restores the inline check independently of the API call site (Section 7 rollback strategy)
- Verify the frontend (Vite) build compiles `src/lib/dates.ts` cleanly — no server-only imports

---

## Phase 3: Cleanup

### T-008: Remove the old inline date helpers from both call sites

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unused inline date parsing, "today in timezone" derivation, and comparison code from `src/api/tasks.ts` and `src/ui/project-board.tsx`, leaving `src/lib/dates.ts` as the only implementation of the overdue rule. No behavior changes — both call sites already run on the shared module.

**Rationale:**
T-006 and T-007 migrated and verified both consumers, so per Section 7 the inline copies are confirmed unused; removing them completes Section 9's single-source-of-truth criterion.

**Acceptance Criteria:**
- [ ] No inline date-comparison helper remains in `src/api/tasks.ts` or `src/ui/project-board.tsx`
- [ ] No references to the old helpers and no dead code remain
- [ ] Backend and frontend builds succeed
- [ ] Full test suite passes with no changed expectations

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - delete the unused inline date helper and any leftover imports
- src/ui/project-board.tsx - delete the unused inline overdue check and any leftover imports

**Technical Notes:**
- Rollback plan: single-commit deletion; `git revert` restores both inline helpers without affecting the shared module or its consumers

---

## Phase 4: Verification

### T-009: Final verification of IMP-001 success criteria

**Type:** Testing
**Workflow:** standard

**Description:**
Run the full verification pass across the refactored area: the complete test suite (original plus the T-002/T-003/T-005 additions) with unchanged expectations, type and lint checks for both builds, and a manual check that the Overdue filter and the chip agree for edge-case timezones. Record the results against Section 9 of IMP-001 and update the project docs.

**Rationale:**
Confirms end-to-end that the refactoring preserved behavior and that every Section 9 success criterion holds before IMP-001 is closed.

**Acceptance Criteria:**
- [ ] All original tests pass with no changed expectations
- [ ] New tests from T-002, T-003, and T-005 pass
- [ ] No type or lint errors in the backend or frontend build
- [ ] All four Section 9 success criteria verified and recorded
- [ ] Documentation updated: CLAUDE.md Project Structure table gains the `src/lib/` shared-code row

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- CLAUDE.md - add the `src/lib/` shared-code row to the Project Structure table
- docs/work-items/IMP-001-coverage-baseline.md (new) - append final verification results against the baseline

---

## Summary

**Improvement Proposal:** IMP-001 — Extract Shared Date Logic (`docs/work-items/IMP-001-extract-date-logic.md`)

### Total Tasks by Phase

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 0 — Preparation (Safety Net) | T-001, T-002, T-003 | 3 |
| Phase 1 — Safe Parallel Implementation | T-004, T-005 | 2 |
| Phase 2 — Migration | T-006, T-007 | 2 |
| Phase 3 — Cleanup | T-008 | 1 |
| Phase 4 — Verification | T-009 | 1 |
| **Total** | | **9** |

### Critical Path and Estimated Sequence

T-001 → (T-002 and T-003 in parallel) → T-004 → T-005 → (T-006 and T-007 in parallel) → T-008 → T-009 — seven sequential steps. Every task leaves the system releasable on its own, satisfying the Section 8 incremental-deployment constraint.

### Risk Assessment

- **Behavior drift between the two copies during migration** (Medium likelihood / High impact): mitigated by locking current behavior in first (T-002, T-003), migrating one call site per task (T-006, T-007), and keeping both implementations coexisting until both call sites are verified.
- **Timezone/DST divergence in the shared implementation** (Medium / Medium): mitigated by writing the edge-case matrix against current behavior first (T-002, T-003) and requiring the module's unit tests to match it (T-005).
- **Dependency creep into the shared module** (Low / Medium): mitigated by the dependency-free acceptance criterion in T-004 and the frontend-build check in T-007.

### Recommended Review Points

1. End of Phase 0 (after T-003) — confirm the safety net actually covers day boundaries, DST transitions, and offset extremes before any restructuring begins.
2. After T-005 — confirm the shared module reproduces the characterization expectations before any call site migrates.
3. After each migration (T-006, T-007) — releasable checkpoints; pause and verify no regression in the filter or the chip.
4. Before T-008 — confirm both migrations are verified so old code is removed only after verification.

### Rollback Strategy Summary

Per the proposal's Section 7: each task is a single, independently revertible commit. The inline helpers stay in place until Phase 3, so reverting one migration restores that call site's previous behavior without touching the other consumer; cleanup runs only after both call sites are migrated and verified, and the cleanup commit itself reverts in isolation.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| SC-1: Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` | T-004, T-008 |
| SC-2: `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; no inline date-comparison helper remains in either file | T-006, T-007, T-008 |
| SC-3: The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets | T-005 |
| SC-4: Full test suite passes with no changes to existing test expectations | T-002, T-003, T-006, T-007, T-009 |
