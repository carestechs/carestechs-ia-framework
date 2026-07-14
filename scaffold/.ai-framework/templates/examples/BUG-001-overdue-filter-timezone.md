<!-- Reference example — for real work items, copy the blank template from docs/work-items/, not this file. -->

# Bug Report: Overdue Filter Shows Wrong Tasks Across Timezones

> **Product**: TaskFlow — a small web-based task tracker (projects, tasks, labels, notifications) with a REST API backend and SPA frontend.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | BUG-001 |
| **Summary** | "Overdue" board filter marks tasks overdue up to 8 hours early for users west of UTC |
| **Severity** | Medium |
| **Status** | Resolved <!-- enum: Reported · Investigating · Fix In Progress · Resolved · Won't Fix --> |
| **Reported By** | User complaint (pilot team in Seattle), confirmed by QA |
| **Date Reported** | 2026-03-06 |
| **Date First Observed** | 2026-03-05 |

### Severity Justification

Core filtering feature returns incorrect results for every user with a negative UTC offset (~40% of active pilot users) during their local evening. No data is corrupted and a workaround exists (check the due date on the card), but it erodes trust in the board — two users reported "TaskFlow says I'm late when I'm not."

---

## 2. Steps to Reproduce

**Preconditions:** Logged in as a project member whose profile timezone is `America/Los_Angeles` (UTC-8); a task exists with due date set to today.

1. Create a task "Ship newsletter" in any project and set **Due date** to today (2026-03-05) via the task detail panel
2. Wait until after 16:00 local time (00:00 UTC of the next day) — or set the workstation clock forward equivalently on a test environment
3. Open the Project Board and select the **"Overdue"** option in the board filter dropdown
4. **Observe:** "Ship newsletter" appears in the Overdue results, although its due date (today, local time) has not yet passed

**Reproducibility:** Always — for any user whose local time is still "today" while UTC has already rolled to "tomorrow" (16:00–23:59 local for UTC-8).

---

## 3. Expected vs Actual Behavior

### Expected Behavior

A task is treated as overdue only after its due date has fully passed **in the user's profile timezone** — i.e., starting at 00:00 local time of the day after the due date. A task due 2026-03-05 must never appear overdue at 18:00 PST on 2026-03-05.

### Actual Behavior

The task appears in the Overdue filter as soon as the **UTC** calendar day advances past the due date. For a UTC-8 user, tasks due "today" flip to overdue at 16:00 local time — up to 8 hours early. The due-date text on the card still shows the correct local date, contradicting the filter.

---

## 4. Environment

| Field | Value |
|-------|-------|
| **App Version** | v1.2.3 (commit `a41c9f0`) |
| **Platform** | Chrome 133 / Windows 11 and Safari 18 / macOS — both confirmed; API-level, so client-independent |
| **User Context** | Member role, profile timezone `America/Los_Angeles`; also reproduced with `America/New_York` (fails from 19:00 local) |
| **Deployment** | Production (also reproduced on Staging) |

---

## 5. Error Evidence

### Error Messages / Logs

```
No exception raised. Staging API log (query logging enabled), 2026-03-06T02:14:07Z:
[TaskQueryService] filter=overdue user=u_5f21 tz=America/Los_Angeles
SELECT ... FROM tasks WHERE project_id = $1
  AND due_date < CURRENT_DATE          -- CURRENT_DATE evaluated in UTC = 2026-03-06
  AND completed_at IS NULL
```

### Network / API Evidence

```
GET /api/v1/projects/42/tasks?filter=overdue
(sent 2026-03-05 18:14 PST = 2026-03-06 02:14 UTC)

200 OK
{
  "data": [
    { "id": "t_9b3", "title": "Ship newsletter", "dueDate": "2026-03-05", "completedAt": null }
  ],
  "meta": { "totalCount": 1 }
}
-- dueDate "2026-03-05" has not passed in the user's timezone, yet it is returned as overdue.
```

### Screenshots / Recordings

Screenshot attached to the pilot team's report (board showing "Overdue (1)" at 6:14 PM local with the card's due-date chip reading "Due today") — `attachments/bug-001-board.png`.

---

## 6. Additional Context

| Field | Value |
|-------|-------|
| **Frequency** | Always, within the local-evening window for UTC-negative users |
| **First occurrence** | Present since v1.0 — first noticed when the Seattle pilot team started using due dates heavily |
| **Workaround exists** | Yes — hover the card and read the due-date chip; inaccurate filter can be ignored |
| **Related bugs** | None on record |
| **Regression** | No (never worked) — the overdue comparison has used the server's UTC day since launch |

### Observations

