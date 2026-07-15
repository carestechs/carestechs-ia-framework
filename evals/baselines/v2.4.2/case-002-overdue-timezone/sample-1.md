# Bug Fix Tasks: BUG-001 — Overdue Filter Shows Wrong Tasks Across Timezones

> **Work item:** `docs/work-items/BUG-001-overdue-filter-timezone.md` (Status: Reported, Severity: Medium)
> **Related feature:** FEAT-003 Board filters — violated AC-2: "a task appears in Overdue only after its due date has passed in the viewing user's timezone"
> **Generated:** 2026-07-15
>
> Tasks follow the bug-fix three-phase structure: investigation identifies the root cause before any fix work begins, the fix addresses that root cause, and verification adds tests that would have caught this exact bug. Phase order is enforced through Dependencies.

---

## Phase 1: Investigation

### T-001: Reproduce the bug with the report's exact steps

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Reproduce BUG-001 on a test or staging environment following Section 2 of the bug report: a task due today, browser timezone `America/Los_Angeles`, clock advanced past the UTC day rollover. Capture the request/response pair for `GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=America/Los_Angeles` to confirm the `tz` parameter arrives intact while the task is wrongly returned. Move the bug report Status from Reported to Investigating.

**Rationale:**
The bug report's usage notes require verifying reproducibility before any analysis; a repeatable reproduction anchors the root-cause work and every later fix-verification step.

**Acceptance Criteria:**
- [ ] Bug reproduced with the exact Section 2 steps; observed result matches Section 3 Actual Behavior
- [ ] Captured request shows a valid `tz` value while the response wrongly includes the task, matching the Section 5 evidence
- [ ] Reproduction details recorded in the bug report's Section 6 Observations and Status set to Investigating

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - record reproduction confirmation in Section 6; set Status to Investigating

**Technical Notes:**
- Investigation steps: create a task due today via the task detail panel; advance the environment clock past 00:00 UTC of the next day; request the board with `filter=overdue&tz=America/Los_Angeles`; repeat with a different `tz` value and compare
- Expected findings: the task appears in Overdue while its local date has not passed, and the result is identical regardless of the `tz` value sent — confirming `tz` has no effect
- America/Los_Angeles is UTC-7 (PDT) on July dates, so the flip occurs at 17:00 local; Section 2's 16:00 reflects the standard-time offset — note the observed boundary precisely

### T-002: Verify the date/timezone contract empirically against PostgreSQL

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Verify against a real PostgreSQL 16 instance how each piece of the overdue comparison actually behaves: how `due_date` values are stored (the spec claims 00:00:00 UTC date-only semantics), which timezone `CURRENT_DATE` and the `due_date::date` cast evaluate in under the API's session settings, and how `AT TIME ZONE` converts a `timestamptz` for a bound IANA zone parameter. Capture real rows and query outputs rather than trusting comments, the spec text, or the Section 6 hypothesis.

**Rationale:**
The comparison spans the API→PostgreSQL boundary; the producer's actual date-cast and session-timezone semantics must be confirmed empirically, or the fix risks encoding the same wrong assumption the current predicate does.

**Acceptance Criteria:**
- [ ] A real stored task row confirms or refutes the 00:00:00 UTC date-only storage of `due_date` documented in docs/data-model/entities/task.md
- [ ] The session timezone and the evaluated values of `CURRENT_DATE` and `due_date::date` are captured at a controlled instant
- [ ] A candidate SQL expression implementing "overdue from 00:00 local time of the day after the due date" is validated at boundary instants for one UTC-negative and one UTC-positive zone
- [ ] Findings documented in the bug report's Section 6 Observations

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- migrations/001-init.sql - confirm the column type backing `due_date`
- src/db/task.ts - identify the session/timezone assumptions the current predicate relies on
- docs/work-items/BUG-001-overdue-filter-timezone.md - record contract findings in Section 6

