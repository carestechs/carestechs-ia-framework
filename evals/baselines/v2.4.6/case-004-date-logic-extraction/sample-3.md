# IMP-001 — Extract Shared Date Logic: Refactoring Tasks

> Generated from `docs/work-items/IMP-001-extract-date-logic.md` (Improvement Proposal, Status: Approved) following `prompts/refactor-tasks.md` and the canonical task schema in `prompts/base-template.md`.
>
> Binding constraints (IMP-001 Section 8): **no behavior changes** (API responses and chip styling byte-for-byte identical), **no new external dependencies** (plain `Date`/`Intl` only), **incrementally deployable** (every task leaves the system releasable). All file paths are relative to the project root.

---

## Phase 0: Preparation (Safety Net)

### T-001: Establish test coverage baseline for the overdue/date-comparison logic

**Type:** Testing
**Workflow:** standard

**Description:**
Measure and document current test coverage for the two copies of the overdue rule — the `filter=overdue` derivation in `src/api/tasks.ts` and the due-date chip check in `src/ui/project-board.tsx` — starting from IMP-001 Section 10. List the untested scenarios: DST-transition days on the API side, and the entire chip overdue check on the UI side, plus day boundaries and negative/zero/positive UTC offsets for both.

**Rationale:**
Refactoring may only begin from a documented, passing baseline; the v1.2.4 incident proves drift in exactly this logic goes unnoticed without one (IMP-001 Sections 3 and 10).

**Acceptance Criteria:**
- [ ] Coverage for the `src/api/tasks.ts` overdue filter and the `src/ui/project-board.tsx` chip check is measured and documented
- [ ] Coverage gaps are listed (DST transitions, day boundaries, UTC-8/UTC/UTC+13 offsets, all chip-styling scenarios)
- [ ] All existing tests pass before any refactoring begins

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-coverage-baseline.md (new) - baseline coverage notes and gap list

### T-002: Add API characterization tests for overdue-filter timezone edge cases

**Type:** Testing
**Workflow:** standard

**Description:**
Extend `tests/api/tasks.test.ts` with characterization tests that lock in the current `filter=overdue` behavior of `GET /api/v1/projects/{projectId}/tasks` for the gaps identified in T-001: instants just before and after local midnight, DST spring-forward and fall-back transition days, and negative/zero/positive offsets exercised via the `tz` parameter. Expectations must encode current behavior, not desired behavior.

**Rationale:**
IMP-001 Section 7 requires characterization tests to lock current behavior in before any restructuring; Section 10 flags DST-transition cases as missing on the API side.

**Acceptance Criteria:**
- [ ] `filter=overdue` is covered for day-boundary instants immediately before and after local midnight of the day following the due date
- [ ] DST spring-forward and fall-back transition days are covered
- [ ] UTC-8, UTC (default `tz`), and UTC+13 zones are covered via the `tz` parameter
- [ ] All new tests pass against the current (pre-refactoring) implementation

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add overdue-filter timezone/DST characterization tests

**Technical Notes:**
- Overdue rule under test: due date has fully passed in the requesting user's timezone AND status is not `done` (docs/api-spec/endpoints/tasks.md)
- `due_date` is stored as 00:00:00 UTC of the picked calendar date — date-only semantics (docs/data-model/entities/task.md)
- Keep the existing v1.2.4 regression test untouched; new cases sit alongside it

### T-003: Add UI characterization tests for the due-date chip overdue check

**Type:** Testing
**Workflow:** standard

**Description:**
Create component tests for `src/ui/project-board.tsx` that lock in the current TaskCard due-date chip behavior: the chip switches to the `error` color once the due date has passed in the browser's local timezone. Control the test clock and timezone to cover day boundaries, DST transition days, and negative/zero/positive UTC offsets.

**Rationale:**
IMP-001 Section 10 identifies the chip check as entirely untested — the biggest gap that must be closed before the refactoring touches this code.

