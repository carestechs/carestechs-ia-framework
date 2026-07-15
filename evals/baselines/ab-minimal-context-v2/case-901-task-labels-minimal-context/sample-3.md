# FEAT-001: Task Labels — Generated Task List

**Feature Brief:** FEAT-001 (Task Labels, target v1.1) — traceability per Section 13.8 of the brief.

**Summary:** 12 tasks across 4 groups implement project-scoped labels: data model documentation and migration first (Section 13.3), then the label API before frontend integration (Section 13.4), then the UI (Label Management Dialog and LabelChip are new UI surfaces and classified `mockup-first` per Section 13.5; board and task-detail-panel changes modify existing screens and reuse the mockup-approved LabelChip, so they are `standard`), and finally tests. This project has no spec documentation yet, so the documentation shards named by the brief's impact tables are created new by these tasks. All items in Section 4.2 (global labels, automation, custom hex colors, multi-label filter combinations) are excluded.

## Group 1: Data Model & Migrations

### T-001: Document Label and TaskLabel entities in data-model shards

**Type:** Documentation
**Workflow:** standard
**Description:** Create the data-model spec shards required by Section 6 of the brief. `docs/data-model/entities/label.md` specifies the Label entity (id, project_id, name 1–30 chars, color as one of the 12 accent-palette tokens, timestamps; name unique per project case-insensitively; deleting a label cascades to assignments only, never to tasks). `docs/data-model/entities/task-label.md` specifies the TaskLabel N:M join (task_id, label_id; max 10 labels per task; task and label must belong to the same project). Because the project has no data-model docs yet, also create `docs/data-model/index.md` with Module Ownership entries for both new entities and a Relationships Overview covering Project 1—N Label and Task N—M Label via TaskLabel.
**Rationale:** The brief mandates creating the new entity shards and their index entries before feature logic (Section 6, Section 13.3); all later tasks reference these business rules.
**Acceptance Criteria:**
- [ ] Both entity shards exist and state the business rules from Section 6: case-insensitive per-project name uniqueness, 12-token palette color constraint, 10-label cap per task, same-project assignment rule, and delete-cascades-to-assignments-only.
- [ ] `docs/data-model/index.md` lists both new entities in Module Ownership and shows the Project–Label and Task–Label relationships.
**Dependencies:** None
**Complexity:** S
**Files to Modify/Create:**
- `docs/data-model/entities/label.md` (new)
- `docs/data-model/entities/task-label.md` (new)
- `docs/data-model/index.md` (new)

### T-002: Migration for labels and task_labels tables

**Type:** Database
**Workflow:** standard
**Description:** Add `migrations/002-task-labels.sql` (plain SQL, numbered per CLAUDE.md). Create `labels` (id, project_id FK → projects ON DELETE CASCADE, name, color, created_at, updated_at) with a unique index on `(project_id, lower(name))` to enforce case-insensitive per-project uniqueness at the database level. Create `task_labels` (task_id FK → tasks ON DELETE CASCADE, label_id FK → labels ON DELETE CASCADE, primary key (task_id, label_id)) so deleting a label removes assignments only, never tasks. Add an index on `task_labels (label_id)` so the server-side `labelId` board filter stays within the 300ms P95 NFR for boards up to 500 tasks. Table and column names are snake_case per CLAUDE.md.
**Rationale:** Establishes the storage for AC-1 through AC-6; the lower(name) unique index backs AC-6 and the case-insensitive duplicate edge case; FK cascade semantics implement the AC-5 rule that deletion removes assignments but leaves tasks untouched.
**Acceptance Criteria:**
- [ ] Migration applies cleanly on top of `migrations/001-init.sql` and creates both tables with the constraints above.
- [ ] Inserting two labels in one project whose names differ only by case ("Urgent" vs "urgent") violates the unique index.
- [ ] Deleting a `labels` row removes its `task_labels` rows and leaves `tasks` rows untouched.
**Dependencies:** T-001
**Complexity:** M
**Files to Modify/Create:**
- `migrations/002-task-labels.sql` (new)

