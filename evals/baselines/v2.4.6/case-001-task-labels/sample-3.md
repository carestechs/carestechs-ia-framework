# FEAT-001 — Task Labels — Implementation Tasks

> **Work item:** `docs/work-items/FEAT-001-task-labels.md` (Feature Brief FEAT-001, target v1.1).
> Paths are relative to the project root. Files that do not exist yet are marked `(new)`.

---

## Foundation

### T-001: Author Label and TaskLabel data-model shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create entity shards for the new `Label` and `TaskLabel` entities and register them in the data-model index (Module Ownership, Relationships Overview, ERD, Changelog). Field definitions follow the Feature Brief's business rules: project-scoped labels with accent-palette colors, case-insensitive name uniqueness, and an N:M task join capped at 10 labels per task.

**Rationale:**
Section 6 of FEAT-001 requires the new entity shards to exist before feature logic; the sharded data model is the authority downstream tasks build against.

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` defines fields (`id`, `project_id`, `name` varchar(30), `color` accent token, timestamps), indexes, relationships, and business rules (case-insensitive per-project uniqueness; color restricted to the 12 accent tokens; delete cascades to assignments only, never tasks)
- [ ] `docs/data-model/entities/task-label.md` defines the join (task_id, label_id, timestamps), the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities, a Section 4.2 many-to-many entry (Task ↔ Label via `task_labels`), and a Changelog row

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- `docs/data-model/entities/label.md` (new) - Label entity shard
- `docs/data-model/entities/task-label.md` (new) - TaskLabel join-entity shard
- `docs/data-model/index.md` - Module Ownership, Relationships Overview (4.2), ERD, Changelog entries

### T-002: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add a plain SQL migration creating the `labels` table and the `task_labels` join table with foreign keys, cascade deletes, and the indexes needed for uniqueness and board filtering. Follow the naming and timestamp conventions in `docs/data-model/index.md` Section 3.

**Rationale:**
AC-1 through AC-5 all persist label data; the schema must exist before repositories and endpoints (Feature Brief: entities before feature logic).

**Acceptance Criteria:**
- [ ] `labels`: `id` UUID PK, `project_id` UUID FK → `projects` ON DELETE CASCADE, `name VARCHAR(30) NOT NULL`, `color` constrained to the 12 accent tokens (CHECK), `created_at`/`updated_at` timestamptz
- [ ] Unique index on `(project_id, lower(name))` enforces case-insensitive per-project name uniqueness at the database level
- [ ] `task_labels`: composite PK `(task_id, label_id)`, both FKs ON DELETE CASCADE, plus an index on `label_id` so label-filtered board queries stay within the 300ms P95 NFR
- [ ] Migration applies cleanly on a database at `migrations/001-init.sql` state

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- `migrations/002-labels.sql` (new) - create `labels` + `task_labels` tables, constraints, indexes

**Technical Notes:**
- The 10-labels-per-task cap is enforced in the repository/API layer (`validation-error`), not as a DB constraint — keeps the rule's error mapping in one place

### T-003: Author labels API spec shard and update tasks endpoint spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` documenting all five label endpoints with DTOs, request/response examples, and status codes. Update `docs/api-spec/endpoints/tasks.md` for the optional `labelId` board filter and the `labels` array embedded in `TaskDto`, and add the new endpoint rows to the index's Endpoint Summary and Changelog.

**Rationale:**
Section 7 of FEAT-001 requires the new endpoint shard before frontend integration; the Endpoint Summary doubles as the shard directory and must stay complete.

