# FEAT-001: Task Labels — Implementation Tasks

> Generated from Feature Brief `docs/work-items/FEAT-001-task-labels.md` (FEAT-001, target v1.1) using the canonical task schema in `prompts/base-template.md`.

## Foundation

### T-001: Author data-model shards for Label and TaskLabel

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for the new Label and TaskLabel entities and register them in the data-model index. Document fields, constraints, relationships, and the business rules from Feature Brief Section 6.

**Rationale:**
The Feature Brief requires the new entity shards to exist before feature logic; downstream tasks retrieve them via the impact-table shard names.

**Acceptance Criteria:**
- [ ] `label.md` documents id, project_id (FK, cascade on project delete), name (varchar(30), unique per project case-insensitively), color (one of the 12 accent palette tokens), and timestamps
- [ ] `task-label.md` documents the Task↔Label N:M join with the max-10-labels-per-task and same-project rules, and cascade behavior (label delete removes assignments, never tasks)
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities, a Section 4.2 many-to-many entry, and a Changelog row

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard (fields, indexes, relationships, rules)
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity shard
- docs/data-model/index.md - Module Ownership, Relationships Overview (4.2), and Changelog entries

**Technical Notes:**
- Follow index Section 3 conventions: snake_case plural tables (`labels`, `task_labels`), UUID `id` PKs, `created_at`/`updated_at` timestamptz on every table
- Store the palette token name (e.g. `accent-07`) in `color`, not a hex value — tokens live in `docs/ui-specification/index.md` Section 2.1

### T-002: Author labels API spec shard and update tasks endpoint spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `endpoints/labels.md` documenting all five label endpoints from Feature Brief Section 7, and update `endpoints/tasks.md` with the optional `labelId` query parameter and the `labels` array embedded in TaskDto. Add the five Endpoint Summary rows and a Changelog entry to the API index.

**Rationale:**
Endpoints must be specified before backend implementation and frontend integration; the shard is the retrieval key for all label API work.

**Acceptance Criteria:**
- [ ] `labels.md` specifies GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` with envelopes, status codes, and existing catalog codes (409 `conflict` for duplicate name, `validation-error` for name/color/limit violations)
- [ ] LabelDto on the list endpoint includes a `taskCount` field so the delete confirmation can state how many tasks are affected
- [ ] `tasks.md` documents the optional `labelId` parameter and the TaskDto `labels` array (labels ride in the board response — no per-card fetch)
- [ ] `docs/api-spec/index.md` Endpoint Summary gains the five rows and a Changelog entry

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - all five label endpoints, LabelDto, error mapping
- docs/api-spec/endpoints/tasks.md - `labelId` query parameter + `labels` array on TaskDto
- docs/api-spec/index.md - Endpoint Summary rows + Changelog entry

**Technical Notes:**
- Reuse existing Error Catalog codes (`validation-error`, `not-found`, `conflict`) — no new catalog rows needed
- PUT `/tasks/{id}/labels` replaces the full label set (array of label IDs); PUT `/labels/{id}` is last-write-wins on concurrent renames (Feature Brief Section 9)

### T-003: Author Label Management Dialog screen shard and update UI spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the screen shard for the new Label Management Dialog, add its Screen Inventory row, document the LabelChip shared component in `components.md`, and update the Project Board and Task Detail Panel shards for their label-related modifications.

**Rationale:**
Feature Brief Section 8 requires the new screen shard and LabelChip inventory entry before the frontend work; modified screen shards must stay in sync with the feature.

**Acceptance Criteria:**
- [ ] `label-management-dialog.md` covers layout, component hierarchy, component→API mapping, all four states per index Section 2.5, and interactions including the delete confirmation with affected task count and the inline duplicate-name error
- [ ] `components.md` documents LabelChip inputs/outputs and variants, including compact usage on board cards
- [ ] `project-board.md` and `task-detail-panel.md` reflect the chips (max 3 + "+N" overflow), the toolbar single-label filter, and the Labels picker field
- [ ] `docs/ui-specification/index.md` gains the Screen Inventory row and a Changelog entry

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/components.md - LabelChip inventory entry
- docs/ui-specification/index.md - Screen Inventory row + Changelog entry
- docs/ui-specification/screens/project-board.md - chips on cards + filter dropdown + manage-labels trigger
- docs/ui-specification/screens/task-detail-panel.md - Labels field with multi-select picker

### T-004: Create migration for labels and task_labels tables

**Type:** Database
**Workflow:** standard

**Description:**
Add `migrations/002-labels.sql` creating the `labels` and `task_labels` tables per the T-001 shards, with foreign keys, uniqueness constraints, and the indexes needed for board filtering.

**Rationale:**
The schema must exist before repository and API work; Feature Brief Section 6 defines both new entities.

**Acceptance Criteria:**
- [ ] `labels` has UUID `id` PK, `project_id` FK with cascade on project delete, `name VARCHAR(30)`, `color`, timestamps, and a unique index on `(project_id, lower(name))` for case-insensitive per-project names
- [ ] `task_labels` joins tasks and labels with cascade deletes from both sides and a unique constraint on `(task_id, label_id)`
- [ ] An index supports filtering board tasks by label (e.g. on `task_labels (label_id)`) toward the <300ms P95 filter NFR

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - labels + task_labels tables, constraints, indexes

**Technical Notes:**
- Follow the data-model conventions: UUID `id` PK and `created_at`/`updated_at` timestamptz on both tables
- Cascade from `labels` to `task_labels` guarantees label deletion removes assignments only — tasks are untouched (AC-5)

## Backend

### T-005: Implement label and task-label repositories

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` and `src/db/task-label.ts` repository modules holding all SQL for label CRUD and assignment management. Include per-label task counts on the list query and a transactional replace-set operation for a task's labels.

