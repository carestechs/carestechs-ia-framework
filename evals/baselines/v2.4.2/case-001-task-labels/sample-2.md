# FEAT-001 — Task Labels: Implementation Tasks

> **Work item:** `docs/work-items/FEAT-001-task-labels.md` · **Generated:** 2026-07-15
> Schema: canonical task schema (`prompts/base-template.md`); procedure: `prompts/feature-tasks.md`.

## Foundation

### T-001: Author Label and TaskLabel data-model shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for Label and TaskLabel in the existing shard format (frontmatter, Fields, Indexes, Relationships, Entity-Specific Rules) and register both in the data-model index. Capture the FEAT-001 Section 6 rules: per-project case-insensitive name uniqueness, name 1–30 chars, color restricted to the 12 accent palette tokens, max 10 labels per task, and label deletion cascading to assignments only.

**Rationale:**
FEAT-001 Section 6 requires the new entity shards to exist before feature logic, with Module Ownership and Relationships Overview entries added to `docs/data-model/index.md`.

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` and `docs/data-model/entities/task-label.md` exist and document fields, indexes, relationships, and business rules matching FEAT-001 Section 6
- [ ] Module Ownership (index Section 2) lists both entities under the Projects module with their repository paths (`src/db/label.ts`, `src/db/task-label.ts`)
- [ ] Relationships Overview Section 4.2 records the Task↔Label N:M relationship via `task_labels` with cascade behavior, and the Changelog gains a FEAT-001 row

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard: fields, unique-name rule, palette-token color rule
- docs/data-model/entities/task-label.md (new) - TaskLabel join-entity shard: composite key, max-10 rule, same-project rule
- docs/data-model/index.md - Module Ownership rows, Section 4.2 M:N entry, ER diagram, Changelog

### T-002: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add `migrations/002-labels.sql` creating the `labels` table (UUID `id` PK, `project_id` FK to `projects` with cascade delete, `name varchar(30)`, `color`, `created_at`, `updated_at`) and the `task_labels` join table (composite PK on `task_id` + `label_id`, both FKs with cascade delete). Enforce case-insensitive per-project name uniqueness at the database level.

**Rationale:**
AC-1, AC-5, and AC-6 need persistent storage with database-level uniqueness and cascade guarantees; conventions require plain SQL migrations following the Section 3 naming rules.

**Acceptance Criteria:**
- [ ] Migration applies cleanly on a database migrated through `001-init.sql` and follows data-model Section 3 conventions (snake_case, UUID `id` PK, timestamptz timestamps, explicit varchar limits)
- [ ] Unique index on `(project_id, lower(name))` rejects "Urgent" vs "urgent" in the same project while allowing the same name in different projects
- [ ] Deleting a label or a task removes only `task_labels` rows; deleting a project removes its labels and their assignments; task rows are never touched by label deletion
- [ ] `task_labels` carries an index on `label_id` to support board filtering

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - labels + task_labels tables, unique and filter indexes, FK cascades

**Technical Notes:**
- Store `color` as the accent token identifier (`accent-01` … `accent-12`), not a hex value — the palette stays the single source of truth in the UI spec
- Composite PK `(task_id, label_id)` prevents duplicate assignments structurally
- The max-10-labels-per-task rule is enforced in the application layer (T-006), not as a DB constraint

### T-003: Implement Label and TaskLabel repository modules

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` (list by project with per-label assigned-task counts, create, update, delete) and `src/db/task-label.ts` (atomically replace a task's label set, batch-load labels for a set of task ids). All label SQL lives in these modules per convention 5 — routers never touch `pg` directly.

**Rationale:**
One repository module per entity is the project's data-access convention; the AC-5 confirmation dialog needs per-label task counts and the board needs batch label loading to avoid per-card queries.

**Acceptance Criteria:**
- [ ] `listByProject` returns each label with its assigned-task count (drives the AC-5 confirmation and the management dialog list)
- [ ] `replaceTaskLabels` swaps a task's full label set in one transaction and rejects labels belonging to a different project
- [ ] `labelsForTasks` returns the labels for all supplied task ids in a single query
- [ ] Duplicate-name inserts/updates surface the unique-index violation so the router can map it to the `conflict` error code

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - Label CRUD queries + task counts
- src/db/task-label.ts (new) - assignment replace-set + batch label loading

## Backend

### T-004: Author labels API shard and update the API index

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` documenting all five label endpoints (LabelDto, request/response bodies, status codes) and update `docs/api-spec/endpoints/tasks.md` with the optional `labelId` query parameter and the `labels` array on TaskDto. Add the five Endpoint Summary rows and a Changelog entry to `docs/api-spec/index.md`.

**Rationale:**
FEAT-001 Section 7 requires the new endpoint shard and its Endpoint Summary rows before implementation; envelope and error-catalog discipline come from the API index.

**Acceptance Criteria:**
- [ ] `labels.md` defines GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` with envelopes and status codes reusing only existing catalog codes (`validation-error`, `unauthorized`, `not-found`, `conflict`)
- [ ] `tasks.md` documents `labelId` on the board list endpoint and `labels: LabelDto[]` on TaskDto
- [ ] `index.md` Endpoint Summary gains one row per new endpoint pointing at `endpoints/labels.md`, plus a Changelog row

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - five label endpoints, LabelDto, validation and error mapping
- docs/api-spec/endpoints/tasks.md - labelId query parameter, labels array on TaskDto
- docs/api-spec/index.md - Endpoint Summary rows, Changelog

**Technical Notes:**
- No new error-catalog rows are needed: duplicate name → existing `conflict` (409); palette/name/max-10 violations → `validation-error` (400)

### T-005: Implement label CRUD endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Create the labels router with GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}`, validated with Zod and mounted in `src/api/index.ts`. Responses use the shared envelope; duplicate names (case-insensitive) throw `ApiError` with the `conflict` code, and invalid name length or non-palette color maps to `validation-error`.

**Rationale:**
Provides the server side of AC-1, AC-4, AC-5, and AC-6 exactly as listed in FEAT-001 Section 7.

**Acceptance Criteria:**
- [ ] POST creates a label from a 1–30 char name plus a palette token and returns `{ "data": LabelDto }`; GET returns the project's labels (with task counts) in the list envelope with `meta`
- [ ] Creating or renaming to a name that differs only by case from an existing label in the project returns 409 `conflict`; invalid color or name returns 400 `validation-error` with `fields`
- [ ] PUT renames/recolors with the same validations; concurrent renames resolve last-write-wins with no version check
- [ ] DELETE removes the label and all of its assignments while leaving task rows untouched
- [ ] List is available to any project member; create/rename/recolor/delete require edit rights per FEAT-001 Section 6

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - labels router: four CRUD routes, Zod schemas, ApiError mapping
- src/api/index.ts - mount the labels router

### T-006: Implement task label assignment endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Add PUT `/api/v1/tasks/{id}/labels` to the labels router, replacing the task's full label set from an array of label ids via the T-003 repository helper. Reject requests exceeding 10 labels, labels from another project, and unknown task or label ids.

**Rationale:**
Persists AC-2 assignments and enforces the TaskLabel business rules from FEAT-001 Section 6 (max 10 per task, same-project only).

**Acceptance Criteria:**
- [ ] A valid request replaces the set atomically and returns the task's updated labels in the `data` envelope
- [ ] More than 10 distinct label ids → 400 `validation-error`; a label from another project → 400 `validation-error`; unknown task or label id → 404 `not-found`
- [ ] Duplicate ids in the request body are de-duplicated before the max-10 check

**Dependencies:** T-003, T-004
**Complexity:** S

**Files to Modify/Create:**
- src/api/labels.ts (new) - PUT /tasks/{id}/labels route + Zod schema

### T-007: Add label data and labelId filter to board task queries

**Type:** Backend
**Workflow:** standard

**Description:**
Extend GET `/api/v1/projects/{projectId}/tasks` with an optional `labelId` query parameter filtered server-side through a `task_labels` join, and include each task's labels in TaskDto for both list and single-task responses. Labels are batch-loaded with `labelsForTasks` so the board response carries everything and no per-card fetches are needed.

**Rationale:**
Implements AC-3's server side and the Section 10 constraints: labels ride the existing board response, and filtering stays a query parameter so results remain correct under pagination.

**Acceptance Criteria:**
- [ ] With `labelId`, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count under pagination
- [ ] Without `labelId`, the full board is returned; a `labelId` that does not exist returns 404 `not-found` so clients can detect a concurrently deleted label
- [ ] Every TaskDto in list and single-task responses includes `labels: LabelDto[]`, loaded in one batched query per request
- [ ] Existing response shape (envelope, `meta`, ordering by status/position) is otherwise unchanged

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - labelId Zod query param, pass-through to repository
- src/db/task.ts - optional task_labels join in the board query, labels attached via task-label repository

**Technical Notes:**
- Single joined/aggregated query plus the batched label load must hold the ≤300ms P95 NFR at 500 tasks — relies on the `task_labels(label_id)` index from T-002

## Frontend

### T-008: Author Label Management Dialog UI shard and register LabelChip

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/ui-specification/screens/label-management-dialog.md` (layout sketch, component hierarchy, component→API mapping, States table, interactions) and add its Screen Inventory row plus a Changelog entry to the UI index. Add a LabelChip entry to `components.md` with inputs/outputs and variants.

**Rationale:**
FEAT-001 Section 8 requires the new screen shard, its inventory row, and the LabelChip component-inventory entry before frontend implementation.

**Acceptance Criteria:**
- [ ] The shard follows the existing screen-shard format and its States table covers default, loading, empty, and error per index Section 2.5
- [ ] The delete interaction documents a destructive confirmation stating the affected-task count (AC-5), and duplicate-name errors are specified as inline field messages (AC-6)
- [ ] `index.md` gains the Screen Inventory row and Changelog entry; `components.md` documents LabelChip props and its use on board cards, the detail-panel picker, and the dialog

**Dependencies:** T-004
**Complexity:** S

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - screen shard for the new dialog
- docs/ui-specification/index.md - Screen Inventory row, Changelog
- docs/ui-specification/components.md - LabelChip inventory entry

### T-009: Build LabelChip shared component

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Implement `src/ui/components/label-chip.tsx` rendering the label name on its accent-token background at caption size with `space-1` padding, truncating long names. This introduces the feature's core visual element, so generate an HTML mockup showing the chip across all 12 palette tokens for stakeholder approval before implementing, per `.ai-framework/prompts/mockup-generation.md`.

**Rationale:**
Board cards, the detail-panel picker, and the management dialog (FEAT-001 Section 8) all render chips — one shared component keeps rendering and contrast handling consistent.

**Acceptance Criteria:**
- [ ] Chip text meets WCAG 2.1 AA contrast (4.5:1) on every one of the 12 accent tokens via a per-token text color
- [ ] Colors, spacing, and typography come from design-token CSS custom properties — no hard-coded values
- [ ] Long names truncate with an ellipsis and expose the full name to assistive technology

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component per the components.md entry

### T-010: Build the Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Implement `src/ui/label-management-dialog.tsx` — list, create, rename, recolor, and delete project labels with a 12-token palette swatch picker — and open it from a new BoardToolbar button. The Label Management Dialog is a new screen and needs an approved HTML mockup first, per `.ai-framework/prompts/mockup-generation.md`; the shared `Dialog` component provides the modal shell and the destructive delete confirmation.

**Rationale:**
Delivers the user-facing side of AC-1, AC-4, AC-5, and AC-6; FEAT-001 Section 8 lists this screen as new.

**Acceptance Criteria:**
- [ ] Creating a label makes it appear in the dialog's label list immediately (AC-1), with the 409 duplicate-name response rendered as an inline message at the name field (AC-6)
- [ ] Deleting asks for confirmation stating how many tasks are affected before removing, using the Dialog destructive variant (AC-5)
- [ ] Rename/recolor invalidates the board and task queries so every visible chip updates without a reload (AC-4)
- [ ] Loading, empty (EmptyState with a create CTA), and error states follow index Section 2.5
- [ ] The palette picker uses only the Section 2.1 accent tokens — no external color-picker dependency (Section 10)

**Dependencies:** T-005, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen: label list, create/rename/recolor forms, delete confirmation
- src/ui/project-board.tsx - BoardToolbar button that opens the dialog

### T-011: Add labels picker to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to the Task Detail Panel with a multi-select picker that previews chips and saves the selection via PUT `/api/v1/tasks/{id}/labels`. Invalidate the board tasks query on success so the card's chips update without a page reload.

**Rationale:**
Implements AC-2 — assigning and removing labels from the panel with changes reflected on the board card immediately.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists and the board card updates without a page reload (AC-2)
- [ ] The picker disables further selection at 10 labels and shows an explanatory tooltip (Section 9)
- [ ] A server `validation-error` (e.g. an 11th label submitted from a stale client) surfaces as an inline error on the field
- [ ] Field states follow index Section 2.5: loading skeleton while the label list loads, inline error with retry on failure

**Dependencies:** T-006, T-007, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field, multi-select picker with chip previews, mutation + invalidation

### T-012: Render board label chips and the single-label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 LabelChips per task card with a "+N" overflow indicator, and add a single-select label filter dropdown to the BoardToolbar that drives the `labelId` query parameter server-side. Clearing the filter restores the full board.

**Rationale:**
Delivers AC-3 and the board display from FEAT-001 Section 8; keeping the filter on the query parameter satisfies the Section 10 server-side-filtering constraint.

**Acceptance Criteria:**
- [ ] Cards show at most 3 chips plus a "+N" indicator, rendered from the labels already in the board response — no per-card fetches (Section 10)
- [ ] Selecting a label refetches with `labelId` and shows only matching tasks; clearing the filter restores the full board (AC-3)
- [ ] A filter with zero matching tasks renders EmptyState with a "Clear filter" action, never a blank board (Section 9)
- [ ] If the filtered label was deleted by another user (refetch returns 404), the filter clears automatically and a notice is shown (Section 9)

**Dependencies:** T-005, T-007, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/project-board.tsx - toolbar filter dropdown, labelId in the board query key, filtered empty state, deleted-label notice
- src/ui/components/task-card.tsx - chip row with overflow indicator

**Technical Notes:**
- Filter dropdown options come from GET `/api/v1/projects/{projectId}/labels` (shared with the management dialog via the same query key)

## Testing

### T-013: Write repository unit tests for labels

**Type:** Testing
**Workflow:** standard

**Description:**
Unit-test `src/db/label.ts` and `src/db/task-label.ts` against the test database, mirroring the `src/` tree per convention 6.

**Rationale:**
Every repository gets a unit test by convention; uniqueness, cascade, and atomic-replace rules live at this layer and back AC-5 and AC-6.

**Acceptance Criteria:**
- [ ] Inserting a name differing only by case from an existing label in the same project fails; the same name in another project succeeds
- [ ] Deleting a label removes only its `task_labels` rows, task rows are untouched, and `listByProject` reported the correct task count beforehand (AC-5 data)
- [ ] `replaceTaskLabels` is atomic — a failing replace leaves the previous set intact — and rejects labels from another project
- [ ] `labelsForTasks` returns the correct labels for a mixed set of task ids in one query

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - Label repository unit tests
- tests/db/task-label.test.ts (new) - TaskLabel repository unit tests

### T-014: Write API integration tests for labels and board filtering

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration coverage for the labels router in `tests/api/labels.test.ts` and extend `tests/api/tasks.test.ts` with `labelId` filtering and labels-array cases.

**Rationale:**
Every router gets a Supertest integration test by convention; the acceptance criteria and Section 9 edge cases need verification through the HTTP layer.

**Acceptance Criteria:**
- [ ] Label CRUD happy paths return enveloped LabelDto responses; duplicate names in any casing → 409 `conflict`; invalid color or name length → 400 `validation-error` (AC-1, AC-6)
- [ ] PUT `/tasks/{id}/labels` persists a replacement set (AC-2); an 11th label → 400; a cross-project label → 400; unknown task or label → 404 (Section 9)
- [ ] DELETE removes assignments but not tasks, and subsequent board responses no longer include the label (AC-5)
- [ ] Board list with `labelId` returns only matching tasks with correct `meta.totalCount`; without it, every task includes its `labels` array (AC-3, Section 10)

**Dependencies:** T-005, T-006, T-007
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - labelId filter and labels-array assertions

## Summary

Generated from **FEAT-001 — Task Labels** (`docs/work-items/FEAT-001-task-labels.md`).

**Total tasks: 14, by type**

| Type | Count |
|------|-------|
| Backend | 4 |
| Frontend | 4 |
| Documentation | 3 |
| Testing | 2 |
| Database | 1 |

**Complexity distribution:** S: 5 · M: 6 · L: 3 · XL: 0

**Critical path** (5 tasks): T-001 → T-002 → T-003 → T-005 → T-010 (data-model shards → migration → repositories → label CRUD endpoints → Label Management Dialog). The testing chain T-001 → T-002 → T-003 → T-005 → T-014 has the same length.

**Risks / open questions:**

- GET board with a deleted `labelId` is specified here as 404 `not-found` so the client can detect the deletion, clear the filter, and show the Section 9 notice — confirm this choice while authoring the API shard (T-004).
- Edit-rights enforcement for label create/rename/delete depends on how the external auth service exposes membership roles; the existing tasks router shows no reusable role check, so T-005 may need a brief look at the JWT claims shape.
- `color` is stored as the accent token identifier — renaming palette tokens later would require a data migration.
- The max-10-labels rule is enforced at the API layer only (no DB constraint); concurrent assignment requests could briefly exceed it, which the pilot-scale usage makes acceptable.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label (name 1–30 chars + palette color); it appears in the project's label list immediately | T-005, T-010, T-014 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and appear on the board card without reload | T-006, T-011, T-014 |
| AC-3: Board filter by a selected label shows only matching tasks; clearing restores the full board | T-007, T-012, T-014 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-005, T-010, T-012 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-005, T-010, T-013, T-014 |
| AC-6: Duplicate label name in the same project returns a validation error with an inline UI message | T-005, T-010, T-014 |
