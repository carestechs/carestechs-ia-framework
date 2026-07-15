# BUG-001 — Bug Fix Tasks: Overdue Filter Shows Wrong Tasks Across Timezones

> Source work item: `docs/work-items/BUG-001-overdue-filter-timezone.md` (Severity: Medium, Status: Reported).
> Three-phase structure per the bugfix prompt: Investigation → Implementation → Verification & Prevention, enforced through Dependencies. The Section 6 hypothesis is treated as unconfirmed until Phase 1 completes.

---

## Phase 1: Investigation

### T-001: Reproduce BUG-001 and capture live request and query evidence

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Follow the Section 2 reproduction steps on staging (member login, browser timezone `America/Los_Angeles`, task due today, local clock past the UTC-day rollover) and confirm the task appears under the Overdue filter while its due date has not passed locally. Capture the live API request/response and the emitted SQL (query logging enabled), extending the Section 5 evidence.

**Rationale:**
Usage Note 4 of the bug report requires reproduction before any diagnosis; a fresh capture confirms the pilot-team report and the QA confirmation on the current build.

**Acceptance Criteria:**
- [ ] Bug reproduced per Section 2: task due "today" (local) listed as overdue during the 16:00–23:59 local window for a UTC-8 user
- [ ] Network capture shows the SPA sending a valid IANA `tz` value and the API returning the task in `data` despite it
- [ ] Query log capture shows the exact SQL predicate the API executed for `filter=overdue`
- [ ] Positive-offset check (e.g. `Europe/Berlin`) performed to confirm the filter errs in the opposite direction (overdue appears late), bounding the defect
- [ ] Findings recorded in the bug report's Section 6 (Observations)

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - append reproduction confirmation and captures to Section 6 Observations

**Technical Notes:**
- Investigation steps: set workstation clock or use a staging clock override to enter the local-evening window; select "Overdue" in the board filter dropdown; record the request, response, and logged SQL
- Expected findings: reproduction matches Section 5 — `tz` arrives intact, the returned task's `dueDate` has not passed in the requesting zone

### T-002: Verify the timezone contract empirically against the producers

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
This bug crosses system boundaries (SPA → API `tz` parameter → PostgreSQL date evaluation), so verify each contract against its producer rather than comments or fixtures. Confirm from real rows that `tasks.due_date` is stored as 00:00:00 UTC of the picked calendar date, and probe PostgreSQL 16 directly (psql) for the actual semantics of `CURRENT_DATE` (session-timezone dependent) and `AT TIME ZONE` conversions, cross-checked against the official PostgreSQL documentation.

**Rationale:**
The bugfix prompt mandates empirical contract verification for cross-system bugs — silent shape/semantics mismatches (e.g. assuming `due_date::date` yields the picked date regardless of session timezone) are invisible to code reading alone.

**Acceptance Criteria:**
- [ ] Sampled production/staging `tasks.due_date` values confirm (or refute) the date-only 00:00:00 UTC storage semantics documented in `docs/data-model/entities/task.md`
- [ ] psql probes document how `CURRENT_DATE`, `now() AT TIME ZONE <zone>`, and `timestamptz::date` behave under the API's actual session timezone setting
- [ ] The `tz` value format the SPA actually sends (IANA zone name) is confirmed from the T-001 capture
- [ ] Any divergence between documented and observed semantics recorded in the bug report

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- migrations/001-init.sql - confirm the `due_date` column type and any default that shapes storage semantics
- docs/data-model/entities/task.md - cross-check the documented storage semantics and overdue rule against observed rows
- docs/work-items/BUG-001-overdue-filter-timezone.md - record contract-verification findings in Section 6 Observations

**Technical Notes:**
- Investigation steps: `SELECT due_date, due_date AT TIME ZONE 'UTC', due_date::date FROM tasks` under different `SET TIME ZONE` values; compare `CURRENT_DATE` vs `(now() AT TIME ZONE 'America/Los_Angeles')::date` around the UTC midnight boundary
- Expected findings: `CURRENT_DATE` follows the session timezone (UTC on the server), and extracting the picked date safely requires `(due_date AT TIME ZONE 'UTC')::date`, not a bare `::date` cast