**Rationale:**
CLAUDE.md restricts SQL to one repository module per entity under `src/db/`; the routers in later tasks depend on these modules.

**Acceptance Criteria:**
- [ ] `listByProject` returns labels with a `taskCount`; `create`/`update` surface case-insensitive duplicate names as a distinguishable error for the router's 409 mapping
- [ ] Label deletion removes the label and its assignments in one transaction and returns the number of affected tasks
- [ ] `replaceTaskLabels` enforces max 10 labels and same-project membership inside a transaction
- [ ] A batch query returns labels for a set of task IDs in one round-trip for embedding in the board response

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label CRUD queries, duplicate detection, delete with assignment cleanup + affected count
- src/db/task-label.ts (new) - replace-set operation, labels-for-tasks batch query, per-label task counts

**Technical Notes:**
- Detect duplicates via the unique-index violation or a `lower(name)` pre-check inside the transaction
- Use `WHERE task_id = ANY($1)` (or similar) for the batch query to honor the no-per-card-fetch constraint (Feature Brief Section 10)

### T-006: Implement labels router with the five label endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` per the T-002 spec, and mount it in `src/api/index.ts`. Validate bodies and parameters with Zod schemas defined next to the handlers.

**Rationale:**
Feature Brief Section 7 requires all five label endpoints; API tasks must precede frontend integration.

**Acceptance Criteria:**
- [ ] All endpoints require auth, use the standard envelope (`data`, plus `meta` on the list), and throw `ApiError` with Error Catalog codes only
- [ ] POST rejects a duplicate name within the project (case-insensitive, e.g. "Urgent" vs "urgent") with 409 `conflict`; name outside 1–30 chars or color outside the 12 accent tokens returns 400 `validation-error`
- [ ] DELETE removes the label and all its assignments while leaving tasks untouched
- [ ] PUT `/tasks/{id}/labels` replaces the task's label set, rejecting more than 10 labels or labels from another project with 400 `validation-error`
- [ ] PUT `/labels/{id}` applies last-write-wins on concurrent renames (no version checks); missing project/label/task returns 404 `not-found`

**Dependencies:** T-002, T-005
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - labels router: five endpoints + Zod schemas
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Validate `color` with a Zod enum of the 12 accent token names
- Routers never touch `pg` directly — delegate all SQL to the T-005 repositories

### T-007: Add labelId filter and embedded labels to the board tasks endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Extend GET `/api/v1/projects/{projectId}/tasks` with an optional `labelId` query parameter and embed each task's labels in the TaskDto, per the updated tasks spec. Filtering stays server-side so results remain correct with pagination.

**Rationale:**
AC-3 requires server-side single-label filtering (Feature Brief Section 10), and labels must ride in the existing board response rather than per-card fetches to protect board load time.

**Acceptance Criteria:**
- [ ] `labelId` returns only tasks carrying that label, and `meta.totalCount` reflects the filtered count under pagination
- [ ] Every returned TaskDto includes a `labels` array (id, name, color) populated without N+1 queries; omitting `labelId` returns the full board unchanged
- [ ] A non-UUID `labelId` returns 400 `validation-error`; a `labelId` matching no tasks returns an empty `data` array, not an error

**Dependencies:** T-002, T-005
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - `labelId` in the Zod query schema, passed through to the repository
- src/db/task.ts - board query joins `task_labels` for the filter and embeds labels via the batch query

**Technical Notes:**
- Attach labels with the T-005 batch query or a `json_agg` join — one round-trip either way
- Filter round-trip must stay under 300ms P95 for 500-task boards — lean on the T-004 indexes

## Frontend

