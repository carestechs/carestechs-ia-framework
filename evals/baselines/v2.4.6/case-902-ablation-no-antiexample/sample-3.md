# FEAT-001 — Task Labels: Implementation Task List

> Generated from Feature Brief `docs/work-items/FEAT-001-task-labels.md` (FEAT-001, target v1.1) using the canonical task schema from `prompts/base-template.md`. File paths are relative to the project root; files that do not exist yet are suffixed `(new)`.

## Foundation

### T-001: Document the Label and TaskLabel entities in the data model

**Type:** Documentation
**Workflow:** standard

**Description:**
Create entity shards for Label and TaskLabel following the existing shard format (frontmatter, Fields, Indexes, Relationships, entity-specific rules), and register both in the data-model index. Label is project-scoped with a name (varchar(30), unique case-insensitively within the project) and one of the 12 accent palette color tokens; TaskLabel is the N:M join between tasks and labels.

**Rationale:**
Feature Brief Section 6 requires the new entity shards and their index entries to exist before feature logic; the index's Module Ownership table doubles as the shard directory.

**Acceptance Criteria:**
- [ ] Both shards exist with frontmatter, Fields, Indexes, Relationships, and business rules matching Feature Brief Section 6 (max 10 labels per task; same-project assignment; delete cascades to assignments only, never to tasks)
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities, a Section 4.2 many-to-many entry (Task ↔ Label via `task_labels`), an updated ER diagram, and a Changelog row
- [ ] Naming follows Section 3 conventions: tables `labels` and `task_labels`, snake_case columns, UUID `id` PKs, timestamptz timestamps

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard (fields, indexes, relationships, rules)
- docs/data-model/entities/task-label.md (new) - TaskLabel join-entity shard
- docs/data-model/index.md - Module Ownership rows, Section 4.2 M:N entry, ER diagram, Changelog

**Technical Notes:**
- Color is stored as the palette token identifier (e.g. `accent-07`), not a hex value — the UI resolves tokens to CSS custom properties
- Repository mapping per convention: `src/db/label.ts` and `src/db/task-label.ts`, owned by the Projects module

### T-002: Create the labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add a SQL migration creating `labels` (id, project_id FK → projects with cascade delete, name varchar(30), color varchar(16), created_at, updated_at) and `task_labels` (task_id + label_id composite PK, FKs with cascade delete on both sides, timestamps). Include a unique index on `(project_id, lower(name))` and an index on `task_labels(label_id)` for board filtering.

**Rationale:**
AC-1 and AC-6 need persisted project-scoped labels with case-insensitive name uniqueness; Section 6 cascade rules require label deletion to remove assignments only.

**Acceptance Criteria:**
- [ ] Running migrations/002-add-labels.sql against a database at 001 creates both tables with the constraints and indexes above
- [ ] Inserting two labels in one project whose names differ only by case violates the unique index (edge case 5)
- [ ] Deleting a label row removes its `task_labels` rows and leaves `tasks` rows untouched; deleting a task removes its assignments

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- migrations/002-add-labels.sql (new) - create labels and task_labels tables, unique + filter indexes

**Technical Notes:**
- The 10-labels-per-task cap is enforced in the application layer (repository/router), not as a database constraint
- Both tables carry `created_at`/`updated_at` per the Section 3 convention, even though `task_labels` rows are effectively immutable

