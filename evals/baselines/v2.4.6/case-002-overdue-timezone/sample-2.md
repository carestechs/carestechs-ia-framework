# BUG-001 — Bug Fix Tasks: Overdue Filter Shows Wrong Tasks Across Timezones

> Generated from `docs/work-items/BUG-001-overdue-filter-timezone.md` (Status: Reported — Section 10 unfilled; root cause not yet established).
> Schema: canonical task schema from `prompts/base-template.md`, with the bugfix `Type` delta (`Investigation`). Three-phase structure enforced via Dependencies.

---

## Phase 1: Investigation

### T-001: Reproduce the overdue filter bug and confirm the failure window

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Reproduce BUG-001 on staging using the exact steps in the bug report's Section 2: a task due "today" for a user in `America/Los_Angeles`, requested after UTC midnight but before local midnight. Confirm the API returns the task under `filter=overdue` while the local due date has not yet passed, and confirm the complementary behavior for a positive-offset zone (`Europe/Berlin` — tasks flip overdue *late*).

**Rationale:**
The bug report (Section 11, note 4) requires reproduction as the first investigation step; a confirmed reproduction and its exact time window are the baseline every later task verifies against.

**Acceptance Criteria:**
- [ ] Bug reproduced with Section 2 steps: API returns the due-today task as overdue for `tz=America/Los_Angeles` after UTC midnight, before local midnight
- [ ] Failure window characterized for a negative offset (`America/Los_Angeles`) and the opposite (late-flip) behavior confirmed for a positive offset (`Europe/Berlin`)
- [ ] Checked whether any existing test pins the wrong UTC-day behavior (would need updating alongside the fix)
- [ ] Findings documented: what was confirmed, what was ruled out

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- tests/api/tasks.test.ts - inspect for existing `filter=overdue` coverage that may assert the wrong (UTC-day) behavior
- docs/work-items/BUG-001-overdue-filter-timezone.md - record reproduction confirmation in Section 6 (Observations); move Status to Investigating

**Technical Notes:**
- Investigation steps: replay the captured request from Section 5 (`GET /api/v1/projects/{projectId}/tasks?filter=overdue&tz=America%2FLos_Angeles`) against staging with a task due "today"; vary request time across the UTC-midnight and local-midnight boundaries
- Expected findings: task appears in overdue results between UTC midnight and local midnight (matches Section 2); Berlin case errs in the opposite direction, consistent with a UTC-day comparison

### T-002: Verify the timezone contract empirically across the client → API → database boundary

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
This bug crosses system boundaries (browser timezone → `tz` query parameter → SQL predicate), so verify each leg of the contract against its producer rather than trusting code comments or fixtures. Capture a real board request from the SPA to confirm the on-the-wire `tz` value, verify against live rows that `due_date` is stored as 00:00:00 UTC of the picked calendar date (date-only semantics per the data model), and confirm on a real PostgreSQL 16 instance how `CURRENT_DATE` and timezone-converted date expressions (e.g. `(now() AT TIME ZONE $tz)::date`) actually evaluate.

**Rationale:**
The bugfix prompt mandates an empirical contract check as the first investigation step for cross-system bugs; the whole "silent shape mismatch" class is invisible if both sides are only checked against each other.

**Acceptance Criteria:**
- [ ] Real SPA request captured: `tz` present as a valid IANA zone matching the browser zone (corroborates Section 5 network evidence and `docs/ui-specification/screens/project-board.md`)
- [ ] `due_date` storage semantics confirmed against live database rows: 00:00:00 UTC of the picked calendar date, per `docs/data-model/entities/task.md`
- [ ] PostgreSQL 16 semantics confirmed empirically with sample queries: `CURRENT_DATE` evaluates in the server (UTC) zone; the timezone-converted alternative yields the user-local calendar date
- [ ] Findings documented: what was confirmed, what was ruled out

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- src/ui/project-board.tsx - confirm the SPA sends `tz=<browser zone>` with the overdue filter, as the screen spec states
- docs/data-model/entities/task.md - the `due_date` semantics and overdue business rule the code must be verified against
- docs/api-spec/endpoints/tasks.md - the `filter`/`tz` parameter contract the code must be verified against
- docs/work-items/BUG-001-overdue-filter-timezone.md - record contract-verification results in Section 6 (Observations)

**Technical Notes:**
- Investigation steps: capture a live request via browser devtools; `SELECT due_date FROM tasks` on real rows; run probe queries on PostgreSQL 16 for `CURRENT_DATE`, `(now() AT TIME ZONE 'America/Los_Angeles')::date`, and DST-transition dates
- Expected findings: contract intact up to the repository — the `tz` value arrives valid and unchanged; the defect, if the Section 6 hypothesis holds, is confined to the predicate

### T-003: Trace the tz parameter through router and repository to identify the root cause

**Type:** Investigation
**Workflow:** investigation-first

