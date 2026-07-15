# Feature Tasks: FEAT-001 — Task Labels

## Task Generation Summary

Generated from Feature Brief **FEAT-001** (Task Labels, target v1.1, priority High). 13 tasks in four groups, ordered data model → backend API → frontend → tests, with spec shards authored before the feature logic that implements them (Section 13, notes 3–4 of the brief). This project has no pre-existing spec documentation, so the shards named by the brief's impact tables (Sections 6–8) — including the data-model, API-spec, and UI-specification indexes — are created by tasks T-001, T-004, and T-008. Frontend tasks for the new Label Management Dialog screen and the new LabelChip component are classified `mockup-first` per Section 8; all other tasks are `standard`. Scope is limited to Section 4.1; nothing is generated for Section 4.2 exclusions (no cross-project labels, no automation, no custom hex colors, no multi-label filter combinations).

## Group 1: Data Model

### T-001: Author data-model spec shards for Label and TaskLabel

**Type:** Documentation
**Workflow:** standard
**Description:** Create the data-model spec shards for the new Label entity and the TaskLabel join entity, and create the data-model index with Module Ownership and Relationships Overview entries for both.
**Rationale:** Section 6 of the brief requires the new-entity shards to exist before feature logic is generated; this project has no spec documentation yet, so `docs/data-model/index.md` must be created alongside the entity shards.
**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` defines Label as project-scoped with a name (1–30 chars, unique within its project case-insensitively) and a color that must be one of the 12 accent palette tokens
- [ ] `docs/data-model/entities/task-label.md` defines the N:M task–label join with a maximum of 10 labels per task and the rule that an assignment requires task and label to belong to the same project
- [ ] Deletion semantics are documented: deleting a label cascades to its assignments only, never to tasks
- [ ] `docs/data-model/index.md` contains Module Ownership and Relationships Overview entries for Label and TaskLabel
**Dependencies:** None
**Complexity:** S
**Files to Modify/Create:**
- docs/data-model/entities/label.md (new)
- docs/data-model/entities/task-label.md (new)
- docs/data-model/index.md (new)
**Technical Notes:** No shards are created for Task or Project: the brief states task fields do not change; the new relationships are captured in `task-label.md` and the index's Relationships Overview.

### T-002: Migration for labels and task_labels tables

**Type:** Database
**Workflow:** standard
**Description:** Add a SQL migration creating the `labels` table (id, project_id, name, color, created_at) and the `task_labels` join table (task_id, label_id, composite primary key), with the constraints and indexes the business rules require.
**Rationale:** Persistence for the new entities defined in T-001; the unique index is the authoritative enforcement of case-insensitive name uniqueness (AC-6), and the join-table index keeps server-side board filtering inside the 300ms P95 budget (Section 10 NFR).
**Acceptance Criteria:**
- [ ] `migrations/002-task-labels.sql` creates `labels` with a foreign key to `projects` and `task_labels` with foreign keys to `tasks` and `labels`
- [ ] A unique index on `(project_id, lower(name))` rejects duplicate label names differing only by case within a project
- [ ] `color` is CHECK-constrained to the 12 accent palette token names
- [ ] Deleting a label cascades to `task_labels` rows only; deleting a task cascades to its `task_labels` rows; no label operation deletes tasks
- [ ] `task_labels(label_id)` is indexed to support the board label filter
**Dependencies:** T-001
**Complexity:** M
**Files to Modify/Create:**
- migrations/002-task-labels.sql (new)
**Technical Notes:** The max-10-labels-per-task rule is enforced in the repository/API layer (T-003, T-006), not as a database constraint; snake_case table and column names per project conventions.

### T-003: Label repository module

**Type:** Backend
**Workflow:** standard
**Description:** Create the `src/db/label.ts` repository module with all label SQL: list labels for a project (each with its assigned-task count), create, rename/recolor, delete (returning the number of assignments removed), and replace the full label set of a task.
**Rationale:** Project convention keeps SQL only in `src/db/` repository modules — one per entity; the per-label task count feeds the delete confirmation dialog (AC-5), and set-replacement backs the `PUT /api/v1/tasks/{id}/labels` endpoint.
**Acceptance Criteria:**
- [ ] `listByProject` returns each label with a `taskCount` of currently assigned tasks
- [ ] Create and rename detect duplicate names case-insensitively within the project and surface a distinct conflict result for the router to map to 409
- [ ] Delete removes the label and its assignments only, returning the count of affected tasks; tasks themselves are untouched
- [ ] Replacing a task's label set is atomic (single transaction), enforces the 10-label maximum, and rejects labels belonging to a different project than the task
- [ ] No `pg` usage outside this module for label data access
**Dependencies:** T-002
**Complexity:** M
**Files to Modify/Create:**
- src/db/label.ts (new)

## Group 2: Backend API

### T-004: API spec shards for label endpoints and the modified board endpoint

**Type:** Documentation
**Workflow:** standard
**Description:** Create the API spec shard documenting all five label endpoints, the shard for the tasks endpoints documenting the board list's new optional `labelId` query parameter and the labels array on returned tasks, and the API spec index with its Endpoint Summary and Error Catalog.
**Rationale:** Section 7 requires new endpoints to be documented in `docs/api-spec/endpoints/labels.md` with summary rows in `docs/api-spec/index.md` before frontend integration; CLAUDE.md forbids using an error code without an Error Catalog row, and no catalog exists yet in this project.
**Acceptance Criteria:**
- [ ] `docs/api-spec/endpoints/labels.md` documents GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` with request/response shapes in the standard `{ "data": ... }` envelope
- [ ] `docs/api-spec/endpoints/tasks.md` documents GET `/api/v1/projects/{projectId}/tasks` including the optional `labelId` filter parameter and the per-task labels array in the board response
- [ ] `docs/api-spec/index.md` contains an Endpoint Summary row for every endpoint above
- [ ] The Error Catalog in `docs/api-spec/index.md` defines `validation-error`, `conflict` (duplicate label name, 409), and `not-found`
**Dependencies:** T-001
**Complexity:** M
**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new)
- docs/api-spec/endpoints/tasks.md (new)
- docs/api-spec/index.md (new)
**Technical Notes:** Nested routes are grouped under the resource being operated on, so the task-label replacement endpoint is documented in `labels.md` per the brief's Section 7 retrieval key.

