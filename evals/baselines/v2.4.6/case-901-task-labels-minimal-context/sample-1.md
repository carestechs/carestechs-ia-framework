# FEAT-001: Task Labels — Implementation Task List

> Generated from `docs/work-items/FEAT-001-task-labels.md` and `CLAUDE.md` per `prompts/feature-tasks.md`, using the canonical task schema from `prompts/base-template.md`. This project has no spec documentation yet — T-001, T-003, and T-007 create the spec shards named by the Feature Brief's impact tables before the code that relies on them.

---

## Foundation

### T-001: Author data model spec shards for Label and TaskLabel

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for the two new entities, Label and TaskLabel, and bootstrap `docs/data-model/index.md` with their Module Ownership and Relationships Overview entries. Capture every business rule from Feature Brief Section 6 so downstream tasks implement against a single authority.

**Rationale:**
FEAT-001 Section 6 requires the new-entity shards to exist before feature logic; this project has no data model documentation yet, so the index must be created alongside them.

**Acceptance Criteria:**
- [ ] `label.md` documents fields (project-scoped, name 1–30 chars, palette color token) and rules: case-insensitive name uniqueness per project, color limited to the 12 accent palette tokens, delete cascades to assignments only — never to tasks
- [ ] `task-label.md` documents the N:M join with its rules: max 10 labels per task, task and label must belong to the same project
- [ ] `docs/data-model/index.md` carries Module Ownership and Relationships Overview entries for both new entities alongside Task and Project

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- docs/data-model/index.md (new) - data model index: conventions, Module Ownership, Relationships Overview
- docs/data-model/entities/label.md (new) - Label entity shard
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity shard

### T-002: Create migration for labels and task_labels tables

**Type:** Database
**Workflow:** standard

**Description:**
Add a plain SQL migration creating the `labels` table (project-scoped, name, color token) and the `task_labels` join table, matching the T-001 entity shards. Include the uniqueness constraint and the indexes the board filter needs.

**Rationale:**
AC-1 and AC-6 need database-level name uniqueness; the sub-300ms filter NFR (Section 10) needs join-table indexes.

**Acceptance Criteria:**
- [ ] `labels` table has a project FK (ON DELETE CASCADE), `name` with a 1–30 length CHECK, and a `color` token column (snake_case naming per CLAUDE.md)
- [ ] Case-insensitive unique index on `(project_id, lower(name))` rejects "Urgent" vs "urgent" duplicates
- [ ] `task_labels` uses a composite primary key `(task_id, label_id)` with ON DELETE CASCADE FKs from both `tasks` and `labels`
- [ ] Index on `task_labels (label_id, task_id)` supports server-side board filtering at 500-task scale

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-task-labels.sql (new) - create labels and task_labels with constraints and indexes

---

## Backend

### T-003: Author API spec shard for label endpoints and error catalog

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` documenting the five label endpoints, `docs/api-spec/endpoints/tasks.md` documenting the board list's new `labelId` parameter and embedded labels array, and bootstrap `docs/api-spec/index.md` with the Endpoint Summary and Error Catalog. CLAUDE.md forbids using an error code without a catalog row, so the catalog must exist before the routers.

**Rationale:**
FEAT-001 Section 7 requires the labels endpoint shard plus Endpoint Summary rows; no API spec exists in this project yet.

**Acceptance Criteria:**
- [ ] All five label endpoints documented with request/response bodies using the `{ "data": ... }` envelope and list `meta` per CLAUDE.md
- [ ] `tasks.md` documents the optional `labelId` query parameter and the per-task `labels` array in the board list response
- [ ] Error Catalog rows exist for `validation-error`, `conflict` (duplicate label name, 409), and `not-found`
- [ ] Endpoint Summary in `docs/api-spec/index.md` lists every new and modified endpoint from Section 7

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/index.md (new) - API conventions, Endpoint Summary, Error Catalog
- docs/api-spec/endpoints/labels.md (new) - five label endpoints
- docs/api-spec/endpoints/tasks.md (new) - board list endpoint incl. labelId filter and labels array

### T-004: Implement label and task-label repository modules

**Type:** Backend
**Workflow:** standard

**Description:**
Add `src/db/label.ts` (label CRUD plus per-label assigned-task counts) and `src/db/task-label.ts` (replace a task's label set, fetch labels for a set of tasks), following the one-repository-per-entity convention. All label SQL lives in these modules only.

**Rationale:**
CLAUDE.md restricts SQL to `src/db/` repositories; these queries underpin every Section 7 endpoint and the AC-5 confirmation count.

**Acceptance Criteria:**
- [ ] `label.ts` exposes list (including per-label assigned-task counts for the delete confirmation), create, update, and delete
- [ ] Create and rename surface case-insensitive duplicate-name violations distinctly so the router can map them to 409 `conflict`
- [ ] `task-label.ts` replaces a task's label set atomically, enforcing max 10 labels and same-project membership
- [ ] Deleting a label removes assignment rows only; tasks are never touched

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label repository: CRUD + task counts
- src/db/task-label.ts (new) - task-label repository: replace set, fetch per task

### T-005: Implement label CRUD router

**Type:** Backend
**Workflow:** standard

**Description:**
Add `src/api/labels.ts` with GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}`, validated by Zod schemas beside the handlers, and mount it in `src/api/index.ts`. Duplicate names return 409 with catalog code `conflict`; rename/recolor is last-write-wins per Section 9.

