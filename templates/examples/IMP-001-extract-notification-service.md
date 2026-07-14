<!-- Reference example — for real work items, copy the blank template from docs/work-items/, not this file. -->

# Improvement Proposal: Extract Notification Service

> **Product**: TaskFlow — a small web-based task tracker (projects, tasks, labels, notifications) with a REST API backend and SPA frontend.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | IMP-001 |
| **Name** | Extract Notification Service |
| **Type** | Maintainability |
| **Status** | Approved <!-- enum: Proposed · Approved · In Progress · Completed · Deferred · Rejected --> |
| **Priority** | Medium |
| **Estimated Effort** | L <!-- S = hours · M = 1-2 days · L = up to a week · XL = multi-week --> |
| **Proposed By** | Tech lead, following the post-mortem of the duplicate-notification incident (2026-02-24) |
| **Date Created** | 2026-03-02 |

---

## 2. Target Area

**Component / Module:** Backend notification dispatch — currently inlined in three API controllers

**Affected Files / Directories:**
- `backend/src/tasks/tasks.controller` (assignment + due-date notifications)
- `backend/src/comments/comments.controller` (mention + reply notifications)
- `backend/src/projects/project-members.controller` (invite + role-change notifications)
- `backend/src/shared/email-client` (SMTP wrapper each controller calls directly)
- New: `backend/src/notifications/` (target home of the extracted service)

---

## 3. Current State

### How It Works Today

Each controller that triggers a notification builds it inline: it resolves recipients, checks the recipient's notification preferences, formats the message, and calls the SMTP client and/or inserts an in-app `Notification` row — all inside the request handler, synchronously before the HTTP response is returned.

### Problems

1. **Triplicated recipient/preference logic**: Recipient resolution and the unsubscribe/preference check exist in three near-identical copies; they have already drifted (comment mentions ignore the "muted project" preference, task assignment respects it)
2. **Controllers coupled to delivery**: Request handlers depend directly on the SMTP client, so a slow mail server inflates API response times (task assignment P95 is 850ms vs 210ms for comparable writes)
3. **Untestable in isolation**: Controller tests must mock the SMTP client and the Notification repository in every suite — 14 separate mock setups across the test codebase
4. **Inconsistent channel behavior**: Task assignment sends email + in-app; comment mentions send email only; member invites send in-app only — differences are accidental, not designed

### Evidence

- Incident 2026-02-24: PR #190 fixed the unsubscribe check in `tasks.controller` but missed the other two copies → users who had opted out kept receiving mention emails for six days (see incident review notes)
- API latency dashboard: task-assignment endpoint P95 850ms, dominated by synchronous SMTP round-trip
- 14 duplicated SMTP/repository mock setups counted across `backend/src/**/__tests__`

---

## 4. Desired State

### Target Implementation

A single `NotificationService` in `backend/src/notifications/` owns recipient resolution, preference checks, channel selection (email / in-app), and dispatch. Controllers call one method (`notify(event)`) with a typed domain event and return immediately; delivery runs after the response (outbox table drained by the existing background worker). The SMTP client becomes an implementation detail of the service.

### Benefits

1. **Single source of truth**: One copy of recipient + preference logic; a fix like PR #190 lands in exactly one place
2. **Fast request paths**: Controllers no longer wait on SMTP; expected task-assignment P95 back near the ~210ms write baseline
3. **Testable seams**: Controller tests assert "event emitted"; delivery logic gets its own focused test suite — the 14 mock setups collapse into one
4. **Deliberate channel policy**: Channel selection is declared per event type in one table, making today's accidental inconsistencies visible and fixable

---

## 5. Trigger and Motivation

**Trigger:** FEAT-006 (Daily digest notifications) needs notification aggregation, which is impractical while dispatch is scattered across three controllers — it would require a fourth copy of the logic.

**Impact if deferred:** FEAT-006 either duplicates the logic again (fourth copy, higher drift risk) or gets blocked; the duplicate-notification incident class remains open — the same fix-one-miss-two failure mode can recur with any preference change.

**Dependencies on this improvement:** FEAT-006 (Daily digest notifications) is blocked by this; BUG-001-class fixes touching notification behavior become single-site changes afterwards.

---

## 6. Affected Entities and Components

| Entity / Component | What Changes | Spec Reference |
|--------------------|-------------|----------------|
| TasksController | Inline dispatch replaced by `NotificationService.notify()` call | `docs/api-spec.md` §3 Tasks (no contract change) |
| CommentsController | Same extraction; mention logic moves to the service | `docs/api-spec.md` §3 Comments (no contract change) |
| ProjectMembersController | Same extraction; invite/role-change logic moves | `docs/api-spec.md` §3 Projects (no contract change) |
| NotificationService (new) | New backend component owning resolution, preferences, channels, dispatch | `docs/ARCHITECTURE.md` §3.2 — new component entry required |
| Notification entity | Unchanged schema; writes move from controllers to the service | `docs/data-model.md` §3 (Notification) |
| NotificationOutbox (new) | New table backing post-response delivery | `docs/data-model.md` — new entity required |

