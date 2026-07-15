# Task List: FEAT-001 Task Labels

## Foundation

### T-001: Create Label and TaskLabel entities with migration

**Type:** Database
**Workflow:** standard

**Description:**
Add the project-scoped Label entity (name + palette color, case-insensitive unique name per project) and the TaskLabel join table (max 10 labels per task), with a migration and new data-model shards.

**Rationale:**
AC-1, AC-2 and AC-6 require labels as first-class entities with a per-project uniqueness constraint.

**Acceptance Criteria:**
- [ ] Migration creates `labels` and `task_labels` tables with unique `(project_id, lower(name))`
- [ ] Repository module follows the one-module-per-entity convention
- [ ] New entity shards written and indexed per the data-model index rules

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - labels and task_labels tables
- src/db/label.ts (new) - Label repository module
- src/db/task.ts - join helpers to load a task's labels
- docs/data-model/entities/label.md (new) - entity shard
- docs/data-model/entities/task-label.md (new) - join entity shard

## Frontend

### T-002: Build the label management dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Build the label management dialog opened from the board toolbar: list labels via GET /api/v1/projects/{projectId}/labels, create via POST, rename/recolor via PUT /api/v1/labels/{id}, and delete via DELETE /api/v1/labels/{id} with a confirmation dialog stating how many tasks are affected.

**Rationale:**
AC-1, AC-4 and AC-5 are exercised through this dialog; AC-6's duplicate-name error surfaces here as an inline message.

**Acceptance Criteria:**
- [ ] Create, rename, recolor, and delete flows work against the label endpoints
- [ ] Delete shows a confirmation stating the number of affected tasks before calling the endpoint
- [ ] Duplicate-name `conflict` response renders an inline validation message
- [ ] Colors restricted to the 12 accent palette tokens

**Dependencies:** T-001
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen component
- docs/ui-specification/screens/label-management-dialog.md (new) - screen shard
- src/ui/project-board.tsx - toolbar button opening the dialog

## Backend

### T-003: Render label chips on board cards and the detail panel picker

**Type:** Backend
**Workflow:** standard

**Description:**
Render up to 3 label chips (+N overflow) on board task cards using a new shared LabelChip component, and add the "Labels" multi-select picker with chip previews to the task detail panel so labels can be assigned and removed without a page reload.

**Rationale:**
AC-2 requires assignment from the detail panel with immediate board reflection; AC-4 requires rename/recolor to propagate to every card.

**Acceptance Criteria:**
- [ ] Board cards show up to 3 chips with a +N overflow indicator
- [ ] Detail panel picker assigns/removes labels and the board card updates via query invalidation
- [ ] Picker disables selection beyond 10 labels with an explanatory tooltip

**Dependencies:** T-004
**Complexity:** L

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared LabelChip component
- src/ui/components/task-card.tsx - chip row rendering
- src/ui/task-detail-panel.tsx - Labels field with multi-select picker
- src/ui/project-board.tsx - pass label data through to cards

### T-004: Implement label CRUD and assignment endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Implement the five label endpoints (list/create under /api/v1/projects/{projectId}/labels, rename-recolor/delete under /api/v1/labels/{id}, set-task-labels under /api/v1/tasks/{id}/labels) with the standard envelope, and add the optional `labelId` filter plus label data to the board task list response.

**Rationale:**
Every AC needs the label contract; the work item's Section 7 defines all five endpoints as new and the board list as modified.

**Acceptance Criteria:**
- [ ] All five endpoints return the standard envelope with Zod-validated inputs
- [ ] Duplicate name within a project returns 409 `conflict`; 11th label returns `validation-error`
- [ ] Board list response includes each task's labels and supports `labelId` filtering server-side

**Dependencies:** T-001
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - label route handlers
- src/api/index.ts - register the labels router
- src/api/tasks.ts - `labelId` query parameter and labels in the list response
- docs/api-spec/endpoints/labels.md (new) - endpoint shard
- docs/api-spec/endpoints/tasks.md - document the modified board list

### T-005: Add label usage analytics export endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Add GET /api/v1/labels/export returning a CSV of per-label usage counts (tasks per label, per project) so team leads can analyze label adoption in a spreadsheet.

**Rationale:**
Usage data will help teams decide which labels to keep as adoption grows.

**Acceptance Criteria:**
- [ ] Endpoint streams a CSV with label name, color, project, and task count columns
- [ ] Counts match the task_labels join table

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - export route handler
- docs/api-spec/endpoints/labels.md (new) - document the export endpoint

### T-006: Add the board label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a label filter dropdown to the board toolbar that narrows visible tasks to those carrying the selected label via the `labelId` query parameter, with a clear-filter control and the standard empty state for zero matches.

**Rationale:**
AC-3 defines the single-label board filtering behavior.

**Acceptance Criteria:**
- [ ] Selecting a label shows only tasks carrying it (server-side filtering)
- [ ] Clearing the filter restores the full board
- [ ] Zero-match filter shows the EmptyState with a "Clear filter" action

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/ui/project-board.tsx - filter dropdown and filtered rendering

## Testing

### T-007: Add label API integration tests

**Type:** Testing
**Workflow:** standard

**Description:**
Cover label CRUD, task-label assignment, the duplicate-name conflict, the 10-label cap, and the export CSV with Supertest integration tests.

**Rationale:**
Locks the label API contract in against regressions before the frontend work is finalized.

**Acceptance Criteria:**
- [ ] CRUD, assignment, and `labelId` filtering covered
- [ ] Duplicate-name 409 and 11th-label validation error covered
- [ ] Export CSV shape and counts covered

**Dependencies:** T-004, T-005
**Complexity:** M

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - label endpoint tests
- tests/api/tasks.test.ts - board list label data and `labelId` filter coverage

### T-008: Add UI regression tests for label flows

**Type:** Testing
**Workflow:** standard

**Description:**
Cover the management dialog flows, detail-panel assignment with board reflection, and filter select/clear with component tests.

**Rationale:**
Locks the user-facing label flows in against regressions across the three touched screens.

**Acceptance Criteria:**
- [ ] Dialog create/rename/recolor/delete flows covered, including the delete confirmation
- [ ] Assignment from the detail panel updates the board card without reload
- [ ] Filter select and clear covered

**Dependencies:** T-002, T-003, T-006
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/label-flows.test.tsx (new) - label UI regression suite

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: create label with name and palette color | T-001, T-002, T-004 |
| AC-2: assign/remove labels from detail panel | T-003, T-004 |
| AC-3: board label filter | T-004, T-006 |
| AC-4: rename/recolor updates every card | T-002, T-003, T-004 |
| AC-6: duplicate name validation error | T-001, T-002, T-004 |
