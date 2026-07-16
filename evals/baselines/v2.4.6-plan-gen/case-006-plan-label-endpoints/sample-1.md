# Implementation Plan: T-002 — Label CRUD endpoints

## Task Reference
- **Task ID:** T-002
- **Type:** Backend
- **Workflow:** standard
- **Complexity:** L
- **Rationale:** AC-1, AC-4, AC-5 and AC-6 need the label management contract.

## Overview
Expose label management as five operations — list, create, rename, recolor, delete — under the project-scoped labels resource, using the standard `{ "data": ... }` envelope and the error catalog from `docs/api-spec/index.md`. T-001 already delivered the `label`/`task_label` tables (unique `(project_id, name)`) and the `src/db/label.ts` repository; this task adds only the HTTP layer and its spec shard.

## Implementation Steps

### Step 1: Create the labels router with Zod schemas and DTO mapping
**File:** `src/api/labels.ts`
**Action:** Create
One Express router per resource (CLAUDE.md Project Structure). Routes live under the `/api/v1` base path (index Section 1.2), nested under the project as the task specifies — five operations across four routes, with PATCH carrying both rename and recolor (mirrors the tasks PATCH partial-update pattern):

| Operation | Method & Path |
|-----------|---------------|
| List | GET `/api/v1/projects/{projectId}/labels` |
| Create | POST `/api/v1/projects/{projectId}/labels` |
| Rename | PATCH `/api/v1/projects/{projectId}/labels/{labelId}` (body: `name`) |
| Recolor | PATCH `/api/v1/projects/{projectId}/labels/{labelId}` (body: `color`) |
| Delete | DELETE `/api/v1/projects/{projectId}/labels/{labelId}` |

In this file define, next to the handlers (CLAUDE.md convention 4): a `LabelDto` mapper (snake_case row → camelCase JSON: `id`, `projectId`, `name`, `color`, `createdAt`, `updatedAt` — confirm exact fields against `docs/data-model/entities/label.md` from T-001; never return raw rows, convention 2) and Zod schemas: create body (`name`, `color` required), update body (`name?`, `color?`, at least one key required), list query (`page`, `pageSize` max 100, per index Section 2.4). All SQL stays in `src/db/label.ts` (convention 5) — handlers only call repository functions and throw `ApiError` with catalog codes (convention 3).

### Step 2: Implement the list and create handlers
**File:** `src/api/labels.ts`
**Action:** Modify
- **GET** — validate query; unknown `projectId` → 404 `not-found` (mirrors the tasks list endpoint); respond `{ "data": LabelDto[], "meta": { totalCount, page, pageSize } }`; default sort `name` ascending (documented per endpoint, index Section 2.4).
- **POST** — validate body (Zod failure → 400 `validation-error`); respond 201 `{ "data": LabelDto }`. Translate the repository's unique-constraint violation on `(project_id, name)` into `ApiError` with catalog code `conflict` (409), message naming the `name` field (index Section 2.5).

### Step 3: Implement the rename/recolor and delete handlers
**File:** `src/api/labels.ts`
**Action:** Modify
- **PATCH** — body must contain at least one of `name`/`color`, else 400 `validation-error` (mirrors the tasks PATCH contract); unknown `labelId`, or a label that does not belong to `:projectId`, → 404 `not-found`; rename that hits the unique constraint → 409 `conflict` as in Step 2; respond 200 `{ "data": LabelDto }` (updated label).
- **DELETE** — same 404 rules; respond **200 with `{ "data": LabelDto }`** (the deleted label) rather than 204, so the operation satisfies AC-1's envelope requirement. Removal of `task_label` join rows follows T-001's FK semantics (see Risks).

### Step 4: Register the labels router
**File:** `src/api/index.ts`
**Action:** Modify
Import the labels router and mount it at the project-nested path alongside the existing resource routers, following the one-router-per-resource layout in CLAUDE.md. Errors continue to flow through the shared middleware in `src/api/errors.ts`.

### Step 5: Write the labels endpoint shard
**File:** `docs/api-spec/endpoints/labels.md`
**Action:** Create
Mirror the structure of `docs/api-spec/endpoints/tasks.md`: frontmatter (`kind: resource`, `resource: labels`, `routes`, `entities: [label, project]`), a "Last verified against code" stamp, a module note pointing at `src/api/labels.ts` and `src/db/label.ts`, a `LabelDto` field table, then one section per route with auth, path/query parameters, request/response examples in the envelope, and status-code tables (200/201; 400 `validation-error`; 401 `unauthorized`; 404 `not-found`; 409 `conflict`). Document that the PATCH route serves both the rename and recolor operations, and note the list's default sort.

### Step 6: Add the labels routes to the endpoint summary and changelog
**File:** `docs/api-spec/index.md`
**Action:** Modify
Required by the index's Usage Note 5 for new resources: add one Endpoint Summary (Section 4) row per route pointing at `endpoints/labels.md`, and a Changelog row recording the labels resource addition.

## Files Affected
| File | Action | Summary |
|------|--------|---------|
| `src/api/labels.ts` | Create | Labels router: list/create/rename/recolor/delete handlers + Zod schemas |
| `src/api/index.ts` | Modify | Register the labels router |
| `docs/api-spec/endpoints/labels.md` | Create | Endpoint shard documenting the five label operations |
| `docs/api-spec/index.md` | Modify | Endpoint Summary rows + Changelog entry (mandated by Usage Note 5) |

## Edge Cases & Risks
- **AC-2 wording vs. catalog:** the AC says "the validation error from the error catalog", but a duplicate name is not a Zod failure — the catalog (index Section 2.5) explicitly assigns duplicate names to `conflict` (409, message names the conflicting field). Implement `conflict`; do not misuse `validation-error` or invent a code (CLAUDE.md convention 3).
- **Repository surface:** `src/db/label.ts` is T-001's deliverable and is not in this task's file list. If it lacks a function this task needs (paged list with total count, create, update, delete), raise the gap instead of putting SQL in the router (convention 5).
- **Duplicate-check race:** do not pre-check name existence in the handler — rely on the DB unique constraint and translate the violation, avoiding a check-then-insert race.
- **Rename no-op:** setting a label's name to its current value must succeed (the row does not conflict with itself).
- **Empty PATCH body:** reject with `validation-error`, mirroring the tasks PATCH contract.
- **`color` format:** validate against the palette-color format defined in `docs/data-model/entities/label.md`; if that shard leaves it open, pick a strict Zod rule and document the accepted format in the labels shard.
- **Cross-project access:** `labelId` under the wrong `projectId` must 404, not operate on another project's label.
- **Delete with assignments:** deleting a label still assigned to tasks depends on T-001's `task_label` FK semantics — confirm cascade behavior before implementing; if there is no cascade, deletion must go through a repository function that removes join rows first. (Affected-task counts for the delete-confirmation UI are owned by later tasks — do not add them here.)

## Acceptance Verification
- [ ] **AC-1 — all five endpoints return the standard envelope:** run the API and exercise all five operations (list, create, rename, recolor, delete), asserting every success response is `{ "data": ... }`, the list adds `meta.totalCount/page/pageSize`, and delete returns 200 with an envelope, not 204. (Automated tests are owned by T-007; this is a manual smoke verification.)
- [ ] **AC-2 — duplicate name returns the catalog error:** create a label, then create another with the same name in the same project → 409 `{ "error": { "code": "conflict", ... } }` with a message naming `name`; renaming a label onto an existing name yields the same error; the same name in a *different* project succeeds.