**Rationale:**
Implements the Section 7 label endpoints backing AC-1, AC-4, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] POST validates name (1–30 chars) and palette color token via Zod; failures map to `validation-error`
- [ ] Duplicate name within a project — including case-only variants — returns 409 `{ "error": { "code": "conflict" } }` (AC-6)
- [ ] GET returns the project's labels with task counts in the `{ data, meta }` list envelope (AC-1, AC-5)
- [ ] PUT renames/recolors last-write-wins; DELETE removes the label and all its assignments (AC-4, AC-5)
- [ ] Create/rename/recolor/delete enforce project edit rights; the label list is readable by all project members (Section 6)

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - label router with Zod schemas
- src/api/index.ts - mount the labels router

**Technical Notes:** (optional)
- Throw `ApiError` and let `src/api/errors.ts` middleware serialize; never invent codes outside the T-003 catalog
- Reuse the existing project-membership/edit-rights check used by other routers

### T-006: Add task label assignment endpoint and board label support

**Type:** Backend
**Workflow:** standard

**Description:**
Extend `src/api/tasks.ts` with PUT `/api/v1/tasks/{id}/labels` (replace the label-ID set) and an optional `labelId` query parameter on the project board list, and extend `src/db/task.ts` so the board query returns each task's labels in the same response. Labels ride along with the existing board payload — never fetched per card.

**Rationale:**
Backs AC-2 and AC-3; Section 10 requires server-side filtering for pagination correctness and forbids slowing initial board load.

**Acceptance Criteria:**
- [ ] PUT replaces the task's label set; attempting an 11th label returns `validation-error` (Section 9 edge case)
- [ ] Assigning a label from a different project is rejected with a catalogued error code
- [ ] Board GET with `labelId` returns only tasks carrying that label with correct `meta` pagination counts; omitting it returns the full board (AC-3)
- [ ] Every board task row includes its `labels` array from a single query — no per-card fetches (Section 10)

**Dependencies:** T-003, T-004
**Complexity:** L

**Files to Modify/Create:**
- src/api/tasks.ts - add PUT labels route and labelId query parameter with Zod validation
- src/db/task.ts - board query aggregates labels per task and applies optional label filter

---

## Frontend

### T-007: Author UI spec shards and accent palette definition

**Type:** Documentation
**Workflow:** standard

**Description:**
Bootstrap `docs/ui-specification/index.md` (Design System with the 12-color accent palette as Section 2.1, plus the Screen Inventory), create the Label Management Dialog screen shard, and create `docs/ui-specification/components.md` documenting LabelChip. Palette tokens must guarantee readable chip text.

**Rationale:**
FEAT-001 Section 8 requires the new-screen shard, its Screen Inventory row, and the LabelChip entry; Section 10 pins the color picker to index Section 2.1 palette tokens, which do not exist yet in this project.

**Acceptance Criteria:**
- [ ] `index.md` Section 2.1 defines 12 accent palette tokens, each paired with a chip text color meeting WCAG 2.1 AA contrast (4.5:1)
- [ ] Screen Inventory row added for the Label Management Dialog
- [ ] `label-management-dialog.md` specifies create/rename/recolor/delete flows, the inline duplicate-name error, and the delete confirmation stating the affected task count
- [ ] `components.md` documents LabelChip (name + color rendering, variants, used by board cards, detail panel, and picker)

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/index.md (new) - Design System incl. Section 2.1 accent palette + Screen Inventory
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen spec
- docs/ui-specification/components.md (new) - shared component inventory incl. LabelChip

### T-008: Implement LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create the reusable LabelChip component rendering a label's name on its palette color, per the T-007 component spec. It serves board cards, the task detail panel, and the label picker.

