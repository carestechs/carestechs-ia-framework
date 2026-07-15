# Task List: BUG-001 Overdue Filter Shows Wrong Tasks Across Timezones

## Phase 1: Investigation

### T-001: Reproduce BUG-001 and trace `tz` from the router to the failing predicate

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Reproduce the bug exactly as reported (browser timezone `America/Los_Angeles`, task due today, request after 16:00 local = 00:00 UTC next day), then follow the `filter=overdue` request from the Zod validation in `src/api/tasks.ts` through the repository call into the executed SQL, and pinpoint the file/line where the validated `tz` value stops influencing the result.

**Rationale:**
The bug's Status is Reported and Section 10 is deliberately unfilled — the Section 6 hypothesis (the predicate compares `due_date::date` against UTC `CURRENT_DATE` and `tz` is dropped between router and repository) is unconfirmed and must be proven or refuted with evidence before any fix is written.

**Acceptance Criteria:**
- [ ] Bug reproduced on a test environment following the Section 2 steps (clock offset or frozen time acceptable)
- [ ] The SQL actually executed for `filter=overdue` captured and diffed against the overdue rule in `docs/data-model/entities/task.md`
- [ ] The exact point where `tz` is dropped identified (file/line) — or the hypothesis refuted and the real cause documented with evidence
- [ ] Findings recorded as a draft of the bug report's Section 10 (root-cause candidate plus supporting evidence)

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - trace how the board list route validates `filter` and `tz` and what it forwards to the repository
- src/db/task.ts - inspect the overdue predicate (Section 5 log shows `due_date::date < CURRENT_DATE`)
- docs/work-items/BUG-001-overdue-filter-timezone.md - record investigation findings as a Section 10 draft

**Technical Notes:**
- Replay the Section 5 network capture verbatim (`GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=America%2FLos_Angeles`) with query logging enabled — the capture already proves `tz` arrives intact, so the defect is internal to the app
- Expected finding per the evidence: the router validates `tz` but never passes it into the predicate, so the comparison runs on the database's UTC day

### T-002: Audit remaining date comparisons for the UTC-day defect class

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Enumerate every place in the repositories and the board UI that compares `due_date` (or any date-only value) against a "today", and classify each occurrence as sharing the confirmed root cause, a separate defect, or correct — documenting findings without rewriting any code.

**Rationale:**
A "today" computed in the wrong timezone is a defect class, not a single defect; any sibling comparison introduced with the v1.2 filters would share it, and the client-side card chip must be confirmed to implement the same spec rule the fixed filter will follow.

**Acceptance Criteria:**
- [ ] All date comparisons in `src/db/` and the board UI enumerated with file/line references
- [ ] Each occurrence classified (same root cause / different defect / correct) with a one-line justification
- [ ] The card chip check in `TaskCard` confirmed against the entity rule (overdue from 00:00 local of the day after the due date) — per `docs/ui-specification/components.md` it uses the browser's local date and is expected correct
- [ ] Findings appended to the bug report's Section 6 Observations; any unrelated defects filed separately, not fixed here

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- src/db/task.ts - other task queries touching `due_date`
- src/db/project.ts - confirm no date-based predicates exist in the project repository
- src/ui/components/task-card.tsx - the client-side due-date chip check
- src/ui/project-board.tsx - board screen usage of the filter and chip
- docs/work-items/BUG-001-overdue-filter-timezone.md - append audit results to Section 6

## Phase 2: Implementation

### T-003: Evaluate the overdue predicate against the user's local "today"

**Type:** Backend
**Workflow:** standard

**Description:**
Pass the validated `tz` from the board list route into the repository and derive the comparison date in that zone, so a task becomes overdue exactly at 00:00 local time of the day after its due date instead of at the UTC day roll-over.

**Rationale:**
Addresses the root cause confirmed by T-001 — the spec (overdue business rule in `docs/data-model/entities/task.md`, `tz` parameter contract in `docs/api-spec/endpoints/tasks.md`) requires the comparison in the requesting user's timezone; filtering rows client-side or adjusting the response would mask the symptom and leave the predicate wrong.

**Acceptance Criteria:**
- [ ] The Section 2 reproduction no longer shows the task as overdue at 18:14 PDT on its due date
- [ ] `tz` flows from the router into the repository predicate; the default `tz=UTC` behavior is unchanged; invalid zones still map to `validation-error`
- [ ] `status` filtering, board ordering, pagination, and the response envelope are unchanged
- [ ] No schema change, migration, or data backfill — stored `due_date` values are correct as-is