**Acceptance Criteria:**
- [ ] `labels.md` documents GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` using the standard envelope and pagination conventions
- [ ] `LabelDto` includes a `taskCount` field on the project list endpoint so the delete confirmation can state how many tasks are affected (AC-5) without adding an out-of-scope endpoint
- [ ] Error responses reuse existing catalog codes only: `validation-error` (name length, non-palette color, >10 labels, cross-project label), `conflict` (duplicate name, 409), `not-found`, `unauthorized`
- [ ] `tasks.md` documents the optional `labelId` query parameter and the embedded `labels` field; `index.md` Endpoint Summary + Changelog updated

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- `docs/api-spec/endpoints/labels.md` (new) - resource shard for the five label endpoints
- `docs/api-spec/endpoints/tasks.md` - `labelId` query parameter + `labels` in `TaskDto`
- `docs/api-spec/index.md` - Endpoint Summary rows + Changelog entry

### T-004: Author UI spec updates for label surfaces

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the Label Management Dialog screen shard and update the UI spec set: Screen Inventory row and Changelog in the index, a LabelChip entry in `components.md`, and label additions (card chips, toolbar filter, Labels field) to the project-board and task-detail-panel shards.

**Rationale:**
Section 8 of FEAT-001 requires the new screen shard and LabelChip inventory entry; frontend tasks implement against these shards.

**Acceptance Criteria:**
- [ ] `screens/label-management-dialog.md` specifies layout, component hierarchy, component → API mapping, all four states (default/loading/empty/error), and user interactions including the destructive delete confirmation
- [ ] `components.md` documents LabelChip (inputs: label, variant; AA-contrast text color chosen per accent token)
- [ ] `project-board.md` gains chips-on-cards (max 3 + "+N" overflow), the toolbar label filter, and filtered-empty-state behavior; `task-detail-panel.md` gains the Labels multi-select field
- [ ] `index.md` Screen Inventory row + Changelog entry added

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- `docs/ui-specification/screens/label-management-dialog.md` (new) - new screen shard
- `docs/ui-specification/index.md` - Screen Inventory row + Changelog
- `docs/ui-specification/components.md` - LabelChip inventory entry
- `docs/ui-specification/screens/project-board.md` - chips, filter dropdown, states
- `docs/ui-specification/screens/task-detail-panel.md` - Labels field + picker

---

## Backend

### T-005: Implement label and task-label repositories

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` (list with task counts, create, rename/recolor, delete) and `src/db/task-label.ts` (replace a task's label set, load labels for a set of task ids) as the only modules issuing label SQL, per the one-repository-per-entity convention. Enforce data rules at this layer: case-insensitive duplicate detection, same-project assignment check, and the 10-label cap.

**Rationale:**
CLAUDE.md requires all SQL to live in `src/db/` repository modules; routers never touch `pg` directly.

**Acceptance Criteria:**
- [ ] `listByProject` returns labels with per-label assigned-task counts (`taskCount`) in a single query
- [ ] `create`/`update` surface the unique-index violation distinctly so the router can map it to `conflict`
- [ ] `replaceForTask` swaps the full assignment set in one transaction and rejects sets with more than 10 labels or labels belonging to a different project
- [ ] `listForTasks(taskIds)` returns labels grouped by task id so the board response embeds labels without per-card queries

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- `src/db/label.ts` (new) - Label repository (CRUD + counts)
- `src/db/task-label.ts` (new) - TaskLabel repository (replace set, batch load)

### T-006: Implement labels router with the five label endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET/POST project labels, PUT/DELETE label, and PUT task label set, and mount it in `src/api/index.ts`. Validate every body and query parameter with Zod schemas beside the handlers; throw `ApiError` with catalog codes; return envelope responses only.

**Rationale:**
Covers the five new endpoints in FEAT-001 Section 7 and the validation/conflict behavior behind AC-1, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] POST validates `name` (1–30 chars after trim) and `color` (one of the 12 accent tokens); duplicate name — including case-only variants — returns 409 `conflict` (AC-6)
- [ ] GET list returns `{ data: LabelDto[], meta }` with `taskCount` per label, paginated per API index Section 2.4
- [ ] PUT `/api/v1/labels/{id}` renames/recolors with the same validation and conflict mapping; concurrent renames are last-write-wins
- [ ] DELETE `/api/v1/labels/{id}` removes the label and its assignments only (tasks untouched); unknown ids return 404 `not-found`
- [ ] PUT `/api/v1/tasks/{id}/labels` replaces the set; more than 10 labels or a label from another project returns 400 `validation-error`

**Dependencies:** T-003, T-005
**Complexity:** L

**Files to Modify/Create:**
- `src/api/labels.ts` (new) - router + Zod schemas for the five endpoints
- `src/api/index.ts` - mount the labels router

