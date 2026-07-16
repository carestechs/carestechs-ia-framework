# FEAT-001 — Task Labels — Implementation Task List

> Generated from `docs/work-items/FEAT-001-task-labels.md` (**FEAT-001**) following `prompts/feature-tasks.md` and the canonical task schema in `prompts/base-template.md`. All file paths are relative to the project root; files that do not exist yet are marked `(new)`.

---

## Foundation

### T-001: Author Label and TaskLabel data-model shards and register them in the index

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for `Label` and `TaskLabel` following the data-model shard conventions, documenting fields, indexes, relationships, and business rules. Register both entities in the index: Module Ownership row (Projects module), Relationships Overview entries (Project 1:N Label; Task N:M Label via `task_labels`), and a Changelog row.

**Rationale:**
Work item Section 6 requires the new entities to be documented before feature logic, and the data-model index Usage Notes require every new entity to get a shard plus index registration.

**Acceptance Criteria:**
- [ ] `entities/label.md` documents: UUID `id` PK, `project_id` FK (cascade delete from project), `name` varchar(30) unique per project case-insensitively, `color` restricted to the 12 accent palette tokens, timestamps
- [ ] `entities/task-label.md` documents the N:M join: composite key, cascade behavior (label delete removes assignments only, never tasks), max 10 labels per task, same-project rule
- [ ] `docs/data-model/index.md` Module Ownership, Relationships Overview (4.1/4.2), and Changelog are updated and consistent with the shards
- [ ] Shards use kebab-case singular naming and the standard entity front-matter (`kind`, `name`, `module`, `endpoints`, `screens`)

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard (fields, indexes, relationships, rules)
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity shard (N:M, max-10, same-project rule)
- docs/data-model/index.md - Module Ownership + Relationships Overview + Changelog entries

**Technical Notes:**
- Multi-word entity maps to kebab-case: `TaskLabel` → `entities/task-label.md`
- Keep index Section 4 and the per-shard Relationships tables in sync (index requirement)

---

### T-002: Create database migration for labels and task_labels tables

**Type:** Database
**Workflow:** standard

**Description:**
Write `migrations/002-labels.sql` creating the `labels` table and the `task_labels` join table with foreign keys, cascade rules, and the indexes needed for uniqueness and board filtering.

**Rationale:**
AC-1 and AC-6 require persistent, per-project, case-insensitively unique labels; AC-2/AC-3 require a task↔label join that supports assignment and server-side filtering.

**Acceptance Criteria:**
- [ ] `labels`: `id` UUID PK, `project_id` UUID NOT NULL FK → `projects(id)` ON DELETE CASCADE, `name` VARCHAR(30) NOT NULL, `color` VARCHAR NOT NULL, `created_at`/`updated_at` TIMESTAMPTZ NOT NULL
- [ ] Unique index on `(project_id, lower(name))` enforces case-insensitive per-project name uniqueness
- [ ] `task_labels`: composite PK `(task_id, label_id)`, both FKs ON DELETE CASCADE, plus an index on `label_id` to support board filtering
- [ ] Migration applies cleanly on a database at `001-init.sql` state

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - labels + task_labels tables, constraints, indexes

**Technical Notes:**
- `color` stores the accent token name (e.g. `accent-07`); membership in the 12-token palette is validated at the API layer
- Table/column naming per data-model index Section 3 (snake_case, plural tables)

---

### T-003: Implement label repository module

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` with repository functions for listing a project's labels, creating, renaming/recoloring, and deleting a label, plus a per-label assigned-task count used by the delete confirmation.

**Rationale:**
CLAUDE.md convention 5: SQL lives only in `src/db/` repository modules, one per entity; routers never touch `pg` directly.

**Acceptance Criteria:**
- [ ] `listByProject`, `create`, `update` (name and/or color), and `delete` functions exist and return typed rows
- [ ] Duplicate-name violations (case-insensitive, per project) surface as a detectable error the router can map to the `conflict` catalog code
- [ ] Deleting a label removes its `task_labels` rows (via cascade) and never deletes tasks
- [ ] A function returns the count of tasks currently carrying a given label (powers AC-5's confirmation text)

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label repository (CRUD + assigned-task count)

---

### T-004: Implement task-label assignment repository module

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/task-label.ts` with a transactional replace-set operation for a task's labels and a batch fetch that returns labels for many tasks at once for the board response.