**Acceptance Criteria:**
- [ ] Chip renders `error` styling only from 00:00 local time of the day after the due date, and default styling before that
- [ ] Day-boundary, DST-transition, and UTC-8/UTC/UTC+13 cases are covered
- [ ] All new tests pass against the current (pre-refactoring) implementation

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/project-board.test.tsx (new) - due-date chip overdue-styling characterization tests

**Technical Notes:**
- Use Vitest fake timers plus a controlled `TZ`/mocked zone to make browser-local "today" deterministic
- Assert against the chip styling contract in docs/ui-specification/components.md (TaskCard) — the contract itself must not change

---

## Phase 1: Safe Parallel Implementation

### T-004: Create shared date module src/lib/dates.ts alongside the inline copies

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/lib/dates.ts` exporting `toUserLocalDate(instant, tz)` and `isOverdue(dueDate, tz, now)`, implementing the overdue rule from `docs/data-model/entities/task.md` with plain `Date`/`Intl` only. Do not modify `src/api/tasks.ts` or `src/ui/project-board.tsx` — both inline copies keep running unchanged.

**Rationale:**
Establishes the single source of truth that resolves the duplicated business rule (IMP-001 Section 3, Problem 1) without touching either consumer, per the strangler-fig coexistence strategy.

**Acceptance Criteria:**
- [ ] `src/lib/dates.ts` exports `toUserLocalDate` and `isOverdue` implementing "overdue from 00:00 local time of the day after the due date"
- [ ] Module is dependency-free plain TypeScript — no date libraries, no DOM or framework imports — and compiles in both the backend and frontend builds
- [ ] All existing code and tests are unchanged and green

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/lib/dates.ts (new) - shared date-only helpers (toUserLocalDate, isOverdue)

**Technical Notes:**
- Approach: derive the user-local calendar date via `Intl.DateTimeFormat` in the given IANA zone; a task is overdue when the local date of `now` is strictly after the due date's calendar date
- Coexistence strategy: the module ships unreferenced; both inline copies remain authoritative until Phase 2 migrates them one at a time
- Guard against IMP-001 Section 7 Risk 3: no `pg`, Express, React, or DOM types anywhere in the module

### T-005: Add unit tests for the shared date module

**Type:** Testing
**Workflow:** standard

**Description:**
Add `tests/lib/dates.test.ts` exercising `toUserLocalDate` and `isOverdue` directly against the IMP-001 Section 9 matrix: day boundaries, DST spring-forward/fall-back transitions, and negative/zero/positive UTC offsets. Expected values must agree with the behavior locked in by the T-002 and T-003 characterization tests.

**Rationale:**
Makes the edge cases fast unit tests instead of full API round-trips (IMP-001 Section 4) and mitigates Section 7 Risk 2 — the shared implementation diverging from either original copy.

**Acceptance Criteria:**
- [ ] Day-boundary cases (instants just before/after local midnight) resolve to the correct local calendar date and overdue verdict
- [ ] DST spring-forward and fall-back transition days produce verdicts identical to the characterization-test expectations
- [ ] UTC-8, UTC, and UTC+13 are covered for both `toUserLocalDate` and `isOverdue`
- [ ] All module tests pass with no changes to existing test expectations

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/lib/dates.test.ts (new) - unit tests for toUserLocalDate and isOverdue

---

## Phase 2: Migration

### T-006: Migrate the API overdue filter to the shared module

**Type:** Backend
**Workflow:** standard

**Description:**
Switch `src/api/tasks.ts` to derive the user-local "today" for the `filter=overdue` predicate from `src/lib/dates.ts` instead of its inline copy. Leave the old inline helper in place, unreferenced, for easy rollback; API responses must be byte-for-byte identical.

**Rationale:**
Migrates the first consumer — the server-side copy whose drift shipped the v1.2.4 overdue-filter incident (IMP-001 Section 3, Problem 2).

**Acceptance Criteria:**
- [ ] The `filter=overdue` derivation flows through `src/lib/dates.ts`
- [ ] All API tests pass unchanged, including the T-002 characterization tests and the existing v1.2.4 regression test
- [ ] The old inline helper remains present but unreferenced (removal deferred to Phase 3)

**Dependencies:** T-002, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - replace inline date derivation at the overdue-filter call site with imports from src/lib/dates.ts

**Technical Notes:**
- Migration steps: import the module → swap the derivation at the single call site → run the full API suite → diff responses for byte-for-byte equality
- Rollback plan: a single-commit `git revert` restores the inline behavior without touching the UI consumer (IMP-001 Section 7 rollback strategy)

### T-007: Migrate the Project Board chip check to the shared module

**Type:** Frontend
**Workflow:** standard

**Description:**
Switch `src/ui/project-board.tsx` to compute the TaskCard due-date chip's overdue state via `isOverdue` from `src/lib/dates.ts`, passing the browser zone. Leave the old inline check in place, unreferenced; chip styling and the TaskCard contract must be unchanged.

**Rationale:**
Migrates the second consumer so the filter and the chip share one rule and cannot disagree by construction (IMP-001 Section 4, Benefit 1).

**Acceptance Criteria:**
- [ ] The chip overdue state is computed via `src/lib/dates.ts`
- [ ] The T-003 characterization tests pass unchanged
- [ ] The old inline check remains present but unreferenced (removal deferred to Phase 3)
- [ ] The TaskCard inputs and chip styling contract in docs/ui-specification/components.md are unchanged

**Dependencies:** T-003, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - replace inline chip overdue check with isOverdue from src/lib/dates.ts

**Technical Notes:**
- Pass the browser zone (`Intl.DateTimeFormat().resolvedOptions().timeZone`) — the same value the SPA already sends as `tz` to the API, so both consumers evaluate the same rule with the same zone
- Rollback plan: a single-commit `git revert` restores the inline check without touching the API consumer

---

## Phase 3: Cleanup

### T-008: Remove old inline date helpers from both call sites

**Type:** Cleanup
**Workflow:** standard

**Description:**
Delete the now-unreferenced inline date parsing, "today in timezone" derivation, and comparison helpers from `src/api/tasks.ts` and `src/ui/project-board.tsx`. Search the codebase to confirm no remaining references to the removed helpers.

**Rationale:**
Both call sites have migrated and been verified (T-006, T-007), so per the IMP-001 Section 7 rollback strategy the coexistence window can close; leaving dead copies invites exactly the drift this improvement exists to end.

**Acceptance Criteria:**
- [ ] No inline date-comparison helper remains in `src/api/tasks.ts` or `src/ui/project-board.tsx` (IMP-001 Section 9)
- [ ] No dead code or commented-out old code is left behind
- [ ] Build succeeds for both backend and frontend
- [ ] All tests pass

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - delete the unused inline date helper and any now-unused imports
- src/ui/project-board.tsx - delete the unused inline overdue check and any now-unused imports

---

## Phase 4: Verification

### T-009: Update CLAUDE.md project structure for src/lib/

**Type:** Documentation
**Workflow:** standard

**Description:**
Add a `src/lib/` row to the CLAUDE.md Project Structure table describing shared dependency-free modules consumed by both backend and frontend, with `src/lib/dates.ts` as the first occupant. Per IMP-001 Section 6, no spec shards change — this improvement moved code, not contracts.

**Rationale:**
IMP-001 Section 11 notes shared code under `src/lib/` is new to the architecture reference; documenting it keeps future task generation routed to the shared module instead of adding a third copy.

**Acceptance Criteria:**
- [ ] CLAUDE.md Project Structure table includes `src/lib/` with its purpose
- [ ] No spec shard under docs/ is modified (contracts unchanged per IMP-001 Section 6)

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- CLAUDE.md - add src/lib/ row to the Project Structure table

### T-010: Run final verification of the extraction

**Type:** Testing
**Workflow:** standard

**Description:**
Run the full verification pass: the entire original suite plus the new tests from T-002/T-003/T-005, type-check and lint across both builds, and an explicit check of every IMP-001 Section 9 success criterion. Record the verification outcome against the proposal.

**Rationale:**
Closes the refactoring with evidence that behavior is preserved end to end — the confidence the v1.2.4 post-mortem action item asked for.

**Acceptance Criteria:**
- [ ] All original tests pass with no changes to existing test expectations (IMP-001 Section 9)
- [ ] All new tests (T-002, T-003, T-005) pass
- [ ] Exactly one overdue/date-only implementation exists, in `src/lib/dates.ts`, imported by both `src/api/tasks.ts` and `src/ui/project-board.tsx`
- [ ] No type or lint errors in the backend or frontend builds
- [ ] Documentation updated (T-009) and a walkthrough of the final diff completed

**Dependencies:** T-008, T-009
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/IMP-001-extract-date-logic.md - record Section 9 verification outcome and completion status

---

## Summary

**Improvement Proposal:** IMP-001 — Extract Shared Date Logic (traceability per Section 12).

**Total tasks by phase:**

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 0 — Preparation (Safety Net) | T-001, T-002, T-003 | 3 |
| Phase 1 — Safe Parallel Implementation | T-004, T-005 | 2 |
| Phase 2 — Migration | T-006, T-007 | 2 |
| Phase 3 — Cleanup | T-008 | 1 |
| Phase 4 — Verification | T-009, T-010 | 2 |
| **Total** | | **10** |

**Critical path and sequence:** T-001 → (T-002 ∥ T-003) → T-004 → T-005 → (T-006 ∥ T-007) → T-008 → T-009 → T-010. The two characterization tasks can run in parallel after the baseline, and the two migrations can run in parallel after the module's unit tests pass; everything else is sequential.

**Risk assessment (from IMP-001 Section 7):**
- *Behavior drift during migration* (Medium/High) — mitigated by characterization tests before restructuring (T-002, T-003), one call site per migration task (T-006, T-007), and coexistence of old and new until cleanup (T-008).
- *Timezone/DST divergence in the shared implementation* (Medium/Medium) — mitigated by the edge-case matrix written against current behavior first (T-002, T-003) and required to hold for the module (T-005).
- *Shared module growing server-only or DOM dependencies* (Low/Medium) — mitigated by the dependency-free acceptance criterion in T-004 and both builds compiling the module (T-004, T-010).

**Recommended review points:**
1. After Phase 0 (T-003): baseline documented, all gaps closed, suite green — approve before any restructuring.
2. After T-005: module unit tests agree with characterization expectations — approve before touching consumers.
3. After each migration (T-006, T-007): full suite green, responses/styling verified identical — each is an independently releasable checkpoint.
4. Before T-008: confirm both call sites are migrated and verified before deleting the old helpers.

**Rollback strategy summary:** Old inline helpers stay in place until Phase 3, so each migration commit is independently revertible with `git revert` — reverting one call-site migration restores its previous inline behavior without touching the other consumer. Cleanup (T-008) happens only after both call sites are migrated and verified (IMP-001 Section 7).

---

## Acceptance Criteria Coverage

IMP-001 defines success criteria (Section 9) rather than a checkbox acceptance-criteria list; each criterion maps to tasks as follows.

| Work Item AC | Covered By |
|--------------|------------|
| SC-1: Exactly one implementation of the overdue/date-only comparison exists, in `src/lib/dates.ts` | T-004, T-008, T-010 |
| SC-2: `src/api/tasks.ts` and `src/ui/project-board.tsx` both import it; no inline date-comparison helper remains in either file | T-006, T-007, T-008 |
| SC-3: The shared module has unit tests covering day boundaries, DST transitions, and negative/zero/positive UTC offsets | T-005 |
| SC-4: Full test suite passes with no changes to existing test expectations | T-002, T-003, T-010 |
