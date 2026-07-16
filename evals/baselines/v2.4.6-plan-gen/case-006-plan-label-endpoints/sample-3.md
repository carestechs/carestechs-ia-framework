# Implementation Plan: T-002 — Label CRUD endpoints

## Task Reference
- **Task ID:** T-002
- **Type:** Backend
- **Workflow:** standard
- **Complexity:** L
- **Rationale:** AC-1, AC-4, AC-5 and AC-6 need the label management contract.

## Overview
Expose project-scoped label management over REST: list, create, rename, recolor, and delete labels under `/api/v1/projects/{projectId}/labels`, giving the label management dialog (T-004) a stable contract. The task delivers the labels router, registers it in the API index, and documents the new resource as an api-spec shard. Dependency T-001 is complete: the `(project_id, name)`-unique schema and the label repository (`src/db/label.ts`) are already delivered.

## Implementation Steps

### Step 1: Create the labels router
**File:** `src/api/labels.ts`
**Action:** Create

Export an Express `Router({ mergeParams: true })` (routes nest under `/projects/:projectId`, so handlers must see `projectId`). The task's five operations map onto four routes — rename and recolor are the two partial-update operations of one PATCH route, mirroring the existing `PATCH /api/v1/tasks/{id}` pattern:

| Operation | Route | Success response |
|-----------|-------|------------------|
| List | `GET /api/v1/projects/{projectId}/labels` | 200 `{ "data": LabelDto[], "meta": { totalCount, page, pageSize } }` |
| Create | `POST /api/v1/projects/{projectId}/labels` | 201 `{ "data": LabelDto }` |
| Rename | `PATCH /api/v1/projects/{projectId}/labels/{labelId}` body `{ "name" }` | 200 `{ "data": LabelDto }` |
| Recolor | `PATCH /api/v1/projects/{projectId}/labels/{labelId}` body `{ "color" }` | 200 `{ "data": LabelDto }` |
| Delete | `DELETE /api/v1/projects/{projectId}/labels/{labelId}` | 200 `{ "data": null }` |

