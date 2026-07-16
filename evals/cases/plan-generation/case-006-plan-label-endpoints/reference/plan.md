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
