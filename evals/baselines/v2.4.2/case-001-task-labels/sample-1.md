# FEAT-001 — Task Labels: Implementation Tasks

> Generated from `docs/work-items/FEAT-001-task-labels.md` (Feature Brief **FEAT-001**) for TaskFlow, following the carestechs IA framework feature-tasks prompt and the canonical task schema in `base-template.md`.

---

## Foundation

### T-001: Author data-model shards for Label and TaskLabel

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for the new Label and TaskLabel entities following the data-model conventions (UUID PKs, `timestamptz` timestamps, snake_case tables). Register both entities in the index's Module Ownership table and add the new N:M relationship to the Relationships Overview.

**Rationale:**
FEAT-001 Section 6 requires the new entity shards to exist before feature logic, and the data-model index doubles as the shard directory.

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` defines fields (`id`, `project_id`, `name` varchar(30), `color` accent-palette token, `created_at`, `updated_at`), case-insensitive per-project name uniqueness, and the rule that deleting a label cascades to assignments only, never to tasks
- [ ] `docs/data-model/entities/task-label.md` defines the join (`task_id`, `label_id`), the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities, a Section 4.2 N:M entry (Task ↔ Label via `task_labels`), and a Changelog row

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard (fields, rules, relationships)
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity shard
- docs/data-model/index.md - Module Ownership rows, Section 4.2 N:M entry, Changelog row

**Technical Notes:**
- `color` stores one of the 12 accent-palette tokens (`accent-01`…`accent-12`) from `docs/ui-specification/index.md` Section 2.1, not a hex value
- Keep each shard's Relationships table in sync with the index's Relationships Overview (framework rule)

---

### T-002: Author API spec shard for label endpoints

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` documenting the five label endpoints from FEAT-001 Section 7 (list/create project labels, rename/recolor, delete, replace a task's label set) and update the tasks shard with the board list's new `labelId` filter and the `labels` array on TaskDto. Add one Endpoint Summary row per new endpoint to the index.

**Rationale:**
FEAT-001 Section 7 requires the new endpoint shard and summary rows before API implementation; the Section 10 constraint embeds labels in the existing board response rather than per-card fetches.

**Acceptance Criteria:**
- [ ] `labels.md` documents all five endpoints with the response envelope, LabelDto, and Error Catalog codes only (`validation-error`, `conflict` 409 for duplicate names, `not-found`) — no new catalog codes
- [ ] LabelDto includes an `assignedTaskCount` field so the delete confirmation can state how many tasks are affected
- [ ] `endpoints/tasks.md` documents the optional `labelId` query parameter on the board list and the `labels` array on TaskDto
- [ ] `api-spec/index.md` gains an Endpoint Summary row per new endpoint and a Changelog row

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - all five label endpoints + LabelDto
- docs/api-spec/endpoints/tasks.md - `labelId` query parameter, `labels` on TaskDto
- docs/api-spec/index.md - Endpoint Summary rows, Changelog row

**Technical Notes:**
- GET labels list follows index Section 2.4 pagination and returns `meta` totals like every list endpoint
- PUT `/api/v1/tasks/{id}/labels` responds with the updated label set so the client needs no follow-up fetch

---

### T-003: Author UI spec updates for labels

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the Label Management Dialog screen shard, add its Screen Inventory row to the UI index, document the LabelChip shared component in `components.md`, and update the Project Board and Task Detail Panel shards with label chips, the filter dropdown, and the Labels picker field.

**Rationale:**
FEAT-001 Section 8 requires the new screen shard and component inventory entry before frontend work so mockups and implementation follow an agreed spec.

**Acceptance Criteria:**
- [ ] `screens/label-management-dialog.md` covers layout sketch, component hierarchy, component→API mapping, all four states (default/loading/empty/error per index Section 2.5), and interactions including the delete confirmation stating the affected task count
- [ ] `components.md` documents LabelChip inputs/outputs and variants (board-card chip, picker preview, compact)
- [ ] `screens/project-board.md` gains the chip display (max 3 + "+N" overflow) and toolbar filter dropdown; `screens/task-detail-panel.md` gains the Labels field and multi-select picker interactions
- [ ] `ui-specification/index.md` gains the Screen Inventory row and a Changelog row

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/components.md - LabelChip entry
- docs/ui-specification/screens/project-board.md - chips + filter dropdown
- docs/ui-specification/screens/task-detail-panel.md - Labels field + picker
- docs/ui-specification/index.md - Screen Inventory row, Changelog row

**Technical Notes:**
- Shard filename follows the kebab-case naming rule: screen "Label Management Dialog" → `screens/label-management-dialog.md`
- Reference the existing shared `Dialog` and `EmptyState` components rather than introducing new modal or empty-state patterns

---

### T-004: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add a migration creating the `labels` table (project-scoped, name, accent-token color, timestamps) and the `task_labels` join table with cascading foreign keys. Enforce case-insensitive per-project name uniqueness with a unique index on `(project_id, lower(name))`.

**Rationale:**
The Section 6 entities need schema before the repositories; database-level uniqueness backs AC-6 and the "Urgent" vs "urgent" edge case.

**Acceptance Criteria:**
- [ ] `labels` has UUID `id` PK, `project_id` FK → `projects` ON DELETE CASCADE, `name` VARCHAR(30) NOT NULL, `color` NOT NULL constrained to the 12 accent tokens, and `created_at`/`updated_at` timestamptz
- [ ] Unique index on `(project_id, lower(name))` rejects case-insensitive duplicate names
- [ ] `task_labels` has PK `(task_id, label_id)` with FKs ON DELETE CASCADE from both `tasks` and `labels`, plus timestamps per convention
- [ ] Migration applies cleanly on a database at `001-init.sql`

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- migrations/002-add-labels.sql (new) - `labels` + `task_labels` DDL, indexes

**Technical Notes:**
- Add an index on `task_labels(label_id)` — the board label filter joins on it (supports the <300ms P95 NFR)
- Follow data-model index Section 3 conventions: snake_case plural tables, explicit varchar limits

---

### T-005: Implement Label and TaskLabel repositories

**Type:** Backend
**Workflow:** standard

**Description:**
Add repository modules for labels (list by project with assigned-task counts, create, rename/recolor, delete) and for task-label assignments (replace a task's label set transactionally). Surface unique-constraint violations as a distinct error so the router can map them to the `conflict` catalog code.

**Rationale:**
CLAUDE.md convention 5 — SQL lives only in `src/db/` repository modules, one module per entity.

**Acceptance Criteria:**
- [ ] `src/db/label.ts` exposes list-by-project (each label with its assigned-task count), create, update, and delete; duplicate-name violations raise a typed/detectable error
- [ ] `src/db/task-label.ts` exposes a replace-for-task operation that enforces all labels belong to the task's project and at most 10 labels, in one transaction
- [ ] All queries are parameterized and results are mapped to camelCase objects — no raw rows escape the repository

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label CRUD + list with assigned-task counts
- src/db/task-label.ts (new) - transactional label-set replacement for a task

**Technical Notes:**
- Assigned-task counts: `LEFT JOIN task_labels … GROUP BY labels.id` in the list query — one query, no N+1
- Replace-for-task: delete + insert inside a transaction; validate label ownership with a single `WHERE project_id = $1` count check

---

## Backend

### T-006: Implement labels router (CRUD endpoints)

**Type:** Backend
**Workflow:** standard

**Description:**
Add the labels router implementing GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}` with Zod validation, envelope responses, and Error Catalog codes, and mount it in `src/api/index.ts`.

**Rationale:**
Implements the four label-resource endpoints from FEAT-001 Section 7; backs AC-1, AC-4, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] POST validates `name` (1–30 chars after trimming) and `color` (one of the 12 accent tokens); a duplicate name in the project — case-insensitive — returns 409 `conflict`
- [ ] GET returns `{ data, meta }` with each label's `assignedTaskCount`, supporting index Section 2.4 pagination
- [ ] PUT renames/recolors with the same validation and 409 duplicate handling; DELETE removes the label and all its assignments; unknown ids return 404 `not-found`
- [ ] Concurrent renames are last-write-wins (no version checks); the later write overwrites and clients receive the stored name on next refetch
- [ ] The router never touches `pg` directly — all SQL goes through `src/db/label.ts`

**Dependencies:** T-002, T-005
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - labels router + Zod schemas
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Throw `ApiError`; `src/api/errors.ts` serializes it — never hand-build error JSON
- Create/rename/delete require edit rights; read is any project member (FEAT-001 Section 6, Project row)

---

### T-007: Implement task label-assignment endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Add PUT `/api/v1/tasks/{id}/labels` to the tasks router, replacing the task's label set from an array of label IDs via the task-label repository. Reject more than 10 labels or labels from a different project with `validation-error`.

**Rationale:**
Implements the fifth Section 7 endpoint; backs AC-2 and the 11th-label edge case in Section 9.

**Acceptance Criteria:**
- [ ] Zod schema validates the body (`labelIds`: UUID array, max length 10); an 11th label returns 400 `validation-error`
- [ ] Label IDs not belonging to the task's project return 400 `validation-error`; an unknown task returns 404 `not-found`
- [ ] Success returns the updated label set in the envelope, matching the `labels.md` spec

**Dependencies:** T-002, T-005
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - PUT `/:id/labels` route + Zod schema

**Technical Notes:**
- The endpoint is specced in `endpoints/labels.md` (work-item retrieval key) but lives in `src/api/tasks.ts` because the route sits under `/api/v1/tasks` — keep spec and router consistent

---

### T-008: Add labels and labelId filter to the board query

**Type:** Backend
**Workflow:** standard

**Description:**
Extend the board list query to aggregate each task's labels in a single joined query and support an optional `labelId` query parameter that filters server-side. Expose `labels` on TaskDto and validate `labelId` in the tasks router.

**Rationale:**
Implements the modified Section 7 endpoint under the Section 10 constraints: labels ride the existing board response (no per-card fetches) and filtering stays server-side so pagination remains correct.

**Acceptance Criteria:**
- [ ] GET `/api/v1/projects/{projectId}/tasks` returns every task with its `labels` array populated via one aggregated query (no N+1)
- [ ] `labelId` filters to tasks carrying that label, composes with the existing `status` filter and pagination, and `meta.totalCount` reflects the filtered count
- [ ] A non-UUID `labelId` returns 400 `validation-error`; a valid `labelId` with zero matches returns 200 with empty `data` and `totalCount` 0

**Dependencies:** T-002, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - aggregate labels into the board query; optional `labelId` filter
- src/api/tasks.ts - `labelId` query validation + `labels` in the TaskDto mapping

**Technical Notes:**
- Use a `json_agg`/lateral join over `task_labels` + `labels`; order labels deterministically (e.g., by name) for stable chip rendering
- Keep the base board query plan unchanged when no `labelId` is supplied — initial board load must not get slower (Section 10)

---

## Frontend

### T-009: Create LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Build the reusable LabelChip component rendering a label's name on its accent-palette color, used by board cards, the detail-panel picker, and the management dialog. Choose the per-token text color so chip text meets WCAG 2.1 AA on every palette color.

**Rationale:**
FEAT-001 Section 8 names LabelChip as a new shared component; the NFR requires 4.5:1 chip-text contrast on all 12 accent colors.

**Acceptance Criteria:**
- [ ] `src/ui/components/label-chip.tsx` renders name + color from a LabelDto using accent tokens via CSS custom properties — no hard-coded hex values
- [ ] Chip text meets 4.5:1 contrast on all 12 accent tokens (per-token text-color choice)
- [ ] Supports a compact variant for dense board cards and truncates long names with an ellipsis plus a `title` attribute

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component

**Technical Notes:**
- Use `caption` typography (12px) and `space-1` padding per the design system; CSS Modules like the other shared components

---

### T-010: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Create the Label Management Dialog screen for creating, renaming, recoloring, and deleting project labels, opened from the board toolbar. This adds a new user-facing screen — generate an HTML mockup of the Label Management Dialog for stakeholder approval (see `.ai-framework/prompts/mockup-generation.md`) before implementing.

**Rationale:**
FEAT-001 Section 8 declares this new screen and mandates mockup-first classification; backs AC-1, AC-4, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] Dialog lists the project's labels with LabelChip previews and a 12-swatch palette picker — no custom hex input, no new dependencies
- [ ] Creating a label shows it in the list immediately; a duplicate name renders the 409 message inline next to the name input
- [ ] Delete uses the shared `Dialog` in destructive mode and states the affected task count (from `assignedTaskCount`) before confirming
- [ ] Rename/recolor propagates to board chips via board-query invalidation, without a page reload
- [ ] All four states handled (default/loading/empty/error) per UI index Section 2.5

**Dependencies:** T-003, T-006, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen, forms, mutations
- src/ui/project-board.tsx - toolbar button that opens the dialog

**Technical Notes:**
- TanStack Query mutations invalidate the labels query and the board tasks query on success
- Mockup should cover: label list, create form, palette picker, inline duplicate error, delete confirmation

---

### T-011: Add Labels picker to Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a Labels field to the Task Detail Panel with a multi-select picker showing LabelChip previews, persisting changes via PUT `/api/v1/tasks/{id}/labels`. Invalidate the board query on save so card chips update without a page reload.

**Rationale:**
Implements the Section 8 Task Detail Panel modification; backs AC-2 and the 11th-label edge case.

**Acceptance Criteria:**
- [ ] Picker lists project labels with chip previews; assigning and removing labels persists and survives a reload
- [ ] Selection disables at 10 labels with an explanatory tooltip; a 400 from the API surfaces as an inline error
- [ ] Board card chips reflect the change without a page reload (board-query invalidation)

**Dependencies:** T-003, T-006, T-007, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field, multi-select picker, mutation + invalidation

**Technical Notes:**
- Label options come from GET project labels — share the query key with T-010/T-012
- Keep the picker as an internal component of the panel file per the one-file-per-screen convention

---

### T-012: Render board label chips and filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 label chips with a "+N" overflow indicator on TaskCard and add a label filter dropdown to the board toolbar that drives the `labelId` query parameter. Handle the zero-match empty state and clear the filter with a notice when the filtered label was deleted by another user.

**Rationale:**
Implements the Section 8 Project Board modification; backs AC-3 and AC-4 plus the Section 9 empty-filter and deleted-while-filtered edge cases.

**Acceptance Criteria:**
- [ ] TaskCard shows up to 3 LabelChips plus a "+N" overflow indicator, sourced from the board response — no per-card fetches
- [ ] Selecting a label refetches the board with `labelId`; clearing the filter restores the full board
- [ ] Zero matching tasks renders `EmptyState` with a "Clear filter" action — never a blank board
- [ ] If the active filter's label disappears from the labels list after a refetch, the filter clears automatically and a notice is shown

**Dependencies:** T-003, T-006, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/project-board.tsx - filter dropdown, `labelId` in the query key, empty/cleared-filter handling
- src/ui/components/task-card.tsx - chip row with overflow indicator

**Technical Notes:**
- Keep `labelId` in the TanStack Query key so filtering is a server round-trip (Section 10 constraint)
- Dropdown options reuse the project-labels query from T-010/T-011; use the chip compact variant on narrow columns

---

## Testing

### T-013: Unit-test label repositories and board query

**Type:** Testing
**Workflow:** standard

**Description:**
Add repository unit tests against the test database covering label CRUD, assignment-replacement rules, and the board query's label aggregation and filtering.

**Rationale:**
CLAUDE.md convention 6 — every repository gets a unit test; verifies the database-level rules behind AC-6 and the Section 9 edge cases.

**Acceptance Criteria:**
- [ ] `tests/db/label.test.ts` covers create, list-with-counts, update, delete, and case-insensitive duplicate rejection ("Urgent" vs "urgent")
- [ ] `tests/db/task-label.test.ts` covers replace-for-task happy path, 11-label rejection, cross-project rejection, and cascade cleanup on label delete
- [ ] `tests/db/task.test.ts` covers label aggregation in the board query and `labelId` filtering with correct pagination totals

**Dependencies:** T-005, T-008
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - assignment repository unit tests
- tests/db/task.test.ts (new) - board query aggregation + filter tests

**Technical Notes:**
- Run with Vitest against the test database per CLAUDE.md convention 6; tests mirror the `src/db/` tree

---

### T-014: Add API integration tests for labels

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests for the labels router and the modified tasks endpoints, covering the API surface of every acceptance criterion and the Section 9 edge cases.

**Rationale:**
CLAUDE.md convention 6 — every router gets a Supertest integration test; verifies AC-1 through AC-6 at the API level.

**Acceptance Criteria:**
- [ ] `tests/api/labels.test.ts` covers list/create/rename/recolor/delete, including 409 on case-insensitive duplicates, 404 on unknown ids, and envelope/error formats
- [ ] Delete tests assert assignments are removed while tasks survive, and that the list response's `assignedTaskCount` matches the assignments
- [ ] `tests/api/tasks.test.ts` covers PUT `/tasks/{id}/labels` (success, max-10 rejection, cross-project rejection) and GET board with `labelId` filter and populated `labels` arrays
- [ ] All error assertions check catalog codes (`validation-error`, `conflict`, `not-found`) — never ad-hoc messages

**Dependencies:** T-006, T-007, T-008
**Complexity:** M

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - PUT labels route, `labelId` filter, `labels` array cases

**Technical Notes:**
- Use Supertest against the Express app per CLAUDE.md; assert the `{ data }` / `{ data, meta }` envelope on every success response

---

## Summary

**Feature Brief:** FEAT-001 — Task Labels (`docs/work-items/FEAT-001-task-labels.md`)

**Total task count by type:** 14 tasks — Documentation 3 (T-001, T-002, T-003), Database 1 (T-004), Backend 4 (T-005, T-006, T-007, T-008), Frontend 4 (T-009, T-010, T-011, T-012), Testing 2 (T-013, T-014).

**Estimated complexity distribution:** S ×5 (T-001, T-002, T-004, T-007, T-009), M ×7 (T-003, T-005, T-006, T-008, T-011, T-013, T-014), L ×2 (T-010, T-012), XL ×0.

**Critical path:** T-001 → T-004 → T-005 → T-006 → T-010 (5 tasks). Equal-length chains run T-001 → T-002 → T-003 → T-009 → T-010/T-012, so spec authoring and schema/repository work can proceed in parallel after T-001.

**Risks / open questions:**

- The delete confirmation's affected-task count is served by `assignedTaskCount` on the label list DTO (decided in T-002); if the count must be exact at confirm time under concurrent edits, a dedicated count fetch could be added later.
- PUT `/api/v1/tasks/{id}/labels` is specced in `endpoints/labels.md` (per the work item's retrieval key) but implemented in `src/api/tasks.ts` where the route lives — the two must be kept consistent.
- Concurrent label renames are last-write-wins with no version checks (per Section 9); acceptable for now, revisit if conflicting edits become visible to users.
- The <300ms P95 filter round-trip on 500-task boards rests on the `task_labels(label_id)` index and the single aggregated board query — verify with realistic data volumes in T-013/T-014.
- "Edit rights" checks reuse the existing auth-service role resolution used by PATCH `/api/v1/tasks/{id}`; the brief defines no new permission model.

---

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: A project member can create a label with a name (1–30 chars) and a palette color; the label immediately appears in the project's label list | T-004, T-006, T-010, T-014 |
| AC-2: A user can assign and remove labels on a task from the task detail panel; changes persist and appear on the board card without a page reload | T-007, T-011, T-012, T-014 |
| AC-3: Selecting a label in the board filter shows only tasks carrying that label; clearing the filter restores the full board | T-008, T-012, T-014 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-006, T-010, T-012, T-014 |
| AC-5: Deleting a label removes it from all tasks after an explicit confirmation dialog stating how many tasks are affected | T-005, T-006, T-010, T-014 |
| AC-6: Attempting to create a duplicate label name within the same project returns a validation error and the UI shows an inline message | T-004, T-006, T-010, T-013, T-014 |