### T-007: Add labelId filter and embedded labels to the board tasks endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Extend GET `/api/v1/projects/{projectId}/tasks` with an optional Zod-validated `labelId` UUID query parameter applied in SQL, and embed each task's labels in the response via one aggregated join. Filtering stays server-side so results and `meta.totalCount` remain correct under pagination, per the Feature Brief constraints.

**Rationale:**
AC-3 requires label filtering, and Section 10 mandates that labels ride the existing board response (no per-card fetches) and that filtering is a server-side query parameter.

**Acceptance Criteria:**
- [ ] `labelId` narrows the list to tasks carrying that label and `meta.totalCount` reflects the filtered total
- [ ] Every returned `TaskDto` includes its `labels` array in the same response — one aggregated query, no N+1
- [ ] Non-UUID `labelId` returns 400 `validation-error`; a valid-but-nonexistent label id returns an empty list, not an error
- [ ] Unfiltered response is unchanged except for the added `labels` field (existing tests in `tests/api/tasks.test.ts` still pass)

**Dependencies:** T-003, T-005
**Complexity:** M

**Files to Modify/Create:**
- `src/db/task.ts` - board query gains label join/aggregation + optional `labelId` predicate
- `src/api/tasks.ts` - Zod query schema gains optional `labelId`

---

## Frontend

### T-008: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create the reusable chip that renders a label's name on its accent-token background with a per-token text color meeting WCAG 2.1 AA (4.5:1), caption typography, and `space-1` padding. Include the small variant used on board cards and the "+N" overflow presentation.

**Rationale:**
FEAT-001 Section 8 defines LabelChip as a shared component reused by board cards, the detail panel picker, and the management dialog; a single implementation keeps contrast handling in one place.

**Acceptance Criteria:**
- [ ] Renders name and palette color via design-token CSS custom properties — no hard-coded hex values
- [ ] Chip text passes 4.5:1 contrast on all 12 accent tokens (per-token text color map)
- [ ] Long names (up to 30 chars) truncate with ellipsis and expose the full name via `title`

**Dependencies:** T-004
**Complexity:** S

**Files to Modify/Create:**
- `src/ui/components/label-chip.tsx` (new) - shared chip component + token/contrast map

### T-009: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
The new Label Management Dialog screen needs an HTML mockup for stakeholder approval before implementation — generate it per `.ai-framework/prompts/mockup-generation.md`. Then implement the dialog (opened from the board toolbar) covering create, rename, recolor, and delete, composing the shared `Dialog` and `LabelChip` components with a 12-token palette picker.

**Rationale:**
FEAT-001 Section 8 marks the Label Management Dialog as a new screen and requires `mockup-first` classification; it carries AC-1, AC-5, and AC-6 user flows.

**Acceptance Criteria:**
- [ ] Mockup of the dialog is generated and approved before implementation starts
- [ ] Creating a label makes it appear in the project's label list immediately (AC-1); a duplicate name shows the server's `conflict` message inline at the name field (AC-6)
- [ ] Delete opens a destructive-variant `Dialog` confirmation stating the affected task count from `taskCount` before anything is removed (AC-5)
- [ ] Create/rename/recolor/delete invalidate the label and board task queries so every visible chip updates without a page reload (AC-4)
- [ ] Loading, empty (uses `EmptyState`), and error states follow UI index Section 2.5

**Dependencies:** T-004, T-006, T-008
**Complexity:** L

**Files to Modify/Create:**
- `src/ui/label-management-dialog.tsx` (new) - dialog screen (list, palette picker, confirmations)
- `src/ui/project-board.tsx` - toolbar "Labels" button opening the dialog

### T-010: Add Labels field to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" multi-select picker with chip previews to the task detail panel, backed by the project labels list and PUT `/api/v1/tasks/{id}/labels`. Successful changes invalidate the board tasks query so the card's chips update without a page reload.

**Rationale:**
AC-2 requires assigning and removing labels from the detail panel with changes reflected on the board card immediately.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists via the replace-set endpoint and survives closing and reopening the panel (AC-2)
- [ ] The board card's chips reflect changes without a page reload, via TanStack Query invalidation (AC-2)
- [ ] The picker disables further selection at 10 labels with an explanatory tooltip; a server 400 surfaces as an inline error
- [ ] Picker loading and error states follow UI index Section 2.5

