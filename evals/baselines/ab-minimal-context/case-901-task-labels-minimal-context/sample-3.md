# Task List — FEAT-001: Task Labels

**Feature Brief:** FEAT-001 (Task Labels, target v1.1, priority High)
**Generated for:** TaskFlow — Express REST API + React SPA, PostgreSQL 16, plain SQL migrations

> **Generation notes (minimal-context arm):** This project has no `docs/data-model/`,
> `docs/api-spec/`, or `docs/ui-specification/` directories yet; the work item and
> CLAUDE.md are the only documentation. Documentation tasks below therefore *bootstrap*
> those spec files (all marked `(new)`), including the Error Catalog and the 12-token
> accent palette that CLAUDE.md and the work item reference but that do not exist yet.
> Task schema follows the canonical schema as inlined in GENERATE.md (the framework
> prompt files were not readable from this case directory).

---

## TASK-001: Document Label and TaskLabel entities in the data model spec

- **Type:** Documentation
- **Workflow:** standard
- **Description:** Create the data model documentation for the two new entities. Bootstrap `docs/data-model/` (it does not exist yet): write `entities/label.md` and `entities/task-label.md`, and create `index.md` with Module Ownership and Relationships Overview entries for both.
- **Rationale:** The work item (Section 6) requires the new-entity shards to exist before feature logic is built; this project has no data model docs at all, so this task also establishes the index they hang off.
- **Acceptance Criteria:**
  - `label.md` specifies: project-scoped ownership; `name` 1–30 chars, unique within a project case-insensitively; `color` restricted to the 12 accent palette tokens; deleting a label cascades to assignments only, never to tasks.
  - `task-label.md` specifies the N:M join between tasks and labels, the max-10-labels-per-task rule, and the rule that a label may only be assigned to a task in the same project.
  - `index.md` contains Module Ownership and Relationships Overview entries for Label and TaskLabel (including their relations to the existing Task and Project entities).
- **Dependencies:** None
- **Complexity:** S
- **Files to Modify/Create:**
  - `docs/data-model/index.md` (new)
  - `docs/data-model/entities/label.md` (new)
  - `docs/data-model/entities/task-label.md` (new)

---

## TASK-002: Document the label API endpoints and error catalog rows

- **Type:** Documentation
- **Workflow:** standard
- **Description:** Create the API spec for the five new label endpoints and the modified board tasks endpoint. Bootstrap `docs/api-spec/` (it does not exist yet): write `endpoints/labels.md`, an `endpoints/tasks.md` covering the board list endpoint with its new `labelId` query parameter, and `index.md` with the Endpoint Summary rows and the Error Catalog entries the routes rely on.
- **Rationale:** The work item (Section 7) requires the endpoint shard before frontend integration, and CLAUDE.md forbids inventing error codes without a catalog row — the catalog itself must be created since no API spec exists in this project.
- **Acceptance Criteria:**
  - `labels.md` documents all five label endpoints (GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, PUT `/api/v1/tasks/{id}/labels`) with request/response envelopes (`{ "data": ... }`, list `meta`), validation rules (name 1–30 chars, color from the 12-token palette, max 10 labels per task), and the 409 `conflict` response for duplicate names.
  - `tasks.md` documents the board list endpoint `GET /api/v1/projects/{projectId}/tasks` including the optional `labelId` filter parameter and the per-task `labels` array in the response.
  - `index.md` contains Endpoint Summary rows for every endpoint above and Error Catalog rows for at least `validation-error`, `conflict` (duplicate label name), and `not-found`.
- **Dependencies:** TASK-001
- **Complexity:** S
- **Files to Modify/Create:**
  - `docs/api-spec/index.md` (new)
  - `docs/api-spec/endpoints/labels.md` (new)
  - `docs/api-spec/endpoints/tasks.md` (new)

---

## TASK-003: Document the Label Management Dialog, LabelChip, and accent palette in the UI spec

