# BUG-001 — Task List: Overdue Filter Shows Wrong Tasks Across Timezones

> Generated from `docs/work-items/BUG-001-overdue-filter-timezone.md` following `prompts/bugfix-tasks.md` with the canonical task schema from `prompts/base-template.md`. All paths are relative to the project root. The bug's Status is **Reported** — Phase 1 performs the investigation; the Section 6 hypothesis is an input to be confirmed or refuted, not an established root cause.

---

## Phase 1: Investigation

### T-001: Reproduce the bug and capture live on-the-wire evidence

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Reproduce BUG-001 on staging using the exact Section 2 steps (browser timezone `America/Los_Angeles`, task due today, local time advanced past 16:00) and capture a real sample of the on-the-wire request/response for `GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=...` together with the corresponding SQL from the query log. Confirm the TaskCard due-date chip and the Overdue filter disagree on the same screen, as reported.

**Rationale:**
The bug report requires the first investigation task to verify reproducibility (Section 11, note 4); the captured payload is also the empirical client→API contract sample that the cross-boundary contract check (T-002) and root-cause trace (T-003) build on.

**Acceptance Criteria:**
- [ ] Bug reproduced on staging following the Section 2 steps exactly, or non-reproduction documented with full environment details
- [ ] Live request/response pair plus the matching query-log SQL captured and attached to the bug report, alongside the 2026-07-13 evidence in Section 5
- [ ] Confirmed the `tz` query parameter arrives at the API intact and valid (the defect is server-side, per Section 6 observations)
- [ ] Reproduction with a positive-offset zone (e.g. `Europe/Berlin`) documented — expected to err in the opposite direction (overdue appears late)
- [ ] Findings recorded in Section 6 (Observations); bug report Status moved to Investigating

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - confirm the filter dropdown sends `filter=overdue` and `tz=<browser zone>` as specced
- docs/work-items/BUG-001-overdue-filter-timezone.md - record reproduction findings in Section 6; set Status to Investigating

**Technical Notes:**
- Investigation steps: set browser timezone; create a task due today via the detail panel; move the clock past 16:00 local (00:00 UTC next day); select Overdue; capture the network exchange and the API query log.
- Expected findings: task returned as overdue while its local due date has not passed; `tz` present and valid in the request, absent from the SQL predicate.

### T-002: Verify the date/timezone contract empirically against PostgreSQL

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Verify against PostgreSQL 16 itself — not comments or assumptions — the semantics the overdue predicate relies on: what timezone the app's `pg` connections run with, how `CURRENT_DATE` evaluates under it, what `due_date::date` yields for a `timestamptz`, and how `AT TIME ZONE` converts. Confirm against real stored rows that `due_date` holds 00:00:00 UTC of the picked calendar date (the date-only semantics in the entity shard), and hand-validate a candidate timezone-correct predicate in psql.

**Rationale:**
This bug crosses the app↔database boundary, so the contract must be verified empirically against the producer (PostgreSQL and the actual stored data) before any fix is designed — a wrong assumption here would produce a fix that is wrong in a new way.

**Acceptance Criteria:**
- [ ] Session timezone of the app's database connections determined empirically and documented
- [ ] Behavior of `CURRENT_DATE`, `timestamptz::date`, and `AT TIME ZONE` confirmed with a psql transcript against staging, captured in the bug report
- [ ] Sampled `due_date` values confirmed to match the 00:00:00 UTC date-only semantics documented in the Task entity shard
- [ ] A candidate timezone-correct predicate validated by hand in psql for a negative-offset zone, a positive-offset zone, and UTC, including the local-midnight boundary

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/task.md - the `due_date` storage semantics and overdue business rule the predicate must satisfy
- docs/data-model/index.md - Section 1.2 timestamptz-always-UTC decision (context for the session timezone check)
- docs/work-items/BUG-001-overdue-filter-timezone.md - record the psql transcript findings in Section 6

