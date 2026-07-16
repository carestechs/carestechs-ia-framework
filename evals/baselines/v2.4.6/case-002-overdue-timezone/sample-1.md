# BUG-001 — Bug Fix Tasks: Overdue Filter Shows Wrong Tasks Across Timezones

> Generated from `docs/work-items/BUG-001-overdue-filter-timezone.md` (Status: Reported, Severity: Medium). Investigation tasks establish the root cause before any fix; fix tasks address the confirmed root cause; verification tasks add the tests that would have caught this bug plus its boundary conditions. All file paths are relative to the project root.

---

## Phase 1: Investigation

### T-001: Reproduce the overdue filter bug and capture live evidence

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Reproduce BUG-001 using the exact steps from bug report Section 2 (task due today, browser timezone `America/Los_Angeles`, local time past 16:00). Capture the request URL with `filter=overdue&tz=America/Los_Angeles`, the JSON response, and the SQL emitted for the board list query with query logging enabled.

**Rationale:**
The bug report requires the first investigation task to verify reproducibility (Section 11, note 4); a fresh capture confirms the Section 5 evidence still holds on the current build before any code changes.

**Acceptance Criteria:**
- [ ] Bug reproduced on the current build following Section 2 exactly, or the failure to reproduce is documented with details
- [ ] Request capture shows `tz` arriving valid and intact at the API, re-confirming the client-to-API leg of the contract
- [ ] The SQL emitted for the overdue filter is captured verbatim from the query log
- [ ] Findings documented: what was confirmed, what was ruled out

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - confirm this router serves the captured request and note where `tz` is validated
- docs/work-items/BUG-001-overdue-filter-timezone.md - record reproduction findings in Section 6 (Observations)

**Technical Notes:**
- Investigation steps: create a task due today → advance local time past 16:00 (UTC-8) → select "Overdue" on the Project Board → capture request, response, and emitted SQL
- Expected findings: the task appears in Overdue while still due today locally, matching the Section 5 evidence

---

### T-002: Verify the date/timezone contract empirically against PostgreSQL and stored data

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Verify against a real PostgreSQL 16 instance and real rows how each piece of the overdue comparison actually behaves: how `due_date` values are stored for picked calendar dates, in which timezone `CURRENT_DATE` and `timestamptz::date` casts evaluate under the API's connection settings, and how a timezone-aware form (e.g. `now() AT TIME ZONE <iana-zone>`) behaves, including on DST-transition days. Do not trust spec shards or code comments — run the expressions and record actual output.

**Rationale:**
The bug crosses the API-to-database boundary, so the contract must be verified empirically against the producer — PostgreSQL's actual evaluation semantics and the actually-stored rows — rather than against documentation that may mirror the same wrong assumption.

**Acceptance Criteria:**
- [ ] Actual stored `due_date` values sampled and compared to the date-only semantics documented in `docs/data-model/entities/task.md`
- [ ] Session timezone of the API's database connections determined, and the evaluation of `CURRENT_DATE` and `due_date::date` under it demonstrated with real queries
- [ ] A timezone-correct comparison form validated empirically for UTC-8, UTC+1, UTC default, and a DST-transition day, with results recorded
- [ ] Findings documented: what was confirmed, what was ruled out

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - the predicate whose emitted SQL is under test (pair with the T-001 capture)
- migrations/001-init.sql - confirm the `tasks.due_date` column definition backing the stored semantics
- docs/work-items/BUG-001-overdue-filter-timezone.md - record contract findings in Section 6 (Observations)

**Technical Notes:**
- Investigation steps: in psql against staging or a seeded test database, run the captured predicate and candidate timezone-aware forms side by side with known due dates
- Expected findings: `CURRENT_DATE` evaluates in the connection's (UTC) timezone, so the predicate compares against the UTC day; an `AT TIME ZONE <tz>` form yields the user's local date
- Also probe invalid IANA names (e.g. `AT TIME ZONE 'not-a-zone'`) and record the raised error, to inform validation hardening in Phase 2

---

### T-003: Trace the tz parameter path through router and repository to identify the root cause

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Read the board list route in `src/api/tasks.ts` and the overdue predicate construction in `src/db/task.ts`, tracing the validated `tz` value from request parsing to SQL parameters. Confirm or refute the Section 6 hypothesis that `tz` is validated but never passed into the predicate, and pin down the precise root cause. Audit the rest of `src/db/` for other date-only comparisons with the same flaw.

**Rationale:**
Fix tasks must address a confirmed root cause, not the symptom; the Section 6 hypothesis is explicitly pre-investigation and unconfirmed, and Section 10 of the bug report is deliberately unfilled.

**Acceptance Criteria:**
- [ ] Root cause identified with the exact code path (file, function, predicate) documented, or the hypothesis refuted with evidence
- [ ] Confirmed whether the validated `tz` value is used anywhere after validation in the route handler
- [ ] `src/db/` audited for other predicates comparing dates against `CURRENT_DATE` or the UTC day; results listed even if empty
- [ ] Findings documented: what was confirmed, what was ruled out