### T-008: Build LabelChip shared component

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Create the reusable LabelChip component rendering a label's name on its accent-token color, used by board cards, the detail-panel picker, and the management dialog. Mockup first: chip rendering across all 12 accent tokens (in board-card context) needs stakeholder approval per `.ai-framework/prompts/mockup-generation.md` before implementation.

**Rationale:**
Feature Brief Section 8 lists LabelChip as a new shared component and classifies related frontend tasks mockup-first; a single chip implementation keeps rename/recolor updates consistent everywhere (AC-4).

**Acceptance Criteria:**
- [ ] Renders the label name and palette color via design-token CSS custom properties (caption typography, space-1 padding) — no hard-coded hex values
- [ ] Chip text color per accent token meets WCAG 2.1 AA contrast (4.5:1) on all 12 palette colors
- [ ] Truncates long names (up to 30 chars) gracefully in both default and compact card contexts

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component with per-token text color mapping

**Technical Notes:**
- In-house components only — no external UI kit or color libraries (UI index Section 1.2, Feature Brief Section 10)
- Pair each accent token with a fixed light/dark text color chosen during mockup review; verify contrast with a checker

### T-009: Build the Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Create the Label Management Dialog for creating, renaming, recoloring, and deleting project labels, opened from the board toolbar. Mockup first: this is a new screen (Feature Brief Section 8) — generate an HTML mockup for stakeholder approval per `.ai-framework/prompts/mockup-generation.md` before implementing.

**Rationale:**
AC-1, AC-4, AC-5, and AC-6 all flow through this new screen; the Feature Brief lists it as the only new screen in the feature.

**Acceptance Criteria:**
- [ ] Creating a label (name 1–30 chars + swatch grid of the 12 accent tokens) shows it immediately in the project's label list
- [ ] A 409 `conflict` response renders an inline duplicate-name message next to the name input
- [ ] Delete opens the shared `Dialog` (destructive variant) stating how many tasks are affected before confirming
- [ ] Rename/recolor/delete mutations invalidate the labels and board queries so every visible card chip updates
- [ ] Loading, empty ("No labels yet" EmptyState), and error states follow UI index Section 2.5

**Dependencies:** T-006, T-008
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - label CRUD dialog built on the shared Dialog component

**Technical Notes:**
- Use TanStack Query mutations invalidating the labels list and board tasks query keys
- The affected-task count for the delete confirmation comes from `taskCount` on the labels list response
- The color picker is a swatch grid of the 12 tokens — no external color-picker dependency

### T-010: Add label chips and single-label filter to the Project Board

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 label chips with a "+N" overflow indicator on TaskCard, add a single-label filter dropdown and a "Manage labels" trigger to the board toolbar, and wire `labelId` into the board query. Chips follow the mockup approved in T-008, so this modification of an existing screen stays standard.

**Rationale:**
Feature Brief Section 8 lists the Project Board as modified (chips + filter); AC-3 and AC-4 surface here.

**Acceptance Criteria:**
- [ ] Cards show up to 3 chips plus "+N" for the remainder, sourced from the labels embedded in the board response (no per-card fetch)
- [ ] Selecting a label refetches the board with `labelId` (server-side filter) and clearing the filter restores the full board
- [ ] A filter with zero matching tasks renders the standard EmptyState with a "Clear filter" CTA — never a blank board
- [ ] If the filtered label was deleted elsewhere, the next refetch clears the filter and shows a notice
- [ ] The toolbar trigger opens the Label Management Dialog

**Dependencies:** T-006, T-007, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/project-board.tsx - filter dropdown, manage-labels trigger, `labelId` in the board query, deleted-filter notice
- src/ui/components/task-card.tsx - chip row (max 3 + "+N" overflow)

**Technical Notes:**
- Include `labelId` in the TanStack Query key so pagination and refetches stay consistent
- Detect the deleted-filter case when the selected label id disappears from the labels list response

### T-011: Add labels field with multi-select picker to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to the Task Detail Panel with a multi-select picker showing chip previews, persisting via PUT `/api/v1/tasks/{id}/labels`. Follows the approved chip mockup and the panel's existing form-field pattern, so no new mockup is required.

**Rationale:**
AC-2 requires assigning and removing labels from the detail panel with changes visible on the board card without a page reload.

**Acceptance Criteria:**
- [ ] The picker lists the project's labels as selectable chip previews; toggling updates the selection and persists the full set
- [ ] Selection is disabled at 10 labels with an explanatory tooltip; an API `validation-error` is still surfaced if it occurs
- [ ] A successful save invalidates the board query so the card's chips update without a page reload

**Dependencies:** T-006, T-008
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field, multi-select picker, replace-set mutation

**Technical Notes:**
- Reuse the labels list query key from the dialog so picker options stay in sync

## Testing