**Technical Notes:**
- Producer sources: PostgreSQL 16 documentation for `CURRENT_DATE`/`AT TIME ZONE` plus a live psql session — capture actual outputs around a UTC midnight boundary, e.g. `SELECT CURRENT_DATE, (now() AT TIME ZONE 'America/Los_Angeles')::date;`.
- Expected findings: `CURRENT_DATE` follows the connection's session timezone (UTC in this deployment), so the existing predicate flips tasks overdue at UTC midnight regardless of the user's zone.

### T-003: Trace the tz parameter through the router and repository to identify the root cause

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Trace `tz` from its Zod validation in the board list route through the repository call into the overdue predicate built in the task repository, and pinpoint exactly where the timezone stops influencing the query. Confirm or refute the Section 6 hypothesis and state the definitive root cause with file/function evidence.

**Rationale:**
Section 10 of the bug report is deliberately unfilled — the fix must target a confirmed root cause, not the symptom or the pre-investigation hypothesis.

**Acceptance Criteria:**
- [ ] Root cause identified with the exact code path (file and function) where `tz` is dropped or ignored — or the hypothesis refuted with evidence and the actual cause identified
- [ ] Findings documented: what was confirmed, what was ruled out
- [ ] The precise predicate to change is identified and a fix approach is sketched against the T-002-validated expression
- [ ] Bug report Section 6 updated with the confirmed findings (Section 10 remains unfilled until the fix is verified)

**Dependencies:** T-001, T-002
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - router; how `filter`/`tz` are validated and what is passed to the repository
- src/db/task.ts - repository; how the overdue predicate is constructed (compare with the Section 5 query log)
- docs/work-items/BUG-001-overdue-filter-timezone.md - record confirmed root-cause evidence in Section 6

**Technical Notes:**
- Investigation steps: read the route's Zod schema; follow the repository function signature; diff the built SQL against the Section 5 log line.
- Expected findings: the repository list function never receives (or discards) `tz`; the predicate hard-codes `due_date::date < CURRENT_DATE`.

### T-004: Audit related date comparisons for the same UTC-day assumption

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Search the backend for other date comparisons that assume the UTC calendar day (`CURRENT_DATE`, `::date` casts, `now()`-based day math) and give each a same-bug / not-affected verdict. Confirm the client-side TaskCard due-date chip logic agrees with the server-side overdue rule so the two cannot disagree after the fix.

**Rationale:**
The guidance requires considering related areas with the same issue while forbidding scope creep into unrelated refactoring — this audit separates in-scope findings (anything feeding the overdue rule) from follow-up work items.

**Acceptance Criteria:**
- [ ] All date-based predicates in `src/db/` reviewed and listed with a same-bug / not-affected verdict
- [ ] TaskCard due-date chip client-side computation confirmed consistent with the overdue business rule (it is believed correct per Section 6)
- [ ] Out-of-scope findings, if any, documented in Section 6 for separate follow-up work items rather than folded into this fix

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- src/db/task.ts - all date-based SQL predicates beyond the overdue one
- src/db/project.ts - any date comparisons carrying the same UTC-day assumption
- src/ui/components/task-card.tsx - the chip's client-side overdue computation that must agree with the server rule
- docs/work-items/BUG-001-overdue-filter-timezone.md - record audit verdicts in Section 6

**Technical Notes:**
- Section 8 states board filtering is the only consumer of the overdue predicate — verify rather than assume.
- No git-archaeology needed: Section 6 confirms this is not a regression (the filter has behaved this way since FEAT-003 shipped).

---

## Phase 2: Implementation

### T-005: Fix the overdue predicate to evaluate in the requesting user's timezone

**Type:** Backend
**Workflow:** standard

**Description:**
Pass the validated `tz` from the board list route into the task repository and rebuild the overdue predicate so the day comparison happens in that timezone (defaulting to `UTC` when `tz` is omitted, per the API spec), using the expression validated in T-002. This is a read-time query fix only — stored data, response envelope, pagination, and the `done`-exclusion rule are unchanged.