**Description:**
Trace the validated `tz` value from the board list route in `src/api/tasks.ts` into the overdue predicate built in `src/db/task.ts`, and pinpoint where it is dropped. Confirm or refute the Section 6 hypothesis that the predicate compares `due_date::date` against UTC `CURRENT_DATE` regardless of `tz`, and audit the repository layer for other date comparisons with the same defect.

**Rationale:**
The Section 5 query log shows the validated `tz` never reaches the predicate, but the exact drop point (router not passing it vs. repository not accepting it) determines the shape of the fix; guidance requires the root cause be identified before any fix task.

**Acceptance Criteria:**
- [ ] Root cause identified with the exact code path (file, function, and the predicate construction) where `tz` is dropped — or the hypothesis refuted with evidence and an alternative documented
- [ ] Section 6 hypothesis explicitly confirmed or refuted
- [ ] Related areas audited: all other `CURRENT_DATE` / UTC-day comparisons in `src/db/` listed, with a note on whether each needs the same treatment (Section 8 says the overdue predicate's only consumer is the FEAT-003 board filter)
- [ ] Findings documented: what was confirmed, what was ruled out

**Dependencies:** T-001, T-002
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - board list route: where the Zod-validated `tz` goes after validation
- src/db/task.ts - overdue predicate construction: how the date comparison is built and parameterized
- src/db/project.ts - audit for similar UTC-day date comparisons
- docs/work-items/BUG-001-overdue-filter-timezone.md - record the confirmed root cause evidence in Section 6 (Observations)

**Technical Notes:**
- Investigation steps: read the route handler's repository call signature; read the repository's query builder for the overdue branch; grep `src/db/` for `CURRENT_DATE` and date casts
- Expected findings: repository builds `due_date::date < CURRENT_DATE` with no `tz` parameter in its signature (matches the Section 5 log); no other consumer of the predicate

---

## Phase 2: Implementation

### T-004: Pass tz into the task repository and rebuild the overdue predicate in the user's timezone

**Type:** Backend
**Workflow:** standard

**Description:**
Thread the validated `tz` value from the board list route into the task repository's overdue query, and replace the UTC-day comparison with one that evaluates "today" in the requesting user's timezone — e.g. `due_date::date < (now() AT TIME ZONE $tz)::date` with `tz` bound as a query parameter. Preserve the documented default (`tz` omitted → `UTC`) and the existing exclusion of `done` tasks.

**Rationale:**
Fixes the root cause confirmed by T-003 — the predicate ignoring the user's timezone — restoring the overdue business rule in `docs/data-model/entities/task.md` and FEAT-003 AC-2, rather than patching the symptom client-side.

**Acceptance Criteria:**
- [ ] Bug no longer reproducible with the original Section 2 steps
- [ ] `filter=overdue` follows the entity rule: a task is overdue only from 00:00 local time of the day after its due date, in the requested `tz`; `done` tasks and tasks without a due date are excluded
- [ ] `tz` omitted falls back to `UTC` per `docs/api-spec/endpoints/tasks.md`; behavior for `tz=UTC` is unchanged from before the fix
- [ ] `tz` is bound as a query parameter (never string-interpolated into SQL); invalid values are rejected by the router's Zod validation with the `validation-error` catalog entry (400)
- [ ] SQL stays in the repository module per CLAUDE.md conventions — the router only passes the validated value through

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - pass the validated `tz` into the repository call for the overdue filter
- src/db/task.ts - accept `tz` and rebuild the overdue predicate to compare against the user-local current date

**Technical Notes:**
- Root cause addressed: the predicate compared against the database's UTC `CURRENT_DATE`; it now derives "today" from the requester's IANA zone
- Implementation approach: `due_date` is stored as 00:00:00 UTC of the picked date (date-only semantics), so `due_date::date` recovers the picked calendar date exactly; compare it to `(now() AT TIME ZONE $tz)::date`
- Regression risk: positive-offset users (Berlin) will see tasks flip overdue *earlier* than before — that is the corrected behavior per spec, but verify no test pins the old timing (per T-001 findings); an invalid zone name reaching `AT TIME ZONE` raises a database error, so the existing Zod validation must remain the gate

---

## Phase 3: Verification & Prevention

### T-005: Add regression tests for the exact bug scenario and timezone boundaries

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests for `GET /api/v1/projects/{projectId}/tasks?filter=overdue` reproducing the Section 2 scenario exactly (task due 2026-07-12, request after UTC midnight but before local midnight, `tz=America/Los_Angeles` → task not returned), plus boundary and related cases. Add a repository unit test for the overdue predicate against the test database, per the CLAUDE.md test conventions.

**Rationale:**
The constraints require a test that would have caught this exact bug and coverage of boundary conditions; without an instant-level boundary test the UTC-day regression could silently return.

**Acceptance Criteria:**
- [ ] A test reproducing the exact Section 2 bug scenario exists, fails against the pre-fix predicate, and passes after the fix
- [ ] Boundary covered: instants immediately before and at 00:00 local time of the day after the due date flip the result (e.g. for a 2026-07-12 due date in `America/Los_Angeles` under PDT: `2026-07-13T06:59:59Z` → not overdue, `2026-07-13T07:00:00Z` → overdue)
- [ ] Related cases covered: `tz` omitted (UTC default), positive offset (`Europe/Berlin`), `status=done` excluded, null `due_date` excluded, invalid `tz` → 400 `validation-error`
- [ ] Full test suite passes — no regressions introduced by the fix

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/api/tasks.test.ts - integration tests for `filter=overdue` + `tz` (exact scenario, boundaries, related cases)
- tests/db/task.test.ts (new) - repository unit tests for the overdue predicate against the test database

**Technical Notes:**
- Test cases: the exact Section 2 scenario; the local-midnight boundary pair; DST-transition day for the same zone; both offset signs; filter-off path unchanged
- Verification steps: run the new tests against the unfixed predicate first to prove they catch the bug, then against the fix; run the full Vitest suite

### T-006: Verify the fix end-to-end on staging and confirm no regressions

**Type:** Testing
**Workflow:** standard

**Description:**
Re-run the Section 2 reproduction on staging with the fix deployed: the due-today task must no longer appear under the Overdue filter during the local-evening window, and the board filter must agree with the card's due-date chip on the same screen. Run the full test suite as the final regression gate.

**Rationale:**
The constraint "fix must not break existing functionality" needs verification at the user-visible level, not just in tests — the original report was triggered by the filter and chip disagreeing on one screen.

**Acceptance Criteria:**
- [ ] Original Section 2 reproduction no longer shows the task as overdue between UTC midnight and local midnight
- [ ] Overdue filter and TaskCard due-date chip agree on the same board, verified for a negative-offset and a positive-offset zone
- [ ] Full test suite passes on the fix branch; unfiltered board listing, `status` filter, and pagination behave unchanged

**Dependencies:** T-005
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - record verification evidence (requests, timestamps, zones tested) in Section 6 (Observations)

**Technical Notes:**
- Verification steps: replay the Section 5 captured request on staging post-deploy; spot-check `Europe/Berlin` for the corrected (earlier) overdue transition; confirm the response envelope and `meta` totals are intact

### T-007: Close out BUG-001 — fill Root Cause & Resolution and set Status to Resolved

**Type:** Documentation
**Workflow:** standard

**Description:**
Fill the bug report's Section 10 (Root Cause, Fix Summary, Fixed In) with the investigation-confirmed root cause and the shipped fix details, and move Status from Investigating to Resolved. Ensure the wording reflects what T-003 actually confirmed, not the pre-investigation hypothesis text.

**Rationale:**
Section 11 (note 9) requires the final task to close the loop: Section 10 seeds future investigations of similar symptoms and feeds regression-test generation.

**Acceptance Criteria:**
- [ ] Section 10 Root Cause, Fix Summary, and Fixed In are filled with the confirmed findings, fix description, and version/commit
- [ ] Status field updated to Resolved
- [ ] Traceability preserved: FEAT-003 AC-2 noted as restored, and the regression tests from T-005 referenced

**Dependencies:** T-006
**Complexity:** S

**Files to Modify/Create:**
- docs/work-items/BUG-001-overdue-filter-timezone.md - Section 10 (Root Cause & Resolution) and the Status field

---

## Summary

**Bug Report:** BUG-001 — "Overdue" board filter marks tasks overdue up to 8 hours early for users west of UTC (Severity: Medium, Status: Reported).

- **Most likely root cause hypothesis:** the board list route in `src/api/tasks.ts` validates `tz` but the overdue predicate built in `src/db/task.ts` compares `due_date::date` against the database's UTC `CURRENT_DATE`, so the timezone never influences the result (per the Section 5 query log). To be confirmed or refuted by T-001–T-003 before any fix lands.
- **Confidence level:** High that the predicate ignores `tz` — the captured SQL shows it directly and the client-side chip (which computes locally) is correct on the same screen. Medium on the exact drop point (router not passing vs. repository not accepting), which T-003 pins down.
- **Risk assessment of proposed fix:** Low-to-medium. Read-time filtering only — no data migration or backfill (Section 8). Risks: positive-offset users see the corrected, earlier overdue transition (behavior change, but per spec); an invalid zone reaching `AT TIME ZONE` would raise a database error, so Zod validation must stay the gate (asserted in T-004/T-005); DST transition days shift the local-midnight boundary, covered by a dedicated test in T-005.
- **Monitoring recommendations post-fix:** temporarily log `filter=overdue` requests with `tz` and result counts to spot anomalies around UTC midnight; alert on `validation-error` spikes for the `tz` parameter; add a staging smoke check that queries the filter just after UTC midnight with a negative-offset zone.
- **Related areas to audit for similar issues:** other date comparisons in `src/db/` using `CURRENT_DATE` or UTC-day casts (audited in T-003); any future date-based filters (e.g. "due soon") must reuse the tz-aware predicate rather than reintroducing a UTC-day comparison. No error-message changes are needed — the failure mode was silent wrong results, not an unclear error.