- Only US-based pilot teams reported it; the Berlin team (UTC+1) never saw it — consistent with a UTC-day comparison (for positive offsets the filter errs in the other direction: tasks show overdue *late*, which users don't complain about)
- Hypothesis (pre-investigation): `due_date` is stored date-only and compared against the API server's UTC `CURRENT_DATE`, ignoring the user's profile timezone — confirmed during investigation, see Section 10

---

## 7. Affected Entities and Components

| Entity / Component | How Affected | Reference |
|--------------------|-------------|-----------|
| Task (`due_date` field) | Semantics — stored as date-only, intended to mean "end of that day in the owner's timezone"; comparison ignores this | `docs/data-model/entities/task.md` (fields); `docs/data-model/index.md` §1.2 (timestamp decision) |
| GET /api/v1/projects/{id}/tasks (`filter=overdue`) | Returns incorrect result set | `docs/api-spec/endpoints/tasks.md` |
| TaskQueryService (backend) | Builds the overdue predicate using UTC `CURRENT_DATE` | `docs/ARCHITECTURE.md` §3.2 (backend services) |
| Project Board — filter dropdown (frontend) | Displays the wrong set; no frontend defect itself | `docs/ui-specification/screens/project-board.md` |

> **Retrieval key:** shards to load — `docs/data-model/entities/task.md`, `docs/api-spec/endpoints/tasks.md`, `docs/ui-specification/screens/project-board.md` (plus each spec's `index.md`).

---

## 8. Impact Assessment

| Dimension | Assessment |
|-----------|------------|
| **Users affected** | Subset — all users with negative UTC offsets (~40% of pilot users), daily during local evenings |
| **Feature affected** | Board filtering (FEAT-003 Board filters); overdue count badge on the dashboard uses the same query |
| **Data impact** | None — read-time filtering only, stored data is correct |
| **Business impact** | User trust — "the tracker lies about lateness" was verbatim pilot feedback; no revenue or compliance exposure |

---

## 9. Traceability

| Reference | Link |
|-----------|------|
| **Related Feature** | FEAT-003 (Board filters) |
| **Violated AC** | FEAT-003 AC-2 — "a task appears in Overdue only after its due date has passed in the viewing user's timezone" |
| **Spec Reference** | `docs/data-model/index.md` §1.2 ("Timestamps: TIMESTAMPTZ, always UTC; date-only fields interpreted in user profile timezone"); `docs/api-spec/endpoints/tasks.md`, `filter` parameter |
| **Related Work Items** | None |

---

## 10. Root Cause & Resolution

> *Filled at resolution — Status is Resolved.*

| Field | Value |
|-------|-------|
| **Root Cause** | `TaskQueryService.BuildOverdueFilter` compared the date-only `due_date` column against the database's `CURRENT_DATE`, which evaluates in UTC. Per the data model, `due_date` is a civil date meant to be interpreted in the task owner's profile timezone, so the predicate declared tasks overdue as soon as the UTC day rolled over — up to `abs(offset)` hours early for west-of-UTC users (and symmetrically late for east-of-UTC users). |
| **Fix Summary** | Overdue predicate now computes "today" in the requesting user's profile timezone and compares `due_date < that date` (`backend/src/tasks/task-query.service` + shared `toUserLocalDate` helper in `backend/src/shared/time`). The dashboard overdue badge reuses the same predicate. Added regression tests covering UTC-8, UTC+1, and UTC+13 at day-boundary instants; frontend unchanged. |
| **Fixed In** | v1.2.4 — PR #218, commit `9f3e2c1` |

---

## 11. Usage Notes for AI Task Generation

When generating investigation and fix tasks from this Bug Report:

1. **Investigation first**: Always generate investigation tasks before fix tasks. Do not assume the root cause based on symptoms alone.
2. **Evidence-driven**: Use Section 5 (Error Evidence) to guide investigation steps. Stack traces point to specific code paths; error messages point to specific error handling.
3. **Scope awareness**: Use Section 7 (Affected Entities) to determine which specs to read for understanding correct behavior.
4. **Reproduction**: The first investigation task should verify reproducibility using Section 2 (Steps to Reproduce).
5. **Regression context**: If Section 6 indicates regression, investigation should include checking recent changes (git log) to the affected area.
6. **Impact-proportionate response**: Use Section 8 (Impact Assessment) to calibrate fix scope. A data-loss bug requires more thorough testing than a cosmetic issue.
7. **Traceability**: Include the Bug Report ID (BUG-XXX) in the task generation output summary for cross-referencing.
8. **Fix verification**: Generated fix tasks must include a test case that reproduces the exact bug scenario from Section 2.
9. **Resolution capture**: The final generated task should include filling Section 10 (Root Cause & Resolution) and setting Status to Resolved once the fix is verified.