**Rationale:**
Addresses the root cause confirmed by T-003 — the validated `tz` never reaches the predicate, which compares against the UTC day — restoring FEAT-003 AC-2 and the overdue business rule in the Task entity shard.

**Acceptance Criteria:**
- [ ] Bug no longer reproducible with the original Section 2 steps (a task due today is not overdue at 18:00 PDT)
- [ ] A task becomes overdue exactly at 00:00 local time of the day after its due date, for negative-offset, positive-offset, and UTC zones
- [ ] Omitting `tz` defaults to UTC as documented; an invalid `tz` still maps to the `validation-error` catalog entry — no new error codes
- [ ] `done` tasks and tasks without a due date remain excluded; unfiltered board listing, ordering, and pagination behavior are unchanged

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - forward the validated `tz` to the repository list call
- src/db/task.ts - build the overdue predicate against the user's timezone via a bound query parameter

**Technical Notes:**
- Candidate predicate (validate in T-002): `(due_date AT TIME ZONE 'UTC')::date < (now() AT TIME ZONE $tz)::date` with `tz` bound as a parameter — never string-interpolated into SQL.
- Root cause addressed: `tz` now flows router → repository → predicate instead of stopping at validation.
- Regression risk: positive-offset users see tasks flip overdue later than before (now correct per spec); confirm the UTC default keeps behavior identical for clients that omit `tz`.
- Keep all SQL inside the repository module per CLAUDE.md — the router must not touch `pg` directly.
- Consider accepting a reference instant in the repository function (defaulting to now) so the predicate is deterministic under test.

---

## Phase 3: Verification & Prevention

### T-006: Add repository unit tests reproducing the exact bug and its boundaries

**Type:** Testing
**Workflow:** standard

**Description:**
Create the missing task-repository unit test against the test database, reproducing the exact Section 2 scenario and pinning the overdue boundary in multiple timezones. The suite must demonstrably fail against the pre-fix predicate — proving it would have caught BUG-001.

**Rationale:**
The constraints require a test that would have caught this bug, and CLAUDE.md requires a unit test per repository — none exists yet for the task repository.

**Acceptance Criteria:**
- [ ] Exact bug scenario covered: task due 2026-07-12, reference time 2026-07-13T01:14Z, `tz=America/Los_Angeles` → not overdue; same instant with `tz=UTC` → overdue
- [ ] Local-midnight boundary covered in UTC-8, UTC, and UTC+1: not overdue at 23:59 local on the due date; overdue from 00:00 local the next day
- [ ] Positive-offset early flip covered: at 2026-07-12T23:30Z a task due 2026-07-12 is overdue for `tz=Europe/Berlin` but not for `tz=UTC`
- [ ] Tasks with `done` status or no due date are never returned by the overdue filter
- [ ] Suite confirmed to fail when run against the unfixed predicate

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- tests/db/task.test.ts (new) - overdue predicate unit tests against the test database

**Technical Notes:**
- Control the reference time deterministically (inject the instant into the repository call, or use a transaction-scoped clock override) — wall-clock-dependent tests would only fail near midnight.
- Test cases: exact bug scenario, three-zone midnight boundary, positive-offset flip, null due date, `done` exclusion, default `tz`.

### T-007: Add API integration tests for filter=overdue with tz and re-verify the fix end-to-end

**Type:** Testing
**Workflow:** standard

**Description:**
Extend the Supertest integration tests to cover `GET /api/v1/projects/{projectId}/tasks` with `filter=overdue` and `tz` through the full HTTP layer — validation, parameter forwarding to the repository, and the standard list envelope. Re-run the Section 2 reproduction on staging to confirm the fix, and run the full test suite.

**Rationale:**
The parameter was originally dropped at the router→repository seam; the repository-only test in T-006 cannot catch that disconnect being reintroduced, so the route layer needs its own coverage.