### T-003: Implement the label and task-label repository modules

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` with label queries (list-by-project including each label's assigned-task count, create, rename/recolor, delete) and `src/db/task-label.ts` with assignment queries (labels for a task, transactional replace of a task's label set, task count for a label). Surface case-insensitive duplicate-name violations as a distinct error the router can map to the `conflict` catalog code.

**Rationale:**
CLAUDE.md convention 5 — SQL lives only in `src/db/` repository modules, one per entity; the assigned-task count powers the AC-5 delete confirmation.

**Acceptance Criteria:**
- [ ] All label CRUD and assignment SQL lives in these two modules; no router touches `pg` directly
- [ ] Replacing a task's label set is transactional and rejects sets larger than 10 or containing labels from a different project
- [ ] The label list query returns assigned-task counts in a single query (no N+1)
- [ ] Unique-index violations are distinguishable from other query failures

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label CRUD queries + list with assigned-task counts
- src/db/task-label.ts (new) - assignment queries, transactional replace, per-label task count

## Backend

### T-004: Document the labels API and tasks endpoint changes

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the labels resource shard documenting all five label endpoints (list, create, rename/recolor, delete, and the nested PUT /api/v1/tasks/{id}/labels) with a LabelDto, and update the tasks shard (optional `labelId` query parameter; TaskDto gains an embedded `labels` array) and the index's Endpoint Summary and Changelog.

**Rationale:**
Feature Brief Section 7 requires the endpoint shard and its Endpoint Summary rows before implementation; the summary table doubles as the shard directory.

**Acceptance Criteria:**
- [ ] `docs/api-spec/endpoints/labels.md` documents all five endpoints with request/response schemas, roles, status codes, and only existing Error Catalog codes (validation-error, unauthorized, not-found, conflict — duplicate name → 409 `conflict`)
- [ ] LabelDto on the list endpoint includes an `assignedTaskCount` field to power the AC-5 delete confirmation
- [ ] `docs/api-spec/endpoints/tasks.md` documents the `labelId` query parameter and the `labels` array embedded in TaskDto (board list and single GET)
- [ ] `docs/api-spec/index.md` Endpoint Summary gains rows for the new endpoints and the Changelog records the change

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - five label endpoints + LabelDto
- docs/api-spec/endpoints/tasks.md - labelId query parameter; labels array in TaskDto
- docs/api-spec/index.md - Endpoint Summary rows, Changelog

**Technical Notes:**
- No new Error Catalog codes are needed — max-10 and cross-project violations map to `validation-error` (400), duplicate names to `conflict` (409)
- Document the label list default sort (name ascending) and standard pagination per index Section 2.4
- Roles mirror the existing tasks endpoints: reads for any project member; create/rename/delete for members with edit rights (Section 6)

### T-005: Build the labels CRUD router

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET and POST `/api/v1/projects/{projectId}/labels` plus PUT and DELETE `/api/v1/labels/{id}`, with Zod validation next to the handlers (name 1–30 chars after trimming; color one of the 12 accent tokens), and mount it in `src/api/index.ts`.

**Rationale:**
Server side of AC-1, AC-4, AC-5, and AC-6, per the Section 7 API impact table.

**Acceptance Criteria:**
- [ ] POST creates a label and GET lists the project's labels in the standard envelope with `meta` totals and `assignedTaskCount` per label
- [ ] POST/PUT with a duplicate name (case-insensitive) returns 409 `conflict`; invalid name or color returns 400 `validation-error` with `fields`
- [ ] DELETE removes the label and all its assignments, leaving tasks untouched; unknown project or label returns 404 `not-found`
- [ ] Concurrent renames resolve last-write-wins with no version conflict error (edge case 4)

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - labels router: list, create, rename/recolor, delete
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Throw `ApiError` and let `src/api/errors.ts` serialize; never return raw rows
- Enforce edit-rights on POST/PUT/DELETE the same way PATCH /api/v1/tasks/{id} does

### T-006: Add the task label-assignment endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Implement PUT `/api/v1/tasks/{id}/labels` in `src/api/tasks.ts`, replacing the task's full label set from a body containing an array of label IDs via the task-label repository, and returning the updated task with its labels.

**Rationale:**
Persistence path for AC-2; enforces the Section 6 business rules (max 10 labels per task, labels and task must share a project).

**Acceptance Criteria:**
- [ ] PUT replaces the label set atomically and the response includes the updated labels
- [ ] Submitting an 11th label returns 400 `validation-error` (edge case 3); a label from another project returns 400 `validation-error`
- [ ] Unknown task returns 404 `not-found`; duplicate IDs in the array are deduplicated rather than rejected

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - add the PUT /api/v1/tasks/{id}/labels route with Zod body schema

**Technical Notes:**
- Zod schema: array of UUID strings, max length 10 (after dedupe), validated before the repository call

### T-007: Embed labels in board responses and add labelId filtering

**Type:** Backend
**Workflow:** standard

**Description:**
Extend the board list query in `src/db/task.ts` to aggregate each task's labels in the same query and honor an optional `labelId` filter, and extend `src/api/tasks.ts` so the list endpoint validates the new query parameter and both the list and single-task endpoints include `labels` in TaskDto.

**Rationale:**
AC-3 plus the Section 10 constraints — labels ride the existing board response (no per-card fetch) and filtering stays server-side so pagination remains correct.

**Acceptance Criteria:**
- [ ] The board list returns each task's labels (id, name, color) aggregated in one query — no per-task follow-up queries
- [ ] `labelId=<uuid>` returns only tasks carrying that label with a correct `meta.totalCount`; omitting it returns the full board (AC-3)
- [ ] GET /api/v1/tasks/{id} includes the task's labels for the detail panel
- [ ] A malformed `labelId` returns 400 `validation-error`

**Dependencies:** T-002, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - aggregate labels into board rows; optional labelId predicate
- src/api/tasks.ts - labelId query validation; labels in TaskDto responses

**Technical Notes:**
- Use a LEFT JOIN with `json_agg` (or a lateral subquery) to keep a single round-trip; the `task_labels(label_id)` index supports the filter
- Watch the Section 10 NFR: filter round-trip under 300ms at P95 for boards up to 500 tasks

## Frontend

### T-008: Document the UI changes across screens and components

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the Label Management Dialog screen shard and add a LabelChip entry to the shared component inventory; update the project-board and task-detail-panel shards (label chips + filter dropdown; Labels field) and the UI index (Screen Inventory row, Changelog).

**Rationale:**
Feature Brief Section 8 — new screens need a shard and Screen Inventory row, and the modified screens' Component → API mappings must stay current before frontend work begins.

**Acceptance Criteria:**
- [ ] `docs/ui-specification/screens/label-management-dialog.md` documents layout, component hierarchy, Component → API mapping, all four states (Section 2.5), and interactions including the destructive delete confirmation with affected-task count
- [ ] `docs/ui-specification/components.md` gains a LabelChip entry with inputs/outputs and variants (default, compact, "+N" overflow)
- [ ] `screens/project-board.md` and `screens/task-detail-panel.md` reflect chips on cards, the toolbar filter dropdown, the Labels field, and their new API calls
- [ ] `docs/ui-specification/index.md` gains the Screen Inventory row and a Changelog entry

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/components.md - LabelChip shared-component entry
- docs/ui-specification/screens/project-board.md - chips on cards + label filter in toolbar
- docs/ui-specification/screens/task-detail-panel.md - Labels field with multi-select picker
- docs/ui-specification/index.md - Screen Inventory row, Changelog

### T-009: Create the LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Build `src/ui/components/label-chip.tsx` rendering a label's name on its accent palette color using design tokens (caption typography, `space-1` padding), with a compact variant and a "+N" overflow affordance for dense card rows.

**Rationale:**
Section 8 defines LabelChip as the one shared chip used by board cards, the detail panel, and pickers — a single component keeps rename/recolor rendering consistent (AC-4).

**Acceptance Criteria:**
- [ ] Chip renders the label name and color from the 12 accent tokens via CSS custom properties — no hard-coded hex values
- [ ] Chip text color meets WCAG 2.1 AA contrast (4.5:1) on every palette token (Section 10 NFR)
- [ ] The overflow variant renders "+N" for hidden labels and exposes the full list to assistive tech

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip: default, compact, and "+N" overflow variants

**Technical Notes:**
- Per-token text color (light/dark) is part of the design-token mapping so AA contrast holds on every accent color
- CSS Modules for styling, consistent with the existing in-house components

### T-010: Build the Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Implement `src/ui/label-management-dialog.tsx` — list, create, rename, recolor, and delete project labels with a 12-token palette picker, inline duplicate-name errors, and a destructive delete confirmation stating how many tasks are affected. This is a new user-facing screen: generate an HTML mockup of the Label Management Dialog for stakeholder approval before implementing, per `.ai-framework/prompts/mockup-generation.md`.

**Rationale:**
UI side of AC-1, AC-4, AC-5, and AC-6; Section 8 marks this screen New, which triggers the mockup-first workflow.

**Acceptance Criteria:**
- [ ] Creating a label makes it appear immediately in the project's label list (AC-1)
- [ ] Rename and recolor persist and update chips everywhere via TanStack Query invalidation (AC-4)
- [ ] Delete uses the shared Dialog destructive variant and states the affected task count (from `assignedTaskCount`) before confirming (AC-5)
- [ ] A duplicate name shows an inline validation message from the 409 response without closing the dialog (AC-6)
- [ ] Loading, empty, and error states follow index Section 2.5 (EmptyState when the project has no labels yet)

**Dependencies:** T-005, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - label CRUD dialog with palette picker and delete confirmation

**Technical Notes:**
- Color picker is built from the accent tokens in `docs/ui-specification/index.md` Section 2.1 — no new external dependencies (Section 10)
- Reuse shared Dialog (destructive variant) and EmptyState; mutations invalidate both the labels query and the board query

### T-011: Add the Labels field to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field with a multi-select picker showing LabelChip previews to `src/ui/task-detail-panel.tsx`, backed by the project labels list and PUT `/api/v1/tasks/{id}/labels`, invalidating the board query so the card updates without a page reload.

**Rationale:**
AC-2 — assigning and removing labels happens in the detail panel and must be reflected on the board card immediately.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists via the PUT endpoint and the board card updates without a reload (AC-2)
- [ ] The picker disables further selection at 10 labels with an explanatory tooltip (edge case 3)
- [ ] Picker options render as LabelChips and the field follows the panel's loading/error state patterns

**Dependencies:** T-005, T-006, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field with multi-select chip picker

**Technical Notes:**
- Follows the existing additive form-field pattern in the panel, so `standard` workflow applies rather than mockup-first

### T-012: Render board label chips and the label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 LabelChips with a "+N" overflow indicator on task cards in `src/ui/components/task-card.tsx`, and add a single-select label filter dropdown plus a "Manage labels" entry point (opening the Label Management Dialog) to the board toolbar in `src/ui/project-board.tsx`, passing `labelId` to the board query.

**Rationale:**
AC-3 and the Section 8 Project Board changes; the toolbar is the entry point for the Label Management Dialog.

**Acceptance Criteria:**
- [ ] Cards show up to 3 chips plus "+N" overflow, sourced from the labels embedded in the board response — no per-card fetching (Section 10)
- [ ] Selecting a label refetches the board server-side and shows only matching tasks; clearing the filter restores the full board (AC-3)
- [ ] A filter with zero matching tasks shows the standard EmptyState with a "Clear filter" action (edge case 2)
- [ ] If the filtered label was deleted by another user, the board refetch clears the filter and shows a notice (edge case 6)

**Dependencies:** T-005, T-007, T-009, T-010
**Complexity:** L

**Files to Modify/Create:**
- src/ui/project-board.tsx - label filter dropdown, Manage-labels entry point, labelId in the board query
- src/ui/components/task-card.tsx - render up to 3 LabelChips + "+N" overflow

**Technical Notes:**
- Keep `labelId` in component state feeding the TanStack Query key so filter changes refetch server-side
- Detect the deleted-filter case by the selected `labelId` disappearing from the labels list response

## Testing

### T-013: Write repository unit tests for labels

**Type:** Testing
**Workflow:** standard

**Description:**
Add unit tests against the test database for the label and task-label repositories and the extended board query, covering CRUD, duplicate detection, the transactional replace rules, cascades, and label filtering with pagination.

**Rationale:**
CLAUDE.md convention 6 — every repository gets a unit test; the modified board query in `src/db/task.ts` also needs coverage.

**Acceptance Criteria:**
- [ ] Label repository covered: create, rename/recolor, delete, list with `assignedTaskCount`
- [ ] Duplicate names differing only by case are rejected (edge case 5); an 11th label and cross-project labels are rejected by the replace operation (edge case 3)
- [ ] Deleting a label removes its assignments and leaves tasks untouched (edge case 1)
- [ ] Board query returns aggregated labels and correct `labelId` filtering with accurate totals across pages

**Dependencies:** T-003, T-007
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - assignment/replace/count unit tests
- tests/db/task.test.ts (new) - board query label aggregation + filter tests

### T-014: Write API integration tests for the label endpoints

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests for the labels router and extend the tasks API tests for PUT `/api/v1/tasks/{id}/labels` and `labelId` filtering, asserting response envelopes, Error Catalog codes, and status codes.

**Rationale:**
CLAUDE.md convention 6 — every router gets a Supertest integration test; verifies AC-1, AC-3, AC-5, and AC-6 at the API boundary.

**Acceptance Criteria:**
- [ ] Happy paths pass: create/list/rename/recolor/delete labels, replace a task's label set, filtered board list with `meta` totals
- [ ] Error paths pass: 409 `conflict` on case-insensitive duplicate names, 400 `validation-error` on bad name/color, 11th label, and cross-project labels, 404 `not-found` on unknown IDs
- [ ] All responses assert the standard envelope — `data` plus `meta` on lists, `error.code` on failures

**Dependencies:** T-005, T-006, T-007
**Complexity:** M

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - PUT /tasks/{id}/labels and labelId filter cases

### T-015: Write frontend component tests for the label UI

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for LabelChip, the Label Management Dialog, the panel's Labels picker, and the board filter, covering chip rendering, inline duplicate errors, the delete confirmation, the 10-label cap, and filter edge cases.

**Rationale:**
Task guidance requires testing at all levels; these verify the UI halves of AC-2 through AC-6.

**Acceptance Criteria:**
- [ ] LabelChip renders name/color per token and the "+N" overflow variant
- [ ] Dialog shows the inline duplicate-name error (AC-6) and the delete confirmation with the affected task count (AC-5)
- [ ] Picker disables at 10 labels with a tooltip; board filter shows the EmptyState with "Clear filter" and clears itself when the filtered label disappears (edge cases 2, 3, 6)

**Dependencies:** T-010, T-011, T-012
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/label-chip.test.tsx (new) - chip rendering + overflow tests
- tests/ui/label-management-dialog.test.tsx (new) - CRUD, inline error, delete confirmation tests
- tests/ui/task-detail-panel.test.tsx (new) - Labels picker behavior tests
- tests/ui/project-board.test.tsx (new) - chips on cards + filter behavior tests

## Summary

**Traceability:** FEAT-001 (Task Labels), Feature Brief `docs/work-items/FEAT-001-task-labels.md`.

**Total task count by type:** 15 tasks — Backend 4 (T-003, T-005, T-006, T-007), Frontend 4 (T-009–T-012), Documentation 3 (T-001, T-004, T-008), Testing 3 (T-013–T-015), Database 1 (T-002).

**Complexity distribution:** S ×3 (T-001, T-002, T-009), M ×10 (T-003–T-008, T-011, T-013–T-015), L ×2 (T-010, T-012), XL ×0.

**Critical path:** T-001 → T-002 → T-003 → T-005 → T-010 → T-012 → T-015 (7 tasks). A parallel documentation chain (T-001 → T-004 → T-008 → T-009) feeds T-010 and can proceed alongside the database/backend chain.

**Risks and open questions:**

- The Section 7 API table defines no endpoint for the AC-5 affected-task count; this list resolves it by adding `assignedTaskCount` to the label list response (documented in T-004). Worth a reviewer's confirmation.
- The Section 10 NFR (filter round-trip < 300ms at P95 for 500-task boards) has no performance harness in the project; T-007 addresses it structurally (single aggregated query + `task_labels(label_id)` index) but measurement remains open.
- Concurrent renames use last-write-wins with no version field, per edge case 4 — stale clients reconcile on the next board refetch.
- Monitoring/logging: no dedicated task — the existing `ApiError` middleware path covers error reporting, and the project defines no logging infrastructure to extend.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label with a name (1–30 chars) and palette color; it immediately appears in the project's label list | T-005, T-010, T-014 |
| AC-2: Assign and remove labels on a task from the detail panel; changes persist and appear on the board card without a page reload | T-006, T-011, T-015 |
| AC-3: Selecting a label in the board filter shows only tasks carrying that label; clearing the filter restores the full board | T-007, T-012, T-014 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-005, T-010, T-012 |
| AC-5: Deleting a label removes it from all tasks after an explicit confirmation stating how many tasks are affected | T-003, T-005, T-010, T-014 |
| AC-6: Creating a duplicate label name within the same project returns a validation error and the UI shows an inline message | T-005, T-010, T-014 |
