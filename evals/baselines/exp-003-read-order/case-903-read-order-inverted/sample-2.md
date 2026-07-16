# Task List: FEAT-001 — Task Labels

> Generated from `docs/work-items/FEAT-001-task-labels.md` (Feature Brief FEAT-001, target v1.1) using the canonical task schema in `prompts/base-template.md` and the procedure in `prompts/feature-tasks.md`. All file paths are relative to the project root.
>
> Spec-shard authoring tasks are grouped under Foundation because the work item (Sections 6–8) requires the new shards to exist before feature logic; the Documentation & Polish group is therefore empty and omitted.

## Foundation

### T-001: Author Label and TaskLabel entity shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the data-model shards for the two new entities and register them in the data-model index (Module Ownership row, Relationships Overview entries, Changelog). Label carries a project-scoped name plus an accent-palette color; TaskLabel is the N:M join between tasks and labels.

**Rationale:**
Work item Section 6 requires the new entity shards to be created before feature logic so the migration and repositories have a spec to implement against.

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` documents fields (id, project_id, name varchar(30), color, created_at, updated_at), the case-insensitive unique-name-per-project rule, and the 12-accent-token color constraint
- [ ] `docs/data-model/entities/task-label.md` documents the join (task_id, label_id), the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities, Relationships Overview entries (Project 1:N Label; Task N:M Label via task_labels), and a Changelog row
- [ ] Cascade behavior is documented: deleting a label removes assignments only, never tasks; deleting a project removes its labels

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity shard
- docs/data-model/index.md - Module Ownership, Relationships Overview, Changelog entries

**Technical Notes:**
- Follow the front-matter and section layout of the existing shards (`entities/task.md`, `entities/project.md`)
- Keep index Section 4 and each shard's own Relationships table in sync (index requirement)

### T-002: Author labels API spec shard and update tasks endpoint spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` covering all five new label endpoints, and update `docs/api-spec/endpoints/tasks.md` for the optional `labelId` board filter and the `labels` array on TaskDto. Register the new endpoints in the api-spec index Endpoint Summary and Changelog.

**Rationale:**
Work item Section 7 requires the new endpoint shard and Endpoint Summary rows; API definitions must precede backend implementation and frontend integration (usage note 4).

**Acceptance Criteria:**
- [ ] labels.md specifies GET/POST /api/v1/projects/{projectId}/labels, PUT/DELETE /api/v1/labels/{id}, and PUT /api/v1/tasks/{id}/labels with request/response bodies and status codes
- [ ] LabelDto is defined including a per-label `taskCount` so the delete confirmation can state how many tasks are affected
- [ ] Error responses reuse catalog codes only — 409 `conflict` for duplicate names, 400 `validation-error`, 404 `not-found` (no new codes without a catalog row)
- [ ] tasks.md documents the `labelId` query parameter and the `labels` array on TaskDto; index Endpoint Summary gains rows for the five new endpoints plus a Changelog row

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - all five label endpoints + LabelDto
- docs/api-spec/endpoints/tasks.md - labelId filter parameter; labels array on TaskDto
- docs/api-spec/index.md - Endpoint Summary rows, Changelog entry

**Technical Notes:**
- The label list endpoint follows the shared envelope and pagination conventions (index Sections 2.1, 2.4)
- Nested routes group under the resource being operated on, so PUT /api/v1/tasks/{id}/labels is documented in labels.md per the work item's retrieval key

### T-003: Author Label Management Dialog shard and update UI spec docs

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the screen shard for the new Label Management Dialog, add its Screen Inventory row and a Changelog entry to the UI index, add LabelChip to the shared component inventory, and update the Project Board and Task Detail Panel shards for chips, the filter dropdown, and the Labels field.

**Rationale:**
Work item Section 8 requires the new screen shard, inventory row, and LabelChip entry; documenting the UI changes first gives the mockup-first frontend tasks an approved spec base.