## Group 2: Backend API

### T-003: Label repository module

**Type:** Backend
**Workflow:** standard
**Description:** Create `src/db/label.ts` (one repository module per entity, SQL only in `src/db/` per CLAUDE.md) with: `listByProject` returning each label with an assigned-task count (needed by the AC-5 delete-confirmation dialog), `create` surfacing the unique-index violation distinctly so the router can map it to the `conflict` error code, `update` for rename/recolor (plain last-write-wins, matching the concurrent-rename edge case in Section 9), `getById`, and `remove` (assignments removed via FK cascade). Repository functions return typed camelCase objects, never raw rows.
**Rationale:** Provides the data-access layer for all label endpoints (AC-1, AC-4, AC-5, AC-6) while keeping routers free of SQL per CLAUDE.md convention 5.
**Acceptance Criteria:**
- [ ] All label persistence operations for the feature go through this module; no other module issues SQL against `labels`.
- [ ] `create` with a case-insensitively duplicate name yields a detectable duplicate error; `listByProject` returns correct assigned-task counts.
**Dependencies:** T-002
**Complexity:** M
**Files to Modify/Create:**
- `src/db/label.ts` (new)

### T-004: Label CRUD endpoints and API spec shards

**Type:** Backend
**Workflow:** standard
**Description:** Create the `src/api/labels.ts` router and mount it in `src/api/index.ts`, implementing GET `/api/v1/projects/{projectId}/labels` (list, `{ data, meta }` envelope, each label including its assigned-task count), POST `/api/v1/projects/{projectId}/labels` (create; 409 with error code `conflict` on duplicate name), PUT `/api/v1/labels/{id}` (rename/recolor, last-write-wins), and DELETE `/api/v1/labels/{id}` (removes all assignments, never tasks). Zod schemas next to the handlers validate name (1–30 chars) and color (enum of the 12 accent-palette tokens); failures map to `validation-error`. Create/rename/delete are restricted to project members with edit rights (Section 6). Routers throw `ApiError` for serialization by `src/api/errors.ts`. Document the four endpoints in `docs/api-spec/endpoints/labels.md` and create `docs/api-spec/index.md` with their Endpoint Summary rows and Error Catalog entries (`validation-error`, `conflict`, `not-found`) — per CLAUDE.md, no error code may exist without a catalog row, and no API spec docs exist yet.
**Rationale:** Implements the server side of AC-1 (create + immediate list visibility), AC-4 (rename/recolor persisted for every consumer), AC-5 (delete with assignment cleanup and affected-count data), and AC-6 (duplicate → 409 `conflict`).
**Acceptance Criteria:**
- [ ] All four endpoints return the `{ data }` / list `{ data, meta }` envelopes and validate input with Zod.
- [ ] POST with a duplicate name (case-insensitive) returns 409 `{ error: { code: "conflict" } }`; invalid color token or name length returns `validation-error`.
- [ ] DELETE removes all of the label's assignments and leaves tasks untouched; list responses include per-label assigned-task counts.
- [ ] `docs/api-spec/endpoints/labels.md` and `docs/api-spec/index.md` (Endpoint Summary + Error Catalog) are created and consistent with the implementation.
**Dependencies:** T-002, T-003
**Complexity:** L
**Files to Modify/Create:**
- `src/api/labels.ts` (new)
- `src/api/index.ts`
- `docs/api-spec/endpoints/labels.md` (new)
- `docs/api-spec/index.md` (new)

### T-005: Replace-task-labels endpoint with cap and same-project checks