**Rationale:**
AC-2 needs atomic assign/remove persistence; the Section 10 constraint requires labels embedded in the existing board response, which needs a batch (non-N+1) fetch.

**Acceptance Criteria:**
- [ ] `replaceForTask(taskId, labelIds)` replaces the task's label set in one transaction
- [ ] Replace rejects sets larger than 10 and label IDs whose `project_id` differs from the task's project, with distinct error signals
- [ ] `getForTasks(taskIds)` returns all labels for the given tasks in one query, keyed by task ID
- [ ] Repository is the only place with SQL for `task_labels` (convention 5)

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/task-label.ts (new) - assignment repository (replace set, batch fetch)

---

## Backend

### T-005: Author labels API-spec shard and update tasks shard and endpoint summary

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` specifying the LabelDto and all five label endpoints (list, create, rename/recolor, delete, and PUT `/api/v1/tasks/{id}/labels`), then add the five rows to the index Endpoint Summary with a Changelog entry. Update `endpoints/tasks.md`: the board list gains the optional `labelId` query parameter and TaskDto gains a `labels` array.

**Rationale:**
Work item Section 7 requires the new endpoints shard before frontend integration; the api-spec index requires every new endpoint to appear in the Endpoint Summary.

**Acceptance Criteria:**
- [ ] `endpoints/labels.md` defines LabelDto (id, projectId, name, color, taskCount) and all five endpoints with request/response bodies, envelope, and status codes using only Error Catalog codes (`validation-error`, `unauthorized`, `not-found`, `conflict`)
- [ ] POST create documents 409 `conflict` for duplicate names (case-insensitive); PUT `/tasks/{id}/labels` documents `validation-error` for >10 labels or cross-project labels
- [ ] `docs/api-spec/index.md` Endpoint Summary gains the five rows and the Changelog records the change
- [ ] `endpoints/tasks.md` documents the `labelId` query parameter on the board list and the `labels: LabelDto[]` field on TaskDto

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - labels resource shard (five endpoints, LabelDto)
- docs/api-spec/index.md - Endpoint Summary rows + Changelog
- docs/api-spec/endpoints/tasks.md - labelId filter parameter + labels field on TaskDto

**Technical Notes:**
- Nested routes group under the resource being operated on, so `/api/v1/tasks/{id}/labels` belongs in the labels shard
- `taskCount` on LabelDto powers the delete-confirmation dialog (AC-5) without an extra endpoint

---

### T-006: Implement label CRUD router

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}` with Zod validation, and mount the router in `src/api/index.ts`.

**Rationale:**
Work item Section 7 defines these endpoints as the backend surface for AC-1, AC-4, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] POST validates name (1–30 chars after trimming) and color (one of the 12 accent tokens) via Zod; failures return 400 `validation-error` with `fields`
- [ ] Duplicate name in the same project (case-insensitive) returns 409 `conflict` naming the field; unknown project/label returns 404 `not-found`
- [ ] GET list returns the envelope with LabelDto items including `taskCount`; responses never expose raw rows
- [ ] PUT renames/recolors with the same validation; DELETE removes the label and its assignments, leaving tasks untouched
- [ ] Router is mounted under `/api/v1` and all endpoints require the bearer token

**Dependencies:** T-003, T-005
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - label CRUD routes + Zod schemas
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Throw `ApiError`; serialization stays in `src/api/errors.ts`
- Concurrent renames are last-write-wins (no version check) per work item Section 9

---

### T-007: Implement replace-task-labels endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Add PUT `/api/v1/tasks/{id}/labels` to the labels router: accept an array of label IDs, replace the task's label set atomically, and return the updated assignment.

**Rationale:**
AC-2 requires assigning/removing labels from the detail panel with persistence; work item Section 6 imposes the max-10 and same-project rules.

