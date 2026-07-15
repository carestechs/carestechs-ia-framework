<!-- Known-good reference output — not used by any judge check in this case; kept as
     the hand-written anchor for a safe five-phase decomposition of IMP-001. -->

# Task List: IMP-001 Extract Shared Date Logic

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue/date-comparison logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current coverage for the two date-logic copies — the overdue predicate path in `src/api/tasks.ts` and the chip check in `src/ui/project-board.tsx` — and list the untested scenarios per the proposal's Section 10.

**Rationale:**
Refactoring must not start without a documented safety net; Section 10 already flags the UI chip logic as fully untested.

**Acceptance Criteria:**
- [ ] Coverage for both copies measured and documented (baseline notes recorded against IMP-001)
- [ ] Gaps listed: DST transitions for the API copy; everything for the UI chip check
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- tests/api/tasks.test.ts - inventory what the existing filter tests actually pin down
- docs/work-items/IMP-001-extract-date-logic.md - record the baseline against Section 10

### T-002: Add characterization tests for the date edge cases

**Type:** Testing
**Workflow:** standard

**Description:**
Add tests that lock in the current pre-refactoring behavior of both copies for the gap scenarios: day-boundary instants in the user's timezone, DST transition days, and negative/zero/positive UTC offsets, on both the API filter and the chip styling.

**Rationale:**
The proposal's top risk is behavior drift during migration; characterization tests written against today's behavior are the only mechanical drift detector.

**Acceptance Criteria:**
- [ ] API characterization cases cover day boundaries, DST transitions, and UTC-8/UTC/UTC+13 against the current predicate
- [ ] New UI test covers the chip's overdue styling across the same matrix with a frozen clock
- [ ] All new tests pass against the current (pre-refactoring) implementations

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - edge-case matrix for `filter=overdue` + `tz`
- tests/ui/project-board.test.tsx (new) - chip overdue-styling characterization tests

## Phase 1: Safe Parallel Implementation

### T-003: Create the shared date service alongside the existing copies

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)` per the overdue rule in `docs/data-model/entities/task.md`, as dependency-free plain TypeScript, without touching either existing call site.

**Rationale:**
Parallel implementation lets the module be verified in isolation while both consumers keep running their old inline copies (Section 7 coexistence mitigation).

**Acceptance Criteria:**
- [ ] Module compiles in both backend and frontend builds with no framework/DOM/external dependencies
- [ ] Unit tests mirror the T-002 characterization matrix and pass
- [ ] Both existing call sites are untouched and all existing tests still pass

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared date-only helpers
- tests/lib/dates.test.ts (new) - unit tests for the helpers

**Technical Notes:**
- Approach: implement against the characterization expectations, not against either existing copy's source
- Coexistence strategy: nothing imports the module yet; old inline helpers remain authoritative until Phase 2

## Phase 2: Migration

### T-004: Migrate the API overdue predicate to the shared date service

**Type:** Backend
**Workflow:** standard

**Description:**
Replace the inline user-local-date derivation in `src/api/tasks.ts` with `toUserLocalDate` from `src/lib/dates.ts`, leaving the route's validation, envelope, and repository call unchanged.

**Rationale:**
First consumer migration — the API side has existing regression tests, so drift surfaces here with the strongest safety net.

**Acceptance Criteria:**
- [ ] Route imports the shared module; its old inline derivation is no longer referenced
- [ ] All API tests, including the T-002 characterization matrix, pass unchanged
- [ ] No response-shape or behavior change on `filter=overdue`

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - swap inline date derivation for the shared helper

**Technical Notes:**
- Migration steps: swap the call, run the full API suite, verify staging behavior matches the chip
- Rollback plan: single-commit change; `git revert` restores the inline copy (it is deleted only in T-006)

### T-005: Migrate the board chip check to the shared date service

**Type:** Frontend
**Workflow:** standard

**Description:**
Replace the inline overdue check in `src/ui/project-board.tsx` with `isOverdue` from `src/lib/dates.ts`, keeping the TaskCard chip contract exactly as documented in `docs/ui-specification/components.md`.

**Rationale:**
Second consumer migration — after this, filter and chip provably share one rule, closing the drift class behind the v1.2.4 incident.

**Acceptance Criteria:**
- [ ] Screen imports the shared module; its old inline check is no longer referenced
- [ ] T-002's UI characterization tests pass unchanged
- [ ] Chip styling agrees with the server filter across the timezone matrix

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - swap inline overdue check for the shared helper

**Technical Notes:**
- Migration steps: swap the call, run the UI suite, spot-check a UTC-8 profile on staging
- Rollback plan: single-commit change, independently revertible per the proposal's rollback strategy

## Phase 3: Cleanup

### T-006: Remove the duplicated date helpers and run final verification

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unused inline date helpers from both call-site files, confirm nothing else references them, and run the full verification pass against the proposal's Section 9 success criteria.

**Rationale:**
Both consumers are migrated and verified (T-004, T-005), so the old copies are dead code; the proposal requires no duplicated helper to remain.

**Acceptance Criteria:**
- [ ] No inline date-comparison helper remains in `src/api/tasks.ts` or `src/ui/project-board.tsx`; no dead code or commented-out remnants
- [ ] Build and full test suite pass (original tests, characterization tests, module unit tests)
- [ ] All Section 9 success criteria verified and recorded against IMP-001

**Dependencies:** T-004, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - remove the old inline helper
- src/ui/project-board.tsx - remove the old inline check
- docs/work-items/IMP-001-extract-date-logic.md - record success-criteria verification; set Status to Completed

## Summary

- **Tasks by phase:** Phase 0 — T-001, T-002 (safety net); Phase 1 — T-003 (parallel implementation); Phase 2 — T-004, T-005 (one consumer each); Phase 3 — T-006 (cleanup + final verification).
- **Critical path:** T-001 → T-002 → T-003 → (T-004 ∥ T-005) → T-006; the two migrations are independent and may land in either order.
- **Risk assessment:** low once Phase 0 lands — the proposal's main risk (drift during migration) is bounded by characterization tests and one-call-site-per-task migration; no schema, API-contract, or spec-shard changes anywhere.
- **Review points:** after T-002 (does the matrix really pin current behavior?), after T-003 (module API review before consumers couple to it), and before T-006 (confirm both migrations verified on staging).
- **Rollback strategy:** old helpers coexist with the module until T-006; every migration is a single revertible commit, per IMP-001 Section 7.

Traceability: generated from IMP-001 (Extract Shared Date Logic).