- **Type:** Documentation
- **Workflow:** standard
- **Description:** Create the UI specification for the new screen and shared component. Bootstrap `docs/ui-specification/` (it does not exist yet): write `screens/label-management-dialog.md`, create `components.md` with a LabelChip entry (inventorying the existing shared components `dialog`, `empty-state`, and `task-card` while at it), and create `index.md` with a Screen Inventory row for the dialog and a Section 2.1 defining the 12 accent palette tokens.
- **Rationale:** The work item (Section 8) requires the new-screen shard and the LabelChip component entry; the Section 10 constraint references palette tokens in `docs/ui-specification/index.md` Section 2.1, which must be authored here because no UI spec exists yet.
- **Acceptance Criteria:**
  - `label-management-dialog.md` specifies create/rename/recolor/delete flows, the palette picker (12 fixed tokens, no external color-picker dependency), inline duplicate-name error display, and the delete confirmation stating the affected task count.
  - `components.md` documents LabelChip: renders label name + palette color; used by board task cards, the task detail panel picker, and the management dialog; chip text meets WCAG 2.1 AA contrast (4.5:1) on every palette token.
  - `index.md` defines the 12 accent palette tokens (Section 2.1) and adds the Label Management Dialog to the Screen Inventory.
- **Dependencies:** None
- **Complexity:** S
- **Files to Modify/Create:**
  - `docs/ui-specification/index.md` (new)
  - `docs/ui-specification/screens/label-management-dialog.md` (new)
  - `docs/ui-specification/components.md` (new)

---

## TASK-004: Migration for `labels` and `task_labels` tables

- **Type:** Database
- **Workflow:** standard
- **Description:** Add SQL migration `002-task-labels.sql` creating the `labels` table (id, `project_id` FK → projects ON DELETE CASCADE, `name`, `color`, timestamps) and the `task_labels` join table (`task_id` FK → tasks ON DELETE CASCADE, `label_id` FK → labels ON DELETE CASCADE, composite PK).
- **Rationale:** Both new entities from Section 6 need persistence before repositories and endpoints can be built; cascade rules encode "deleting a label removes assignments, never tasks" at the schema level.
- **Acceptance Criteria:**
  - `labels.name` is limited to 30 chars and a unique index on `(project_id, lower(name))` enforces case-insensitive per-project uniqueness (AC-6, edge case "Urgent" vs "urgent").
  - `labels.color` has a CHECK constraint restricting it to the 12 accent palette token values.
  - `task_labels` has composite primary key `(task_id, label_id)` and an index on `label_id` to keep server-side board filtering fast (Section 10 constraint, ≤300ms P95 NFR).
  - Deleting a label row cascades only to `task_labels`; task rows are untouched. Deleting a task cascades its assignments.
  - The max-10-labels-per-task rule is documented as enforced in the application layer (TASK-006).
- **Dependencies:** TASK-001
- **Complexity:** S
- **Files to Modify/Create:**
  - `migrations/002-task-labels.sql` (new)

---

## TASK-005: Label repository module

- **Type:** Backend
- **Workflow:** standard
- **Description:** Create `src/db/label.ts` with all SQL for the Label entity: `listByProject` (including an assigned-task count per label), `getById`, `create`, `update` (rename/recolor), and `delete`. Add a repository unit test against the test database.
- **Rationale:** CLAUDE.md requires SQL to live only in one repository module per entity; the per-label task count is needed by the delete confirmation dialog (AC-5).
- **Acceptance Criteria:**
  - `listByProject` returns each label with its assigned-task count in a single query.
  - `create` and `update` surface the unique-index violation distinctly so the router can map it to the `conflict` error code (case-insensitive duplicates included).
  - `delete` removes the label and relies on the cascade for assignments; the function returns the number of assignments removed.
  - Unit tests in `tests/db/label.test.ts` cover CRUD, case-insensitive duplicate rejection, and delete cascade behavior.