**Technical Notes:**
- Investigation steps: insert a task due 2026-07-12 through the API; SELECT `due_date`, `due_date::date`, `CURRENT_DATE`, and candidate expressions such as `(due_date AT TIME ZONE $tz)::date` at instants around 2026-07-13T07:00Z
- Expected findings: `CURRENT_DATE` evaluates in the connection's UTC session zone, so the predicate flips at UTC midnight regardless of the requester's zone
- Validate candidate expressions on a DST-transition date as well — IANA zone rules, not fixed offsets

### T-003: Trace the tz parameter flow and identify the root cause

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Trace the validated `tz` value from the Zod schema in `src/api/tasks.ts` through the repository call into the SQL built in `src/db/task.ts`, and pinpoint where it stops influencing the overdue predicate. Confirm or refute the Section 6 hypothesis that the router validates `tz` but the repository compares against UTC `CURRENT_DATE` without ever receiving it. Also record how an invalid `tz` value is handled today, including the response code and message clarity.

**Rationale:**
The fix must address a confirmed root cause, not the pre-investigation hypothesis or the symptom; the bug report's Section 10 is deliberately unfilled until this investigation concludes.

**Acceptance Criteria:**
- [ ] Root cause identified with the exact file and code path where the `tz` value is dropped or ignored — or the hypothesis refuted with evidence and the alternative cause documented
- [ ] Findings documented: what was confirmed, what was ruled out
- [ ] Current behavior for an invalid `tz` value recorded: response status, error catalog code, and whether the message is clear

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - examine the query-parameter Zod schema and what the board list handler passes to the repository
- src/db/task.ts - examine the overdue predicate construction and its bound parameters
- docs/work-items/BUG-001-overdue-filter-timezone.md - record the confirmed root cause evidence in Section 6

**Technical Notes:**
- Investigation steps: read the router's validation and handler; follow the repository function signature; diff the parameters actually bound to the SQL in the Section 5 log against what the route validated
- Expected findings: the repository's board list function has no timezone parameter, matching the Section 5 log note "the validated tz value is never passed into the predicate"

### T-004: Audit related code for other UTC-day date comparisons

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Search the codebase for other places that compare calendar days and could share the defect: additional `CURRENT_DATE` or `::date` usages in `src/db/`, server-side date logic in `src/api/`, and the client-side due-date chip in `src/ui/components/task-card.tsx` (reported correct — confirm it matches the spec rule). Confirm Section 8's claim that the board filter is the overdue predicate's only consumer.

**Rationale:**
Related areas may hide the same UTC-day comparison, and confirming the predicate's consumer list bounds the blast radius of the Phase 2 change before it is made.

**Acceptance Criteria:**
- [ ] All `CURRENT_DATE`, `::date`, and day-comparison sites under `src/` enumerated, each with a correct/defective verdict
- [ ] The overdue predicate's consumer list confirmed (expected: only the board list route)
- [ ] Chip logic in task-card.tsx confirmed consistent with the overdue rule in docs/data-model/entities/task.md, or a follow-up bug filed

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- src/db/task.ts - check for date predicates beyond the overdue filter
- src/db/project.ts - check for any date comparisons
- src/ui/components/task-card.tsx - confirm the client-side overdue chip computation
- docs/work-items/BUG-001-overdue-filter-timezone.md - record audit results in Section 6

**Technical Notes:**
- Expected findings: the overdue predicate is the only server-side calendar-day comparison; the chip computes from the browser-local date and already matches the rule

---

## Phase 2: Implementation

### T-005: Fix the overdue predicate to evaluate day boundaries in the requester's timezone

**Type:** Backend
**Workflow:** standard

**Description:**
Thread the validated `tz` value from the board list route in `src/api/tasks.ts` into the repository, and rewrite the overdue predicate in `src/db/task.ts` to compare calendar days in that zone using the expression validated in T-002 — converting both `due_date` and the current instant with the bound zone before the date comparison. Keep the documented default of UTC when `tz` is omitted, and leave the response envelope, pagination, ordering, and the `status <> 'done'` exclusion untouched.

**Rationale:**
Addresses the root cause confirmed by T-003 — the predicate evaluates the day boundary in UTC because the validated `tz` never reaches it — restoring FEAT-003 AC-2 and the overdue business rule in docs/data-model/entities/task.md.

