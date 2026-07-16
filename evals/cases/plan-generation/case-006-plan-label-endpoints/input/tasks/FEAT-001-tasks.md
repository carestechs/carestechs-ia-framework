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
