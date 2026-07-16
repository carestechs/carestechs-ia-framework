# Eval Judge

You are an impartial judge grading a generated task list against a fixed rubric.
Read everything below. Do not use any other context. Your entire response must end
with a single JSON object on its own line — no prose after it.

## Rubric

# Judge Rubric — implementation plan for T-002 (Label CRUD endpoints)

Score the candidate plan 1-10 against these six dimensions. The reference output shows
one known-good plan — use it as an anchor for what "good" looks like; the candidate
does not need to match it verbatim, judge substance.

1. **Task fidelity.** The plan covers exactly T-002 — the five label CRUD operations,
   route registration, and the labels endpoint shard — and nothing owned by other
   tasks: no migrations or repository work (T-001), no task-label assignment endpoints
   or task-response changes (T-003), no UI (T-004–T-006), no test suites (T-007).
   Every file in T-002's Files to Modify/Create is covered by at least one step.
2. **Step quality.** ≤ 10 implementation steps, each naming a real file, an explicit
   action (Create / Modify / Delete), and a specific change; steps are in buildable
   dependency order (router and schemas before registration; code before the spec
   shard that documents it). No step is vague ("implement the endpoints") or a
   placeholder.
3. **Conventions fidelity.** Technical details match the project ground truth: routes
   under the `/api/v1` base path; every success response in the `{ "data": ... }`
   envelope with `meta` on lists; errors as catalog codes only — duplicate names map
   to `conflict` (409), schema-validation failures to `validation-error` (400); SQL
   confined to `src/db/` repositories; kebab-case filenames and camelCase JSON keys.
   Penalize contradictions with the ground truth and invented conventions; details
   not derivable from the provided context should be flagged or deferred to a named
   source, not guessed.
4. **Verification.** The plan's verification items map concretely to T-002's two
   acceptance criteria (standard envelope on all five operations; duplicate-name
   error from the error catalog) — checkable actions, not restatements of the ACs.
5. **Budget.** Within the plan budget (≤ ~150 lines, ≤ 10 steps) without padding,
   boilerplate repetition, or pasted spec excerpts that add no planning value.
6. **Plan-ability.** An implementation session could execute the plan without
   re-deriving decisions: routes, status codes, error mapping, response shapes, and
   spec-doc updates are pinned down or explicitly deferred to a named source.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.


## Project ground truth (spec and convention excerpts)

The following excerpts are the project's authoritative conventions and contracts.
Use them to judge spec fidelity: technical details in the candidate (routes, error
codes, envelopes, field names, constraints) must match these — contradictions and
invented conventions are penalized. Judge the output, not the process: the candidate
may not have been shown all of these excerpts.

### ../../feature-tasks/case-001-task-labels/input/CLAUDE.md

# CLAUDE.md — TaskFlow

TaskFlow is a small web-based task tracker (projects, kanban boards, tasks) built as a REST API + SPA.

## Stack

- **Language:** TypeScript (strict mode) across backend and frontend
- **Backend:** Node.js + Express 4, `pg` driver against PostgreSQL 16 (no ORM)
- **Frontend:** React 18 (function components + hooks), Vite, TanStack Query for server state
- **Testing:** Vitest everywhere; Supertest for API integration tests

## Project Structure

| Path | Contents |
|------|----------|
| `src/server.ts` | Express app entry — mounts the router from `src/api/index.ts` |
| `src/api/` | One Express router per resource, e.g. `src/api/tasks.ts`; error middleware in `src/api/errors.ts` |
| `src/db/` | One repository module per entity, e.g. `src/db/task.ts`, `src/db/project.ts` |
| `src/ui/` | One React file per screen, e.g. `src/ui/project-board.tsx`, `src/ui/task-detail-panel.tsx` |
| `src/ui/components/` | Shared React components (inventory: `docs/ui-specification/components.md`) |
| `migrations/` | Plain SQL migrations, numbered `NNN-description.sql`, e.g. `migrations/001-init.sql` |
| `tests/` | Tests mirror `src/`, e.g. `tests/api/tasks.test.ts` |

## Conventions