**Acceptance Criteria:**
- [ ] The original Section 2 steps no longer reproduce the bug: a task due today in America/Los_Angeles is not returned as overdue before 00:00 local time of the following day
- [ ] A task becomes overdue starting exactly at 00:00 local time of the day after its due date, for both a UTC-negative and a UTC-positive `tz`
- [ ] Omitting `tz` preserves UTC behavior; done tasks and tasks with no due date remain excluded
- [ ] Invalid `tz` values are rejected with the `validation-error` catalog entry before any SQL runs, and `tz` reaches the query only as a bind parameter

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - accept a timezone argument and rewrite the overdue predicate to compare local calendar days
- src/api/tasks.ts - pass the validated `tz` through to the repository; tighten `tz` validation if T-003 found it lax

**Technical Notes:**
- Root cause addressed: the `tz` value validated by the router is now bound into the predicate, replacing the UTC `CURRENT_DATE` comparison
- Implementation approach: use the exact SQL expression proven against PostgreSQL 16 in T-002; never interpolate `tz` into the SQL text
- Regression risk: UTC-positive users will now correctly see tasks flip overdue at their local midnight — earlier than the old UTC behavior; covered by the T-006/T-007 boundary tests and the full-suite run in T-008

---

## Phase 3: Verification & Prevention

### T-006: Add repository boundary tests for the overdue predicate

**Type:** Testing
**Workflow:** standard

**Description:**
Create the missing repository unit test for `src/db/task.ts` against the test database, covering the overdue predicate across a timezone matrix and boundary instants. Include the exact BUG-001 scenario as a permanent regression case.

**Rationale:**
CLAUDE.md requires a unit test per repository, and this bug shipped precisely because no test pinned the day-boundary semantics of the overdue predicate.

**Acceptance Criteria:**
- [ ] Regression case exists and passes: a task due 2026-07-12 queried at 2026-07-13T01:14Z with `tz=America/Los_Angeles` is not overdue — and this case fails against the pre-fix predicate
- [ ] Boundary cases pass: instants just before and exactly at 00:00 local of the day after the due date, for a UTC-negative zone, a UTC-positive zone, and UTC itself
- [ ] Edge cases pass: null `due_date` is never overdue; `done` tasks are excluded; a DST-transition date behaves per IANA rules rather than a fixed offset

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- tests/db/task.test.ts (new) - overdue predicate unit tests with a controlled clock and timezone matrix

**Technical Notes:**
- Test cases: the exact Section 2/5 scenario; 2026-07-13T06:59:59Z vs 2026-07-13T07:00:00Z for America/Los_Angeles (PDT boundary); Europe/Berlin task due yesterday becoming overdue at 22:00Z, before UTC midnight; omitted `tz` defaulting to UTC
- Verification steps: run the new suite against the pre-fix predicate to confirm the regression case fails, then against the fix to confirm all cases pass

### T-007: Add API integration test reproducing BUG-001 end-to-end

**Type:** Testing
**Workflow:** standard

**Description:**
Extend the tasks router integration test to drive `GET /api/v1/projects/{projectId}/tasks` with `filter=overdue` and `tz` through Supertest under a frozen clock, asserting the enveloped response excludes and includes tasks at the correct local-midnight boundaries. Cover the omitted-`tz` and invalid-`tz` paths at the API surface.

**Rationale:**
The defect was only observable through the full route→repository path — validation succeeded while the result was wrong — so a router-level test is required in addition to T-006's repository tests.

**Acceptance Criteria:**
- [ ] Integration case reproducing Section 2/5 passes: a request at frozen 2026-07-13T01:14Z with `tz=America/Los_Angeles` omits a task due 2026-07-12, with the standard data/meta envelope
- [ ] The same task is returned once the frozen clock passes 00:00 local time of 2026-07-13
- [ ] Omitted `tz` falls back to UTC semantics, and `filter=overdue` continues to exclude `done` tasks
- [ ] An invalid `tz` returns 400 with error code `validation-error`

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add an overdue-filter timezone describe block with frozen-clock cases