**Acceptance Criteria:**
- [ ] `docs/ui-specification/screens/label-management-dialog.md` documents layout, component hierarchy, Component → API mapping (label CRUD endpoints), user interactions, and default/loading/empty/error states
- [ ] `docs/ui-specification/components.md` gains a LabelChip entry (inputs, outputs, variants; used by board cards, picker, and dialog)
- [ ] `screens/project-board.md` documents up-to-3 label chips with a "+N" overflow on TaskCard, the toolbar label filter, and the zero-match empty state with a "Clear filter" CTA
- [ ] `screens/task-detail-panel.md` documents the Labels multi-select picker with chip previews mapped to PUT /api/v1/tasks/{id}/labels
- [ ] `docs/ui-specification/index.md` gains the Screen Inventory row and a Changelog entry

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/index.md - Screen Inventory row, Changelog entry
- docs/ui-specification/components.md - LabelChip inventory entry
- docs/ui-specification/screens/project-board.md - chips, filter dropdown, filtered empty state
- docs/ui-specification/screens/task-detail-panel.md - Labels field + picker

### T-004: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add `migrations/002-add-labels.sql` creating the `labels` table and the `task_labels` join table with constraints and indexes per the new entity shards. Include the case-insensitive per-project unique index and the accent-token color check.

**Rationale:**
The Label and TaskLabel entities (work item Section 6) need persistence before any repository or API code; database changes come before code that uses them.

**Acceptance Criteria:**
- [ ] `labels`: UUID `id` PK, `project_id` FK to projects with ON DELETE CASCADE, `name` VARCHAR(30) NOT NULL, `color` constrained by CHECK to the 12 accent tokens, `created_at`/`updated_at` timestamptz
- [ ] Unique index on `(project_id, lower(name))` enforces case-insensitive name uniqueness within a project
- [ ] `task_labels`: composite PK `(task_id, label_id)`, both FKs with ON DELETE CASCADE, `created_at`/`updated_at` timestamptz
- [ ] Index on `task_labels(label_id)` supports the server-side board filter within the 300ms P95 NFR

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-add-labels.sql (new) - labels + task_labels tables, constraints, indexes

**Technical Notes:**
- snake_case plural table names, explicit varchar limits, timestamptz per data-model index Section 3
- The max-10-labels-per-task rule is enforced in the repository transaction (T-006), not as a database constraint

## Backend

### T-005: Implement label repository module

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` with SQL for list-by-project (including per-label assigned-task counts), create, rename/recolor, and delete. Surface case-insensitive duplicate-name violations as a typed error so the router can map them to 409 `conflict`.

**Rationale:**
CLAUDE.md convention 5: SQL lives only in one repository module per entity — routers never touch `pg` directly; label CRUD (AC-1, AC-4, AC-5, AC-6) needs this data layer.

**Acceptance Criteria:**
- [ ] listByProject returns the project's labels with a `taskCount` per label
- [ ] create and rename reject names that duplicate an existing label differing only by case, surfacing a distinct error for the 409 mapping
- [ ] delete removes the label and, via FK cascade, its assignments only — tasks are untouched — and reports the number of affected tasks
- [ ] All label SQL lives in this module; parameterized queries throughout

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label repository (CRUD + task counts)

### T-006: Implement task-label assignment repository module

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/task-label.ts` with a transactional replace-set operation for a task's labels and a batch loader that fetches labels for many task ids at once. Enforce the max-10 and same-project rules at write time.

**Rationale:**
Label assignment (AC-2) and the no-per-card-fetch board constraint (Section 10) need an assignment data layer with the join-table rules from work item Section 6.

**Acceptance Criteria:**
- [ ] replaceForTask atomically replaces a task's label set inside one transaction; more than 10 label ids or ids belonging to another project are rejected with typed errors
- [ ] getForTaskIds returns labels for a set of tasks in a single query (no N+1), keeping initial board load fast
- [ ] Concurrent replace operations cannot exceed the 10-label cap (transactional check)

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/task-label.ts (new) - assignment repository (replace set, batch fetch)

### T-007: Implement labels router

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET/POST /api/v1/projects/{projectId}/labels and PUT/DELETE /api/v1/labels/{id}, and mount it in `src/api/index.ts`. Validate bodies with Zod (name 1–30 chars after trimming, color one of the 12 accent tokens) and map failures to the error catalog.

**Rationale:**
Work item Section 7 defines four of the five new endpoints on the labels resource; API endpoints must exist before frontend integration.