1. **Naming:** kebab-case filenames (`task-detail-panel.tsx`); PascalCase React components and types; camelCase functions and variables; snake_case database tables and columns. JSON payloads use camelCase keys.
2. **Response envelope:** every success response is `{ "data": ... }`; list responses add `"meta": { "totalCount", "page", "pageSize" }`. Never return raw database rows.
3. **Error handling:** error responses are `{ "error": { "code", "message", "fields?" } }`, where `code` is a stable identifier from the Error Catalog in `docs/api-spec/index.md`. Routers throw `ApiError`; the middleware in `src/api/errors.ts` serializes it. Never invent an error code without adding a catalog row first.
4. **Validation:** every router validates request bodies and query parameters with Zod schemas defined next to the route handlers; validation failures map to the `validation-error` catalog entry.
5. **Data access:** SQL lives only in `src/db/` repository modules — routers never touch `pg` directly. One repository module per entity.
6. **Test location:** tests live under `tests/` mirroring the `src/` tree; every router gets a Supertest integration test and every repository gets a unit test against a test database.

## AI-Assisted Development Framework

This project uses the carestechs IA framework. The prompts live in the framework repo, not in this project.

- Specs are **sharded** under `docs/`: `docs/data-model/`, `docs/api-spec/`, `docs/ui-specification/` — read each spec's `index.md` plus **only** the shards named by the work item's impact tables (kebab-case naming rule). Do not read whole spec directories.
- Work items live in `docs/work-items/`.
- Task generation follows `../../../../../prompts/feature-tasks.md` (relative to this file) together with the canonical task schema in `../../../../../prompts/base-template.md`.
- Generated task lists are written to the location given by the harness instructions (`GENERATE.md` in the case directory), not to `tasks/`.
- This project has no `docs/stakeholder-definition.md` or persona documents — the work item's Feature Scope section is the scope authority.


### ../../feature-tasks/case-001-task-labels/input/docs/api-spec/index.md

# API Specification — TaskFlow

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

## 1. Overview

### 1.1 API Summary

A single Express API under `/api/v1`, JSON only. Every endpoint requires a JWT bearer token issued by the external auth service. All responses use the shared envelope; all errors use stable codes from the Error Catalog.

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Base path | `/api/v1` | Room for breaking changes behind a new prefix |
| Auth mechanism | JWT Bearer tokens (external auth service) | No local credential storage |
| Response envelope | `{ "data": ... }` (+ `"meta"` on lists) | Uniform client parsing |
| Error format | `{ "error": { "code", "message", "fields?" } }` | Stable machine-readable codes |
| Pagination style | Offset with `page` + `pageSize` | Simple; data volumes are small |

---

## 2. Common Conventions

### 2.1 Response Envelope

**Success (list):**

```json
{
  "data": [],
  "meta": { "totalCount": 0, "page": 1, "pageSize": 50 }
}
```

**Single-item responses** are `{ "data": { ... } }` — no `meta`.

### 2.2 Error Response

```json
{
  "error": {
    "code": "validation-error",
    "message": "title must be 1-200 characters",
    "fields": { "title": ["must be 1-200 characters"] }
  }
}
```

`fields` is present only for `validation-error`. Routers throw `ApiError`; `src/api/errors.ts` serializes it.

### 2.3 Authentication

- **Mechanism**: JWT Bearer token in the `Authorization` header — `Authorization: Bearer <token>`
- **Unauthenticated endpoints**: none

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-based) |
| pageSize | int | 50 | Items per page (max 100) |

List responses always include `meta` with `totalCount`, `page`, `pageSize`. Default sort is documented per endpoint.

### 2.5 Error Catalog

> *Stable, machine-readable error codes. Endpoints reference these instead of inventing ad-hoc errors. Add a row before introducing a new code; never repurpose one.*

| Error Code | HTTP Status | When Used | Notes |
|------------|-------------|-----------|-------|
| validation-error | 400 | Request body or query fails Zod validation | `fields` maps field → messages |
| unauthorized | 401 | Missing, expired, or invalid bearer token | Client redirects to login |
| not-found | 404 | Resource does not exist | — |
| conflict | 409 | Uniqueness or state conflict (e.g., duplicate name) | `message` names the conflicting field |

---

## 3. Shared DTOs

None yet — DTOs used by a single resource live in that resource's shard.

---

## 4. Endpoint Summary

> *Quick reference of ALL endpoints across all shards — this table doubles as the shard directory. Add a row here whenever a resource shard gains an endpoint.*