**Type:** Backend
**Workflow:** standard
**Description:** Add PUT `/api/v1/tasks/{id}/labels` to `src/api/tasks.ts`, accepting `{ labelIds: string[] }` and replacing the task's full label set. Zod rejects arrays longer than 10 with `validation-error` (the 11th-label edge case, Section 9). Create `src/db/task-label.ts` (one repository per entity) with a transactional `replaceForTask` that verifies every label belongs to the same project as the task (otherwise `validation-error`, Section 6 rule) before deleting and re-inserting assignment rows. Document the endpoint in `docs/api-spec/endpoints/labels.md` (nested routes group under the labels resource per the brief's Section 7 retrieval key).
**Rationale:** Implements persistence for AC-2 (assign/remove from the task detail panel) and enforces the 10-label cap and same-project business rules server-side.
**Acceptance Criteria:**
- [ ] PUT with ≤10 valid same-project label IDs replaces the set atomically and returns the updated set in the `{ data }` envelope.
- [ ] PUT with 11 IDs, or with a label from another project, returns `validation-error` and changes nothing.
**Dependencies:** T-002, T-004
**Complexity:** M
**Files to Modify/Create:**
- `src/api/tasks.ts`
- `src/db/task-label.ts` (new)
- `docs/api-spec/endpoints/labels.md` (new)

### T-006: Board tasks query — labels in response and labelId filter

**Type:** Backend
**Workflow:** standard
**Description:** Extend GET `/api/v1/projects/{projectId}/tasks`: add an optional Zod-validated `labelId` query parameter, and extend the board query in `src/db/task.ts` to aggregate each task's labels (e.g. a `json_agg` join) into the existing response so chips render without per-card fetches (Constraint: must not slow initial board load). When `labelId` is present, filter server-side (`WHERE EXISTS` on `task_labels`) before pagination so `meta.totalCount` and pages stay correct (Constraint: filtering stays server-side). A `labelId` matching no assignments returns an empty page with correct meta. Query shape and the `task_labels (label_id)` index from T-002 keep the select-to-render round trip within the 300ms P95 NFR at 500 tasks. Document the `labelId` parameter and the labels array in `docs/api-spec/endpoints/tasks.md` (created new — no API spec docs exist yet).
**Rationale:** Server side of AC-3 (single-label board filtering) and the data source for AC-2/AC-4 chip rendering, honoring all three Section 10 constraints.
**Acceptance Criteria:**
- [ ] Board list responses include each task's labels; response time for an unfiltered 500-task board does not regress.
- [ ] With `labelId`, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count; omitting the parameter returns the full board.
- [ ] `docs/api-spec/endpoints/tasks.md` documents the modified endpoint.
**Dependencies:** T-002
**Complexity:** M
**Files to Modify/Create:**
- `src/api/tasks.ts`
- `src/db/task.ts`
- `docs/api-spec/endpoints/tasks.md` (new)

## Group 3: Frontend UI

### T-007: LabelChip shared component and UI-spec foundations

**Type:** Frontend
**Workflow:** mockup-first
**Description:** Create the reusable `LabelChip` component (`src/ui/components/label-chip.tsx`, PascalCase component per CLAUDE.md) rendering a label's name and palette color, used by board task cards, the task-detail-panel picker, and the Label Management Dialog. Define the fixed 12-token accent palette in `docs/ui-specification/index.md` Section 2.1 (created new — no UI spec exists yet) and pair each token with a chip text color meeting WCAG 2.1 AA contrast (4.5:1) per the NFR, with no new external dependencies (Constraint 2). Add the LabelChip entry to the shared-component inventory `docs/ui-specification/components.md` (created new). Mockup-first: chip visuals across all 12 tokens are approved before implementation.
**Rationale:** The brief's Section 8 names LabelChip as a new shared component that every label surface reuses; defining the palette and contrast pairs once keeps AC-2/AC-3/AC-4 rendering consistent.
**Acceptance Criteria:**
- [ ] LabelChip renders name + color for any of the 12 palette tokens with text contrast ≥ 4.5:1 on each.
- [ ] `docs/ui-specification/index.md` documents the 12 accent-palette tokens (Section 2.1) and `docs/ui-specification/components.md` lists LabelChip.
**Dependencies:** T-001
**Complexity:** S
**Files to Modify/Create:**
- `src/ui/components/label-chip.tsx` (new)
- `docs/ui-specification/components.md` (new)
- `docs/ui-specification/index.md` (new)

