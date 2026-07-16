# FEAT-001 — Task Labels — Implementation Tasks

Task breakdown for the **Task Labels** feature (work item: `docs/work-items/FEAT-001-task-labels.md`). Schema: canonical task schema from `prompts/base-template.md`; grouping: Foundation → Backend → Frontend → Testing. All file paths are relative to the project root; files that do not exist yet are suffixed `(new)`.

---

## Foundation

### T-001: Author Label and TaskLabel data-model shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for `Label` and `TaskLabel` following the existing shard format (frontmatter, Fields, Indexes, Relationships, Entity-Specific Rules). Update the data-model index: Module Ownership rows, the Many-to-Many section of Relationships Overview, and the Changelog.

**Rationale:**
Work item Section 6 requires the new entities to be documented before feature logic, and the index must stay in sync with its shards (it doubles as the shard directory).

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` defines fields (`id` UUID PK, `project_id` FK, `name` varchar(30), `color` accent token, timestamps), case-insensitive per-project name uniqueness, and the 12-token palette rule
- [ ] `docs/data-model/entities/task-label.md` defines the Task↔Label N:M join (`task_id`, `label_id`), the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities and a Section 4.2 M:N entry recording that deleting a label cascades to assignments only, never to tasks
- [ ] Changelog rows record the additions with date and reason (FEAT-001)

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard
- docs/data-model/entities/task-label.md (new) - TaskLabel join-entity shard
- docs/data-model/index.md - Module Ownership rows, M:N relationship entry, Changelog

### T-002: Create labels and task_labels database migration

**Type:** Database
**Workflow:** standard

**Description:**
Add a plain SQL migration creating the `labels` and `task_labels` tables exactly as specified by the new entity shards, including uniqueness and filtering indexes and FK cascade behavior.

**Rationale:**
AC-1 through AC-5 need persistent storage; the schema must guarantee that deleting a label removes assignments but never tasks.

**Acceptance Criteria:**
- [ ] `labels`: `id` UUID PK, `project_id` FK → `projects` ON DELETE CASCADE, `name` VARCHAR(30) NOT NULL, `color` VARCHAR(12) NOT NULL, `created_at`/`updated_at` timestamptz
- [ ] Unique index on `(project_id, lower(name))` enforces case-insensitive per-project name uniqueness
- [ ] `task_labels`: composite PK `(task_id, label_id)`, both FKs ON DELETE CASCADE, timestamps per convention, plus an index on `label_id` to support board filtering
- [ ] Migration applies cleanly on PostgreSQL 16 after `migrations/001-init.sql`

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- migrations/002-task-labels.sql (new) - create labels and task_labels tables with indexes

**Technical Notes:**
- `color` stores an accent-palette token string (`accent-01` … `accent-12`); token validity is enforced in the application layer (Zod), not a DB CHECK
- The max-10-labels-per-task rule is enforced in the repository transaction, not by a trigger — keeps the migration simple
- snake_case plural table names per data-model index Section 3

---

## Backend

### T-003: Author labels API spec shard and update tasks endpoint spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` documenting all five label endpoints (list/create project labels, rename/recolor, delete, replace a task's label set) with a `LabelDto`. Update `endpoints/tasks.md` for the `labelId` query parameter and the `labels` array embedded in `TaskDto`, and add the new rows to the index Endpoint Summary and Changelog.

**Rationale:**
Work item Section 7 requires the new endpoints specified before implementation; the Endpoint Summary doubles as the shard directory and must list every endpoint.

**Acceptance Criteria:**
- [ ] `labels.md` documents the five endpoints with request/response envelopes and status codes using existing Error Catalog codes: 409 `conflict` for duplicate names, 400 `validation-error` for bad input, >10 labels, or cross-project assignment
- [ ] `LabelDto` includes `id`, `projectId`, `name`, `color`, and `taskCount` (assignment count feeding the delete confirmation)
- [ ] `tasks.md` documents the optional `labelId` query parameter on the board list and the `labels` array on `TaskDto`
- [ ] `index.md` Endpoint Summary gains rows for all five endpoints pointing at `endpoints/labels.md`; Changelog updated

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - labels resource shard, all five endpoints
- docs/api-spec/endpoints/tasks.md - labelId query parameter, labels array on TaskDto
- docs/api-spec/index.md - Endpoint Summary rows, Changelog

**Technical Notes:**
- No new error codes are needed — `validation-error`, `conflict`, `not-found`, `unauthorized` cover every case, so the Error Catalog is unchanged
- Per the work item's retrieval key, nested routes group under the resource being operated on, so `PUT /api/v1/tasks/{id}/labels` is documented in `labels.md`

### T-004: Implement label and task-label repository modules

**Type:** Backend
**Workflow:** standard

**Description:**
Add `src/db/label.ts` (CRUD plus list-with-task-counts) and `src/db/task-label.ts` (transactional replace of a task's label set, batch fetch of labels for a page of tasks). Enforce the max-10 and same-project business rules inside the replace operation.

**Rationale:**
CLAUDE.md requires SQL to live only in `src/db/` with one repository module per entity; the join entity gets its own module.

**Acceptance Criteria:**
- [ ] Label create/rename surfaces the `(project_id, lower(name))` unique violation distinctly so the router can map it to 409 `conflict` (catches "Urgent" vs "urgent")
- [ ] `listByProject` returns labels with per-label assigned-task counts in a single query
- [ ] `replaceTaskLabels` runs in one transaction and rejects sets larger than 10 or containing labels from another project
- [ ] `deleteLabel` removes the label (assignments go via FK cascade) and returns the number of affected tasks; task rows are untouched
- [ ] `labelsForTaskIds` returns the labels for a whole page of tasks in one query (no N+1 for the board)

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - Label repository (CRUD, list with task counts)
- src/db/task-label.ts (new) - TaskLabel repository (replace set, batch fetch)

**Technical Notes:**
- Map pg error code 23505 on the unique index to a typed "duplicate" result rather than leaking the driver error

### T-005: Implement the labels router with the five label endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Add `src/api/labels.ts` implementing `GET`/`POST /api/v1/projects/{projectId}/labels`, `PUT`/`DELETE /api/v1/labels/{id}`, and `PUT /api/v1/tasks/{id}/labels` with Zod validation, and mount it in `src/api/index.ts`.

**Rationale:**
Implements the work item Section 7 API surface under the project's envelope, validation, and error-catalog conventions.

**Acceptance Criteria:**
- [ ] `POST` validates `name` (1–30 chars after trim) and `color` (one of the 12 accent tokens); duplicate name in the project → 409 `conflict`, invalid input → 400 `validation-error` with `fields`
- [ ] `GET` returns the `{ data, meta }` list envelope of `LabelDto` items including `taskCount`
- [ ] `PUT /labels/{id}` renames/recolors with the same validation; concurrent renames resolve last-write-wins (no version check) and the response returns the stored state
- [ ] `DELETE /labels/{id}` removes the label and its assignments but never tasks; unknown ids → 404 `not-found`
- [ ] `PUT /tasks/{id}/labels` replaces the full set; more than 10 labels or cross-project label ids → 400 `validation-error`

**Dependencies:** T-003, T-004
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - labels router, Zod schemas, all five endpoints
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Throw `ApiError` and let `src/api/errors.ts` serialize — never hand-build error JSON
- Label list is readable by any project member; create/rename/recolor/delete require edit rights — mirror the role check used by `PATCH /api/v1/tasks/{id}` in `src/api/tasks.ts`

### T-006: Add labelId filter and embedded labels to the board tasks endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Extend `GET /api/v1/projects/{projectId}/tasks` with an optional `labelId` query parameter filtered server-side in the board query, and embed each task's labels in the response via one batched lookup. Touches the Zod query schema in `src/api/tasks.ts` and the board query in `src/db/task.ts`.

**Rationale:**
AC-3 plus the Section 10 constraints: filtering must stay server-side so pagination remains correct, and labels ride the existing board response instead of per-card fetches.

**Acceptance Criteria:**
- [ ] With `labelId`, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count with pagination intact
- [ ] Without `labelId`, behavior is unchanged except each `TaskDto` gains a `labels` array
- [ ] Labels are attached with a single additional query for the whole page (no N+1), keeping initial board load flat
- [ ] Malformed `labelId` (non-UUID) → 400 `validation-error`; a `labelId` with zero matches returns an empty `data` array, not an error

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - board query gains labelId filter join and batched label attachment
- src/api/tasks.ts - Zod query schema gains optional labelId

**Technical Notes:**
- Filter via EXISTS/JOIN on `task_labels` using the `label_id` index — this is what keeps the 300ms P95 filter round-trip NFR reachable at 500 tasks
- Sort each task's labels deterministically (by name) so chip order is stable across refetches

---

## Frontend

### T-007: Author Label Management Dialog spec and update UI shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/ui-specification/screens/label-management-dialog.md` (layout sketch, component hierarchy, component→API mapping, all four states, interactions) and add its Screen Inventory row. Add LabelChip to `components.md`, and update the project-board and task-detail-panel shards for chips, the filter dropdown, and the Labels field.

**Rationale:**
Work item Section 8 requires the new screen's shard and inventory row; screen shards must keep describing what their screens actually render.

**Acceptance Criteria:**
- [ ] `label-management-dialog.md` covers create/rename/recolor/delete flows, the 12-token palette swatch picker, the inline duplicate-name error, and the destructive delete confirmation stating the affected task count
- [ ] `components.md` documents LabelChip (inputs, removable variant, used by board cards, detail-panel picker, and the dialog)
- [ ] `index.md` gains the Screen Inventory row for the dialog and a Changelog entry
- [ ] `project-board.md` and `task-detail-panel.md` reflect chips on cards (≤3 plus "+N" overflow), the toolbar filter dropdown, and the Labels picker field with their API mappings

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/index.md - Screen Inventory row, Changelog
- docs/ui-specification/components.md - LabelChip inventory entry
- docs/ui-specification/screens/project-board.md - chips, filter dropdown, toolbar button
- docs/ui-specification/screens/task-detail-panel.md - Labels picker field

### T-008: Build the LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Add `src/ui/components/label-chip.tsx` rendering a label's name on its accent-token color, with a per-token text color chosen to keep AA contrast, plus a removable variant for the picker.

**Rationale:**
Section 8 defines LabelChip as the one chip implementation shared by board cards, the detail-panel picker, and the management dialog; the WCAG NFR applies to every palette color.

**Acceptance Criteria:**
- [ ] Renders the label name on its accent-token background using CSS custom properties (no hard-coded hex), caption typography, and space-1 padding
- [ ] Chip text meets WCAG 2.1 AA contrast (4.5:1) on all 12 accent tokens
- [ ] Long names truncate with an ellipsis while the full name stays available (title attribute / sr-only)
- [ ] Removable variant exposes an accessible remove button firing `onRemove`

**Dependencies:** T-007
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component with removable variant

### T-009: Build the Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
The Label Management Dialog is a new user-facing screen — generate an HTML mockup for stakeholder approval per `.ai-framework/prompts/mockup-generation.md` before implementing. Then implement `src/ui/label-management-dialog.tsx` (create, rename, recolor, delete-with-confirmation) on the shared Dialog component, opened from a new board-toolbar button.

**Rationale:**
Covers the management flows behind AC-1 and AC-4–AC-6; the work item classifies tasks for this new screen as mockup-first.

**Acceptance Criteria:**
- [ ] Creating a label (name 1–30 chars plus a swatch from the 12 accent tokens — no new color-picker dependency) shows it immediately in the project's label list (AC-1)
- [ ] A duplicate name (case-insensitive) surfaces the server's 409 as an inline field message without closing the dialog (AC-6)
- [ ] Rename/recolor persists and updates every visible chip via TanStack Query invalidation, without a page reload (AC-4)
- [ ] Delete uses the destructive Dialog variant, states how many tasks are affected (from `taskCount`), and removes only assignments (AC-5)
- [ ] Loading, empty (EmptyState with a create CTA), and error states follow UI index Section 2.5

**Dependencies:** T-005, T-007, T-008
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen with CRUD flows
- src/ui/project-board.tsx - toolbar button that opens the dialog

**Technical Notes:**
- Reuse the shared `Dialog` (destructive variant) and `EmptyState` components — no external UI kit
- `taskCount` from the labels list response feeds the confirmation copy; refetch the list after every mutation

### T-010: Render label chips on board cards and add the label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 LabelChips with a "+N" overflow indicator on TaskCard, and add a single-select label filter dropdown to the BoardToolbar that drives the board query's `labelId` parameter.

**Rationale:**
The board is where labels become visible and filterable (AC-3, AC-4); the work item's Project Board modifications in Section 8.

**Acceptance Criteria:**
- [ ] Cards render at most 3 chips plus a "+N" overflow indicator; the compact variant stays title-only
- [ ] Selecting a label refetches the board server-side with `labelId`; clearing the filter restores the full board (AC-3)
- [ ] A filter with zero matching tasks shows the shared EmptyState with a "Clear filter" action — never a blank board
- [ ] If the active filter's label no longer exists after a refetch (deleted by another user), the filter clears automatically and a notice is shown
- [ ] Chips pick up renames/recolors from cache invalidation without a page reload (AC-4)

**Dependencies:** T-006, T-008
**Complexity:** L

**Files to Modify/Create:**
- src/ui/components/task-card.tsx - render label chips with overflow indicator
- src/ui/project-board.tsx - filter dropdown, labelId in the board query key, filtered empty state

**Technical Notes:**
- Include `labelId` in the TanStack Query key so filtered and unfiltered boards cache separately
- Labels arrive embedded in the board response (T-006) — no per-card label fetches

### T-011: Add the Labels picker to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to `src/ui/task-detail-panel.tsx` with a multi-select picker showing chip previews; changes call `PUT /api/v1/tasks/{id}/labels` with the full label-id set.

**Rationale:**
AC-2 makes the detail panel the place where labels are assigned and removed; Section 8 Task Detail Panel modification.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists via the PUT endpoint, and the board card updates through query invalidation without a page reload (AC-2)
- [ ] The picker disables further selection at 10 labels and shows an explanatory tooltip
- [ ] The picker lists the project's labels with chip previews; loading and error states follow UI index Section 2.5
- [ ] A server rejection (11th label, cross-project id) surfaces as an inline error and the selection reverts to the persisted set

**Dependencies:** T-005, T-008
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field with multi-select picker and save wiring

**Technical Notes:**
- Follows the existing field-editing pattern (standard form-field addition), so no mockup is required per the mockup-first exception for standard form screens

---

## Testing

### T-012: Write repository unit tests for labels

**Type:** Testing
**Workflow:** standard

**Description:**
Unit tests against the test database for the label and task-label repositories, covering uniqueness, cascade behavior, and assignment rules.

**Rationale:**
CLAUDE.md requires a unit test per repository; the Section 9 edge cases around duplicates, cascades, and the 10-label cap live at this layer.

**Acceptance Criteria:**
- [ ] Names differing only by case ("Urgent" vs "urgent") are rejected within a project but the same name is allowed in different projects
- [ ] Deleting a label removes its assignments, reports the affected-task count, and leaves task rows untouched
- [ ] `replaceTaskLabels` rejects an 11th label and labels belonging to another project; a valid replace is atomic
- [ ] `labelsForTaskIds` returns the correct labels for multiple tasks in one call

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - task-label repository unit tests

### T-013: Write API integration tests for label endpoints and board filter

**Type:** Testing
**Workflow:** standard

**Description:**
Supertest integration tests for the five label endpoints and the modified board list endpoint, asserting envelopes, error-catalog codes, and filter correctness.

**Rationale:**
CLAUDE.md requires a Supertest integration test per router; AC-1 through AC-6 all need API-level verification.

**Acceptance Criteria:**
- [ ] Label CRUD happy paths return the `{ data }` / `{ data, meta }` envelopes; duplicate-name POST → 409 `conflict`; invalid name or color token → 400 `validation-error` with `fields`
- [ ] `PUT /tasks/{id}/labels` persists a valid replace; an 11-label set or a cross-project label id → 400 `validation-error`
- [ ] Board GET with `labelId` returns only matching tasks with correct `meta.totalCount`, correct pagination, and embedded `labels` arrays
- [ ] DELETE removes assignments (a subsequent board fetch shows the tasks without the label) and an unknown id → 404 `not-found`
- [ ] Two sequential renames resolve last-write-wins — a final GET returns the second name

**Dependencies:** T-005, T-006
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - board list labelId filter and embedded-labels assertions

### T-014: Write UI component tests for label surfaces

**Type:** Testing
**Workflow:** standard

**Description:**
Vitest component tests for LabelChip, the Label Management Dialog, the board chips and filter, and the detail-panel picker.

**Rationale:**
Verifies the user-visible halves of AC-1 through AC-6 and the Section 9 UI edge cases (overflow, zero-match filter, 10-label cap, deleted-while-filtered).

**Acceptance Criteria:**
- [ ] LabelChip renders all 12 accent tokens with their AA-contrast text colors and truncates long names
- [ ] Dialog: creating shows the new label in the list, a duplicate name shows the inline error, and the delete confirmation displays the affected task count
- [ ] Board: at most 3 chips plus "+N" render per card; selecting and clearing the filter updates the rendered tasks; a zero-match filter shows EmptyState with "Clear filter"; a deleted filtered label clears the filter with a notice
- [ ] Panel picker: disables at 10 labels with a tooltip; assigning/removing a label updates the board card render without a reload

**Dependencies:** T-009, T-010, T-011
**Complexity:** L

**Files to Modify/Create:**
- tests/ui/label-chip.test.tsx (new) - chip rendering and contrast tests
- tests/ui/label-management-dialog.test.tsx (new) - dialog CRUD flow tests
- tests/ui/project-board.test.tsx (new) - chips, filter, empty-state tests
- tests/ui/task-detail-panel.test.tsx (new) - picker behavior tests

---

## Summary

Generated from Feature Brief **FEAT-001** (Task Labels, target v1.1).

**Total task count by type:**

| Type | Count |
|------|-------|
| Documentation | 3 (T-001, T-003, T-007) |
| Database | 1 (T-002) |
| Backend | 3 (T-004, T-005, T-006) |
| Frontend | 4 (T-008, T-009, T-010, T-011) |
| Testing | 3 (T-012, T-013, T-014) |
| **Total** | **14** |

**Complexity distribution:** S ×3 (T-001, T-002, T-008) · M ×6 (T-003, T-004, T-006, T-007, T-011, T-012) · L ×5 (T-005, T-009, T-010, T-013, T-014) · XL ×0 — no task warranted XL; the largest surfaces were split instead.

**Critical path (longest dependency chain, 6 tasks):** T-001 → T-002 → T-004 → T-005 → T-009 → T-014.

**Risks and open questions:**

- Edit-rights enforcement is delegated to the auth service's claims; T-005 must mirror the exact role-check pattern used by `PATCH /api/v1/tasks/{id}` in `src/api/tasks.ts`, which should be confirmed during implementation.
- The stack has no e2e harness (Vitest + Supertest only), so verification tops out at component/integration level; the 300ms P95 filter NFR should be spot-checked against a seeded 500-task board rather than asserted in CI.
- Detection of "filtered label deleted by another user" (Section 9) relies on the client noticing the label's absence in the refetched label list — there is no server push; acceptable per the last-write-wins concurrency stance.
- `taskCount` on `LabelDto` adds an aggregate to the label list query; trivial at current data volumes but worth an index-backed count if label lists grow.
- No monitoring/logging tasks were generated: the project defines no logging infrastructure, and adding one is outside this feature's scope.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label (name 1–30 chars + palette color); it immediately appears in the project's label list | T-004, T-005, T-009, T-013 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and appear on the board card without reload | T-005, T-011, T-013, T-014 |
| AC-3: Selecting a label in the board filter shows only matching tasks; clearing restores the full board | T-006, T-010, T-013, T-014 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-005, T-009, T-010, T-014 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-004, T-005, T-009, T-013, T-014 |
| AC-6: Duplicate label name in the same project returns a validation error with an inline UI message | T-004, T-005, T-009, T-013 |