- **Dependencies:** TASK-004
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/db/label.ts` (new)
  - `tests/db/label.test.ts` (new)

---

## TASK-006: TaskLabel repository and board query changes

- **Type:** Backend
- **Workflow:** standard
- **Description:** Create `src/db/task-label.ts` with `replaceForTask(taskId, labelIds)` (transactional replace of a task's label set) and extend the board list query in `src/db/task.ts` to aggregate each task's labels into the row set and accept an optional `labelId` filter.
- **Rationale:** Assignment rules (max 10, same project) belong in the data layer per CLAUDE.md; the Section 10 constraint requires labels to ride along in the existing board response and filtering to stay server-side so pagination remains correct.
- **Acceptance Criteria:**
  - `replaceForTask` runs in a transaction: rejects sets larger than 10 labels and any label not belonging to the task's project, then replaces the assignment set atomically.
  - The board list query returns a `labels` array per task via join/aggregation in the same query — no per-task follow-up queries (Section 10 constraint).
  - An optional `labelId` parameter filters the board query server-side and composes correctly with existing pagination.
  - Unit tests in `tests/db/task-label.test.ts` cover the max-10 rejection, cross-project rejection, and atomic replace; `tests/db/task.test.ts` covers label aggregation and `labelId` filtering.
- **Dependencies:** TASK-004
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/db/task-label.ts` (new)
  - `src/db/task.ts`
  - `tests/db/task-label.test.ts` (new)
  - `tests/db/task.test.ts` (new)

---

## TASK-007: Labels API router

- **Type:** Backend
- **Workflow:** standard
- **Description:** Create `src/api/labels.ts` implementing `GET`/`POST /api/v1/projects/:projectId/labels` and `PUT`/`DELETE /api/v1/labels/:id`, with Zod schemas beside the handlers, and mount it in `src/api/index.ts`. Add Supertest integration tests.
- **Rationale:** These are four of the five new endpoints from Section 7; they must exist before any frontend integration task.
- **Acceptance Criteria:**
  - `GET` returns `{ "data": [...], "meta": { totalCount, page, pageSize } }` with each label carrying its assigned-task count (feeds the AC-5 confirmation dialog); a newly created label appears immediately in the list (AC-1).
  - `POST` validates name (1–30 chars) and color (12-token enum) via Zod; violations map to `validation-error`; a duplicate name within the project (case-insensitive) returns 409 with error code `conflict` (AC-6).
  - `PUT` renames/recolors with the same validation and duplicate handling; concurrent renames resolve last-write-wins, with the stale client picking up the new name on next refresh (Section 9 edge case).
  - `DELETE` removes the label and all its assignments, leaving tasks untouched, and returns the affected-task count for the client notice.
  - Create/rename/delete are restricted to project members with edit rights; the label list is readable by all project members (Section 6).
  - All errors are thrown as `ApiError` and serialized by `src/api/errors.ts`; no raw rows are returned; `tests/api/labels.test.ts` covers every route including the 409 duplicate and delete-cascade cases.
- **Dependencies:** TASK-002, TASK-005
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/api/labels.ts` (new)
  - `src/api/index.ts`
  - `tests/api/labels.test.ts` (new)

---

## TASK-008: Task label assignment endpoint and board `labelId` filter

- **Type:** Backend
- **Workflow:** standard
- **Description:** Extend `src/api/tasks.ts` with `PUT /api/v1/tasks/:id/labels` (replace the task's label set from an array of label IDs) and add the optional `labelId` query parameter to `GET /api/v1/projects/:projectId/tasks`, whose response now includes each task's labels.
- **Rationale:** Completes the Section 7 API surface: the fifth new endpoint plus the modified board endpoint that the board filter (AC-3) and card chips depend on.
- **Acceptance Criteria:**
  - `PUT /api/v1/tasks/:id/labels` validates the body with Zod (array of label IDs); an 11th label or a label from another project returns `validation-error` (Section 9 edge case); on success the response returns the task's updated label set (AC-2).
  - `GET .../tasks` accepts an optional `labelId` query parameter validated by Zod; when present only tasks carrying that label are returned, and pagination/`meta` stay correct (AC-3, Section 10 constraint).
  - Board list responses include a `labels` array per task sourced from the single aggregated query — no extra requests per card (Section 10 constraint).
  - `tests/api/tasks.test.ts` gains cases for replace-set success, max-10 rejection, cross-project rejection, filtered listing, and filter-cleared listing.
- **Dependencies:** TASK-002, TASK-006
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/api/tasks.ts`
  - `tests/api/tasks.test.ts`