| Method | Path | Module | Auth | Shard | Description |
|--------|------|--------|------|-------|-------------|
| GET | /api/v1/projects/{projectId}/tasks | Projects | Required | `endpoints/tasks.md` | List tasks for the project board |
| GET | /api/v1/tasks/{id} | Projects | Required | `endpoints/tasks.md` | Get a single task |
| PATCH | /api/v1/tasks/{id} | Projects | Required | `endpoints/tasks.md` | Partially update a task |

---

## Usage Notes for AI Task Generation

1. **Shard loading**: Read this index plus ONLY the resource shards named by the work item's impact tables — kebab-case, plural, matching the route segment (e.g., `/api/v1/tasks/{id}` operates on tasks → `endpoints/tasks.md`; nested routes group under the resource being operated on, so `/api/v1/projects/{id}/labels` maps to a `labels` shard). Do not read the whole `endpoints/` directory.
2. **Envelope discipline**: All responses use the envelope in Section 2.1 — never return raw rows.
3. **Error catalog discipline**: Error responses use codes from Section 2.5 — add a catalog row before introducing a new code.
4. **Pagination**: List endpoints must support Section 2.4 parameters and return `meta` totals.
5. **New resources**: Create a new shard at `endpoints/<resource>.md`, add its endpoints to the Endpoint Summary (Section 4), and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-01 | TaskFlow team | Initial version (tasks resource) | v1.0 baseline |


### input/tasks/FEAT-001-tasks.md

# Task List: FEAT-001 Task Labels

## Foundation

### T-001: Create Label and TaskLabel entities with migration

**Type:** Database
**Workflow:** standard

**Description:**
Add the Label entity (project-scoped, name + palette color) and the TaskLabel join table, with a migration and updated data-model shards.

**Rationale:**
AC-1, AC-2 and AC-6 require labels as first-class entities with a uniqueness constraint per project.

**Acceptance Criteria:**
- [ ] Migration creates label and task_label tables with unique (project_id, name)
- [ ] docs/data-model/entities/label.md (new) and docs/data-model/entities/task-label.md (new) written with frontmatter and stamps

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - label and task_label tables
- src/db/label.ts (new) - Label data access
- src/db/task.ts - join helpers for task labels

## Backend

### T-002: Label CRUD endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Implement list/create/rename/recolor/delete label endpoints under /api/projects/:id/labels using the standard envelope and error catalog.

**Rationale:**
AC-1, AC-4, AC-5 and AC-6 need the label management contract.

**Acceptance Criteria:**
- [ ] All five endpoints return the standard envelope
- [ ] Duplicate name within a project returns the validation error from the error catalog

**Dependencies:** T-001
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - label route handlers
- src/api/index.ts - register label routes
- docs/api-spec/endpoints/labels.md (new) - endpoint shard

### T-003: Task label assignment endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Add assign/remove label operations on tasks and include labels in task list/detail responses.

**Rationale:**
AC-2 and AC-3 require label data on tasks and mutation endpoints.

**Acceptance Criteria:**
- [ ] Assign and remove operations persist and return the updated task
- [ ] Task list responses include label ids for board filtering

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - label assignment routes and response shape
- docs/api-spec/endpoints/tasks.md - document response changes

## Frontend

### T-004: Label management dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Build the label management dialog (create, rename, recolor, delete with confirmation) using the shared dialog component and the Section 2.1 palette tokens.

**Rationale:**
AC-1, AC-4 and AC-5 are exercised through this dialog.

**Acceptance Criteria:**
- [ ] Create/rename/recolor/delete flows work against the label endpoints
- [ ] Delete shows a confirmation stating how many tasks are affected
- [ ] Duplicate-name error shows an inline validation message

**Dependencies:** T-002
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog component
- docs/ui-specification/screens/label-management-dialog.md (new) - screen shard

### T-005: Labels on task detail panel and board cards

**Type:** Frontend
**Workflow:** standard

**Description:**
Show and edit labels from the task detail panel; render label chips on board cards without a page reload.

**Rationale:**
AC-2 requires assignment from the detail panel with immediate board reflection.

**Acceptance Criteria:**
- [ ] Labels can be assigned/removed from the detail panel and persist
- [ ] Board card chips update without a page reload

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - label assignment UI
- src/ui/project-board.tsx - label chips on cards
- src/ui/components/task-card.tsx - chip rendering