**Dependencies:** T-001, T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - overdue predicate compares against the user-local date (e.g. `due_date::date < (now() AT TIME ZONE $tz)::date`) instead of `CURRENT_DATE`
- src/api/tasks.ts - forward the validated `tz` to the repository call

**Technical Notes:**
- Keep the SQL inside the repository and pass the IANA zone as a bind parameter — routers never touch `pg` directly (CLAUDE.md conventions 4–5)
- Read-time predicate change only; Section 8 confirms no data impact, so no migration task
- Behavioral shift to flag: positive-offset users currently see tasks flip overdue *late*; after the fix their results change too (correctly) — covered by T-005's matrix

## Phase 3: Verification & Prevention

### T-004: Add regression tests for the reported scenario and the local day boundary

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest coverage that recreates the exact Section 2 scenario — task due today in `America/Los_Angeles`, request issued after 00:00 UTC of the next day — plus repository-level unit tests pinning the day-boundary instants in the user's timezone.

**Rationale:**
This bug shipped because nothing exercised `filter=overdue` with a non-UTC `tz`; a test replaying the reported request would have caught it at review time and now guards the fix against regression.

**Acceptance Criteria:**
- [ ] An integration test replaying the Section 5 captured request fails against the old predicate and passes with the fix
- [ ] Boundary conditions pinned: 23:59:59 local on the due date → not overdue; 00:00:00 local of the next day → overdue
- [ ] At least one positive-offset zone (e.g. `Europe/Berlin`) asserted, and `done` tasks are never returned by the filter
- [ ] Full Vitest suite passes with no regressions

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - overdue-filter timezone scenario and boundary cases against the board list route
- tests/db/task.test.ts (new) - repository unit tests for the overdue predicate per CLAUDE.md convention 6 (every repository gets a unit test)

**Technical Notes:**
- Freeze the clock (`vi.setSystemTime` or an injected `now`) and derive boundary instants from the IANA zone rather than hard-coded offsets, so DST transitions don't skew the cases

### T-005: Verify across timezones and close out BUG-001

**Type:** Testing
**Workflow:** standard

**Description:**
Run a timezone matrix (UTC-8, UTC, UTC+1, UTC+13, including a DST-observing zone) against the overdue filter and the unfiltered board list, confirm the board filter now agrees with the card chip on the same screen, then fill the bug report's Section 10 and move Status to Resolved.

**Rationale:**
The fix changes results for every non-UTC user in both offset directions, so verification must cover more than the reported UTC-8 case; filling Section 10 closes the loop so future investigations of similar symptoms start from the confirmed root cause.

**Acceptance Criteria:**
- [ ] Matrix passes for negative, zero, and positive offsets, including a date inside a DST transition window
- [ ] Unfiltered board list, `status` filter, and pagination behavior confirmed unchanged
- [ ] Staging spot-check with an `America/Los_Angeles` profile: the Overdue filter and the card's due-date chip agree
- [ ] Bug report Section 10 filled (Root Cause, Fix Summary, Fixed In) and Status set to Resolved

**Dependencies:** T-003, T-004
**Complexity:** S

**Files to Modify/Create:**
- tests/api/tasks.test.ts - timezone matrix cases alongside the T-004 regression tests
- docs/work-items/BUG-001-overdue-filter-timezone.md - fill Section 10 and set Status to Resolved

## Summary

- **Bug reference:** BUG-001 — "Overdue" board filter marks tasks overdue up to 8 hours early for users west of UTC (violates FEAT-003 AC-2).
- **Most likely root cause hypothesis:** the board list route in `src/api/tasks.ts` validates `tz` but the overdue predicate in `src/db/task.ts` compares `due_date::date` against UTC `CURRENT_DATE`, so tasks flip overdue at the UTC day roll-over instead of the user's — to be confirmed by T-001.
- **Confidence:** high — the Section 5 query log shows the UTC comparison and the network capture shows `tz` arriving intact, placing the defect inside the app's own predicate; no external contract is involved, so no producer-contract verification step is needed.
- **Fix risk:** low — a read-time predicate change with no stored-data impact; the main behavioral shift is for positive-offset users (tasks stop flipping overdue late), covered by T-005's matrix.
- **Monitoring:** log the resolved user-local date alongside `tz` on `filter=overdue` requests for one release; alert if `tz` parsing ever silently falls back to UTC.
- **Related areas to audit:** T-002 enumerates the remaining `due_date` comparisons in `src/db/` and confirms the client-side chip in `src/ui/components/task-card.tsx` matches the spec rule.
