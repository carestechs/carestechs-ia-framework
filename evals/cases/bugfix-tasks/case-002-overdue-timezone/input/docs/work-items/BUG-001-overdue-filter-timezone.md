# Bug Report: Overdue Filter Shows Wrong Tasks Across Timezones

> **Product**: TaskFlow — a small web-based task tracker (projects, kanban boards, tasks) with an Express REST API backend and a React SPA frontend.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | BUG-001 |
| **Summary** | "Overdue" board filter marks tasks overdue up to 8 hours early for users west of UTC |
| **Severity** | Medium |
| **Status** | Reported <!-- enum: Reported · Investigating · Fix In Progress · Resolved · Won't Fix --> |
| **Reported By** | User complaint (pilot team in Seattle), confirmed by QA |
| **Date Reported** | 2026-07-13 |
| **Date First Observed** | 2026-07-12 |

### Severity Justification

Core filtering feature returns incorrect results for every user with a negative UTC offset (~40% of active pilot users) during their local evening. No data is corrupted and a workaround exists (check the due-date chip on the card), but it erodes trust in the board — two users reported "TaskFlow says I'm late when I'm not."

---

## 2. Steps to Reproduce

**Preconditions:** Logged in as a project member; browser timezone is `America/Los_Angeles` (UTC-8); a task exists with due date set to today.

1. Create a task "Ship newsletter" in any project and set **Due date** to today (2026-07-12) via the task detail panel
2. Wait until after 16:00 local time (00:00 UTC of the next day) — or set the workstation clock forward equivalently on a test environment
3. Open the Project Board and select **"Overdue"** in the board filter dropdown
4. **Observe:** "Ship newsletter" appears in the Overdue results, although its due date (today, local time) has not yet passed

**Reproducibility:** Always — for any user whose local time is still "today" while UTC has already rolled to "tomorrow" (16:00–23:59 local for UTC-8).

---

## 3. Expected vs Actual Behavior

### Expected Behavior

A task is treated as overdue only after its due date has fully passed **in the requesting user's timezone** — i.e., starting at 00:00 local time of the day after the due date (per the overdue business rule in `docs/data-model/entities/task.md` and the `filter`/`tz` parameters in `docs/api-spec/endpoints/tasks.md`). A task due 2026-07-12 must never appear overdue at 18:00 PDT on 2026-07-12.

### Actual Behavior

The task appears in the Overdue filter as soon as the **UTC** calendar day advances past the due date — the `tz` query parameter the SPA sends is accepted but has no effect on the result. For a UTC-8 user, tasks due "today" flip to overdue at 16:00 local time — up to 8 hours early. The due-date chip on the card (which uses the browser's local date) still reads "Due today", contradicting the filter.

---

## 4. Environment

| Field | Value |
|-------|-------|
| **App Version** | v1.2.3 (commit `a41c9f0`) |
| **Platform** | Chrome 138 / Windows 11 and Safari 18 / macOS — both confirmed; API-level, so client-independent |
| **User Context** | Member role, browser timezone `America/Los_Angeles`; also reproduced with `America/New_York` (fails from 20:00 local) |
| **Deployment** | Production (also reproduced on Staging) |

---

## 5. Error Evidence

### Error Messages / Logs

```
No exception raised. Staging API log (query logging enabled), 2026-07-13T02:14:07Z:
[tasks router] GET board list filter=overdue tz=America/Los_Angeles
SELECT ... FROM tasks WHERE project_id = $1
  AND due_date::date < CURRENT_DATE     -- CURRENT_DATE evaluates in UTC = 2026-07-13
  AND status <> 'done'
-- the validated tz value is never passed into the predicate built in src/db/task.ts
```

### Network / API Evidence

```
GET /api/v1/projects/42/tasks?filter=overdue&tz=America%2FLos_Angeles
(sent 2026-07-12 18:14 PDT = 2026-07-13 01:14 UTC)

200 OK
{
  "data": [
    { "id": "t_9b3", "title": "Ship newsletter", "dueDate": "2026-07-12T00:00:00Z", "status": "todo" }
  ],
  "meta": { "totalCount": 1, "page": 1, "pageSize": 50 }
}
-- dueDate 2026-07-12 has not passed in America/Los_Angeles, yet the task is returned as overdue.
-- Note the tz parameter is present and valid in the request.
```

### Screenshots / Recordings

Screenshot attached to the pilot team's report (board showing "Overdue (1)" at 6:14 PM local with the card's due-date chip reading "Due today") — `attachments/bug-001-board.png`.

---

## 6. Additional Context

| Field | Value |
|-------|-------|
| **Frequency** | Always, within the local-evening window for UTC-negative users |
| **First occurrence** | Present since the filter shipped in v1.2 (FEAT-003) — first noticed when the Seattle pilot team started using due dates heavily |
| **Workaround exists** | Yes — hover the card and read the due-date chip; the inaccurate filter can be ignored |
| **Related bugs** | None on record |
| **Regression** | No (never worked) — the overdue comparison has used the server's UTC day since the filter shipped |