**Acceptance Criteria:**
- [ ] Valid request replaces the full label set transactionally and returns the updated labels in the envelope
- [ ] More than 10 label IDs returns 400 `validation-error` (the 11th-label edge case)
- [ ] Label IDs from another project return 400 `validation-error`; unknown task returns 404 `not-found`
- [ ] Duplicate IDs in the request are deduplicated rather than rejected

**Dependencies:** T-004, T-005, T-006
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - PUT /tasks/{id}/labels handler + Zod schema

---

### T-008: Add labelId board filter and embed labels in task responses

**Type:** Backend
**Workflow:** standard

**Description:**
Extend GET `/api/v1/projects/{projectId}/tasks` with an optional `labelId` query parameter filtering server-side in SQL, and embed each task's labels in the board response via the batch fetch. Include the `labels` array in GET `/api/v1/tasks/{id}` as well so the detail panel gets initial state.

**Rationale:**
AC-3 requires label filtering, and Section 10 constraints require server-side filtering (correct with pagination) and labels included in the existing board response (no per-card fetches).

**Acceptance Criteria:**
- [ ] `labelId` (UUID, optional) is Zod-validated; invalid values return 400 `validation-error`
- [ ] With `labelId` set, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count
- [ ] Board items and the single-task response include `labels: LabelDto[]`, populated with one batch query (no N+1)
- [ ] Omitting `labelId` preserves current behavior exactly (ordering, pagination, envelope)

**Dependencies:** T-004, T-005
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - labelId query param, labels in responses
- src/db/task.ts - filtered board query (join on task_labels when labelId present)

**Technical Notes:**
- The `task_labels(label_id)` index from T-002 supports the filter; target the ≤300ms P95 NFR for 500-task boards

---

## Frontend