**Technical Notes:**
- Test cases: the Section 2 scenario verbatim; the boundary flip at 2026-07-13T07:00:00Z; a `tz=Europe/Berlin` early-overdue case; `tz=Not/AZone` expecting `validation-error`
- Verification steps: confirm the Section 2 case fails on the pre-fix code, then run the full Vitest suite post-fix

### T-008: Verify the fix against the original report and run the full regression suite

**Type:** Testing
**Workflow:** standard

**Description:**
Re-run the exact Section 2 reproduction on a staging build with `America/Los_Angeles` and `America/New_York` browser zones, confirming the board's Overdue filter now agrees with the due-date chip on the same screen. Run the complete test suite to confirm nothing else regressed.

**Rationale:**
The fix must not break existing functionality, and the reported symptom was observed in two zones — both need re-checking in a real environment, not only in tests.

**Acceptance Criteria:**
- [ ] Section 2 steps on staging show the task absent from Overdue during the former failure window and present only after local midnight
- [ ] The due-date chip and the Overdue filter agree for the same task on the same screen
- [ ] The full Vitest suite (repository unit tests and Supertest integration tests) passes with no new failures

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - record verification evidence in Section 6

**Technical Notes:**
- Verification steps: repeat with `America/New_York` (formerly failing from 20:00 local per Section 4) and one positive-offset zone to confirm the corrected earlier-flip behavior

### T-009: Close out the bug report with root cause and resolution

**Type:** Documentation
**Workflow:** standard

**Description:**
Fill Section 10 (Root Cause & Resolution) of the bug report with the confirmed root cause, a fix summary, and the release the fix ships in, then set Status to Resolved. Cross-reference FEAT-003 AC-2 as restored.

**Rationale:**
The bug report's usage notes require resolution capture so future investigations of similar symptoms start from a documented root cause and the record feeds regression-test generation.

**Acceptance Criteria:**
- [ ] Section 10 fields (Root Cause, Fix Summary, Fixed In) filled with investigation-backed content, replacing all placeholders
- [ ] Status set to Resolved
- [ ] Traceability noted: FEAT-003 AC-2 satisfied by the fix and guarded by the T-006/T-007 tests

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - fill Section 10 and update Status to Resolved

## Summary

**Work item:** BUG-001 — Overdue board filter marks tasks overdue up to 8 hours early for users west of UTC.

- **Most likely root cause hypothesis:** The board list route in `src/api/tasks.ts` validates the `tz` query parameter, but the overdue predicate built in `src/db/task.ts` compares `due_date::date < CURRENT_DATE`, which evaluates in the connection's UTC session zone — the validated `tz` is never passed into the query, so the day boundary is UTC midnight for everyone. (Pre-investigation hypothesis from Section 6, to be confirmed or refuted by T-001–T-003.)
- **Confidence level:** High — the Section 5 staging query log shows the exact predicate and states the `tz` value is never bound, and the network capture proves `tz` arrives intact; confidence is pending empirical confirmation because Section 10 is deliberately unfilled and the tasks, not the report, perform the investigation.
- **Risk assessment of proposed fix:** Low-to-moderate. The change is read-time filtering only (no data migration, per Section 8), and T-004 confirms the predicate's only consumer is the board list route. The main behavioral side effect is intentional: UTC-positive users will start seeing tasks flip overdue at their local midnight, earlier than the old UTC rollover. Residual risks — invalid IANA zone names reaching SQL and DST boundaries — are covered by validation in T-005 and the boundary matrix in T-006/T-007.
- **Monitoring recommendations post-fix:** Log the `tz` value applied per `filter=overdue` query for a few weeks; alert on PostgreSQL "time zone not recognized" errors (should be zero if validation holds); track overdue-count discontinuities around UTC midnight, which would indicate the old behavior resurfacing.
- **Related areas to audit for similar issues:** All other `CURRENT_DATE`/`::date` day comparisons in `src/db/` and `src/api/` (T-004); the client-side due-date chip in `src/ui/components/task-card.tsx` and the due-date display in `src/ui/task-detail-panel.tsx`, which must stay consistent with the server rule; any future features that consume `due_date` (digests, notifications) must reuse the timezone-aware predicate rather than reintroducing a UTC-day comparison.