### T-006: Board label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a label filter to the project board that narrows visible tasks to those carrying the selected label, with a clear-filter control.

**Rationale:**
AC-3 defines the filtering behavior.

**Acceptance Criteria:**
- [ ] Selecting a label shows only tasks carrying it
- [ ] Clearing the filter restores the full board

**Dependencies:** T-003, T-005
**Complexity:** M

**Files to Modify/Create:**
- src/ui/project-board.tsx - filter control and filtered rendering

## Testing

### T-007: Label API and UI regression tests

**Type:** Testing
**Workflow:** standard

**Description:**
Cover label CRUD, assignment, duplicate-name validation, and delete-confirmation flows with API tests and UI tests.

**Rationale:**
Locks in AC-1 through AC-6 against regressions.

**Acceptance Criteria:**
- [ ] API tests cover CRUD, assignment, and duplicate-name error
- [ ] UI test covers filter select/clear and delete confirmation

**Dependencies:** T-002, T-003, T-004, T-005, T-006
**Complexity:** M

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - label API tests
- tests/api/tasks.test.ts - assignment coverage

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: create label with name and palette color | T-001, T-002, T-004 |
| AC-2: assign/remove labels from detail panel | T-003, T-005 |
| AC-3: board label filter | T-003, T-006 |
| AC-4: rename/recolor updates every card | T-002, T-004, T-005 |
| AC-5: delete with confirmation | T-002, T-004 |
| AC-6: duplicate name validation error | T-001, T-002, T-004 |


## Reference output (known-good anchor)

The candidate does NOT need to match this verbatim — it anchors what "good" looks
like. Judge substance, not wording.

<!-- Known-good reference output — the judge check's anchor. Not a golden string to
     match verbatim; a demonstration of a plan that satisfies the rubric. -->

# Implementation Plan: T-002 — Label CRUD endpoints

## Task Reference
- **Task ID:** T-002
- **Type:** Backend
- **Workflow:** standard
- **Complexity:** L
- **Rationale:** AC-1, AC-4, AC-5 and AC-6 need the label management contract.
- **Dependencies:** T-001 (complete) — the `label` and `task_label` tables, the Label
  entity shard, and the label repository (`src/db/label.ts`, new in T-001) already
  exist when this plan runs.

## Overview
Expose label management for a project over HTTP: list, create, rename, recolor, and
delete labels. The five operations map onto four `/api/v1` routes — rename and recolor
are both partial updates on `PATCH /api/v1/labels/{id}`, mirroring the tasks resource's
PATCH pattern. No schema or migration work belongs here; T-001 owns the tables and the
repository.

## Implementation Steps

### Step 1: Create the labels router skeleton with validation schemas
**File:** `src/api/labels.ts` (new)
**Action:** Create
Create an Express router following the structure of `src/api/tasks.ts` (one router per
resource — CLAUDE.md Project Structure). Define Zod schemas next to the handlers
(CLAUDE.md convention 4): `labelCreateSchema` (`name` + `color`, both required) and
`labelUpdateSchema` (`name?`, `color?`, at least one required). Mirror the name/color
constraints from the Label entity shard `docs/data-model/entities/label.md` (new in
T-001) rather than inventing new ones. All SQL goes through the T-001 label repository —
the router never touches `pg` (convention 5).

### Step 2: Implement GET /api/v1/projects/{projectId}/labels (list)
**File:** `src/api/labels.ts`
**Action:** Modify
List the project's labels. Support `page`/`pageSize` per index Section 2.4 and return
the list envelope `{ "data": [LabelDto], "meta": { "totalCount", "page", "pageSize" } }`.
Unknown `projectId` → `ApiError` `not-found` (404).

### Step 3: Implement POST /api/v1/projects/{projectId}/labels (create)
**File:** `src/api/labels.ts`
**Action:** Modify
Validate the body with `labelCreateSchema` (failures → `validation-error`, 400). On a
duplicate name within the project, throw `ApiError` with catalog code `conflict` (409) —
the catalog's uniqueness-conflict entry, with `message` naming the `name` field (index
Section 2.5). On success return 201 with `{ "data": LabelDto }`.