**Acceptance Criteria:**
- [ ] POST creates a label and returns it in the `{ "data": ... }` envelope; a duplicate name (case-insensitive) returns 409 `conflict` naming the field (AC-1, AC-6)
- [ ] GET returns the project's labels with `meta` pagination and per-label `taskCount` (feeds the delete confirmation, AC-5)
- [ ] PUT renames/recolors with the same validation and conflict handling; concurrent renames resolve last-write-wins (AC-4, edge case)
- [ ] DELETE removes the label and all its assignments and returns the affected-task count; unknown ids return 404 `not-found` (AC-5)
- [ ] Invalid bodies or params return 400 `validation-error` with a `fields` map; missing token returns 401 `unauthorized`

**Dependencies:** T-002, T-005
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - labels router (4 endpoints + Zod schemas)
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Throw `ApiError`; serialization stays in `src/api/errors.ts` middleware
- Create/rename/delete are restricted to members with edit rights; the label list is visible to all project members (work item Section 6)

### T-008: Extend tasks API with label assignment and board filter

**Type:** Backend
**Workflow:** standard

**Description:**
Implement PUT /api/v1/tasks/{id}/labels (replace the task's label set) in `src/api/tasks.ts`, add the optional `labelId` query parameter to the board list endpoint, and embed each task's `labels` array in task responses. Extend the board query in `src/db/task.ts` to filter by label server-side and batch-attach labels via the assignment repository.

**Rationale:**
Work item Section 7 modifies the board list and adds the assignment endpoint; Section 10 requires labels in the existing board response and server-side filtering so pagination stays correct.

**Acceptance Criteria:**
- [ ] PUT /api/v1/tasks/{id}/labels replaces the set and returns the updated TaskDto including `labels`; an 11th label returns 400 `validation-error` (AC-2, edge case)
- [ ] GET /api/v1/projects/{projectId}/tasks accepts `labelId` and returns only matching tasks with `meta.totalCount` reflecting the filter (AC-3)
- [ ] Board and single-task responses embed `labels` from one batch query — no per-card fetches (Section 10 constraint)
- [ ] Label ids from another project return 400 `validation-error`; unknown task returns 404 `not-found`

**Dependencies:** T-002, T-006
**Complexity:** L

**Files to Modify/Create:**
- src/api/tasks.ts - PUT /tasks/{id}/labels route, labelId query validation, labels in responses
- src/db/task.ts - label filter join in the board query, batch label attachment

## Frontend

### T-009: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create `src/ui/components/label-chip.tsx` rendering a label's name on its accent-palette color, with a per-token text color that preserves WCAG 2.1 AA contrast. It is reused by board cards, the detail-panel picker, and the management dialog.

**Rationale:**
Work item Section 8 names LabelChip as a new shared component; a single chip implementation keeps color/contrast handling consistent across all three surfaces.

**Acceptance Criteria:**
- [ ] Renders name and color from a LabelDto using accent tokens as CSS custom properties — no hard-coded hex values
- [ ] Chip text meets 4.5:1 contrast on every one of the 12 palette colors (NFR)
- [ ] Uses `caption` typography and `space-1` padding per the design system
- [ ] Truncates 30-char names gracefully at card-sized widths

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component

**Technical Notes:**
- No external dependencies; define a token-to-text-color map validated for AA contrast (UI spec Section 2.1 note)

### T-010: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Build the new Label Management Dialog opened from the board toolbar: list the project's labels, create with a name field and palette swatch picker, rename/recolor inline, and delete behind a confirmation. This adds a new user-facing screen, so an HTML mockup of the Label Management Dialog must be generated and approved first (see `.ai-framework/prompts/mockup-generation.md`).

**Rationale:**
Work item Section 8 introduces this screen as the management surface for AC-1, AC-4, AC-5, and AC-6; the work item classifies frontend tasks for new screens as mockup-first.

**Acceptance Criteria:**
- [ ] Creating a label with a valid name and palette color shows it in the list immediately (AC-1)
- [ ] A duplicate-name 409 from the API renders as an inline field message (AC-6)
- [ ] Delete opens the shared `Dialog` in destructive mode stating how many tasks carry the label (from `taskCount`); confirming removes it from all tasks (AC-5)
- [ ] Rename/recolor persists and invalidates label and task queries so every chip that displays the label updates (AC-4)
- [ ] The color picker offers exactly the 12 accent tokens — no custom colors (scope lock)

**Dependencies:** T-003, T-007, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - label management screen
- src/ui/project-board.tsx - toolbar entry point to open the dialog

**Technical Notes:**
- Reuse the shared `Dialog` component (focus trap, Escape-to-close); destructive variant for delete
- TanStack Query mutations invalidate both label and board-task queries so chips refresh without reload

### T-011: Add Labels picker to Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to the Task Detail Panel with a multi-select picker showing LabelChip previews, saving via PUT /api/v1/tasks/{id}/labels. The field follows the panel's existing form-field pattern, so no separate mockup is required (workflow-classification exception).

**Rationale:**
AC-2 requires assigning and removing labels from the task detail panel with changes reflected on the board card without a page reload.

**Acceptance Criteria:**
- [ ] Assigning or removing labels persists and updates the board card via query invalidation without a page reload (AC-2)
- [ ] The picker disables further selection at 10 labels and shows an explanatory tooltip (edge case)
- [ ] API errors (11th label, label deleted meanwhile) surface as inline messages, not silent failures
- [ ] Loading and error states follow the panel's existing skeleton and banner patterns

**Dependencies:** T-008, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field with multi-select picker

### T-012: Add label chips and single-label filter to Project Board

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Render up to three LabelChips per TaskCard with a "+N" overflow indicator, and add a single-label filter dropdown to the board toolbar driving the `labelId` query parameter. This significantly changes the board card layout and toolbar, so an HTML mockup of the updated Project Board must be generated and approved first (see `.ai-framework/prompts/mockup-generation.md`).

**Rationale:**
Work item Section 8 modifies the Project Board for chip display and filtering (AC-3); the visible card redesign triggers the mockup-first classification.

**Acceptance Criteria:**
- [ ] Cards render up to 3 label chips plus a "+N" indicator for the remainder (Section 8)
- [ ] Selecting a label shows only matching tasks via the server-side `labelId` parameter; clearing the filter restores the full board (AC-3)
- [ ] A zero-match filter renders `EmptyState` with a "Clear filter" CTA — never a blank board (edge case)
- [ ] If the filtered label was deleted by another user, the refetch clears the filter and shows a notice (edge case)

**Dependencies:** T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/components/task-card.tsx - chip row with overflow indicator
- src/ui/project-board.tsx - filter dropdown, filtered query state, empty/notice states

**Technical Notes:**
- Filtering stays a server-side query parameter so results remain correct with pagination (Section 10 constraint)
- Include `labelId` in the board query key so TanStack Query refetches on filter change

## Testing

### T-013: Write repository unit tests for labels

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest unit tests for `src/db/label.ts` and `src/db/task-label.ts` against the test database, covering uniqueness, cascades, and assignment rules.

**Rationale:**
CLAUDE.md convention 6 requires a unit test per repository; the label business rules (case-insensitive uniqueness, cascade-to-assignments-only, max 10) live in this layer.

**Acceptance Criteria:**
- [ ] Duplicate names differing only by case ("Urgent" vs "urgent") are rejected within a project and allowed across projects (edge case)
- [ ] Deleting a label removes its assignments only; the tasks themselves remain (edge case)
- [ ] replaceForTask enforces the 10-label cap and the same-project rule; the batch loader returns labels for many tasks in one query
- [ ] Deleting a task or project cascades away its assignments/labels

**Dependencies:** T-005, T-006
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - assignment repository unit tests

### T-014: Write API integration tests for label endpoints

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration coverage for the labels router and the extended tasks routes, exercising happy paths, error-catalog responses, and the board filter with pagination.

**Rationale:**
CLAUDE.md convention 6 requires a Supertest integration test per router; the error-path ACs (AC-6, 11th label, delete count) need end-to-end verification.

**Acceptance Criteria:**
- [ ] Label CRUD happy paths return envelope-conformant responses; duplicate create/rename returns 409 `conflict` (AC-1, AC-6)
- [ ] PUT /api/v1/tasks/{id}/labels replaces the set; an 11th label returns 400 `validation-error` (AC-2, edge case)
- [ ] GET board tasks with `labelId` returns only matching tasks with correct `meta.totalCount`; a label with zero matches returns an empty data array (AC-3)
- [ ] DELETE removes assignments and reports the affected-task count; concurrent renames resolve last-write-wins (AC-5, edge case)
- [ ] Requests without a valid bearer token return 401 `unauthorized`

**Dependencies:** T-007, T-008
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - labelId filter and label-assignment cases

### T-015: Write UI component tests for label features

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for the chip, management dialog, board filter, and panel picker flows, mirroring the `src/` tree under `tests/`.

**Rationale:**
The user-visible ACs (chips, filter, picker cap, delete confirmation, inline duplicate error) need frontend verification beyond API tests.

**Acceptance Criteria:**
- [ ] LabelChip renders every palette token with its AA-contrast text color (NFR)
- [ ] Dialog: creating shows the new label, a duplicate shows an inline error, and delete confirmation states the affected-task count (AC-1, AC-5, AC-6)
- [ ] Picker caps selection at 10 with a tooltip; assignment changes update card chips without a reload (AC-2)
- [ ] Filter dropdown filters and clears correctly; the zero-match state shows `EmptyState` with a "Clear filter" CTA (AC-3)
- [ ] Rename/recolor updates chips on board cards after query invalidation (AC-4)

**Dependencies:** T-010, T-011, T-012
**Complexity:** L

**Files to Modify/Create:**
- tests/ui/components/label-chip.test.tsx (new) - chip rendering/contrast tests
- tests/ui/label-management-dialog.test.tsx (new) - dialog CRUD flow tests
- tests/ui/project-board.test.tsx (new) - chips + filter behavior tests
- tests/ui/task-detail-panel.test.tsx (new) - picker behavior tests

## Summary

- **Work item:** FEAT-001 — Task Labels (target v1.1)
- **Total tasks:** 15 — Documentation 3 (T-001–T-003), Database 1 (T-004), Backend 4 (T-005–T-008), Frontend 4 (T-009–T-012), Testing 3 (T-013–T-015)
- **Complexity distribution:** S ×3 (T-001, T-002, T-009) · M ×6 (T-003, T-004, T-005, T-006, T-011, T-013) · L ×6 (T-007, T-008, T-010, T-012, T-014, T-015) · XL ×0
- **Critical path (6 tasks):** T-001 → T-004 → T-005 → T-007 → T-010 → T-015. An equal-length chain runs through the docs/UI side: T-001 → T-002 → T-003 → T-009 → T-010 → T-015.
- **Risks / open questions:**
  - The delete confirmation's affected-task count comes from `taskCount` on the label list response; it can be momentarily stale between list load and confirm. If real-time accuracy is required, add a count fetch at confirm time.
  - Concurrent rename is last-write-wins per the work item — no optimistic locking is introduced; stale clients pick up the new name on the next refetch.
  - AA contrast across all 12 accent tokens needs a per-token text-color map (per UI spec Section 2.1); dark text may be required on mid-luminance tokens — validate in T-009 rather than assuming white.
  - The 300ms P95 filter NFR for 500-task boards rests on the `task_labels(label_id)` index plus the existing board index; verify with a seeded board during T-014 and revisit indexing if it misses.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: A project member can create a label with a name (1–30 chars) and a palette color; the label immediately appears in the project's label list | T-005, T-007, T-010, T-014, T-015 |
| AC-2: A user can assign and remove labels on a task from the task detail panel; changes persist and appear on the board card without a page reload | T-006, T-008, T-011, T-014, T-015 |
| AC-3: Selecting a label in the board filter shows only tasks carrying that label; clearing the filter restores the full board | T-008, T-012, T-014, T-015 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-007, T-010, T-012, T-015 |
| AC-5: Deleting a label removes it from all tasks after an explicit confirmation dialog stating how many tasks are affected | T-005, T-007, T-010, T-014, T-015 |
| AC-6: Attempting to create a duplicate label name within the same project returns a validation error and the UI shows an inline message | T-005, T-007, T-010, T-014 |