**Dependencies:** T-006, T-007, T-008
**Complexity:** M

**Files to Modify/Create:**
- `src/ui/task-detail-panel.tsx` - Labels field, multi-select picker, mutation + invalidation

### T-011: Render label chips on board task cards

**Type:** Frontend
**Workflow:** standard

**Description:**
Extend `TaskCard` to render up to 3 `LabelChip`s from the task's embedded `labels` array with a "+N" overflow indicator when more are assigned. The compact variant stays title-only per `components.md`.

**Rationale:**
FEAT-001 Section 8 requires chips on board cards so labels are visible at a glance (AC-2/AC-4 display path).

**Acceptance Criteria:**
- [ ] Cards show up to 3 chips plus a "+N" indicator when the task carries more than 3 labels
- [ ] Chips render from the labels embedded in the board response — no per-card fetches (Section 10 constraint)
- [ ] Compact variant remains a single title line without chips

**Dependencies:** T-007, T-008
**Complexity:** S

**Files to Modify/Create:**
- `src/ui/components/task-card.tsx` - render `LabelChip` row + overflow indicator

### T-012: Add label filter to the board toolbar

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a single-select label filter dropdown to `BoardToolbar` that sets the `labelId` parameter on the board tasks query (server-side filtering) with a clear-filter action. Handle the zero-match and label-deleted-while-filtered edge cases.

**Rationale:**
AC-3 requires filtering the board to one label and restoring the full board when cleared; Section 4.2 excludes multi-label AND/OR combinations.

**Acceptance Criteria:**
- [ ] Selecting a label shows only tasks carrying it; clearing the filter restores the full board (AC-3)
- [ ] Zero matching tasks renders `EmptyState` with a "Clear filter" CTA — never a blank board
- [ ] If the filtered label no longer exists after a refetch, the filter clears automatically and a notice is shown
- [ ] Filtering round-trips through the `labelId` query parameter (no client-side filtering), keeping pagination correct and meeting the ≤300ms P95 NFR for boards up to 500 tasks

**Dependencies:** T-006, T-007
**Complexity:** M

**Files to Modify/Create:**
- `src/ui/project-board.tsx` - toolbar filter dropdown, query param wiring, empty/notice states

---

## Testing

### T-013: Write API integration tests for labels and board filtering

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest coverage for the five label endpoints and extend the board tasks tests for `labelId` filtering, following the envelope and error-shape assertions patterned in `tests/api/tasks.test.ts`.

**Rationale:**
CLAUDE.md requires a Supertest integration test per router; these tests verify AC-1, AC-3, AC-5, and AC-6 at the API boundary plus the Section 9 edge cases.

**Acceptance Criteria:**
- [ ] Happy paths: create → list (includes `taskCount`) → rename/recolor → delete, with delete removing assignments but leaving tasks intact
- [ ] Duplicate names — including case-only variants ("Urgent" vs "urgent") — return 409 `conflict`; invalid name/color returns 400 `validation-error`
- [ ] Replace-set: an 11th label and a cross-project label each return 400 `validation-error`; concurrent renames resolve last-write-wins
- [ ] Board list with `labelId` returns only matching tasks with correct `meta.totalCount` under pagination; a nonexistent label id yields an empty list

**Dependencies:** T-006, T-007
**Complexity:** L

**Files to Modify/Create:**
- `tests/api/labels.test.ts` (new) - integration tests for the labels router
- `tests/api/tasks.test.ts` - `labelId` filter + embedded `labels` assertions

### T-014: Write repository unit tests for label modules

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest unit tests against the test database for `src/db/label.ts` and `src/db/task-label.ts`, per the convention that every repository module gets a unit test.

**Rationale:**
The repositories carry the feature's data rules (uniqueness, cap, same-project, cascades); unit tests pin them independently of the routers.

**Acceptance Criteria:**
- [ ] Case-insensitive duplicate inserts surface the unique-index violation distinctly for `conflict` mapping
- [ ] `replaceForTask` is transactional — a rejected set (11 labels or cross-project) leaves prior assignments unchanged
- [ ] Deleting a label or a task removes only `task_labels` rows (cascade behavior)
- [ ] `listForTasks` groups labels correctly for a mixed set of task ids, and `listByProject` reports accurate `taskCount`s

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- `tests/db/label.test.ts` (new) - Label repository unit tests
- `tests/db/task-label.test.ts` (new) - TaskLabel repository unit tests