---

## 7. Risk Assessment

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Behavior change slips in during extraction (recipients, wording, channels) | Medium | High | Characterization tests first (Phase 0) capturing current recipients/channels per event; extraction must keep them green — including the known inconsistencies, which are fixed separately afterwards |
| Outbox delivery delays notifications noticeably | Low | Medium | Worker polls every 5s (existing worker cadence); alert if outbox lag exceeds 60s |
| Notifications lost if process dies between response and dispatch | Low | High | Outbox row is written in the same DB transaction as the triggering change; worker retries with backoff |
| Merge conflicts with FEAT-001 (labels) touching `tasks.controller` | Medium | Low | Migrate `tasks.controller` last; coordinate merge order with the labels branch |

### Rollback Strategy

Per-controller migration behind a config flag (`notifications.useService`, per event type). Old inline path stays intact until all three controllers are migrated and the flag has been on in production for a week; rollback = flip the flag. Cleanup phase deletes the inline paths only after that soak period.

---

## 8. Constraints

- No user-observable change to notification content, recipients, or channels in the extraction phases (channel-policy fixes come after, as a separate follow-up)
- No change to public API contracts — request/response shapes and status codes stay identical
- Incrementally deployable — one controller per PR, system fully working after each merge
- No new external dependencies (no message broker; reuse the existing background worker for the outbox)

---

## 9. Success Criteria

- All notification dispatch flows through `NotificationService`; zero direct `email-client` imports remain in controllers (enforced by a lint rule)
- Recipient/preference logic exists in exactly one module, covered by its own test suite
- Task-assignment endpoint P95 ≤ 300ms (from 850ms) with SMTP out of the request path
- Characterization tests confirm identical recipients and channels for all six event types before vs after
- The 14 duplicated SMTP mock setups in controller tests are removed
- `docs/ARCHITECTURE.md` and `docs/data-model.md` updated (NotificationService component, NotificationOutbox entity) in the same PRs

---

## 10. Current Test Coverage

| Area | Coverage | Notes |
|------|----------|-------|
| `tasks.controller` notification paths | Partial | Happy path only; no test for preference/unsubscribe branch (the PR #190 gap) |
| `comments.controller` notification paths | Partial | Mention parsing tested; delivery branch mocked out entirely |
| `project-members.controller` notification paths | None | No tests touch invite notifications |
| `shared/email-client` | Good | Unit-tested against a local SMTP stub |
| In-app Notification creation | Partial | Repository tested; controller-level insertion untested |

Low coverage on the exact logic being moved → expect a substantial Phase 0 (characterization/safety-net) task set before any extraction.

---

## 11. Traceability

| Reference | Link |
|-----------|------|
| **Triggered By** | Duplicate-notification incident post-mortem (2026-02-24) + FEAT-006 planning |
| **Stakeholder Alignment** | Guiding principle "Quiet by default — users only get notifications they asked for" (`docs/stakeholder-definition.md` §3.1) |
| **Architecture Reference** | `docs/ARCHITECTURE.md` §3.2 (backend components), §4.1 (write-path data flow) |
| **Related Work Items** | FEAT-001 (Task Labels — shared file `tasks.controller`, coordinate merges) |
| **Blocked Features** | FEAT-006 (Daily digest notifications) |

---

## 12. Usage Notes for AI Task Generation

When generating refactoring/improvement tasks from this Improvement Proposal:

1. **Safety-first phasing**: Always generate Phase 0 (test coverage) tasks based on Section 10 before any refactoring tasks. Lower coverage = more safety-net tasks.
2. **Problem-driven**: Each generated task should address a specific problem from Section 3. Don't generate tasks that don't map to a stated problem.
3. **Incremental approach**: Use the risks in Section 7 to determine phasing. High-risk improvements should use parallel implementation (old + new coexist) before migration.
4. **Constraint respect**: All constraints in Section 8 must be respected — especially backward compatibility and deployment strategy.
5. **Success verification**: Generate a final verification task that checks all success criteria from Section 9.
6. **No feature creep**: This is an improvement, not a feature. Do not generate tasks that add new functionality. If new behavior is needed, it belongs in a separate Feature Brief.
7. **Rollback awareness**: Each phase should leave the system in a working state. Reference the rollback strategy from Section 7 in migration tasks.
8. **Traceability**: Include the Improvement Proposal ID (IMP-XXX) in the task generation output summary for cross-referencing.