**Rationale:**
Section 8 names LabelChip as a new shared component; a single implementation keeps chips visually consistent everywhere a label appears (AC-4).

**Acceptance Criteria:**
- [ ] Renders the label name on its palette color token exactly as specified in `docs/ui-specification/components.md`
- [ ] Chip text meets 4.5:1 contrast on all 12 palette tokens (Section 10 NFR)
- [ ] Provides a compact variant for board cards and a removable variant for the picker

**Dependencies:** T-007
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared LabelChip component

### T-009: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
The Label Management Dialog is a new user-facing screen — generate an HTML mockup for stakeholder approval per `.ai-framework/prompts/mockup-generation.md` before implementing. Then build the dialog (create, rename, recolor, delete labels) on the shared dialog component, wired to the T-005 endpoints with TanStack Query.

**Rationale:**
Section 8 requires the new Label Management Dialog and classifies its tasks mockup-first; it is the UI surface for AC-1, AC-4, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] Mockup of the dialog approved before implementation begins
- [ ] Creating a label (name input + palette picker built from Section 2.1 tokens, no new dependencies) shows it in the project's label list immediately (AC-1)
- [ ] A duplicate-name 409 renders an inline validation message next to the name input (AC-6)
- [ ] Rename/recolor invalidates label and board queries so every displayed chip updates (AC-4)
- [ ] Delete first shows a confirmation dialog stating how many tasks are affected, then removes the label (AC-5)

**Dependencies:** T-005, T-007, T-008
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - label management screen using the shared dialog component

**Technical Notes:** (optional)
- Use the existing `src/ui/components/dialog.tsx` shell; no new external dependencies for the color picker (Section 10)
- Source the affected-task count for the delete confirmation from the label list's task counts (T-005)

### T-010: Add Labels field with multi-select picker to task detail panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to the task detail panel with a multi-select picker showing LabelChip previews, saving through PUT `/api/v1/tasks/{id}/labels`. Invalidate the board query on mutation so the card updates without a page reload.

**Rationale:**
AC-2 requires assigning and removing labels from the detail panel with changes visible on the board immediately.

**Acceptance Criteria:**
- [ ] Assigning or removing labels persists and the board card reflects the change without a page reload (AC-2)
- [ ] The picker lists the project's labels as chip previews using LabelChip
- [ ] Selection disables at 10 labels with an explanatory tooltip (Section 9 edge case)

**Dependencies:** T-006, T-008
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - add Labels field, multi-select picker, and label mutation

### T-011: Add label chips and single-label filter to project board

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 label chips with a "+N" overflow indicator on task cards, add a toolbar label-filter dropdown that drives the server-side `labelId` parameter, and add the toolbar entry that opens the Label Management Dialog. Chip and filter data come from the labels already embedded in the board response.

**Rationale:**
Implements the Section 8 Project Board changes and AC-3; Section 10 requires filtering to stay server-side so results remain correct with pagination.

**Acceptance Criteria:**
- [ ] Task cards show up to 3 chips plus a "+N" overflow indicator when a task has more labels
- [ ] Selecting a label refetches the board with `labelId` and shows only matching tasks; clearing the filter restores the full board (AC-3)
- [ ] A filter with zero matching tasks shows the standard empty state with a "Clear filter" action, not a blank board (Section 9)
- [ ] If the filtered label was deleted by another user, the board refetch clears the filter and shows a notice (Section 9)
- [ ] A toolbar button opens the Label Management Dialog (T-009)

**Dependencies:** T-006, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/project-board.tsx - filter dropdown, filter state in the query key, dialog entry point
- src/ui/components/task-card.tsx - render LabelChips with 3-chip overflow

**Technical Notes:** (optional)
- Reuse `src/ui/components/empty-state.tsx` for the zero-match state
- Keep `labelId` in the TanStack Query key so filtering always refetches server-side

---

## Testing

### T-012: Write repository unit tests for label and task-label modules

**Type:** Testing
**Workflow:** standard

**Description:**
Add unit tests against the test database for both new repository modules, mirroring `src/db/` under `tests/db/` per the CLAUDE.md test-location convention.

**Rationale:**
Every repository gets a unit test per CLAUDE.md; the Section 6 business rules and Section 9 edge cases need database-level verification.

**Acceptance Criteria:**
- [ ] Case-insensitive duplicate names ("Urgent" vs "urgent") are rejected (Section 9)
- [ ] Replacing a task's label set enforces the 10-label maximum and same-project membership
- [ ] Deleting a label removes its assignments while the tasks remain intact
- [ ] The label list query returns correct per-label assigned-task counts

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - task-label repository unit tests