### T-008: Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first
**Description:** Create the Label Management Dialog (`src/ui/label-management-dialog.tsx`, one React file per screen), opened from the project-board toolbar, built on the shared `src/ui/components/dialog.tsx`. It lists the project's labels and supports: create with name input and a palette swatch picker limited to the 12 tokens from `docs/ui-specification/index.md` Section 2.1; rename; recolor; and delete behind an explicit confirmation dialog stating how many tasks are affected (assigned-task count from the T-004 list response). Duplicate-name 409 `conflict` responses and 1–30-char violations surface as inline validation messages (AC-6). Mutations via TanStack Query invalidate the label list and board task queries so every card reflects renames/recolors without a reload (AC-4). Create `docs/ui-specification/screens/label-management-dialog.md` and add its Screen Inventory row to `docs/ui-specification/index.md` (new screen per Section 8; task classified mockup-first per Section 13.5).
**Rationale:** Delivers the management UI for AC-1 (create → appears in the list immediately), AC-4 (rename/recolor propagation), AC-5 (confirmed delete with affected count), and AC-6 (inline duplicate message).
**Acceptance Criteria:**
- [ ] Creating a label shows it in the dialog's list immediately; duplicate names show an inline error without closing the dialog.
- [ ] Delete requires confirming a dialog that states the affected task count; after confirmation the label disappears from all tasks.
- [ ] Rename/recolor updates every visible chip after query invalidation, with no page reload.
**Dependencies:** T-004, T-007
**Complexity:** L
**Files to Modify/Create:**
- `src/ui/label-management-dialog.tsx` (new)
- `src/ui/project-board.tsx`
- `docs/ui-specification/screens/label-management-dialog.md` (new)
- `docs/ui-specification/index.md` (new)

### T-009: Task detail panel — labels multi-select picker

**Type:** Frontend
**Workflow:** standard
**Description:** Add a "Labels" field to `src/ui/task-detail-panel.tsx`: a multi-select picker listing the project's labels with LabelChip previews. Selecting or removing labels sends the full set to PUT `/api/v1/tasks/{id}/labels` via a TanStack Query mutation that invalidates the board tasks query, so the card's chips update without a page reload (AC-2). At 10 assigned labels the picker disables further selection and shows an explanatory tooltip (Section 9 edge case), matching the server-side cap. Update the screen spec `docs/ui-specification/screens/task-detail-panel.md` (created new) with the Labels field. Standard workflow: this modifies an existing screen reusing the mockup-approved LabelChip.
**Rationale:** Delivers the user-facing half of AC-2 and the client-side 10-label cap experience.
**Acceptance Criteria:**
- [ ] Assigning and removing labels from the panel persists and updates the board card chips without a reload.
- [ ] With 10 labels assigned, additional options are disabled and a tooltip explains the limit.
**Dependencies:** T-005, T-007
**Complexity:** M
**Files to Modify/Create:**
- `src/ui/task-detail-panel.tsx`
- `docs/ui-specification/screens/task-detail-panel.md` (new)

### T-010: Project board — label chips and single-label filter

**Type:** Frontend
**Workflow:** standard
**Description:** Render up to 3 LabelChips per card with a "+N" overflow indicator in `src/ui/components/task-card.tsx`, sourced from the labels array already included in the board response (no per-card fetching, Constraint 1). Add a single-select label filter dropdown to the `src/ui/project-board.tsx` toolbar (populated from GET project labels) that drives the `labelId` query parameter of the board query so filtering stays server-side and pagination-correct (Constraint 3); clearing the selection restores the full board (AC-3). A filter with zero matching tasks shows the shared `src/ui/components/empty-state.tsx` with a "Clear filter" action, not a blank board. If a board refetch reveals the filtered label was deleted by another user, clear the filter and show a notice (Section 9); renames by other users appear on the next refresh (last-write-wins edge case). Update the screen spec `docs/ui-specification/screens/project-board.md` (created new). Standard workflow: modifies an existing screen reusing the mockup-approved LabelChip.
**Rationale:** Delivers the board half of AC-3 and the chip display that makes AC-2/AC-4 visible, plus three Section 9 edge cases (zero-match filter, filtered-label deleted, concurrent rename refresh).
**Acceptance Criteria:**
- [ ] Cards show at most 3 chips plus a correct "+N" indicator; chip data comes from the board response with no extra requests.
- [ ] Selecting a label shows only matching tasks (server-filtered, pagination intact); clearing restores the full board.
- [ ] Zero-match filter shows the empty state with a working "Clear filter" action; a deleted filtered label clears the filter and shows a notice on refetch.
**Dependencies:** T-004, T-006, T-007
**Complexity:** L
**Files to Modify/Create:**
- `src/ui/project-board.tsx`
- `src/ui/components/task-card.tsx`
- `docs/ui-specification/screens/project-board.md` (new)