---

## TASK-009: LabelChip shared component

- **Type:** Frontend
- **Workflow:** mockup-first
- **Description:** Create the reusable `LabelChip` component rendering a label's name on its palette color, per the component spec from TASK-003. Used by board task cards, the task detail panel picker, and the label management dialog.
- **Rationale:** Section 8 names LabelChip as a new shared component; building it first keeps chip rendering consistent across all three consumers.
- **Acceptance Criteria:**
  - Renders label name and color for any of the 12 palette tokens with chip text meeting WCAG 2.1 AA contrast (4.5:1) on every token (Section 10 NFR).
  - Supports the compact rendering needed by board cards (used in the up-to-3-chips row) and the picker/dialog contexts.
  - Mockup is reviewed against the TASK-003 component spec before implementation is finalized (mockup-first workflow).
  - Component test in `tests/ui/components/label-chip.test.tsx` covers rendering across palette tokens.
- **Dependencies:** TASK-003
- **Complexity:** S
- **Files to Modify/Create:**
  - `src/ui/components/label-chip.tsx` (new)
  - `tests/ui/components/label-chip.test.tsx` (new)

---

## TASK-010: Label Management Dialog

- **Type:** Frontend
- **Workflow:** mockup-first
- **Description:** Create the Label Management Dialog screen (create/rename/recolor/delete labels) reusing the existing `dialog` shared component, opened from a new button in the project board toolbar. Wire mutations through TanStack Query with invalidation of label and board queries.
- **Rationale:** This is the one new screen in Section 8; mockup-first per the work item. Query invalidation is what propagates renames/recolors to every card without a reload (AC-4).
- **Acceptance Criteria:**
  - Creating a label with a name (1–30 chars) and a palette color makes it appear in the project's label list immediately (AC-1).
  - The color picker offers exactly the 12 accent palette tokens and introduces no new external dependency (Section 10 constraint).
  - Submitting a duplicate name shows the server's `conflict` error as an inline message next to the name field (AC-6).
  - Rename/recolor invalidates label and board task queries so every card displaying the label updates without a page reload (AC-4).
  - Delete shows a confirmation dialog stating how many tasks currently carry the label (from the list endpoint's task count) before deleting; after deletion assignments are gone and tasks are untouched (AC-5, Section 9 edge case).
  - Mockup is reviewed against the TASK-003 screen spec before implementation is finalized (mockup-first workflow).
  - `tests/ui/label-management-dialog.test.tsx` covers create, duplicate inline error, rename propagation, and delete confirmation content.
- **Dependencies:** TASK-003, TASK-007, TASK-009
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/ui/label-management-dialog.tsx` (new)
  - `src/ui/project-board.tsx`
  - `tests/ui/label-management-dialog.test.tsx` (new)

---

## TASK-011: Labels field in the task detail panel

- **Type:** Frontend
- **Workflow:** standard
- **Description:** Add a "Labels" field to the task detail panel: a multi-select picker showing LabelChip previews of the project's labels, persisting changes via `PUT /api/v1/tasks/:id/labels` and invalidating the board tasks query.
- **Rationale:** AC-2 requires assigning/removing labels from the detail panel with changes reflected on board cards without a reload; the panel is a modified screen (standard workflow), consuming the mockup-first LabelChip.
- **Acceptance Criteria:**
  - A user can assign and remove labels from the panel; changes persist via the replace-set endpoint and appear on the task's board card without a page reload via TanStack Query invalidation (AC-2).
  - The picker disables further selection once 10 labels are assigned and shows an explanatory tooltip (Section 9 edge case); a rejected 11th assignment from the server is surfaced as a validation message.
  - Picker options render as LabelChip previews in the label's palette color.
  - `tests/ui/task-detail-panel.test.tsx` covers assign, remove, and the 10-label limit behavior.
- **Dependencies:** TASK-008, TASK-009
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/ui/task-detail-panel.tsx`
  - `tests/ui/task-detail-panel.test.tsx` (new)

---

## TASK-012: Board card chips and single-label board filter

- **Type:** Frontend
- **Workflow:** standard
- **Description:** Render label chips on board task cards (up to 3, then a "+N" overflow indicator) using the labels already present in the board tasks response, and add a single-select label filter dropdown to the board toolbar that drives the server-side `labelId` query parameter.
- **Rationale:** Completes AC-3 and the board half of the Section 8 UI impact; server-side filtering keeps results correct with pagination (Section 10 constraint) and card chips come from the existing response, protecting initial board load time.
- **Acceptance Criteria:**
  - Task cards show up to 3 LabelChips plus a "+N" indicator when a task has more; chip data comes from the board tasks response with no per-card fetches (Section 10 constraint).
  - Selecting a label in the toolbar dropdown refetches the board with `labelId` and shows only tasks carrying that label; clearing the filter restores the full board (AC-3).
  - Filtering to a label with zero matching tasks shows the existing `empty-state` component with a "Clear filter" action, not a blank board (Section 9 edge case).
  - If the actively filtered label is deleted by another user, the board refetch clears the filter and shows a notice (Section 9 edge case).
  - Filter round-trip (select → filtered board rendered) meets the <300ms P95 NFR for boards up to 500 tasks (Section 10).
  - `tests/ui/project-board.test.tsx` covers chip overflow, filter/clear behavior, and the zero-match empty state.
- **Dependencies:** TASK-008, TASK-009
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/ui/project-board.tsx`
  - `src/ui/components/task-card.tsx`
  - `tests/ui/project-board.test.tsx` (new)

---

## Acceptance Criteria Coverage

| Work Item AC | Covered By | How |
|---|---|---|
| AC-1 — create label (1–30 chars, palette color), appears in label list | TASK-005, TASK-007, TASK-010 | Repository create; POST endpoint with Zod validation; dialog create flow with immediate list update |
| AC-2 — assign/remove labels from detail panel, persists, board card updates without reload | TASK-006, TASK-008, TASK-011 | Transactional replace-set in repository; PUT `/tasks/:id/labels`; panel picker + TanStack Query invalidation |
| AC-3 — filter board by label, clear restores full board | TASK-006, TASK-008, TASK-012 | Server-side `labelId` in board query; validated query parameter; toolbar filter dropdown with clear action |
| AC-4 — rename/recolor updates every card displaying the label | TASK-007, TASK-010, TASK-012 | PUT label endpoint; dialog mutation invalidating board queries; cards render label data from the board response |
| AC-5 — delete removes label from all tasks after confirmation stating affected task count | TASK-004, TASK-005, TASK-007, TASK-010 | Cascade to assignments only; per-label task count in list; DELETE endpoint; confirmation dialog stating count |
| AC-6 — duplicate name in project → validation error + inline UI message | TASK-004, TASK-007, TASK-010 | Case-insensitive unique index; 409 `conflict` catalog response; inline error on the name field |

### Edge Case Coverage (Section 9)

| Edge Case | Covered By |
|---|---|
| Delete label assigned to tasks — confirm with affected count, tasks untouched | TASK-004, TASK-005, TASK-007, TASK-010 |
| Filter with zero matching tasks — empty state with "Clear filter" | TASK-012 |
| Assigning an 11th label — API validation error; picker disables at 10 with tooltip | TASK-006, TASK-008, TASK-011 |
| Concurrent rename — last write wins, stale client updates on refresh | TASK-007 |
| Duplicate name differing only by case — rejected | TASK-004, TASK-005, TASK-007 |
| Filtered label deleted by another user — refetch clears filter, shows notice | TASK-012 |

---

## Summary

12 tasks generated from Feature Brief **FEAT-001** (Task Labels): 3 documentation tasks bootstrapping the data model, API, and UI specs that this project does not yet have; 1 migration; 3 backend tasks (two repositories, two routers); 5 frontend tasks (2 classified `mockup-first` for the new Label Management Dialog screen and the new LabelChip shared component). Ordering follows the work item's usage notes: entity documentation before feature logic, API tasks before frontend integration. All six acceptance criteria, all six Section 9 edge cases, and all Section 10 constraints are mapped above. Excluded-scope items (global labels, automation, custom hex colors, multi-label filter combinations) have no tasks.