### Step 4: Implement PATCH /api/v1/labels/{id} (rename / recolor)
**File:** `src/api/labels.ts`
**Action:** Modify
Partial update accepting `name` and/or `color`; an empty body is `validation-error`
(400), the same rule as `PATCH /api/v1/tasks/{id}`. Renaming to a name already used in
the same project → `conflict` (409). Unknown id → `not-found` (404). Return
`{ "data": LabelDto }` with the updated label.

### Step 5: Implement DELETE /api/v1/labels/{id}
**File:** `src/api/labels.ts`
**Action:** Modify
Delete through the repository; `task_label` rows are cleaned up by the schema T-001
defined — no extra queries here. Unknown id → `not-found` (404). Return 200 with
`{ "data": LabelDto }` (the deleted label), not 204, so the fifth operation also
satisfies the envelope requirement.

### Step 6: Register the labels router
**File:** `src/api/index.ts`
**Action:** Modify
Mount the labels router alongside the tasks router so its routes resolve under the
`/api/v1` base path (index Section 1.2). Errors keep flowing to the `ApiError`
middleware in `src/api/errors.ts` — no new error handling here.

### Step 7: Write the labels endpoint shard
**File:** `docs/api-spec/endpoints/labels.md` (new)
**Action:** Create
New resource shard mirroring `docs/api-spec/endpoints/tasks.md`: frontmatter
(`kind: resource`, `resource: labels`,
`routes: [/api/v1/projects/{projectId}/labels, /api/v1/labels/{id}]`,
`entities: [label, project]`), a LabelDto table, and one section per route with
parameters, request/response envelopes, and status-code tables that reference catalog
codes only.

### Step 8: Update the API spec index
**File:** `docs/api-spec/index.md`
**Action:** Modify
Add the new routes to the Endpoint Summary (Section 4) pointing at
`endpoints/labels.md`, and record the addition in the Changelog — the index's usage
note 5 requires both for new resources. No new error codes are introduced, so the
Error Catalog is untouched.

## Files Affected
| File | Action | Summary |
|------|--------|---------|
| `src/api/labels.ts` | Create | Labels router: Zod schemas + list/create/update/delete handlers |
| `src/api/index.ts` | Modify | Register the labels router |
| `docs/api-spec/endpoints/labels.md` | Create | New labels resource shard (frontmatter, LabelDto, route sections) |
| `docs/api-spec/index.md` | Modify | Endpoint Summary rows + Changelog entry |

## Edge Cases & Risks
- **Duplicate names on rename, not just create** — renaming to an existing name
  violates the same `(project_id, name)` uniqueness as creating one; both paths must
  map the repository's uniqueness violation to `conflict` (409), never a raw driver
  error.
- **"Validation error from the error catalog" (task AC)** — the catalog maps duplicate
  names to `conflict` (409), not `validation-error` (400); follow the catalog (index
  Section 2.5). Zod failures (missing name, unknown color token, empty PATCH body) are
  the 400 `validation-error` cases.
- **Delete must keep the envelope** — return 200 with `{ "data": ... }`, not
  204 No Content, or the fifth operation fails AC-1.
- **Scope boundary** — assigning labels to tasks and label data in task responses
  belong to T-003; the delete-confirmation "affected tasks" count is T-004's UI
  concern. Nothing in this plan adds either.

## Acceptance Verification
- [ ] AC-1 (standard envelope): against a dev server, exercise all five operations —
  list, create, rename, recolor, delete — and confirm every success response is
  `{ "data": ... }`, with `meta` present on the list response only.
- [ ] AC-2 (duplicate name): create label `bug` twice in one project → the second
  returns 409 `{ "error": { "code": "conflict", ... } }` with a message naming `name`;
  rename another label to `bug` → same 409; create `bug` in a different project →
  succeeds.
- [ ] Doc consistency: the new routes appear in the index Endpoint Summary, the shard's
  frontmatter matches its routes, and no error code outside the catalog appears in the
  shard.

## Rollback
Revert is contained: delete `src/api/labels.ts` and `docs/api-spec/endpoints/labels.md`,
revert the `src/api/index.ts` registration and the two `docs/api-spec/index.md` edits.
No migration or data changes to unwind — T-001 owns the schema.


## Candidate output (under evaluation)

# Implementation Plan: T-002 — Label CRUD endpoints