## Group 4: Testing

### T-011: API integration tests for labels, assignment, and board filter

**Type:** Testing
**Workflow:** standard
**Description:** Supertest integration tests per CLAUDE.md convention 6. New `tests/api/labels.test.ts`: CRUD happy paths with envelope assertions; 409 `conflict` on duplicate names including the case-only difference ("Urgent" vs "urgent"); `validation-error` on empty/31-char names and non-palette colors; delete removes assignments while tasks survive; list includes assigned-task counts; edit-rights enforcement on create/rename/delete. Extend `tests/api/tasks.test.ts`: PUT label-set replace semantics; rejection of 11 labels and of cross-project labels; board list includes labels per task; `labelId` filtering returns only matching tasks with correct `meta.totalCount` across pages; unknown/unassigned `labelId` yields an empty page.
**Rationale:** Locks in the server-side behavior behind AC-1 through AC-6 and the Section 9 edge cases (duplicate case-insensitivity, 11th label, delete cascade).
**Acceptance Criteria:**
- [ ] All listed scenarios have assertions and pass against the test database.
- [ ] Every new label endpoint and the modified board endpoint has at least one happy-path and one failure-path test.
**Dependencies:** T-004, T-005, T-006
**Complexity:** M
**Files to Modify/Create:**
- `tests/api/labels.test.ts` (new)
- `tests/api/tasks.test.ts`

### T-012: Repository unit tests for label, task-label, and board query

**Type:** Testing
**Workflow:** standard
**Description:** Vitest unit tests against the test database, one per repository per CLAUDE.md convention 6. New `tests/db/label.test.ts`: create/duplicate detection via the lower(name) unique index, rename/recolor last-write-wins, delete cascading to assignments only, assigned-task counts. New `tests/db/task-label.test.ts`: transactional `replaceForTask` (all-or-nothing), 10-label cap interaction, same-project validation. New `tests/db/task.test.ts` (the task repository previously had no unit test): board query label aggregation and `labelId` filtering with pagination.
**Rationale:** Verifies the persistence rules (uniqueness, cascade, cap, same-project) independently of the HTTP layer, and brings the modified task repository up to the CLAUDE.md rule that every repository has a unit test.
**Acceptance Criteria:**
- [ ] All listed scenarios have assertions and pass against the test database.
- [ ] Each of the three repositories touched by this feature has a unit test file covering its new behavior.
**Dependencies:** T-003, T-005, T-006
**Complexity:** M
**Files to Modify/Create:**
- `tests/db/label.test.ts` (new)
- `tests/db/task-label.test.ts` (new)
- `tests/db/task.test.ts` (new)

## Acceptance Criteria Coverage

| Work Item AC | Description | Covered By |
|--------------|-------------|------------|
| AC-1 | Create label (name 1–30, palette color); appears in project label list immediately | T-002, T-004, T-008 |
| AC-2 | Assign/remove labels from task detail panel; persists and updates board card without reload | T-005, T-009 |
| AC-3 | Board filter by selected label; clearing restores full board | T-006, T-010 |
| AC-4 | Rename/recolor updates every task card displaying the label | T-004, T-008, T-010 |
| AC-5 | Delete removes label from all tasks after confirmation stating affected task count | T-002, T-004, T-008 |
| AC-6 | Duplicate label name in project → validation error with inline UI message | T-002, T-004, T-008 |