### T-005: Label CRUD router

**Type:** Backend
**Workflow:** standard
**Description:** Create the Express router for label management — GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}` — and mount it in `src/api/index.ts`.
**Rationale:** Implements the label management API (AC-1, AC-4, AC-5, AC-6) on top of the T-003 repository, following the documented spec from T-004.
**Acceptance Criteria:**
- [ ] GET returns the project's labels (each with `taskCount`) in the `{ "data": [...] }` envelope; POST creates a label and returns it, and the label appears in a subsequent list call
- [ ] Request bodies are validated with Zod schemas defined next to the handlers: name 1–30 chars, color one of the 12 palette tokens; failures map to `validation-error`
- [ ] POST and PUT return 409 with error code `conflict` for a duplicate name within the project, including names differing only by case
- [ ] PUT renames/recolors the label; concurrent renames resolve last-write-wins with no version precondition, and a stale client simply receives the updated name on its next refetch
- [ ] DELETE removes the label and its assignments only and returns the number of tasks that were affected
- [ ] Errors are thrown as `ApiError` and serialized by the middleware in `src/api/errors.ts`
**Dependencies:** T-003, T-004
**Complexity:** M
**Files to Modify/Create:**
- src/api/labels.ts (new)
- src/api/index.ts
**Technical Notes:** `taskCount` in the list response is what the frontend confirmation dialog (T-010) uses to state how many tasks a deletion affects (AC-5).

### T-006: Task-label assignment endpoint and board label filter

**Type:** Backend
**Workflow:** standard
**Description:** Add PUT `/api/v1/tasks/{id}/labels` (replace the task's label set from an array of label IDs) to the tasks router, and extend the board list endpoint and task repository so GET `/api/v1/projects/{projectId}/tasks` accepts an optional `labelId` query parameter and includes each task's labels in the response.
**Rationale:** Backs label assignment from the detail panel (AC-2) and server-side board filtering (AC-3); including labels in the existing board response honors the Section 10 constraint that labels must not be fetched per card, and the query parameter keeps filtering correct with pagination.
**Acceptance Criteria:**
- [ ] PUT `/api/v1/tasks/{id}/labels` replaces the task's label set and returns the updated set; the Zod schema and repository reject more than 10 labels with a `validation-error` (assigning an 11th label fails)
- [ ] Labels belonging to a different project than the task are rejected with a `validation-error`
- [ ] GET board list with `labelId` returns only tasks carrying that label, with `meta.totalCount` reflecting the filtered count so pagination stays correct; omitting `labelId` returns the full board
- [ ] Every task in the board response carries its labels array, loaded in the same query round-trip (no per-card fetch)
- [ ] Filtering by a label with zero matching tasks returns an empty `data` array with a well-formed `meta`, not an error
**Dependencies:** T-003, T-004
**Complexity:** M
**Files to Modify/Create:**
- src/api/tasks.ts
- src/db/task.ts
**Technical Notes:** The label filter joins through `task_labels(label_id)` (indexed in T-002) to stay inside the 300ms P95 round-trip NFR for boards up to 500 tasks.

### T-007: Backend tests for label endpoints and repository

**Type:** Testing
**Workflow:** standard
**Description:** Add Supertest integration tests for the label router and the modified tasks endpoints, plus unit tests for the label repository against the test database.
**Rationale:** Project convention: every router gets a Supertest integration test and every repository gets a unit test; these tests pin the business rules the ACs and edge cases depend on.
**Acceptance Criteria:**
- [ ] Label CRUD is covered: create → appears in list with `taskCount`; rename/recolor; delete removes assignments only and reports the affected-task count while tasks survive
- [ ] Duplicate-name creation returns 409 `conflict`, including a name differing only by case ("Urgent" vs "urgent")
- [ ] Label-set replacement is covered: valid replace persists; an 11th label is rejected with `validation-error`; a label from another project is rejected
- [ ] Board filtering is covered: `labelId` returns only matching tasks with correct `meta.totalCount` under pagination; zero-match filter returns an empty list; no filter returns the full board
- [ ] Repository unit tests in `tests/db/label.test.ts` cover case-insensitive duplicate detection, atomic set replacement, and delete cascade counts
**Dependencies:** T-005, T-006
**Complexity:** M
**Files to Modify/Create:**
- tests/api/labels.test.ts (new)
- tests/db/label.test.ts (new)
- tests/api/tasks.test.ts

## Group 3: Frontend

### T-008: UI spec shards — accent palette, screens, and component inventory

**Type:** Documentation
**Workflow:** standard
**Description:** Create the UI specification index (including the Section 2.1 accent palette token definitions and the Screen Inventory), the Label Management Dialog screen shard, the component inventory entries for LabelChip and LabelPicker, and screen shards for the modified Project Board and Task Detail Panel.
**Rationale:** Section 8 requires the new screen shard, its Screen Inventory row, and the LabelChip entry in `docs/ui-specification/components.md`; the palette tokens the color picker and chips must use (Section 10) are defined in the index's Section 2.1, which does not exist yet in this project and so must be created here.
**Acceptance Criteria:**
- [ ] `docs/ui-specification/index.md` Section 2.1 defines the 12 accent palette tokens, each with a chip text color meeting WCAG 2.1 AA contrast (4.5:1), and the Screen Inventory includes the Label Management Dialog
- [ ] `docs/ui-specification/screens/label-management-dialog.md` specifies create/rename/recolor/delete flows, the palette swatch picker, the inline duplicate-name error, and the delete confirmation stating the affected task count
- [ ] `docs/ui-specification/components.md` documents LabelChip (name + color chip, board and picker variants) and LabelPicker alongside the existing dialog, empty-state, and task-card components
- [ ] `docs/ui-specification/screens/project-board.md` documents task-card chips (up to 3 plus a +N overflow indicator) and the toolbar's single-select label filter dropdown
- [ ] `docs/ui-specification/screens/task-detail-panel.md` documents the new Labels field with its multi-select picker and chip previews
**Dependencies:** T-001
**Complexity:** M
**Files to Modify/Create:**
- docs/ui-specification/index.md (new)
- docs/ui-specification/components.md (new)
- docs/ui-specification/screens/label-management-dialog.md (new)
- docs/ui-specification/screens/project-board.md (new)
- docs/ui-specification/screens/task-detail-panel.md (new)

### T-009: LabelChip shared component

**Type:** Frontend
**Workflow:** mockup-first
**Description:** Create the reusable LabelChip component rendering a label's name on its palette color, with a compact variant for board cards and a regular variant for the picker and detail panel.
**Rationale:** Section 8 names LabelChip as a new shared component used by board cards, the detail panel, and the picker; building it first keeps chip rendering and contrast handling in one place.
**Acceptance Criteria:**
- [ ] Renders the label name on the palette token's color with text meeting WCAG 2.1 AA contrast (4.5:1) on all 12 tokens, per the T-008 palette spec
- [ ] Exposes compact (board card) and regular (picker/panel) variants
- [ ] Colors resolve from the accent palette tokens only — no arbitrary hex input
**Dependencies:** T-008
**Complexity:** S
**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new)

### T-010: Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first
**Description:** Create the Label Management Dialog screen for creating, renaming, recoloring, and deleting a project's labels, using the shared dialog component and a palette-token swatch picker built in-repo.
**Rationale:** New screen from Section 8 implementing AC-1, AC-4, AC-5, and AC-6 UI flows; the fixed swatch picker satisfies the Section 10 constraint of no new external dependencies for color picking.
**Acceptance Criteria:**
- [ ] A member can create a label with a name (1–30 chars) and a palette color, and it appears in the dialog's label list immediately (AC-1)
- [ ] A duplicate name (including case-only differences) surfaces the API's 409 `conflict` as an inline validation message next to the name field (AC-6)
- [ ] Rename and recolor mutations invalidate the label list and board queries via TanStack Query so every task card displaying the label updates (AC-4)
- [ ] Delete first shows an explicit confirmation dialog stating how many tasks are affected (from the label's `taskCount`), and only deletes on confirm (AC-5)
- [ ] The color picker is a swatch grid over the 12 accent palette tokens from the UI spec — no new external dependency and no custom hex input
**Dependencies:** T-005, T-008, T-009
**Complexity:** L
**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new)
**Technical Notes:** Reuses `src/ui/components/dialog.tsx` for the dialog shell and confirmation; the board toolbar entry point is wired in T-011.

### T-011: Project board — label chips, filter dropdown, and filter edge cases

**Type:** Frontend
**Workflow:** standard
**Description:** Render label chips on board task cards, add the label filter dropdown and the Label Management Dialog entry point to the board toolbar, and handle the filter edge cases (zero matches, filtered label deleted elsewhere).
**Rationale:** Implements the board half of AC-3 and the chip display from Section 8 on the modified Project Board screen, keeping filtering server-side per Section 10.
**Acceptance Criteria:**
- [ ] Task cards render up to 3 label chips with a +N overflow indicator, using label data already present in the board tasks response (no per-card fetch)
- [ ] The toolbar filter dropdown selects a single label; selection passes `labelId` to the board query so filtering is server-side and remains correct with pagination (AC-3)
- [ ] Clearing the filter restores the full board (AC-3)
- [ ] A filter with zero matching tasks shows the standard empty state with a "Clear filter" action, not a blank board
- [ ] If a board refetch shows the actively filtered label no longer exists (deleted by another user), the filter clears automatically and a notice is shown
- [ ] The toolbar opens the Label Management Dialog from T-010
**Dependencies:** T-006, T-009, T-010
**Complexity:** L
**Files to Modify/Create:**
- src/ui/project-board.tsx
- src/ui/components/task-card.tsx
- src/ui/components/empty-state.tsx

### T-012: Task detail panel — Labels field with multi-select picker

**Type:** Frontend
**Workflow:** standard
**Description:** Add a Labels field to the task detail panel with a multi-select picker showing chip previews, persisting changes through the label-set replacement endpoint.
**Rationale:** Implements AC-2 on the modified Task Detail Panel screen and the 10-label picker limit from Section 9.
**Acceptance Criteria:**
- [ ] The panel shows the task's labels as chips and opens a multi-select picker listing the project's labels with chip previews
- [ ] Assigning and removing labels persists via PUT `/api/v1/tasks/{id}/labels`, and TanStack Query invalidation updates the board card without a page reload (AC-2)
- [ ] The picker disables further selection at 10 labels and shows an explanatory tooltip; a server-side rejection of an 11th label is surfaced as a validation message
**Dependencies:** T-006, T-009
**Complexity:** M
**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx
- src/ui/components/label-picker.tsx (new)

## Group 4: Frontend Testing

### T-013: Frontend tests for label UI

**Type:** Testing
**Workflow:** standard
**Description:** Add Vitest tests for the label UI: chip rendering and overflow, dialog flows (create, duplicate-name error, delete confirmation with count), board filter select/clear and edge cases, and picker limit behavior.
**Rationale:** Pins the UI halves of AC-1 through AC-6 and the Section 9 edge cases; tests live under `tests/` mirroring `src/` per project convention.
**Acceptance Criteria:**
- [ ] LabelChip tests cover name/color rendering and the board card's 3-chip + overflow display
- [ ] Dialog tests cover create-appears-in-list, inline duplicate-name error on 409, and the delete confirmation showing the affected-task count before deletion
- [ ] Board tests cover filter selection showing only matching tasks, clear restoring the full board, the zero-match empty state with "Clear filter", and the auto-clear-with-notice when the filtered label was deleted elsewhere
- [ ] Detail panel tests cover assign/remove persisting and the picker disabling at 10 labels with a tooltip
**Dependencies:** T-010, T-011, T-012
**Complexity:** M
**Files to Modify/Create:**
- tests/ui/components/label-chip.test.tsx (new)
- tests/ui/label-management-dialog.test.tsx (new)
- tests/ui/project-board.test.tsx (new)
- tests/ui/task-detail-panel.test.tsx (new)

## Acceptance Criteria Coverage

| Work Item AC | Description | Covered By |
|--------------|-------------|------------|
| AC-1 | Create a label (name 1–30 chars + palette color); appears immediately in the project's label list | T-002, T-003, T-005, T-007, T-010, T-013 |
| AC-2 | Assign/remove labels from the task detail panel; persists and updates the board card without reload | T-006, T-007, T-012, T-013 |
| AC-3 | Filtering by a label shows only matching tasks; clearing restores the full board | T-006, T-007, T-011, T-013 |
| AC-4 | Renaming/recoloring a label updates every task card displaying it | T-005, T-010, T-011, T-013 |
| AC-5 | Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-003, T-005, T-007, T-010, T-013 |
| AC-6 | Duplicate label name in a project returns a validation error with an inline UI message | T-002, T-005, T-007, T-010, T-013 |