**Dependencies:** T-001, T-002
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - locate the `tz` Zod validation and what the route actually passes to the repository
- src/db/task.ts - locate the overdue predicate construction and its bound parameters
- src/db/project.ts - audit for similar date comparisons sharing the flaw
- docs/work-items/BUG-001-overdue-filter-timezone.md - record the confirmed root cause in Section 6 (Observations)

**Technical Notes:**
- Investigation steps: follow the call chain route handler → repository function → SQL string and parameter list; diff against the SQL captured in T-001
- Expected findings: the repository builds `due_date::date < CURRENT_DATE` with no timezone parameter, per the Section 5 log
- Section 10 of the bug report stays as placeholders until resolution (T-009); interim findings belong in Section 6

---

## Phase 2: Implementation

### T-004: Implement a timezone-aware overdue predicate in the task repository

**Type:** Backend
**Workflow:** standard

**Description:**
Change the overdue predicate in `src/db/task.ts` to compare the task's stored calendar date against the current date in the requesting user's timezone, taking the IANA zone as a function parameter defaulting to `UTC`. Apply the same predicate to both the page query and the `totalCount` computation so the `meta` envelope stays consistent.

**Rationale:**
Addresses the root cause confirmed in T-003 — the predicate evaluates the UTC calendar day and ignores the user's timezone, violating the overdue business rule in `docs/data-model/entities/task.md` and FEAT-003 AC-2.

**Acceptance Criteria:**
- [ ] Overdue predicate uses the timezone-aware comparison form validated in T-002, with `tz` bound as a query parameter (no string interpolation)
- [ ] A task due "today" in the user's timezone is not returned as overdue at any local time on that day
- [ ] Tasks with `status = 'done'` remain excluded, and `meta.totalCount` matches the filtered set
- [ ] Behavior with `tz` omitted matches the documented `UTC` default

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - accept a timezone parameter and build the timezone-aware overdue comparison