**Acceptance Criteria:**
- [ ] Integration test: `filter=overdue` with `tz=America/Los_Angeles` returns the correct result set in the standard list envelope with `meta` totals
- [ ] Invalid `tz` returns 400 with the `validation-error` code; omitted `tz` behaves as UTC
- [ ] Manual re-verification of the Section 2 steps passes on staging, with evidence noted in the bug report
- [ ] Full test suite passes — no regressions introduced by the fix

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- tests/api/tasks.test.ts - add `filter=overdue` + `tz` integration cases alongside the existing board list tests
- docs/work-items/BUG-001-overdue-filter-timezone.md - note the staging re-verification evidence

**Technical Notes:**
- Test cases: the exact bug scenario through HTTP, invalid `tz` → `validation-error`, default `tz`, envelope/pagination unchanged.
- Verification steps: full Vitest run; staging reproduction with the clock past 16:00 local in a UTC-8 zone.

### T-008: Close out the bug report with root cause and resolution

**Type:** Documentation
**Workflow:** standard

**Description:**
Fill Section 10 (Root Cause & Resolution) of the bug report with the confirmed root cause, a fix summary, and the version the fix ships in, then set Status to Resolved. Cross-reference the regression tests so future investigations of similar symptoms start from this record.

**Rationale:**
Resolution capture closes the loop per the bug report's usage notes (Section 11, note 9) — Section 10 feeds future investigations and regression-test generation, and may only be filled once the fix is verified.

**Acceptance Criteria:**
- [ ] Section 10 filled with the confirmed root cause, fix summary, and the release/commit the fix ships in
- [ ] Status updated to Resolved
- [ ] The T-006/T-007 regression tests referenced from the report for traceability

**Dependencies:** T-006, T-007
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - fill Section 10; set Status to Resolved

---

## Summary

**Bug:** BUG-001 — the board's Overdue filter marks tasks overdue up to 8 hours early for users west of UTC.

**Most likely root cause hypothesis:** the board list route in `src/api/tasks.ts` validates the `tz` query parameter but never passes it into the overdue predicate built in `src/db/task.ts`, which compares `due_date::date < CURRENT_DATE` — evaluated on the database connection's UTC session timezone — so tasks flip overdue at UTC midnight instead of the user's local midnight.

**Confidence level:** High. The Section 5 query log shows the UTC-day predicate with no timezone term, and the network capture proves `tz` arrives intact and valid; the direction of the error for positive-offset users (overdue appears late, never reported) is consistent. Still, the hypothesis must be confirmed by T-001–T-003 before implementation begins — Section 10 stays unfilled until then.

**Risk assessment of proposed fix:** Low-to-medium. It is a read-time query change with no data migration or backfill (stored data is correct per Section 8). Specific risks: SQL injection if `tz` were interpolated (mitigated by binding it as a query parameter behind the existing Zod validation); a visible behavior shift for positive-offset users, whose tasks now flip overdue later — correct per spec but worth a release note; and query-plan changes on the tasks board query (the board index on `(project_id, status, position)` still drives the lookup, so impact should be negligible).

**Monitoring recommendations post-fix:** log `filter=overdue` requests with their `tz` value; track the `validation-error` rate on the board list endpoint for malformed `tz` values; add a staging synthetic check around UTC midnight comparing overdue counts for a UTC-8 zone versus UTC (they must differ by exactly the tasks due "today" in the negative-offset zone); watch pilot feedback channels from both the Seattle and Berlin teams after release.

**Related areas to audit for similar issues (T-004):** other `CURRENT_DATE`/`::date`/`now()` day-math usage across `src/db/` repository modules; the TaskCard due-date chip's client-side overdue computation (believed correct — must stay in agreement with the server rule); the Task Detail Panel's due-date display formatting.

**Traceability:** the fix restores FEAT-003 AC-2 ("a task appears in Overdue only after its due date has passed in the viewing user's timezone") — covered by T-005 (fix), T-006 (repository regression tests), and T-007 (API integration tests). The bug report defines no acceptance-criteria checklist of its own, so no coverage table is emitted.