### T-012: Write repository unit tests for label and task-label

**Type:** Testing
**Workflow:** standard

**Description:**
Add unit tests against the test database for the two new repository modules, per the CLAUDE.md convention that every repository gets a unit test.

**Rationale:**
The core business rules (case-insensitive uniqueness, max 10 labels, same-project assignment, cascade to assignments only) live in the repositories and need direct coverage.

**Acceptance Criteria:**
- [ ] Duplicate names differing only by case are rejected within a project but allowed across different projects
- [ ] Deleting a label removes its assignments and returns the affected-task count; the tasks themselves remain
- [ ] `replaceTaskLabels` rejects an 11th label and rejects labels belonging to a different project
- [ ] The labels-for-tasks batch query returns the correct labels per task, including empty sets

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - task-label repository unit tests

### T-013: Write integration tests for the labels router

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests covering all five label endpoints, response envelopes, and error paths, per the CLAUDE.md convention that every router gets an integration test.

**Rationale:**
AC-1, AC-2, AC-5, and AC-6 are verified at the API boundary, including the duplicate-name and label-limit edge cases from Feature Brief Section 9.

**Acceptance Criteria:**
- [ ] CRUD happy paths return the standard envelope (list includes `meta` and `taskCount`) and persist changes
- [ ] Creating "urgent" when "Urgent" exists returns 409 with code `conflict`; invalid name length or non-palette color returns 400 `validation-error` with `fields`
- [ ] PUT `/tasks/{id}/labels` with 11 labels or a cross-project label returns 400 `validation-error`
- [ ] DELETE removes the label's assignments, and a subsequent board fetch shows the tasks intact without the label

**Dependencies:** T-006
**Complexity:** M

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - Supertest coverage for the five label endpoints

### T-014: Extend board endpoint tests for label filtering and embedded labels

**Type:** Testing
**Workflow:** standard

**Description:**
Extend the existing tasks router tests to cover the `labelId` filter and the labels array embedded in board responses.

**Rationale:**
AC-3 and the server-side-filtering constraint (Feature Brief Section 10) are verified at the API boundary, including the zero-match edge case.

**Acceptance Criteria:**
- [ ] `labelId` returns only matching tasks with correct `meta.totalCount` under pagination
- [ ] Board responses embed each task's labels; tasks without labels return an empty array
- [ ] A `labelId` with zero matches returns an empty `data` array (not an error); a non-UUID `labelId` returns 400 `validation-error`

**Dependencies:** T-007
**Complexity:** S

**Files to Modify/Create:**
- tests/api/tasks.test.ts - `labelId` filter, embedded labels, and zero-match cases

## Summary

**Feature Brief:** FEAT-001 — Task Labels (`docs/work-items/FEAT-001-task-labels.md`)

**Task count by type (14 total):**

| Type | Count | Tasks |
|------|-------|-------|
| Documentation | 3 | T-001, T-002, T-003 |
| Database | 1 | T-004 |
| Backend | 3 | T-005, T-006, T-007 |
| Frontend | 4 | T-008, T-009, T-010, T-011 |
| Testing | 3 | T-012, T-013, T-014 |

**Complexity distribution:** S ×3 (T-001, T-004, T-014) · M ×8 (T-002, T-003, T-005, T-007, T-008, T-011, T-012, T-013) · L ×3 (T-006, T-009, T-010) · XL ×0

**Critical path (6 tasks):** T-001 → T-004 → T-005 → T-006 → T-009 → T-010 (spec shards and the parallel T-002/T-003/T-008 chain feed the same endpoints; T-010 lands last as it integrates chips, filter, and the dialog trigger).

**Risks / open questions:**

- The response shape of PUT `/tasks/{id}/labels` (updated label set vs. full TaskDto) is decided in T-002; T-011 assumes the updated label set is returned.
- No e2e test infrastructure exists in this project — UI-level acceptance (AC-2/AC-3 interactions) is verified through mockup approval, the frontend tasks' acceptance criteria, and the API integration tests.
- Filtering by a label deleted by another user returns an empty result rather than an error; T-010 clears the filter and shows a notice on refetch — confirm this UX during mockup review.
- Per-token chip text colors must be fixed during the T-008 mockup approval to guarantee 4.5:1 contrast on all 12 accent tokens.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label (name 1–30 chars + palette color); it immediately appears in the project's label list | T-006, T-009, T-013 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and appear on the board card without reload | T-006, T-011, T-013 |
| AC-3: Selecting a label filters the board to tasks carrying it; clearing restores the full board | T-007, T-010, T-014 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-006, T-008, T-009, T-010 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-005, T-006, T-009, T-013 |
| AC-6: Duplicate label name within a project returns a validation error and the UI shows an inline message | T-006, T-009, T-013 |