### T-003: Identify the root cause — trace tz from router validation to the SQL predicate

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Trace the `filter=overdue` request path through the router's Zod validation in `src/api/tasks.ts` into the predicate construction in `src/db/task.ts`, and determine why the validated `tz` value never influences the query. Confirm or refute the Section 6 hypothesis (predicate compares `due_date` against UTC `CURRENT_DATE`, ignoring `tz`), and audit related code for other server-side date-vs-today comparisons with the same defect.

**Rationale:**
Fix tasks must address a confirmed root cause, not the symptom; Section 10 of the bug report is deliberately unfilled until investigation establishes it.

**Acceptance Criteria:**
- [ ] Root cause identified with file-and-line evidence, or the Section 6 hypothesis refuted and the actual cause documented with supporting evidence
- [ ] Findings documented: what was confirmed, what was ruled out (e.g. transport of `tz` ruled out via the T-001 capture)
- [ ] Consumers of the overdue predicate enumerated — Section 8 expects the FEAT-003 board filter to be the only one; confirm or correct
- [ ] Related areas audited for the same pattern (other queries in `src/db/` comparing dates to "today"); results listed even if empty
- [ ] Bug report Status moved to Investigating with findings recorded in Section 6

**Dependencies:** T-001, T-002
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - examine the board-list route: Zod validation of `filter`/`tz` and what it passes to the repository
- src/db/task.ts - examine the overdue predicate construction; look for the `CURRENT_DATE` comparison from the Section 5 query log
- src/db/project.ts - audit for other date-vs-today comparisons sharing the defect
- docs/work-items/BUG-001-overdue-filter-timezone.md - record confirmed root cause in Section 6; set Status to Investigating

**Technical Notes:**
- Investigation steps: match the logged SQL from T-001 to the code that builds it; check the repository function signature for a timezone parameter; check the router call site for whether `tz` is forwarded
- Expected findings: `tz` is validated but dropped at the router→repository boundary, and the predicate hardcodes `due_date::date < CURRENT_DATE`
- No git archaeology needed: Section 6 records this is not a regression — the filter has behaved this way since FEAT-003 shipped

---

## Phase 2: Implementation

### T-004: Fix the overdue predicate to evaluate due dates in the requesting user's timezone

**Type:** Backend
**Workflow:** standard

**Description:**
Thread the validated `tz` value from the board-list route in `src/api/tasks.ts` into the repository call, and rebuild the overdue predicate in `src/db/task.ts` so a task is overdue only from 00:00 local time (in `tz`) of the day after its due date, per the business rule in `docs/data-model/entities/task.md`. Preserve the documented default of `tz=UTC` when the parameter is absent, and reject invalid timezone values cleanly.

**Rationale:**
Addresses the root cause confirmed in T-003 — the predicate compares against the database's UTC day and ignores the accepted `tz` parameter — instead of patching the symptom client-side.

**Acceptance Criteria:**
- [ ] Bug no longer reproducible with the original Section 2 steps: a task due today in `America/Los_Angeles` is not returned as overdue at 18:00 local
- [ ] Boundary honored: the task first appears in Overdue exactly at 00:00 local time of the day after its due date, for both negative and positive UTC offsets
- [ ] `tz` reaches the SQL as a bound parameter — no string interpolation into the query
- [ ] An invalid `tz` (non-IANA string) is rejected with a 400 `validation-error` envelope instead of surfacing a database error
- [ ] Existing `filter=overdue` semantics otherwise unchanged: `done` tasks and tasks without a due date are still excluded; `tz` omitted still means UTC

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - rebuild the overdue predicate as a timezone-aware comparison taking `tz` as a query parameter
- src/api/tasks.ts - forward the validated `tz` into the repository call; tighten Zod validation to accept only IANA zone names