## Task Reference
- **Task ID:** T-002
- **Type:** Backend
- **Workflow:** standard
- **Complexity:** L
- **Rationale:** AC-1, AC-4, AC-5 and AC-6 need the label management contract.

## Overview
Implement the label management API for TaskFlow: list, create, rename, recolor, and delete labels scoped to a project, all using the standard `{ "data": ... }` envelope and Error Catalog codes from `docs/api-spec/index.md`, and documented as a new api-spec shard. Dependency T-001 is complete: the `label`/`task_label` tables (`migrations/002-labels.sql`), the entity shards, and the `src/db/label.ts` repository this task builds on are already delivered. T-002 delivers only the HTTP contract — task-side assignment (T-003) and all UI (T-004–T-006) are out of scope.

## Implementation Steps

### Step 1: Create the labels router with the endpoint contract, DTO, and validation schemas
**File:** `src/api/labels.ts`
**Action:** Create
Create an Express router (`Router({ mergeParams: true })` so `projectId` from the mount path is visible) implementing the five operations. The task's `/api/projects/:id/labels` resolves under the spec's `/api/v1` base path (index §1.2):

| Operation | Method & Path | Success |
|-----------|---------------|---------|
| List | `GET /api/v1/projects/{projectId}/labels` | 200, `data[]` + `meta` |
| Create | `POST /api/v1/projects/{projectId}/labels` | 201, `data` |
| Rename | `PATCH /api/v1/projects/{projectId}/labels/{labelId}` — body `{ "name" }` | 200, `data` |
| Recolor | `PATCH /api/v1/projects/{projectId}/labels/{labelId}` — body `{ "color" }` | 200, `data` |
| Delete | `DELETE /api/v1/projects/{projectId}/labels/{labelId}` | 200, `data` |

Rename and recolor share one `PATCH` handler accepting `{ name?, color? }` (at least one key), mirroring the partial-update pattern of `PATCH /api/v1/tasks/{id}` in `docs/api-spec/endpoints/tasks.md`. Delete returns `200` with an envelope body (`{ "data": { "id": ... } }`), never `204`, so all five operations satisfy AC-1.

Define `LabelDto` with camelCase JSON keys (CLAUDE.md convention 1), mapped from repository rows — never raw rows (convention 2): `id`, `projectId`, `name`, `color`, `taskCount`, `createdAt`, `updatedAt`. `taskCount` (count of `task_label` rows) belongs to the management contract because T-004's delete confirmation must state how many tasks are affected. Define Zod schemas next to the handlers (convention 4): `createLabelSchema` (`name` and `color` required), `updateLabelSchema` (`name?`/`color?`, refined to require at least one), and a list-query schema (`page`, `pageSize` per index §2.4, `pageSize` max 100). Take `name` length and allowed palette `color` values from the label entity shard `docs/data-model/entities/label.md` (delivered by T-001). Zod failures throw `ApiError` with code `validation-error` (400) so the middleware in `src/api/errors.ts` serializes them (convention 3).

### Step 2: Implement the collection endpoints (list, create)
**File:** `src/api/labels.ts`
**Action:** Modify
`GET /` — validate the query, return `not-found` (404) if the project does not exist, then fetch the project's labels via `src/db/label.ts` (SQL lives only in repositories, convention 5) sorted by `name` ascending, and respond with `{ "data": LabelDto[], "meta": { totalCount, page, pageSize } }` per index §2.1/§2.4. `POST /` — validate the body, insert via the repository, respond `201` with `{ "data": LabelDto }`. Map the repository's unique-violation on `(project_id, name)` to `ApiError` with code `conflict` (409) and a message naming the `name` field — the catalog row for duplicate names (index §2.5).