**Technical Notes:**
- Root cause addressed: predicate previously compared `due_date::date < CURRENT_DATE` (UTC day); it now derives "today" from the caller's zone
- Implementation approach: use the exact SQL form validated empirically in T-002 (comparing the stored UTC calendar date of `due_date` to the user's local current date); SQL stays in the repository per CLAUDE.md
- Consider accepting an injectable reference time ("now") so boundary tests in T-006 are deterministic instead of wall-clock dependent
- Regression risk: positive-offset users (e.g. Berlin) will see tasks flip to overdue earlier than before — correct per spec, but worth noting in release notes; verify ordering and pagination are unchanged

---

### T-005: Pass the validated tz from the board list route into the repository and reject invalid zones

**Type:** Backend
**Workflow:** standard

**Description:**
Wire the validated `tz` query parameter in `src/api/tasks.ts` into the repository call for `filter=overdue`, defaulting to `UTC` when absent. Strengthen the Zod validation so a non-IANA zone name fails with the `validation-error` catalog code instead of reaching SQL.

**Rationale:**
The root cause includes the router discarding the validated value; now that `tz` is load-bearing, an invalid zone must produce a clear 400 rather than a database runtime error (error-handling clarity constraint).

**Acceptance Criteria:**
- [ ] The repository overdue call receives exactly the validated `tz` value (or the `UTC` default)
- [ ] Invalid `tz` values return 400 with the `validation-error` code and a `fields` entry for `tz`
- [ ] Response envelope and status codes remain as documented in `docs/api-spec/endpoints/tasks.md`
- [ ] Bug no longer reproducible with the original Section 2 steps

**Dependencies:** T-004
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - pass `tz` through to the repository; harden the Zod schema's IANA-zone check

**Technical Notes:**
- Root cause addressed: closes the gap between validating `tz` and actually using it
- Implementation approach: validate the zone against the runtime's IANA support (e.g. an Intl-based check) inside the existing Zod schema; existing `validation-error` catalog row covers it — no new error codes
- Regression risk: previously-accepted garbage `tz` values now 400 — the SPA only ever sends the browser zone per `docs/ui-specification/screens/project-board.md`, so no client change is expected

---

## Phase 3: Verification & Prevention

### T-006: Add repository unit tests for the overdue predicate across timezones

**Type:** Testing
**Workflow:** standard

**Description:**
Create repository unit tests against the test database covering the overdue predicate's timezone behavior, including the exact bug scenario from Section 2 and the boundary conditions of the overdue rule.

**Rationale:**
This bug shipped because no test exercised the `tz` parameter's effect on the predicate; these tests would have caught it and now guard the 00:00-local boundary semantics.

**Acceptance Criteria:**
- [ ] Exact bug scenario covered: task due "today", evaluated after 00:00 UTC of the next day but before 00:00 local next day in `America/Los_Angeles` → not overdue
- [ ] Boundary covered: a task becomes overdue at 00:00 local time of the day after its due date, and not one moment before
- [ ] Positive-offset (`Europe/Berlin`), `UTC` default, DST-transition day, and null `due_date` cases covered
- [ ] `done`-status exclusion covered; full test suite passes — no regressions introduced by the fix

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/db/task.test.ts (new) - unit tests for the overdue predicate's timezone behavior

**Technical Notes:**
- Test cases: drive the boundary cases through the injectable reference time from T-004 rather than the wall clock, so tests are deterministic
- Verification steps: run with Vitest against the test database per the CLAUDE.md repository-test convention

---

### T-007: Add API integration tests for filter=overdue with tz

**Type:** Testing
**Workflow:** standard

**Description:**
Extend the Supertest integration tests for the tasks router to cover `GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=...` end to end, including validation failures.

**Rationale:**
The router previously validated `tz` and then dropped it — only an API-level test proves the parameter actually affects the result set; repository tests alone cannot catch a dropped parameter.

**Acceptance Criteria:**
- [ ] Integration test reproduces the Section 2 scenario through the HTTP layer and asserts the task is absent from Overdue results
- [ ] A task genuinely overdue in the given `tz` is returned, with correct `meta.totalCount`
- [ ] Invalid `tz` returns 400 `validation-error`; omitted `tz` behaves as `UTC`
- [ ] Full test suite passes — no regressions introduced by the fix

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add overdue-with-tz integration cases to the existing router suite

**Technical Notes:**
- Test cases: exact bug scenario via HTTP; overdue-in-tz positive case; invalid `tz`; omitted `tz`
- Verification steps: run the Supertest suite against the test database

---

### T-008: Verify the fix end-to-end against the original report

**Type:** Testing
**Workflow:** standard

**Description:**
Re-run the exact Section 2 reproduction steps on a deployed build (staging) with browser timezone `America/Los_Angeles`, confirming the Overdue filter and the card's due-date chip now agree on the same screen. Run the complete test suite once more on the final merged state.

**Rationale:**
Unit and integration tests use synthetic clocks and fixtures; a final pass on the real stack confirms the user-visible symptom reported by the pilot team is gone before the bug is closed.

**Acceptance Criteria:**
- [ ] Section 2 steps no longer reproduce the bug on staging
- [ ] Board filter and card due-date chip agree for a UTC-8 user during the 16:00–23:59 local window
- [ ] Full test suite green on the final state

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - append verification evidence to Section 6 (Observations)

**Technical Notes:**
- Verification steps: repeat Section 2 preconditions and steps 1–4 verbatim; capture a screenshot mirroring `attachments/bug-001-board.png` showing the corrected state

---

### T-009: Close out BUG-001 — fill Root Cause & Resolution and set Status to Resolved

**Type:** Documentation
**Workflow:** standard

**Description:**
Fill bug report Section 10 with the confirmed root cause, fix summary, and fixed-in version, and change the Status field from Reported to Resolved.

**Rationale:**
Section 10 closes the loop so future investigations of similar symptoms start from the confirmed cause, and it feeds regression-test generation (bug report Section 11, note 9).

**Acceptance Criteria:**
- [ ] Section 10 Root Cause, Fix Summary, and Fixed In filled with verified facts from T-003 and T-008
- [ ] Status updated to Resolved
- [ ] Traceability preserved: FEAT-003 AC-2 noted as satisfied again

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - complete Section 10 and update the Status field

---

## Summary — BUG-001

- **Most likely root cause hypothesis:** The board list route in `src/api/tasks.ts` validates the `tz` query parameter but never passes it to the repository; the overdue predicate in `src/db/task.ts` compares `due_date::date < CURRENT_DATE`, which evaluates on the database's UTC calendar day, so tasks flip to overdue when UTC rolls over rather than at 00:00 in the user's timezone. To be confirmed or refuted by T-001–T-003.
- **Confidence level in diagnosis:** High — the Section 5 query log shows the exact predicate and notes the validated `tz` is never bound, and the network capture proves `tz` arrives intact — but Status is Reported and Section 10 is unfilled, so the fix tasks are gated on investigation confirming it.
- **Risk assessment of proposed fix:** Low-to-medium. The change is read-time filtering only (no data migration or backfill), confined to one predicate and one router wire-up. Main risks: timezone/DST edge cases in the SQL comparison (mitigated by T-002's empirical validation and T-006's boundary tests) and a behavior shift for positive-offset users, who will now see tasks become overdue at their local midnight — earlier than the UTC rollover they see today, which is the spec-correct behavior.
- **Monitoring recommendations post-fix:** Log the effective `tz` alongside each `filter=overdue` query (extending the existing query logging) and count `validation-error` responses on `tz` to spot clients sending bad zones; watch pilot-team feedback channels for lateness complaints from both negative- and positive-offset teams for a couple of weeks after release.
- **Related areas to audit for similar issues:** Other date comparisons in `src/db/` repositories (covered by T-003's audit, e.g. `src/db/project.ts`); the client-side due-date chip logic in `src/ui/components/task-card.tsx`, which computes overdue from the browser clock and must stay consistent with the server rule; any future feature that reuses the overdue predicate (per Section 8 the board filter is currently its only consumer) — e.g. digests or notifications — should take the user's zone as an explicit input.

*No Acceptance Criteria Coverage table: BUG-001 defines no acceptance-criteria checklist; the violated criterion (FEAT-003 AC-2) is covered by T-006 and T-007.*