**Technical Notes:**
- Root cause addressed: the validated `tz` is currently dropped at the router→repository boundary while the predicate uses UTC `CURRENT_DATE`
- Implementation approach: compare the picked calendar date to the user's current local date, e.g. `(due_date AT TIME ZONE 'UTC')::date < (now() AT TIME ZONE $tz)::date AND status <> 'done'` — extract the picked date explicitly in UTC because `due_date` stores 00:00:00 UTC (T-002)
- Do not `SET TIME ZONE` on the connection — keep the conversion request-scoped inside the predicate (connections are pooled)
- Error handling: reuse the existing `validation-error` catalog code; no new Error Catalog row is needed
- Regression risk: the board-list query also serves the unfiltered board and `status` filter — verify pagination, ordering, and those paths are untouched; no migration or backfill (read-time filtering only, Section 8)

---

## Phase 3: Verification & Prevention

### T-005: Add repository unit tests for the timezone-aware overdue predicate

**Type:** Testing
**Workflow:** standard

**Description:**
Create the missing repository unit test file for `src/db/task.ts` (per the CLAUDE.md rule that every repository gets a unit test against a test database) covering the overdue predicate across timezones with a controlled clock.

**Rationale:**
The predicate had no direct test — which is why an always-reproducible defect shipped in v1.2 and survived until pilot users noticed; boundary-level tests at the repository layer would have caught it.

**Acceptance Criteria:**
- [ ] Test reproducing the exact bug at the repository level: task due 2026-07-12, clock frozen at 2026-07-13T01:14Z, `tz=America/Los_Angeles` → not overdue; same instant with `tz=UTC` → overdue
- [ ] Boundary tests: 23:59:59 local on the due date → not overdue; 00:00:00 local the next day → overdue
- [ ] Positive-offset case (`Europe/Berlin`): a task overdue locally is returned even while the UTC day lags behind
- [ ] Exclusions verified: `done` tasks and tasks with no due date never appear overdue regardless of `tz`

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/db/task.test.ts (new) - unit tests for the overdue predicate against the test database

**Technical Notes:**
- Test cases: exact BUG-001 scenario, day-boundary values in both hemisphere offsets, a DST-transition date for `America/Los_Angeles` to prove IANA-zone (not fixed-offset) arithmetic
- Verification steps: inject or freeze "now" (pass a reference timestamp into the query or stub the clock) so assertions are deterministic in CI regardless of the runner's timezone

### T-006: Add API integration regression test for the exact BUG-001 scenario

**Type:** Testing
**Workflow:** standard

**Description:**
Extend the tasks router integration tests with Supertest coverage of `GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=...`, reproducing the Section 2/Section 5 scenario end-to-end through router validation, repository, and response envelope.

**Rationale:**
Guards the full request path — a repository-only test would not catch a recurrence of the router dropping `tz` before it reaches the query, which is the confirmed failure mode.

**Acceptance Criteria:**
- [ ] Regression test passes: with the clock frozen at 2026-07-13T01:14Z and a task due 2026-07-12, `filter=overdue&tz=America/Los_Angeles` returns an empty `data` array with `meta.totalCount` 0
- [ ] Default documented: the same request without `tz` (defaults to UTC) returns the task, matching the API spec
- [ ] Invalid `tz` (e.g. `Not/AZone`) yields 400 with the `validation-error` code and envelope
- [ ] Response shape unchanged: `data` items are full TaskDto objects and `meta` carries `totalCount`/`page`/`pageSize`

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add a `filter=overdue` + `tz` regression suite for BUG-001

**Technical Notes:**
- Test cases: exact bug scenario, UTC default, invalid-zone rejection, and one positive-offset case at the API level
- Verification steps: freeze time at the suite level so the UTC/local day divergence window is deterministic

### T-007: Verify the fix end-to-end and run the full regression suite

