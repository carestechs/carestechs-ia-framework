# IMP-001 — Extract Shared Date Logic: Refactoring Task List

> Generated from `docs/work-items/IMP-001-extract-date-logic.md` (Improvement Proposal, Approved). Refactoring only — the overdue rule, API responses, and chip styling stay byte-for-byte identical (Section 8). No new dependencies; plain `Date`/`Intl` only. Every phase leaves the system releasable.

---

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue date logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current test coverage for the two copies of the overdue logic: the `filter=overdue` predicate in `src/api/tasks.ts` and the due-date chip check in `src/ui/project-board.tsx`. Confirm the proposal's Section 10 picture and list every untested scenario (API DST transitions; all UI chip scenarios).

**Rationale:**
Refactoring may not begin without a documented safety-net baseline; Section 10 already shows real gaps that must be named and closed first.

**Acceptance Criteria:**
- [ ] Coverage for the API overdue filter and the UI chip check measured and documented
- [ ] Coverage gaps listed: API DST-transition cases missing; UI chip styling entirely untested
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - baseline notes and gap list

### T-002: Add DST-transition tests for the API overdue filter

**Type:** Testing
**Workflow:** standard

**Description:**
Extend the tasks API integration tests with characterization cases for `filter=overdue` + `tz` on DST transition days and at day boundaries across negative/zero/positive UTC offsets. Assertions lock in current (pre-refactoring) server behavior.

**Rationale:**
Section 10 marks API coverage as partial (happy path + v1.2.4 regression only, no DST cases); the risk mitigation in Section 7 requires the edge-case matrix to exist against current behavior before the shared module is written.

**Acceptance Criteria:**
- [ ] `filter=overdue` covered on spring-forward and fall-back DST transition days for an IANA zone that observes DST (e.g. `America/Los_Angeles`)
- [ ] Day-boundary cases covered at UTC-8, UTC, and UTC+13 (due today → not overdue; overdue from 00:00 local of the next day)
- [ ] Tests exercise current (pre-refactoring) behavior and pass unchanged

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add DST-transition and offset day-boundary cases

**Technical Notes:**
- Characterize behavior as-is: the API currently derives the local date via the database session (Section 3 evidence) — do not "fix" oddities in this phase
- Overdue filter excludes `status = done` per `docs/api-spec/endpoints/tasks.md`

### T-003: Add characterization tests for the Project Board due-date chip

**Type:** Testing
**Workflow:** standard

**Description:**
Create component tests for the due-date chip overdue check in `src/ui/project-board.tsx`/TaskCard: the chip switches to `error` color once the due date has passed in the browser's local timezone. Mock the system clock and timezone to pin each scenario.

**Rationale:**
Section 10 calls the untested chip logic the biggest gap before refactoring; without these tests the UI migration in Phase 2 has no safety net.

**Acceptance Criteria:**
- [ ] Chip renders `error` color for a due date fully passed in the browser-local timezone, default color otherwise
- [ ] Day-boundary case covered: due today is not overdue until 00:00 local time of the day after the due date
- [ ] Cases cover negative/zero/positive UTC offsets and a DST transition day
- [ ] Tests exercise current (pre-refactoring) behavior and pass

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/project-board.test.tsx (new) - chip overdue-styling characterization tests

**Technical Notes:**
- Pin time with Vitest fake timers (`vi.setSystemTime`) and control the zone via the `TZ` environment/`Intl` options
- The TaskCard chip contract in `docs/ui-specification/components.md` stays exactly as documented

## Phase 1: Safe Parallel Implementation