### T-009: Author label-management-dialog UI shard and update UI spec docs

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/ui-specification/screens/label-management-dialog.md` (layout sketch, component hierarchy, component→API mapping, states, interactions), add its Screen Inventory row and a Changelog entry to the UI index, and add LabelChip to `components.md`. Update the project-board and task-detail-panel shards for label chips, the filter dropdown, and the Labels field.

**Rationale:**
Work item Section 8 requires the new screen shard and LabelChip inventory entry; the UI index requires spec updates for modified screens so shards stay in sync with the feature.

**Acceptance Criteria:**
- [ ] `screens/label-management-dialog.md` covers all four states (default, loading, empty, error) and maps interactions to the five label endpoints
- [ ] `components.md` documents LabelChip (inputs/outputs, variants) as a shared component
- [ ] `docs/ui-specification/index.md` gains the Screen Inventory row and a Changelog entry
- [ ] `screens/project-board.md` documents chips on cards (max 3 + overflow), the toolbar label filter, and the filtered empty state; `screens/task-detail-panel.md` documents the Labels multi-select field

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/index.md - Screen Inventory row + Changelog
- docs/ui-specification/components.md - LabelChip inventory entry
- docs/ui-specification/screens/project-board.md - chips, filter dropdown, empty-filter state
- docs/ui-specification/screens/task-detail-panel.md - Labels field + picker

---

### T-010: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create `src/ui/components/label-chip.tsx` rendering a label's name on its accent-palette color, with a per-token text color that keeps WCAG 2.1 AA contrast, for reuse by board cards, the detail-panel picker, and the management dialog.

**Rationale:**
Work item Section 8 defines LabelChip as a new shared component; the NFR requires 4.5:1 chip text contrast on every palette color.

**Acceptance Criteria:**
- [ ] Renders label name + color from the accent tokens via CSS custom properties (no hard-coded hex)
- [ ] Text color per token meets 4.5:1 contrast on all 12 accent colors
- [ ] Supports an optional remove affordance (for the picker) and truncates long names within the chip
- [ ] Uses `caption` typography and `space-1` padding per the design system

**Dependencies:** T-009
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component (CSS Modules)

---

### T-011: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Build the Label Management Dialog — a new screen requiring an HTML mockup for stakeholder approval before implementation (see `.ai-framework/prompts/mockup-generation.md`) — opened from the board toolbar. It lists the project's labels and supports create, rename, recolor, and delete using the fixed 12-token palette picker.

**Rationale:**
Work item Section 8 introduces this new screen (flagged mockup-first) as the management surface behind AC-1, AC-4, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] Creating a label (name 1–30 chars + palette color) makes it appear in the dialog's list immediately (AC-1)
- [ ] Submitting a duplicate name shows the server's validation message inline next to the name field without closing the dialog (AC-6)
- [ ] Delete first shows a confirmation `Dialog` (destructive variant) stating how many tasks carry the label, then removes it everywhere (AC-5)
- [ ] Rename/recolor persists and updates every visible chip via query invalidation (AC-4)
- [ ] Color picker offers exactly the 12 accent tokens — no custom hex input, no new dependencies

**Dependencies:** T-006, T-009, T-010
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen (list + create/rename/recolor/delete)
- src/ui/project-board.tsx - "Manage labels" button in BoardToolbar

**Technical Notes:**
- Reuse shared `Dialog` for the shell and the delete confirmation; `EmptyState` (inline variant) when the project has no labels
- Handle all four states per UI index Section 2.5; TanStack Query mutations invalidate the labels and board queries

---

### T-012: Add Labels field with multi-select picker to the task detail panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to the task detail panel: a multi-select picker showing LabelChip previews of the project's labels, saving changes via PUT `/api/v1/tasks/{id}/labels`.

**Rationale:**
AC-2 requires assigning and removing labels from the detail panel with changes appearing on the board card without a page reload.

**Acceptance Criteria:**
- [ ] Current labels render as chips; the picker lists the project's labels with chip previews and toggles assignment
- [ ] Saving persists via the replace endpoint, and the board card's chips update through query invalidation without a page reload (AC-2)
- [ ] With 10 labels assigned, further selection is disabled with an explanatory tooltip (11th-label edge case)
- [ ] Loading and error states follow UI index Section 2.5 patterns

**Dependencies:** T-007, T-009, T-010
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field + picker wiring

---

### T-013: Render label chips on board cards and add single-label board filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 LabelChips per TaskCard with a "+N" overflow indicator, and add a single-label filter dropdown to the BoardToolbar that drives the board query's `labelId` parameter.

**Rationale:**
AC-3 requires filtering the board to one label and restoring it on clear; Section 8 specifies chips on cards and the toolbar filter.

**Acceptance Criteria:**
- [ ] Cards show at most 3 chips plus a "+N" indicator when a task has more (default variant; compact variant stays title-only)
- [ ] Selecting a label in the dropdown refetches with `labelId` so only matching tasks render; clearing the filter restores the full board (AC-3)
- [ ] A filter with zero matching tasks shows `EmptyState` with a "Clear filter" CTA — never a blank board
- [ ] If the filtered label no longer exists after a refetch (deleted by another user), the filter clears automatically and a notice is shown

**Dependencies:** T-008, T-009, T-010
**Complexity:** L

**Files to Modify/Create:**
- src/ui/project-board.tsx - filter dropdown state, labelId in the board query key, empty/notice handling
- src/ui/components/task-card.tsx - chip row + overflow indicator

**Technical Notes:**
- Filtering stays server-side (query parameter) per Section 10 — do not filter client-side over the paginated response
- Rename/recolor propagate to cards via board query invalidation (stale clients converge on refresh)

---

## Testing

### T-014: Write backend tests for label repositories and routers

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests for the labels router and the replace-labels endpoint, unit tests for both new repositories against the test database, and extend the tasks router tests for the `labelId` filter and embedded labels.

**Rationale:**
CLAUDE.md convention 6: every router gets a Supertest integration test and every repository gets a unit test; the work item's edge cases need regression coverage.

**Acceptance Criteria:**
- [ ] Label CRUD happy paths pass, including envelope shape and `taskCount`
- [ ] Duplicate names — including case-only variants ("Urgent" vs "urgent") — return 409 `conflict`; invalid name/color returns 400 with `fields`
- [ ] Replace-set tests cover the 11-label rejection, cross-project rejection, and transactional replace
- [ ] Deleting an assigned label removes assignments while tasks survive
- [ ] Board list tests cover `labelId` filtering with correct `meta.totalCount` and labels embedded without N+1 regressions

**Dependencies:** T-006, T-007, T-008
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router + replace-endpoint integration tests
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - assignment repository unit tests
- tests/api/tasks.test.ts - labelId filter + embedded-labels cases

---

### T-015: Write frontend component tests for label UI

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for LabelChip, the Label Management Dialog, the detail-panel picker, and the board chips/filter behavior.

**Rationale:**
CLAUDE.md convention 6 places tests under `tests/` mirroring `src/`; the UI acceptance criteria (AC-2, AC-3, AC-5, AC-6) need automated verification.

**Acceptance Criteria:**
- [ ] LabelChip renders every accent token with its mapped text color and truncates long names
- [ ] Dialog tests cover create success, inline duplicate-name error, and delete confirmation showing the affected-task count
- [ ] Picker tests cover toggling labels and the disabled state + tooltip at 10 labels
- [ ] Board tests cover the 3-chip + "+N" overflow rendering, filter select/clear, and the filtered empty state with "Clear filter" CTA

**Dependencies:** T-011, T-012, T-013
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/label-chip.test.tsx (new) - chip rendering + contrast token mapping
- tests/ui/label-management-dialog.test.tsx (new) - dialog CRUD flows
- tests/ui/task-detail-panel.test.tsx (new) - picker behavior
- tests/ui/project-board.test.tsx (new) - chips, filter, empty state

---

## Summary

**Work item:** FEAT-001 — Task Labels (v1.1)

**Total tasks by type:**

| Type | Count |
|------|-------|
| Documentation | 3 (T-001, T-005, T-009) |
| Database | 1 (T-002) |
| Backend | 5 (T-003, T-004, T-006, T-007, T-008) |
| Frontend | 4 (T-010, T-011, T-012, T-013) |
| Testing | 2 (T-014, T-015) |
| **Total** | **15** |

**Complexity distribution:** S ×2 (T-001, T-010) · M ×9 (T-002, T-003, T-004, T-005, T-007, T-008, T-009, T-012, T-015) · L ×4 (T-006, T-011, T-013, T-014) · XL ×0

**Critical path (longest dependency chain, 7 tasks):**
T-001 → T-002 → T-003 → T-006 → T-007 → T-012 → T-015

**Risks / open questions:**

- The tasks shard update (T-005) assumes GET `/api/v1/tasks/{id}` also embeds `labels` so the detail panel has initial state — confirm this during spec authoring, since the work item only marks the board list as modified.
- `taskCount` on LabelDto adds a count aggregate to the label list query; trivial at pilot scale but worth watching against the ≤300ms P95 board NFR as boards approach 500 tasks.
- The "filtered label deleted by another user" notice (Section 9) has no specified UX copy or surface — T-009 must define it before T-013 implements it.
- Last-write-wins on concurrent renames is accepted per Section 9; no optimistic-locking task was generated to avoid over-engineering beyond the stated requirement.

---

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: A project member can create a label with a name (1–30 chars) and a palette color; the label immediately appears in the project's label list | T-002, T-003, T-006, T-011, T-014, T-015 |
| AC-2: A user can assign and remove labels on a task from the task detail panel; changes persist and appear on the board card without a page reload | T-004, T-007, T-012, T-014, T-015 |
| AC-3: Selecting a label in the board filter shows only tasks carrying that label; clearing the filter restores the full board | T-008, T-013, T-014, T-015 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-006, T-011, T-013, T-014, T-015 |
| AC-5: Deleting a label removes it from all tasks after an explicit confirmation dialog stating how many tasks are affected | T-003, T-006, T-011, T-014, T-015 |
| AC-6: Attempting to create a duplicate label name within the same project returns a validation error and the UI shows an inline message | T-002, T-006, T-011, T-014, T-015 |