### T-015: Write UI component tests for label features

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests covering the LabelChip, the Label Management Dialog flows, the detail panel's label picker, and the board's chips and filter behavior.

**Rationale:**
Verifies the UI halves of AC-2, AC-3, AC-4, and AC-6, including the picker cap and filtered-empty-state edge cases from Section 9.

**Acceptance Criteria:**
- [ ] LabelChip renders name and token color and truncates long names
- [ ] Dialog: duplicate-name 409 shows the inline error; delete confirmation displays the affected task count before confirming
- [ ] Picker disables at 10 labels with a tooltip; assignment changes propagate to the board card without reload (query invalidation)
- [ ] Board filter: selecting filters cards, clearing restores the board, and zero matches shows `EmptyState` with "Clear filter"

**Dependencies:** T-009, T-010, T-011, T-012
**Complexity:** L

**Files to Modify/Create:**
- `tests/ui/label-chip.test.tsx` (new) - chip rendering + contrast token map
- `tests/ui/label-management-dialog.test.tsx` (new) - dialog CRUD flows
- `tests/ui/task-detail-panel.test.tsx` (new) - picker behavior + invalidation
- `tests/ui/project-board.test.tsx` (new) - chips on cards + filter behavior

---

## Summary

**Feature Brief:** FEAT-001 — Task Labels (traceability reference for all tasks above).

**Total task count by type (15 tasks):**

| Type | Count | Tasks |
|------|-------|-------|
| Documentation | 3 | T-001, T-003, T-004 |
| Database | 1 | T-002 |
| Backend | 3 | T-005, T-006, T-007 |
| Frontend | 5 | T-008, T-009, T-010, T-011, T-012 |
| Testing | 3 | T-013, T-014, T-015 |

**Complexity distribution:** S ×3 (T-001, T-008, T-011) · M ×8 (T-002, T-003, T-004, T-005, T-007, T-010, T-012, T-014) · L ×4 (T-006, T-009, T-013, T-015) · XL ×0.

**Critical path (6 tasks):** T-001 → T-002 → T-005 → T-006 → T-009 → T-015. The documentation chain T-001 → T-003 → T-004 → T-008 → T-009 → T-015 is equally long, so spec authoring (T-003/T-004) should start in parallel with the migration and repositories.

**Edge-case coverage (Feature Brief Section 9):** delete-with-assignments confirmation → T-005/T-006/T-009 (tested in T-013/T-015); zero-match filter empty state → T-012/T-015; 11th label rejection → T-006/T-010 (tested in T-013/T-014/T-015); concurrent rename last-write-wins → T-006/T-013; case-only duplicate → T-002/T-006/T-013/T-014; label deleted while filter active → T-007/T-012.

**Risks / open questions:**

- The delete confirmation needs the affected task count before deletion; this is served by `taskCount` on the label list DTO (T-003/T-005) rather than a new endpoint — if product later wants a live recount at confirm time, that would require a scope discussion.
- Edit-rights enforcement for create/rename/delete relies on the same auth-service role resolution the existing PATCH task endpoint uses; if that mechanism turns out to be coarser than "member with edit rights", the labels router inherits the gap.
- The per-token AA text-color map for chips (T-008) needs a one-time design decision (light vs. dark text per accent token); the UI spec update in T-004 should record the chosen mapping.
- `task_labels` carries `created_at`/`updated_at` to follow the index Section 3 convention even though join rows are immutable; flagged in T-001 in case the team prefers `created_at` only.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label with name (1–30 chars) + palette color; appears in the project's label list immediately | T-006, T-009, T-013 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and show on the board card without reload | T-006, T-007, T-010, T-015 |
| AC-3: Board filter shows only tasks with the selected label; clearing restores the full board | T-007, T-012, T-013, T-015 |
| AC-4: Renaming or recoloring a label updates every task card displaying it | T-006, T-009, T-011, T-015 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-005, T-006, T-009, T-013 |
| AC-6: Duplicate label name in the same project returns a validation error with an inline UI message | T-006, T-009, T-013 |