**Type:** Testing
**Workflow:** standard

**Description:**
Re-run the original Section 2 reproduction on staging with the fix deployed, confirming the board filter and the TaskCard due-date chip now agree, and run the full Vitest suite to confirm no regressions elsewhere.

**Rationale:**
The fix constraint requires that existing functionality is not broken; automated tests cover the predicate, but the original user-visible scenario must be confirmed on a real environment before the bug is closed.

**Acceptance Criteria:**
- [ ] Original reproduction steps no longer show the task as overdue during the 16:00–23:59 local window (`America/Los_Angeles`), and the filter matches the card chip on screen
- [ ] Spot-check in a positive-offset zone (`Europe/Berlin`): tasks overdue locally now appear on time rather than late
- [ ] Full test suite passes — no regressions introduced by the fix

**Dependencies:** T-005, T-006
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - note verification evidence in Section 6 Observations

**Technical Notes:**
- Verification steps: repeat T-001's clock/timezone setup on staging post-deploy; compare board results against the chip state in the same session; run `vitest` across `tests/`
- Confirm the Section 5 query log now shows the timezone-aware predicate with `tz` bound

### T-008: Close out BUG-001 — record root cause and resolution

**Type:** Documentation
**Workflow:** standard

**Description:**
Fill Section 10 (Root Cause & Resolution) of the bug report with the confirmed root cause, fix summary, and the version/commit the fix ships in, and move Status from Investigating to Resolved.

**Rationale:**
Usage Note 9 requires resolution capture once the fix is verified — Section 10 seeds future investigations of similar symptoms and regression-test generation.

**Acceptance Criteria:**
- [ ] Section 10 fields (Root Cause, Fix Summary, Fixed In) replaced with confirmed values traceable to T-003 findings and the T-004 change
- [ ] Status field set to Resolved
- [ ] Traceability intact: FEAT-003 AC-2 referenced as satisfied by the fix

**Dependencies:** T-007
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - fill Section 10 and set Status to Resolved

## Summary

**Work item:** BUG-001 — "Overdue" board filter marks tasks overdue up to 8 hours early for users west of UTC.

**Most likely root cause hypothesis:** The board-list route in `src/api/tasks.ts` validates the `tz` query parameter but never forwards it; the overdue predicate built in `src/db/task.ts` compares `due_date::date` against the database's UTC `CURRENT_DATE`, so the overdue boundary tracks the UTC day instead of the user's local day (per the Section 5 query log and Section 6 observations — unconfirmed until T-003 completes).

**Confidence level in diagnosis:** High — the captured SQL shows the UTC `CURRENT_DATE` comparison and the network capture proves `tz` arrives valid and intact, isolating the defect server-side; T-001–T-003 exist to confirm it with file-level evidence rather than assume it.

**Risk assessment of proposed fix:** Low-to-medium. The change is confined to one read-only predicate and one parameter hand-off; no data migration or backfill (read-time filtering only). Residual risks: timezone-name injection if `tz` were interpolated (mitigated by parameter binding, T-004 AC), database errors on invalid zone names (mitigated by IANA validation mapping to `validation-error`), and DST/day-boundary arithmetic mistakes (mitigated by boundary and DST tests in T-005/T-006).

**Monitoring recommendations post-fix:** Log `filter` and `tz` per board-list request and track the `validation-error` rate for `tz` to spot malformed-zone clients; add a periodic canary that compares the API's overdue set for a fixture project against an independently computed local-date reference in two zones (one negative, one positive offset), alerting on divergence around UTC midnight.

**Related areas to audit for similar issues:** Other server-side date-vs-today comparisons in `src/db/` repositories (T-003 audits `src/db/project.ts`; currently none expected); the TaskCard due-date chip and Task Detail Panel date display (client-side, reported correct — confirm they share the same day-boundary rule as the fixed predicate); any future due-date features (reminders, digests) must reuse the timezone-aware predicate rather than reintroducing a UTC-day comparison.