### T-013: Write API integration tests for label endpoints and board filter

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration coverage for the new label router and extend the existing task route tests with the label assignment endpoint and `labelId` board filter.

**Rationale:**
Every router gets a Supertest integration test per CLAUDE.md; these tests verify the API side of all six acceptance criteria.

**Acceptance Criteria:**
- [ ] Label CRUD happy path passes with `{ "data" }` envelopes; duplicate names — including case-only variants — return 409 `conflict` (AC-1, AC-6)
- [ ] PUT task labels persists the replacement set; an 11th label returns `validation-error` (AC-2)
- [ ] Board GET with `labelId` returns only matching tasks with correct pagination `meta`; without it, the full board (AC-3)
- [ ] A rename is visible in the next board response (AC-4)
- [ ] DELETE removes the label's assignments from all tasks while tasks survive (AC-5)

**Dependencies:** T-005, T-006
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - label router integration tests
- tests/api/tasks.test.ts - add PUT labels and labelId filter cases

### T-014: Write UI tests for chips, picker, dialog, and board filter

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for the new and modified UI surfaces, mirroring `src/ui/` under `tests/ui/`.

**Rationale:**
Verifies the frontend behavior behind AC-1, AC-2, AC-3, AC-5, and AC-6, including the Section 9 edge cases that only manifest in the UI.

**Acceptance Criteria:**
- [ ] LabelChip renders name and color token correctly in compact and removable variants
- [ ] Dialog flows pass: created label appears in the list, duplicate name shows the inline error, delete shows the affected-task-count confirmation (AC-1, AC-5, AC-6)
- [ ] Picker disables further selection at 10 labels with the explanatory tooltip; assign/remove updates the board card without reload (AC-2)
- [ ] Board shows 3-chip overflow, filters and clears by label, renders the empty state with "Clear filter", and shows the deleted-label notice (AC-3)

**Dependencies:** T-009, T-010, T-011
**Complexity:** L

**Files to Modify/Create:**
- tests/ui/label-chip.test.tsx (new) - LabelChip component tests
- tests/ui/label-management-dialog.test.tsx (new) - dialog flow tests
- tests/ui/task-detail-panel.test.tsx (new) - picker behavior tests
- tests/ui/project-board.test.tsx (new) - chips, filter, empty-state, deleted-label notice tests

---

## Summary

**Feature Brief:** FEAT-001 — Task Labels (`docs/work-items/FEAT-001-task-labels.md`)

**Task count by type:** Backend 3 · Frontend 4 · Database 1 · Documentation 3 · Testing 3 — **14 tasks total**

**Complexity distribution:** S × 1 (T-008) · M × 8 (T-001–T-005, T-007, T-010, T-012) · L × 5 (T-006, T-009, T-011, T-013, T-014) · XL × 0

**Critical path (longest dependency chain, 7 tasks):** T-001 → T-002 → T-004 → T-005 → T-009 → T-011 → T-014 (data model shards → migration → repositories → label API → dialog with mockup gate → board integration → UI tests)

**Risks / open questions:**

- This project has no spec documentation; T-001, T-003, and T-007 bootstrap all three spec trees, so the conventions they establish will set precedent for every future feature.
- "Edit rights" enforcement (Section 6) assumes an existing project-membership check in the API layer — confirm one exists before starting T-005.
- The 12 accent palette tokens are not defined anywhere yet; T-007 must choose tokens that pass 4.5:1 chip-text contrast, which constrains the palette choice.
- The sub-300ms P95 filter NFR at 500 tasks depends on the T-002 indexes; verify against a seeded board while writing T-013.
- Concurrent renames are last-write-wins per the brief — no optimistic locking; stale clients reconcile on the next board refetch.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label with name (1–30 chars) and palette color; it appears in the project's label list immediately | T-002, T-005, T-009, T-013, T-014 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and appear on the board card without a page reload | T-006, T-010, T-013, T-014 |
| AC-3: Selecting a label in the board filter shows only tasks carrying it; clearing restores the full board | T-006, T-011, T-013, T-014 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-005, T-009, T-011, T-013 |
| AC-5: Deleting a label removes it from all tasks after a confirmation dialog stating how many tasks are affected | T-004, T-005, T-009, T-013, T-014 |
| AC-6: Creating a duplicate label name within the same project returns a validation error and the UI shows an inline message | T-002, T-005, T-009, T-013, T-014 |
