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