### T-004: Create shared date module src/lib/dates.ts

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`, implementing the overdue rule from `docs/data-model/entities/task.md`. The module is plain TypeScript with no framework or DOM dependencies; neither call site imports it yet — both inline copies stay untouched.

**Rationale:**
Resolves Section 3 Problem 1 (duplicated business rule) by building the single source of truth alongside the old copies, strangler-fig style, without touching existing behavior.

**Acceptance Criteria:**
- [ ] Module exports `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)` implementing "overdue from 00:00 local time of the day after the due date"
- [ ] No new external dependencies — plain `Date`/`Intl` only; no framework or DOM imports
- [ ] Backend and frontend builds both compile the module
- [ ] Old inline copies in `src/api/tasks.ts` and `src/ui/project-board.tsx` are unchanged and all existing tests pass

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared toUserLocalDate/isOverdue helpers

**Technical Notes:**
- Approach: derive the user-local date with `Intl.DateTimeFormat` + `timeZone`, replacing both divergent derivations (database session vs browser `Date`)
- Coexistence strategy: the module is unreferenced until Phase 2 — old and new implementations coexist until both call sites are verified
- `due_date` is stored as 00:00:00 UTC of the picked date (date-only semantics per the Task entity shard)

### T-005: Add edge-case unit tests for the shared date module

**Type:** Testing
**Workflow:** standard

**Description:**
Write fast unit tests for `src/lib/dates.ts` covering the full edge-case matrix — day boundaries, DST spring-forward/fall-back transitions, and UTC-8/UTC/UTC+13 offsets. Expectations mirror the Phase 0 characterization results so the module reproduces current call-site behavior exactly.

**Rationale:**
Resolves Section 3 Problem 3 (logic untestable in isolation) and satisfies the Section 7 mitigation: the matrix written against current behavior must pass unchanged against the module.

**Acceptance Criteria:**
- [ ] Day-boundary cases pass: due today not overdue; overdue from 00:00 local time of the next day
- [ ] DST spring-forward and fall-back transition days pass
- [ ] Negative/zero/positive offsets (UTC-8, UTC, UTC+13) pass
- [ ] Expectations match the behavior locked in by T-002 and T-003

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/lib/dates.test.ts (new) - edge-case matrix unit tests for the shared module

## Phase 2: Migration

### T-006: Migrate the API overdue filter to the shared module

**Type:** Backend
**Workflow:** standard

**Description:**
Switch the `filter=overdue` predicate in `src/api/tasks.ts` to import `toUserLocalDate`/`isOverdue` from `src/lib/dates.ts`. The old inline helper stays in the file (unused) until Phase 3 cleanup.

**Rationale:**
First consumer migration toward the single source of truth (Section 3 Problems 1–2); per Section 7 the call sites migrate one per task while old and new coexist.

**Acceptance Criteria:**
- [ ] The overdue predicate derivation uses `src/lib/dates.ts`
- [ ] Old inline helper remains in the file, unused, pending cleanup
- [ ] All API tests — including the v1.2.4 regression scenario and the T-002 DST cases — pass with no changed expectations
- [ ] API responses are byte-for-byte identical (envelope, TaskDto, meta)

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - replace inline date derivation with shared-module imports

**Technical Notes:**
- Migration steps: import the module → swap the predicate's date derivation → run the full API suite and verify identical responses
- Rollback plan: single-commit `git revert` restores the inline behavior without touching the UI consumer (Section 7 rollback strategy)

### T-007: Migrate the Project Board chip check to the shared module

**Type:** Frontend
**Workflow:** standard

**Description:**
Switch the due-date chip overdue check in `src/ui/project-board.tsx` to import `isOverdue` from `src/lib/dates.ts`, passing the browser zone as `tz`. The old inline check stays in the file (unused) until Phase 3 cleanup.

**Rationale:**
Second and final consumer migration — after this the filter and the chip cannot disagree by construction (Section 4 Benefit 1); migrated separately from T-006 per Section 7.

**Acceptance Criteria:**
- [ ] The chip overdue check uses `src/lib/dates.ts`
- [ ] Old inline check remains in the file, unused, pending cleanup
- [ ] T-003 characterization tests pass with no changed expectations
- [ ] Chip styling contract stays exactly as documented in `docs/ui-specification/components.md`

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - replace inline overdue check with shared-module import

**Technical Notes:**
- Migration steps: import the module → pass `Intl.DateTimeFormat().resolvedOptions().timeZone` as `tz` → run the T-003 suite and verify identical chip rendering
- Rollback plan: single-commit `git revert` restores the inline chip check without touching the API consumer (Section 7 rollback strategy)

## Phase 3: Cleanup

### T-008: Remove old inline date helpers from both call sites

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unused inline date parsing, "today in timezone" derivation, and comparison helpers from `src/api/tasks.ts` and `src/ui/project-board.tsx`.

**Rationale:**
Both consumers are migrated and verified (T-006, T-007), so the old copies are dead code; Section 9 requires that no inline date-comparison helper remain in either file.

**Acceptance Criteria:**
- [ ] No inline date-comparison helper remains in `src/api/tasks.ts` or `src/ui/project-board.tsx`
- [ ] No references to the old helpers remain anywhere; no dead code left behind
- [ ] Build succeeds
- [ ] Full test suite passes

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - remove unused inline date helper and stale imports
- src/ui/project-board.tsx - remove unused inline overdue check and stale imports

## Phase 4: Verification

### T-009: Run final verification across the refactored area

**Type:** Testing
**Workflow:** standard

**Description:**
Run the full verification pass: complete test suite (original plus all new tests), type and lint checks, and both builds compiling `src/lib/dates.ts`. Verify every Section 9 success criterion and record `src/lib/` in the CLAUDE.md Project Structure table.

**Rationale:**
Confirms the refactoring preserved behavior end-to-end before IMP-001 is closed — all four Section 9 criteria verified in one pass over the finished state.

**Acceptance Criteria:**
- [ ] All original tests pass with no changed expectations; all new tests (T-002, T-003, T-005) pass
- [ ] No type or lint errors; backend and frontend builds both compile the shared module
- [ ] Exactly one implementation of the overdue comparison exists (`src/lib/dates.ts`) and both call sites import it
- [ ] CLAUDE.md Project Structure table documents `src/lib/` as the shared-code location

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- CLAUDE.md - add src/lib/ shared-code row to the Project Structure table

## Summary

Task list for **IMP-001 — Extract Shared Date Logic** (9 tasks).

### Total Tasks by Phase

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 0 — Preparation (Safety Net) | T-001, T-002, T-003 | 3 |
| Phase 1 — Safe Parallel Implementation | T-004, T-005 | 2 |
| Phase 2 — Migration | T-006, T-007 | 2 |
| Phase 3 — Cleanup | T-008 | 1 |
| Phase 4 — Verification | T-009 | 1 |

### Critical Path and Estimated Sequence

T-001 → (T-002 ∥ T-003) → T-004 → T-005 → (T-006 ∥ T-007) → T-008 → T-009. The two Phase 0 gap-closing tasks can run in parallel, as can the two Phase 2 migrations; everything else is sequential.

### Risk Assessment

- **Behavior drift during migration** (Section 7, Medium/High): mitigated by characterization tests before restructuring (T-002, T-003), one call site per migration task (T-006, T-007), and coexistence until cleanup (T-008)
- **Timezone/DST divergence in the shared implementation** (Medium/Medium): mitigated by the edge-case matrix written against current behavior first (T-002, T-003) and required to pass unchanged against the module (T-005)
- **Module growing server-only or DOM dependencies** (Low/Medium): mitigated by dependency-free acceptance criteria in T-004 and both-builds-compile checks in T-004 and T-009

### Recommended Review Points

1. After Phase 0 (T-003): baseline documented, both coverage gaps closed, suite green — restructuring may begin
2. After T-005: edge-case matrix green against the module before any call site migrates
3. After each migration (T-006, T-007): responses/rendering verified identical before proceeding
4. Before T-008: confirm both call sites are migrated and verified — only then remove old code

### Rollback Strategy Summary

Per Section 7: old inline helpers stay in place until Phase 3, so each migration commit is independently revertible with `git revert` — reverting one call-site migration restores its previous inline behavior without touching the other consumer. Cleanup runs only after both call sites are migrated and verified.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| SC-1: Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` (new) | T-004, T-008, T-009 |
| SC-2: `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; no inline date-comparison helper remains in either file | T-006, T-007, T-008 |
| SC-3: The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets | T-005 |
| SC-4: Full test suite passes with no changes to existing test expectations | T-006, T-007, T-009 |