### Observations

- Only US-based pilot teams reported it; the Berlin team (UTC+1) never saw it — consistent with a UTC-day comparison (for positive offsets the filter errs in the other direction: tasks show overdue *late*, which users don't complain about)
- The card's due-date chip and the board filter disagree on the same screen: the chip computes "overdue" client-side from the browser's local date and is correct; the filter is computed server-side and is wrong — so the defect is confined to the server-side predicate, not to how the timezone reaches the API
- Hypothesis (pre-investigation, unconfirmed): the board list route in `src/api/tasks.ts` validates `tz` but the overdue predicate built in `src/db/task.ts` compares against the database's UTC `CURRENT_DATE`, ignoring the timezone entirely — to be confirmed or refuted by investigation

---

## 7. Affected Entities and Components

| Entity / Component | How Affected | Reference |
|--------------------|-------------|-----------|
| Task (`due_date` field) | Semantics — stored as 00:00:00 UTC of the picked calendar date (date-only semantics); the overdue rule says the comparison happens in the user's timezone, but the query ignores this | `docs/data-model/entities/task.md` (fields + overdue business rule); `docs/data-model/index.md` §1.2 (timestamp decision) |
| GET /api/v1/projects/{projectId}/tasks (`filter=overdue`, `tz`) | Returns an incorrect result set; `tz` is accepted but has no effect | `docs/api-spec/endpoints/tasks.md` |
| Task repository — overdue predicate (backend) | Builds the overdue comparison using UTC `CURRENT_DATE` (see Section 5 log) | `src/db/task.ts` (repository), `src/api/tasks.ts` (router that validates `tz`) |
| Project Board — filter dropdown (frontend) | Displays the wrong set; no frontend defect itself — the card chip in `docs/ui-specification/components.md` is correct | `docs/ui-specification/screens/project-board.md` |

> **Retrieval key:** shards to load — `docs/data-model/entities/task.md`, `docs/api-spec/endpoints/tasks.md`, `docs/ui-specification/screens/project-board.md` (plus each spec's `index.md`).

---

## 8. Impact Assessment

| Dimension | Assessment |
|-----------|------------|
| **Users affected** | Subset — all users with negative UTC offsets (~40% of pilot users), daily during local evenings |
| **Feature affected** | Board filtering (FEAT-003 Board filters) — the only consumer of the overdue predicate |
| **Data impact** | None — read-time filtering only, stored data is correct |
| **Business impact** | User trust — "the tracker lies about lateness" was verbatim pilot feedback; no revenue or compliance exposure |

---

## 9. Traceability

| Reference | Link |
|-----------|------|
| **Related Feature** | FEAT-003 (Board filters, shipped v1.2) |
| **Violated AC** | FEAT-003 AC-2 — "a task appears in Overdue only after its due date has passed in the viewing user's timezone" |
| **Spec Reference** | `docs/data-model/entities/task.md` (overdue business rule); `docs/api-spec/endpoints/tasks.md` (`filter` + `tz` parameters) |
| **Related Work Items** | None |

---

## 10. Root Cause & Resolution

> *Fill this section when the Status moves to Resolved. It closes the loop: future investigations of similar symptoms start here, and it feeds regression-test generation.*

| Field | Value |
|-------|-------|
| **Root Cause** | [Not yet investigated — do not guess here; pre-investigation hypotheses live in Section 6 (Observations)] |
| **Fix Summary** | [Pending investigation] |
| **Fixed In** | [Pending] |

<!-- TODO: Leave this section with placeholder values until the bug is actually resolved. Do not guess the root cause here while Status is Reported/Investigating — hypotheses belong in Section 6 (Observations). -->

---

## 11. Usage Notes for AI Task Generation

When generating investigation and fix tasks from this Bug Report:

1. **Investigation first**: Always generate investigation tasks before fix tasks. Do not assume the root cause based on symptoms alone — Section 10 is deliberately unfilled.
2. **Evidence-driven**: Use Section 5 (Error Evidence) to guide investigation steps. The captured query log points at the overdue predicate; the network capture proves the `tz` parameter arrives intact.
3. **Scope awareness**: Use Section 7 (Affected Entities) to determine which specs to read for understanding correct behavior.
4. **Reproduction**: The first investigation task should verify reproducibility using Section 2 (Steps to Reproduce).
5. **Regression context**: Section 6 indicates this is not a regression — the filter has behaved this way since it shipped; no git-archaeology task is needed.
6. **Impact-proportionate response**: Use Section 8 (Impact Assessment) to calibrate fix scope. This is read-time filtering only — no data migration or backfill tasks.
7. **Traceability**: Include the Bug Report ID (BUG-001) in the task generation output summary for cross-referencing.
8. **Fix verification**: Generated fix tasks must include a test case that reproduces the exact bug scenario from Section 2.
9. **Resolution capture**: The final generated task should include filling Section 10 (Root Cause & Resolution) and setting Status to Resolved once the fix is verified.