### Step 3: Implement the item endpoints (rename/recolor, delete)
**File:** `src/api/labels.ts`
**Action:** Modify
`PATCH /:labelId` — validate the body (at least one of `name`/`color`), return `not-found` (404) if the label does not exist within this project; on rename, apply the same duplicate-name → `conflict` mapping as create; respond `{ "data": LabelDto }` with the updated label. `DELETE /:labelId` — `not-found` (404) if missing; delete via the repository (join rows in `task_label` are removed by the migration's cascade — verify, see Risks); respond `200` with `{ "data": { "id": labelId } }` to keep the envelope (AC-1).

### Step 4: Register the labels router
**File:** `src/api/index.ts`
**Action:** Modify
Import the labels router and mount it at `/projects/:projectId/labels` on the API router that `src/server.ts` mounts (CLAUDE.md Project Structure), alongside the existing tasks registration. All label routes require the JWT bearer auth already applied to the API (index §2.3) — no new auth code.

### Step 5: Create the labels endpoint shard
**File:** `docs/api-spec/endpoints/labels.md`
**Action:** Create
Mirror the structure of `docs/api-spec/endpoints/tasks.md`: frontmatter (`kind: resource`, `resource: labels`, `routes`, `entities: [label, task-label, project]`), a "Last verified against code" stamp, the `LabelDto` table, and one section per operation with auth, path/query parameters, request/response examples using the §2.1 envelope, and status-code tables referencing only catalog codes (`validation-error`, `unauthorized`, `not-found`, `conflict`). Document the default sort (`name` ascending) and the create status (`201`).

### Step 6: Register the new shard in the spec index
**File:** `docs/api-spec/index.md`
**Action:** Modify
Per the index's Usage Note 5, add the five label endpoints to the Endpoint Summary (Section 4) pointing at `endpoints/labels.md`, and add a Changelog row. This file is not in the task's file list, but the api-spec conventions require it whenever a shard gains endpoints — skipping it leaves the new shard unreachable from the shard directory.

## Files Affected
| File | Action | Summary |
|------|--------|---------|
| `src/api/labels.ts` | Create | Labels router: five CRUD operations, Zod schemas, envelope + catalog error mapping |
| `src/api/index.ts` | Modify | Mount the labels router at `/projects/:projectId/labels` |
| `docs/api-spec/endpoints/labels.md` | Create | Labels resource shard documenting all five operations |
| `docs/api-spec/index.md` | Modify | Endpoint Summary rows + Changelog entry (required by index Usage Note 5) |

## Edge Cases & Risks
- **AC-2 wording vs. catalog:** the AC says "validation error", but the Error Catalog (index §2.5) explicitly maps uniqueness conflicts such as duplicate names to `conflict` (409); `validation-error` is reserved for Zod failures (CLAUDE.md convention 4). Use `conflict` — it is the catalog's error for duplicates; never invent a new code without a catalog row (convention 3).
- **Duplicate-detection race:** do not pre-check then insert; rely on the DB unique constraint on `(project_id, name)` and map the unique-violation surfaced by `src/db/label.ts` to `conflict`. Applies to both create and rename.
- **Empty `PATCH` body:** `{}` must fail with `validation-error` (400), mirroring the "at least one field" rule of `PATCH /api/v1/tasks/{id}`.
- **Delete with assignments:** verify `migrations/002-labels.sql` cascades `task_label` rows on label delete; if it does not, the repository must delete join rows in the same transaction, or deletes of in-use labels fail on FK violations.
- **Cross-project access:** `:labelId` lookups must be scoped by `projectId` — a label belonging to another project returns `not-found`, not another project's data.
- **Same name in different projects:** allowed — uniqueness is per project; create and rename must both permit it.
- **T-004 integration:** the delete-confirmation dialog needs the number of affected tasks; `taskCount` in `LabelDto` covers this now so the contract does not churn mid-FEAT-001.

## Acceptance Verification
- [ ] **AC-1 — all five endpoints return the standard envelope:** exercise list, create, rename, recolor, and delete against a seeded project; every success response is `{ "data": ... }`, the list response includes `meta` with `totalCount`/`page`/`pageSize`, and delete returns `200` with an envelope body (not `204`).
- [ ] **AC-2 — duplicate name returns the error-catalog error:** create label "Bug" twice in one project — the second attempt returns `409 { "error": { "code": "conflict", "message": ... } }` naming the `name` field; renaming another label to "Bug" returns the same; creating "Bug" in a different project succeeds.
- [ ] Routes are reachable through the `src/server.ts` → `src/api/index.ts` mount chain, and a request without a bearer token returns `unauthorized` (401).
- [ ] `docs/api-spec/endpoints/labels.md` documents all five operations and the spec index's Endpoint Summary and Changelog reference it.


## Verdict contract

Score the candidate 1-10 against the rubric (use the rubric's own scoring guide).
Final line, JSON only, exactly this shape:
{"score": <integer 1-10>, "reasons": ["<short reason>", "..."]}