`LabelDto` (camelCase JSON keys per CLAUDE.md naming): `id`, `projectId`, `name`, `color`, `taskCount` (number of tasks currently carrying the label — T-004's delete confirmation needs it, and T-002 co-covers AC-5), `createdAt`, `updatedAt`.

Implementation notes:
- Zod schemas live next to the handlers (CLAUDE.md convention 4): create body `{ name, color }`, both required; update body `{ name?, color? }` with an at-least-one-key refinement; list query `{ page, pageSize }` per api-spec index Section 2.4 (`pageSize` max 100). `name` is trimmed, 1–100 chars; `color` follows the palette-color format defined in the T-001 entity shard `docs/data-model/entities/label.md` (align both constraints with that shard if it differs).
- All data access goes through the T-001 repository `src/db/label.ts` — routers never touch `pg` (CLAUDE.md convention 5).
- List is sorted by `name` ascending (documented as the endpoint's default sort, per index Section 2.4).
- DELETE returns 200 with `{ "data": null }`, not 204 — AC-1 requires the Section 2.1 envelope on all five operations.
- Errors are thrown as `ApiError` with catalog codes only, serialized by `src/api/errors.ts` (CLAUDE.md convention 3): Zod failure → `validation-error` 400 with `fields`; unknown `projectId`/`labelId`, or a label belonging to another project → `not-found` 404; duplicate name within the project on create or rename → `conflict` 409 with a message naming `name`.

### Step 2: Register the labels router
**File:** `src/api/index.ts`
**Action:** Modify

Mount the new router alongside the existing per-resource routers so it resolves under the `/api/v1` base path: `router.use('/projects/:projectId/labels', labelsRouter)` — one Express router per resource, per the CLAUDE.md project structure. The existing JWT bearer auth (api-spec index Section 2.3) must cover these routes exactly as it covers tasks.

### Step 3: Write the labels endpoint shard
**File:** `docs/api-spec/endpoints/labels.md`
**Action:** Create

Mirror the structure of `docs/api-spec/endpoints/tasks.md`: frontmatter (`kind: resource`, `resource: labels`, `routes: [/api/v1/projects/{projectId}/labels, /api/v1/projects/{projectId}/labels/{labelId}]`, `entities: [label, task-label, project]`), a "Last verified against code" stamp, a module note pointing at `src/api/labels.ts` and `src/db/label.ts`, the `LabelDto` table, then one section per route with auth/roles (GET: any project member; POST/PATCH/DELETE: project member with edit rights, mirroring tasks), path/query/body parameters, response examples, and status-code tables (200/201 success; 400 `validation-error`; 401 `unauthorized`; 404 `not-found`; 409 `conflict`). Document rename and recolor as the two PATCH operations, and note that deleting a label also removes its `task_label` assignment rows (T-001 cascade).

### Step 4: Register the new endpoints in the spec index
**File:** `docs/api-spec/index.md`
**Action:** Modify

Mandated by the spec's own rule for new resources (index Usage Notes, item 5): add the four routes to the Section 4 Endpoint Summary (Module: Projects, Shard: `endpoints/labels.md`) and add a Changelog row. Nothing else in the index changes — the Section 2.5 error catalog already contains every code these endpoints use.

## Files Affected
| File | Action | Summary |
|------|--------|---------|
| `src/api/labels.ts` | Create | Labels router: list/create/rename/recolor/delete handlers + Zod schemas |
| `src/api/index.ts` | Modify | Mount the labels router at `/projects/:projectId/labels` |
| `docs/api-spec/endpoints/labels.md` | Create | New resource shard documenting the label endpoint contract |
| `docs/api-spec/index.md` | Modify | Endpoint Summary rows + Changelog entry for the labels resource |

## Edge Cases & Risks
- **Duplicate-name error code:** AC-2 says "the validation error from the error catalog"; the catalog's designated code for uniqueness conflicts is `conflict` (409 — its own example is "duplicate name"), while `validation-error` is reserved for Zod failures. Use `conflict` with a message naming `name`; never invent a new code (CLAUDE.md convention 3). T-004 can render `error.message` as its inline message.
- **Uniqueness race:** do not rely on a pre-insert SELECT alone — also catch the DB unique-violation from the T-001 `(project_id, name)` constraint surfaced by the repository and map it to `conflict`, so concurrent creates cannot both succeed.
- **Cross-project access:** a `labelId` that exists but belongs to a different project returns `not-found` — never mutate or leak another project's label.
- **Empty PATCH body:** `{}` fails the at-least-one-key refinement → `validation-error`, mirroring `PATCH /api/v1/tasks/{id}`.
- **Delete with assignments:** deletion cascades to `task_label` rows (T-001 migration); `taskCount` in `LabelDto` lets T-004's confirmation state how many tasks are affected. Risk: if the delivered T-001 repository exposes no usage count, flag the gap against T-001 rather than modifying `src/db/*` (outside this task's file list).
- **Case sensitivity:** uniqueness behavior follows the T-001 DB constraint exactly — the API must not layer a different comparison rule on top of it.

## Acceptance Verification
- [ ] **AC-1 — all five endpoints return the standard envelope:** against a dev server (e.g., with curl), exercise list, create, rename, recolor, and delete; every success body matches index Section 2.1 — `{ "data": ... }`, the list adds `meta` with `totalCount`/`page`/`pageSize`, and delete returns 200 with the envelope rather than a bodyless 204.
- [ ] **AC-2 — duplicate name returns the catalog error:** create label "Bug" twice in one project → the second create returns 409 `{ "error": { "code": "conflict", "message": "…name…" } }`; rename another label to "Bug" → same `conflict`; create "Bug" in a different project → succeeds (uniqueness is per project).
