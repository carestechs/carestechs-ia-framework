<!-- Known-good reference output — the judge check's anchor. Not a golden string to
     match verbatim; a demonstration of a decomposition that satisfies the rubric. -->

# Task List: BUG-001 Overdue Filter Shows Wrong Tasks Across Timezones

## Phase 1: Investigation

### T-001: Reproduce the overdue filter error and isolate the failing comparison

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Reproduce the bug with the report's exact steps (UTC-8 user, task due today, after 16:00 local), then trace the `filter=overdue` request from the router through the repository to the SQL predicate and pinpoint where the validated `tz` value stops mattering.

**Rationale:**
The bug report's Status is Reported and Section 10 is unfilled — the Section 6 hypothesis (predicate compares against UTC `CURRENT_DATE`, ignoring `tz`) must be confirmed or refuted before any fix.

**Acceptance Criteria:**
- [ ] Bug reproduced with the Section 2 steps on a test environment
- [ ] Root cause identified, or hypothesis documented with supporting evidence (the exact predicate and the point where `tz` is dropped)
- [ ] Findings documented in the bug report's Section 10 draft: what was confirmed, what was ruled out

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - how the board list route validates and forwards `filter` and `tz`
- src/db/task.ts - the overdue predicate the repository builds (Section 5 log shows `due_date::date < CURRENT_DATE`)
- docs/work-items/BUG-001-overdue-filter-timezone.md - record findings under Section 10

**Technical Notes:**
- Investigation steps: replay the captured request from Section 5; log the SQL actually executed; diff it against the overdue rule in docs/data-model/entities/task.md
- Expected findings: `tz` validated in the router but never passed to the repository, so the comparison runs on the server's UTC day

### T-002: Audit remaining date comparisons for the same UTC-day assumption

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Search the repositories and board UI for other places that compare `due_date` (or any date-only value) against a UTC "today", and document each occurrence as affected or clean.

**Rationale:**
A predicate built on the wrong "today" is a defect class, not a single defect — any sibling comparison added with the v1.2 filters would share it.

**Acceptance Criteria:**
- [ ] All date comparisons in `src/db/` and the board UI enumerated with file/line references
- [ ] Each occurrence classified: same root cause, different bug, or correct
- [ ] Findings appended to the bug report's Section 6 observations

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- src/db/task.ts - other task queries touching due_date
- src/db/project.ts - confirm no date-based predicates exist here
- src/ui/project-board.tsx - client-side chip check (expected correct; confirm it matches the spec rule)
- docs/work-items/BUG-001-overdue-filter-timezone.md - audit results

## Phase 2: Implementation

### T-003: Fix the overdue predicate to compare in the requesting user's timezone

**Type:** Backend
**Workflow:** standard

**Description:**
Compute "today" in the request's validated `tz` and compare `due_date::date` against that local date in the repository's overdue predicate, so a task becomes overdue at 00:00 local time of the day after its due date.

**Rationale:**
Addresses the root cause confirmed by T-001 — the predicate uses the database's UTC `CURRENT_DATE` while the spec (task entity overdue rule, `tz` parameter contract) requires the user's timezone.

**Acceptance Criteria:**
- [ ] Bug no longer reproducible with the original Section 2 steps
- [ ] `tz` flows from the router into the repository predicate; invalid zones still map to `validation-error`
- [ ] Behavior for `tz=UTC` (the default) is unchanged
- [ ] Bug report Section 10 filled in and Status moved to Resolved after verification

**Dependencies:** T-001, T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - overdue predicate takes the user-local "today" instead of `CURRENT_DATE`
- src/api/tasks.ts - pass the validated `tz` through to the repository call
- docs/work-items/BUG-001-overdue-filter-timezone.md - fill Root Cause & Resolution (Section 10)

**Technical Notes:**
- Root cause addressed: the comparison date, not the stored data — no migration or backfill
- Implementation approach: derive the local date server-side (e.g. `(now() AT TIME ZONE $tz)::date`) and keep SQL in the repository per CLAUDE.md convention 5
- Regression risk: positive-offset users currently see tasks flip overdue *late*; the fix changes their results too — cover in T-005

## Phase 3: Verification & Prevention

### T-004: Add regression test for the reported scenario and day-boundary dates

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest coverage that recreates the exact Section 2 scenario — task due "today" in `America/Los_Angeles`, request sent after 00:00 UTC of the next day — and pins the day boundary in the user's timezone.

**Rationale:**
This bug shipped because no test exercised `filter=overdue` with a non-UTC `tz`; this test would have caught it and guards the fix.

**Acceptance Criteria:**
- [ ] Test covering the exact bug scenario exists, fails against the old predicate, and passes with the fix
- [ ] Boundary cases covered: 23:59 local on the due date (not overdue) and 00:00 local the next day (overdue)
- [ ] Full test suite passes — no regressions introduced by the fix

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - overdue-filter timezone scenario and boundary cases with a frozen clock

**Technical Notes:**
- Test cases: the Section 5 captured request replayed verbatim; boundary instants generated from the tz, not hard-coded UTC offsets

### T-005: Verify the fix across timezones and confirm no filter regressions

**Type:** Testing
**Workflow:** standard

**Description:**
Run a timezone matrix (UTC-8, UTC, UTC+1, UTC+13) against the overdue filter and the unfiltered board list to confirm results match the spec rule everywhere and that `status` filtering and pagination are unaffected.

**Rationale:**
The fix changes results for every non-UTC user (east-of-UTC users were seeing tasks flip overdue late); verification must cover both offset directions, not just the reported one.

**Acceptance Criteria:**
- [ ] Matrix tests pass for negative, zero, and positive offsets, including a DST-observing zone
- [ ] Unfiltered board list, `status` filter, and pagination behavior unchanged
- [ ] Manual spot-check on staging with a UTC-8 profile matches the card chip

**Dependencies:** T-003, T-004
**Complexity:** S

**Files to Modify/Create:**
- tests/api/tasks.test.ts - timezone matrix cases alongside the regression test

## Summary

- **Most likely root cause hypothesis:** the board list route validates `tz` but the overdue predicate in `src/db/task.ts` compares `due_date::date` against UTC `CURRENT_DATE`, so the UTC day roll-over — not the user's — flips tasks to overdue (Section 5 log and network capture support this; T-001 confirms).
- **Confidence:** high — the captured SQL shows the UTC comparison and the captured request shows `tz` arriving intact, so the defect is internal to the predicate; no external contract is involved.
- **Fix risk:** low — read-time predicate change only, no stored data touched; the main behavioral shift is for positive-offset users, covered by T-005's matrix.
- **Monitoring:** log the resolved user-local date next to `tz` on `filter=overdue` requests for one release; alert if `tz` parsing ever falls back to UTC unexpectedly.
- **Related areas to audit:** T-002 covers the remaining `due_date` comparisons in `src/db/` and the client-side chip check in `src/ui/project-board.tsx` for drift from the spec rule.
