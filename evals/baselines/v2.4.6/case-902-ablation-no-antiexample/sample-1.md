# FEAT-001 — Task Labels: Implementation Tasks

Task breakdown for the Task Labels feature (FEAT-001, TaskFlow v1.1), generated per the feature-tasks prompt and the canonical task schema in `prompts/base-template.md`. Spec-shard documentation tasks are scheduled ahead of the code that implements them, per the work item's docs-first requirements (Sections 6–8).

## Foundation

### T-001: Author data-model spec shards for Label and TaskLabel

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for the two new entities and register them in the data-model index (Module Ownership, Relationships Overview, Changelog). The shards define the fields, constraints, indexes, and business rules that the migration and repositories implement.

**Rationale:**
FEAT-001 Section 6 requires the new entity shards to exist before feature logic; the data-model index mandates shard + index updates for every new entity.

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` documents fields (UUID id, project_id FK, name ≤ 30 chars, color as accent-palette token, timestamps), case-insensitive per-project name uniqueness, and cascade rules (assignments only, never tasks)
- [ ] `docs/data-model/entities/task-label.md` documents the N:M join (task_id, label_id), the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities, a Section 4.2 many-to-many entry, and a Changelog row

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity shard
- docs/data-model/index.md - Module Ownership, Relationships Overview, and Changelog entries

### T-002: Create the labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add a SQL migration creating the `labels` and `task_labels` tables per the new entity shards. Include the uniqueness constraint, FK cascade behavior, and the indexes needed for board filtering.

**Rationale:**
AC-1 and AC-6 need persisted project-scoped labels with duplicate protection; the label-filter NFR (≤ 300ms P95) needs supporting indexes.

**Acceptance Criteria:**
- [ ] `labels` table: UUID `id` PK, `project_id` FK → projects with cascade delete, `name` VARCHAR(30) NOT NULL, `color` restricted to the 12 accent tokens, `created_at`/`updated_at` timestamptz per Section 3 conventions
- [ ] Unique index on `(project_id, lower(name))` enforces case-insensitive per-project name uniqueness
- [ ] `task_labels` table: composite PK `(task_id, label_id)`, FKs cascading on both task delete and label delete, index on `label_id` for filter queries
- [ ] Migration applies cleanly on a database at migration 001

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-task-labels.sql (new) - labels + task_labels tables, indexes, constraints

**Technical Notes:**
- Enforce `color` with a CHECK constraint against the 12 token names (`accent-01` … `accent-12`)
- Cascade from `labels` deletes assignments only — tasks are never touched (Section 6 rule)
- The max-10-labels-per-task rule is enforced in the repository transaction, not as a DB constraint

### T-003: Implement Label and TaskLabel repository modules

**Type:** Backend
**Workflow:** standard

**Description:**
Add `src/db/label.ts` and `src/db/task-label.ts` repository modules — one per entity, per CLAUDE.md Convention 5 — holding all SQL for label CRUD and assignment management. Include the queries the routers need: list with per-label task counts, case-insensitive duplicate detection, and atomic label-set replacement.

**Rationale:**
Convention 5 keeps SQL out of routers; these modules are the persistence layer behind every label endpoint.

**Acceptance Criteria:**
- [ ] `src/db/label.ts` exposes list (with per-label task counts), get-by-id, create, update (rename/recolor), and delete
- [ ] `src/db/task-label.ts` exposes a replace-set operation running in one transaction that rejects more than 10 labels or labels from another project
- [ ] Duplicate-name detection is case-insensitive and surfaces a typed result the router can map to the `conflict` error code

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label repository (CRUD + task counts)
- src/db/task-label.ts (new) - assignment repository (replace set, list per task)

## Backend

### T-004: Document the label endpoints in the API spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the `labels` resource shard covering all five label endpoints, update the tasks shard for the board changes, and register the new endpoints in the index Endpoint Summary and Changelog.

**Rationale:**
FEAT-001 Section 7 requires the endpoint shard and summary rows before API implementation; the API index mandates summary and changelog discipline for new resources.

**Acceptance Criteria:**
- [ ] `docs/api-spec/endpoints/labels.md` documents GET/POST project labels, PUT/DELETE label, and PUT task label set — request/response bodies in the shared envelope, status codes, and error codes drawn from the existing catalog
- [ ] `LabelDto` (camelCase; list responses include `taskCount`) is defined in the shard
- [ ] `docs/api-spec/endpoints/tasks.md` documents the optional `labelId` query parameter and the `labels` array added to `TaskDto`
- [ ] `docs/api-spec/index.md` Endpoint Summary gains the five new label rows and a Changelog entry

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - labels resource shard (5 endpoints + DTOs)
- docs/api-spec/endpoints/tasks.md - labelId filter + labels array on TaskDto
- docs/api-spec/index.md - Endpoint Summary rows + Changelog

**Technical Notes:**
- Existing catalog codes suffice (`validation-error`, `unauthorized`, `not-found`, `conflict`) — no new catalog rows
- `taskCount` on the list response feeds the delete-confirmation dialog (AC-5) without adding a second endpoint

### T-005: Implement the label CRUD router

**Type:** Backend
**Workflow:** standard

**Description:**
Add `src/api/labels.ts` implementing GET/POST `/api/v1/projects/:projectId/labels` and PUT/DELETE `/api/v1/labels/:id`, mounted from `src/api/index.ts`. Validate with Zod, respond in the shared envelope, and map duplicate names to the `conflict` catalog code.

**Rationale:**
Implements label management (AC-1, AC-4, AC-5, AC-6) behind the endpoints defined in FEAT-001 Section 7.

**Acceptance Criteria:**
- [ ] POST validates name (1–30 chars after trimming) and color (one of the 12 accent tokens); violations return 400 `validation-error` with `fields`
- [ ] Duplicate name within the project (case-insensitive) returns 409 `conflict`; a successfully created label appears in the next GET list (AC-1)
- [ ] GET list returns `{ data, meta }` with per-label `taskCount`
- [ ] DELETE removes the label and all its assignments while leaving tasks intact; PUT renames/recolors with the same validation as create
- [ ] Concurrent renames resolve last-write-wins with no version-conflict error; a stale client sees the updated name on its next refetch

**Dependencies:** T-003, T-004
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - label CRUD router + Zod schemas
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Routers throw `ApiError`; the middleware in `src/api/errors.ts` serializes it
- Create/rename/delete are restricted to members with edit rights, reusing the authorization pattern of PATCH `/api/v1/tasks/:id`

### T-006: Implement the task label-set replacement endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Add PUT `/api/v1/tasks/:id/labels` to the tasks router, replacing the task's label set from an array of label IDs via the T-003 repository transaction. Enforce the max-10 rule and the same-project rule at the API boundary.

**Rationale:**
AC-2 needs label assignments to persist; the Section 9 edge case requires the 11th label to be rejected by the API with a validation error.

**Acceptance Criteria:**
- [ ] A valid request replaces the assignment set atomically and returns the task's updated label list in the envelope
- [ ] More than 10 label IDs returns 400 `validation-error`
- [ ] A label ID belonging to a different project returns 400 `validation-error`; a nonexistent task or label returns 404 `not-found`

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - PUT /api/v1/tasks/:id/labels route + Zod schema

### T-007: Add label data and labelId filtering to the board tasks query

**Type:** Backend
**Workflow:** standard

**Description:**
Extend the board list endpoint with an optional `labelId` query parameter and include each task's labels in `TaskDto`. Filtering stays server-side so results remain correct with pagination.

**Rationale:**
AC-3 requires label filtering, which Section 10 constrains to server-side; Section 10 also requires labels to ride the existing board response instead of per-card fetches.

**Acceptance Criteria:**
- [ ] GET `/api/v1/projects/:projectId/tasks` accepts an optional `labelId` (UUID) and returns only tasks carrying that label, with correct `meta.totalCount`
- [ ] Every returned `TaskDto` (board list and single-task GET) includes its `labels` array without an N+1 query pattern
- [ ] A malformed `labelId` returns 400 `validation-error`; a valid label with zero matching tasks returns an empty `data` array

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - labelId query validation + response assembly
- src/db/task.ts - board query label aggregation + filter join

**Technical Notes:**
- Aggregate labels in a single round-trip (JOIN + `json_agg`, or one batched IN-query) to hold the 300ms P95 filter NFR on 500-task boards
- Filtering by a deleted label returns an empty set; the client clears the filter on refetch (T-012)

## Frontend

### T-008: Document the UI changes across the UI specification

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the screen shard for the new Label Management Dialog, add LabelChip to the shared component inventory, and update the two modified screen shards plus the index Screen Inventory and Changelog.

**Rationale:**
FEAT-001 Section 8 requires the new screen shard, its inventory row, and the components.md entry; the UI index mandates shard discipline for new screens.

**Acceptance Criteria:**
- [ ] `docs/ui-specification/screens/label-management-dialog.md` covers layout, component hierarchy, Component → API mapping, all four states per index Section 2.5, and the create/rename/recolor/delete interactions including the delete confirmation
- [ ] `docs/ui-specification/components.md` gains a LabelChip entry with inputs/outputs and variants
- [ ] `docs/ui-specification/index.md` gains the Screen Inventory row and a Changelog entry
- [ ] `screens/project-board.md` (chips + filter dropdown) and `screens/task-detail-panel.md` (labels picker) reflect the modified hierarchies, states, and API mappings

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/components.md - LabelChip inventory entry
- docs/ui-specification/index.md - Screen Inventory row + Changelog
- docs/ui-specification/screens/project-board.md - chips + filter dropdown updates
- docs/ui-specification/screens/task-detail-panel.md - labels picker updates

### T-009: Build the LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Implement the reusable chip rendering a label's name on its accent color, used by board cards, the detail-panel picker, and the management dialog. Per-token text color must preserve WCAG 2.1 AA contrast.

**Rationale:**
Section 8 defines LabelChip as a shared component; a single implementation keeps rename/recolor updates consistent everywhere it renders (AC-4).

**Acceptance Criteria:**
- [ ] Renders the label name on its accent-token background using design-token CSS custom properties — no hard-coded hex values
- [ ] Chip text meets 4.5:1 contrast on all 12 accent tokens (NFR)
- [ ] Uses caption typography and `space-1` padding per the design system; long names truncate with an ellipsis and expose the full name via `title`

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared label chip component

### T-010: Build the Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Implement the Label Management Dialog — a new screen opened from the board toolbar — for creating, renaming, recoloring, and deleting project labels. Because this is a new user-facing screen, generate an HTML mockup of the Label Management Dialog for stakeholder approval per `.ai-framework/prompts/mockup-generation.md` before implementing.

**Rationale:**
Implements the label-management UI for AC-1, AC-5, and AC-6; FEAT-001 Section 8 classifies frontend work on this new screen as mockup-first.

**Acceptance Criteria:**
- [ ] Create form offers a name input and a 12-token palette picker; a newly created label appears in the dialog's label list immediately (AC-1)
- [ ] Submitting a duplicate name shows the server's validation message inline next to the name field (AC-6)
- [ ] Delete requires a confirmation `Dialog` (destructive variant) stating how many tasks carry the label before assignments are removed (AC-5)
- [ ] Rename/recolor changes propagate to every rendered chip via TanStack Query invalidation, without a page reload (AC-4)
- [ ] Loading, empty, and error states follow index Section 2.5 (`EmptyState` when the project has no labels)

**Dependencies:** T-005, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen component
- src/ui/project-board.tsx - toolbar entry point that opens the dialog

**Technical Notes:**
- Reuse the shared `Dialog` component (destructive variant) for the delete confirmation
- The palette picker uses the accent tokens from UI index Section 2.1 — no external color-picker dependency (Section 10 constraint)
- `taskCount` from the labels list response supplies the confirmation dialog's affected-task count

### T-011: Add the labels picker to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to the task detail panel with a multi-select picker showing chip previews. Selections persist via the label-set replacement endpoint and reflect on the board card without a page reload.

**Rationale:**
AC-2 requires assigning and removing labels from the detail panel with immediate board reflection; the Section 9 edge case requires the picker to stop at 10 labels.

**Acceptance Criteria:**
- [ ] Picker lists all project labels with LabelChip previews and pre-selects the task's current labels
- [ ] Assigning/removing persists via PUT `/api/v1/tasks/:id/labels` and updates the board card through query invalidation, with no page reload (AC-2)
- [ ] With 10 labels assigned, remaining options are disabled with an explanatory tooltip
- [ ] Field states follow index Section 2.5 (skeleton row while loading, inline error banner on failed save)

**Dependencies:** T-005, T-006, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field, picker, and mutation wiring

### T-012: Render board label chips and the single-label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Show up to 3 label chips with a "+N" overflow indicator on each task card and add a single-label filter dropdown to the board toolbar. The filter drives the server-side `labelId` parameter; clearing it restores the full board.

**Rationale:**
Implements AC-3 and the chip display from Section 4.1; Section 9 defines the zero-match and deleted-while-filtered behaviors this task must handle.

**Acceptance Criteria:**
- [ ] Task cards render up to 3 LabelChips plus a "+N" overflow indicator when a task has more labels (default and compact variants)
- [ ] Selecting a label in the toolbar dropdown refetches the board with `labelId` and shows only matching tasks; "Clear filter" restores the full board (AC-3)
- [ ] A filter with zero matching tasks shows the standard `EmptyState` with a "Clear filter" CTA — never a blank board
- [ ] If the filtered label was deleted by another user, the next refetch clears the filter and shows a notice

**Dependencies:** T-005, T-007, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/project-board.tsx - filter dropdown, filter state, deleted-label notice
- src/ui/components/task-card.tsx - chip row in default and compact variants

**Technical Notes:**
- The dropdown's options come from the same GET labels query the dialog uses (shared TanStack Query cache)
- Rename/recolor propagate to cards automatically because chips render from query data (AC-4)

## Testing

### T-013: Unit-test the label repositories

**Type:** Testing
**Workflow:** standard

**Description:**
Add unit tests for `src/db/label.ts` and `src/db/task-label.ts` against the test database, mirroring the `src/` tree per Convention 6.

**Rationale:**
Convention 6 requires a unit test per repository; the core business rules (uniqueness, max 10, cascades) live in this layer.

**Acceptance Criteria:**
- [ ] Case-insensitive duplicate detection covered ("Urgent" vs "urgent" is rejected)
- [ ] Replace-set: atomic replacement verified; more than 10 labels rejected; cross-project label rejected
- [ ] Deleting a label removes its assignments but not the tasks; deleting a task removes its assignments
- [ ] Per-label task-count query returns correct counts for the delete confirmation

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - assignment repository unit tests

### T-014: Integration-test the label API

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests for the label endpoints and the modified board endpoint, covering happy paths and the Section 9 edge cases observable at the API boundary.

**Rationale:**
Convention 6 requires a Supertest integration test per router; AC-1, AC-2, AC-3, AC-5, and AC-6 are verified at this level.

**Acceptance Criteria:**
- [ ] Label CRUD happy path: create → list (with `taskCount`) → rename/recolor → delete, all responses in the shared envelope
- [ ] 409 `conflict` on duplicate names including case-only differences; 400 `validation-error` on bad name/color and on an 11th label
- [ ] DELETE removes assignments while tasks survive; the label-set PUT round-trips correctly
- [ ] Board GET with `labelId` returns only matching tasks with correct `meta`; without it, every task carries its `labels` array

**Dependencies:** T-005, T-006, T-007
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - label + assignment endpoint tests
- tests/api/tasks.test.ts - board filter and labels-in-response tests

### T-015: UI-test the label flows

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest UI tests for the three touched surfaces — board, detail panel, and management dialog — covering the end-to-end label flows against mocked API responses.

**Rationale:**
AC-2, AC-3, AC-4, AC-5, and AC-6 include UI behaviors (no-reload updates, filter behavior, confirmation dialog, inline errors) that only UI tests verify.

**Acceptance Criteria:**
- [ ] Cards render up to 3 chips plus overflow; chips update after a rename/recolor invalidation (AC-4)
- [ ] Filter select/clear shows and restores the correct cards; a zero-match filter renders `EmptyState` with the clear CTA (AC-3)
- [ ] Picker assigns/removes labels, disables at 10 with a tooltip, and the board card updates without reload (AC-2)
- [ ] Dialog: created label appears in the list, duplicate name shows the inline error (AC-6), and delete confirmation states the affected task count (AC-5)

**Dependencies:** T-010, T-011, T-012
**Complexity:** L

**Files to Modify/Create:**
- tests/ui/label-management-dialog.test.tsx (new) - dialog flow tests
- tests/ui/project-board.test.tsx (new) - chips + filter tests
- tests/ui/task-detail-panel.test.tsx (new) - labels picker tests

## Summary

**Feature Brief:** FEAT-001 — Task Labels (TaskFlow v1.1)

**Task count by type (15 total):**

| Type | Count | Tasks |
|------|-------|-------|
| Documentation | 3 | T-001, T-004, T-008 |
| Database | 1 | T-002 |
| Backend | 4 | T-003, T-005, T-006, T-007 |
| Frontend | 4 | T-009, T-010, T-011, T-012 |
| Testing | 3 | T-013, T-014, T-015 |

**Complexity distribution:** S: 2 · M: 8 · L: 5 · XL: 0

**Critical path (6 tasks):** T-001 → T-002 → T-003 → T-005 → T-010 → T-015. An equal-length chain runs through the spec/UI side: T-001 → T-004 → T-008 → T-009 → T-010 → T-015 — authoring the spec shards early keeps the two chains parallel rather than serialized.

**Risks / open questions:**

- The delete-confirmation task count (AC-5) is sourced from `taskCount` on the labels list response — a deliberate API design choice documented in T-004. The count can go momentarily stale under concurrent edits, consistent with the feature's last-write-wins posture.
- "Members with edit rights" is resolved by the external auth service; label mutation endpoints reuse the existing PATCH-task authorization pattern rather than introducing a local permission model.
- The 300ms P95 filter NFR depends on the `task_labels(label_id)` index and single-round-trip label aggregation (T-002, T-007); verify against a 500-task board before release.
- Documentation-type spec-shard tasks are placed ahead of implementation (Foundation/Backend/Frontend groups) to honor the work item's create-shards-before-feature-logic mandate; the Documentation & Polish group is therefore empty and omitted.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label (name 1–30 chars + palette color); it appears in the project's label list | T-002, T-005, T-010, T-014 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and appear on the board card without a reload | T-006, T-011, T-014, T-015 |
| AC-3: Filtering by a label shows only tasks carrying it; clearing restores the full board | T-007, T-012, T-014, T-015 |
| AC-4: Renaming or recoloring a label updates every task card displaying it | T-005, T-009, T-012, T-015 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-005, T-010, T-014, T-015 |
| AC-6: Duplicate label name in the same project returns a validation error with an inline UI message | T-002, T-005, T-010, T-014 |
