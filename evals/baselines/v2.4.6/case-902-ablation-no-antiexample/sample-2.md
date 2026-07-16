# FEAT-001: Task Labels — Implementation Tasks

> Generated from `docs/work-items/FEAT-001-task-labels.md` (Feature Brief FEAT-001, TaskFlow v1.1).
> Schema: canonical task schema from `prompts/base-template.md`. Scope authority: Feature Brief Section 4.

---

## Foundation

### T-001: Author Label and TaskLabel data-model shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the entity shards for the two new entities, Label and TaskLabel, and register them in the data-model index. Document fields, constraints, relationships, and business rules following the conventions in `docs/data-model/index.md` Section 3.

**Rationale:**
Feature Brief Section 6 requires the new entity shards to exist before feature logic; downstream database and repository tasks build against this model.

**Acceptance Criteria:**
- [ ] `entities/label.md` documents id/project_id/name/color/timestamps, case-insensitive name uniqueness per project, and the 12-token accent palette constraint
- [ ] `entities/task-label.md` documents the N:M join, the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] Both shards state cascade behavior: deleting a label removes assignments only, never tasks; deleting a project removes its labels
- [ ] `index.md` gains Module Ownership rows, a Many-to-Many Relationships entry, an updated ER diagram, and a Changelog row

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard (fields, rules, relationships)
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity shard
- docs/data-model/index.md - Module Ownership rows, Relationships Overview (Section 4.2), ER diagram, Changelog

**Technical Notes:**
- Follow the kebab-case singular shard naming rule (`TaskLabel` → `task-label.md`)
- Keep index Relationships Overview and per-shard relationship tables in sync, per the index note

---

### T-002: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Write the SQL migration adding the `labels` table and the `task_labels` join table with foreign keys, cascade rules, and the uniqueness index backing case-insensitive label names per project.

**Rationale:**
Both new entities from Feature Brief Section 6 need storage before any repository or API work; the unique index enforces AC-6 at the database level.

**Acceptance Criteria:**
- [ ] `labels`: `id` UUID PK, `project_id` UUID FK → projects (ON DELETE CASCADE), `name` VARCHAR(30) NOT NULL, `color` VARCHAR(16) NOT NULL, `created_at`/`updated_at` TIMESTAMPTZ NOT NULL
- [ ] Unique index on `(project_id, lower(name))` enforces case-insensitive per-project name uniqueness
- [ ] `task_labels`: `task_id` FK → tasks (ON DELETE CASCADE), `label_id` FK → labels (ON DELETE CASCADE), unique on the pair, plus timestamps per convention
- [ ] Index on `task_labels(label_id)` supports board filtering and delete-impact counts

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-add-labels.sql (new) - labels + task_labels tables, indexes, cascades

**Technical Notes:**
- Follow `migrations/NNN-description.sql` numbering after `001-init.sql`
- Color stores an accent palette token string (`accent-01` … `accent-12`); token validation lives in the API layer (Zod), keeping the palette swappable without a migration

---

### T-003: Implement Label repository

**Type:** Backend
**Workflow:** standard

**Description:**
Create the Label repository module with list, create, rename/recolor, and delete operations. Listing returns each label with its assigned-task count so the UI can state delete impact.

**Rationale:**
CLAUDE.md mandates one repository module per entity with all SQL in `src/db/`; the task count powers the AC-5 confirmation dialog.

**Acceptance Criteria:**
- [ ] `listByProject` returns the project's labels with an `assignedTaskCount` per label in one query
- [ ] `create` and `rename` surface the unique-index violation distinctly so the router can map it to the `conflict` error code (case-insensitive duplicates included)
- [ ] `remove` deletes the label; assignments disappear via cascade and tasks are untouched
- [ ] All functions use parameterized queries via the `pg` driver; no SQL outside `src/db/`

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - Label CRUD + per-label assigned-task counts

**Technical Notes:**
- Detect duplicates by catching the unique-violation error code (23505) rather than a check-then-insert race
- Count assignments with a LEFT JOIN + GROUP BY on `task_labels` — avoid per-label queries

---

### T-004: Implement TaskLabel repository

**Type:** Backend
**Workflow:** standard

**Description:**
Create the TaskLabel repository module that replaces the set of labels on a task transactionally and batch-fetches labels for a set of tasks for the board response.

**Rationale:**
Feature Brief Section 6 defines the join entity's business rules (max 10 per task, same-project only); the batch fetch satisfies the Section 10 constraint that board load gains no per-card queries.

**Acceptance Criteria:**
- [ ] `replaceForTask` swaps a task's label set in a single transaction (delete + insert)
- [ ] Replacing with more than 10 labels is rejected before any write
- [ ] Labels belonging to a different project than the task are rejected before any write
- [ ] `listByTaskIds` returns labels for many tasks in one query, keyed by task id

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/task-label.ts (new) - transactional label-set replacement + batch fetch for board

**Technical Notes:**
- Validate the same-project rule inside the transaction by joining candidate label ids against the task's `project_id`
- Return distinguishable error kinds (limit-exceeded vs cross-project) so the router maps both to `validation-error` with precise messages

---

## Backend

### T-005: Author labels API spec shard and update API index

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `endpoints/labels.md` documenting all five label endpoints (list, create, rename/recolor, delete, replace-task-labels) and update the tasks shard for the `labelId` filter and the labels array on `TaskDto`. Register the new endpoints in the index's Endpoint Summary.

**Rationale:**
Feature Brief Section 7 requires the new endpoint shard before frontend integration; the API contract must be agreed before router and UI work consume it.

**Acceptance Criteria:**
- [ ] `endpoints/labels.md` documents `GET`/`POST /api/v1/projects/{projectId}/labels`, `PUT`/`DELETE /api/v1/labels/{id}`, and `PUT /api/v1/tasks/{id}/labels` with request/response shapes, envelope, and status codes
- [ ] `LabelDto` includes `id`, `projectId`, `name`, `color`, and `taskCount` (drives the AC-5 delete confirmation); duplicate names documented as 409 `conflict`
- [ ] `endpoints/tasks.md` gains the optional `labelId` query parameter on the board list and a `labels: LabelDto[]` field on `TaskDto`
- [ ] `index.md` Endpoint Summary gains one row per new endpoint and a Changelog entry; only existing Error Catalog codes are referenced

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - all five label endpoints + LabelDto
- docs/api-spec/endpoints/tasks.md - `labelId` query param + labels on TaskDto
- docs/api-spec/index.md - Endpoint Summary rows, Changelog

**Technical Notes:**
- No new error codes needed: `validation-error` (400), `conflict` (409), `not-found` (404), `unauthorized` (401) cover every case — do not add catalog rows
- Nested route `PUT /api/v1/tasks/{id}/labels` groups under the labels shard per the index's shard-mapping note

---

### T-006: Implement labels router with the five label endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Create the Express router implementing label CRUD and task-label replacement per the spec shard, with Zod validation beside the handlers, and mount it in `src/api/index.ts`.

**Rationale:**
Implements the API Impact table (Feature Brief Section 7) and enforces the business rules behind AC-1, AC-2, AC-4, AC-5, and AC-6 at the API boundary.

**Acceptance Criteria:**
- [ ] `GET .../labels` returns the list envelope with `meta`; `POST` validates name (1–30 chars after trim) and color (one of the 12 accent tokens) and returns the created label
- [ ] Duplicate names — including case-only variants like "Urgent" vs "urgent" — return 409 with code `conflict`
- [ ] `PUT /api/v1/labels/{id}` renames/recolors with last-write-wins semantics (no version check); `DELETE` removes the label and all its assignments, never tasks
- [ ] `PUT /api/v1/tasks/{id}/labels` replaces the set; an 11th label or a cross-project label returns 400 `validation-error` with a field message
- [ ] All errors are thrown as `ApiError` with Error Catalog codes and serialized by `src/api/errors.ts`; all routes require auth

**Dependencies:** T-003, T-004, T-005
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - router for the five label endpoints + Zod schemas
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Concurrent renames resolve last-write-wins per Feature Brief Section 9; the stale client picks up the new name on its next refetch
- Write/delete operations are restricted to members with edit rights, mirroring the existing `PATCH /api/v1/tasks/{id}` role handling

---

### T-007: Add labelId filter and labels array to the board tasks endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Extend `GET /api/v1/projects/{projectId}/tasks` with an optional `labelId` query parameter filtered in SQL, and include each task's labels in the response via a single batched fetch.

**Rationale:**
AC-3 requires server-side board filtering (Feature Brief Section 10 — correctness under pagination), and the board-load constraint requires labels in the existing response rather than per-card fetches.

**Acceptance Criteria:**
- [ ] `labelId` (UUID, optional) filters tasks to those carrying the label; `meta.totalCount` reflects the filtered total and pagination stays correct
- [ ] A non-UUID `labelId` returns 400 `validation-error`; omitting it preserves current behavior exactly
- [ ] Every returned `TaskDto` includes a `labels` array (id, name, color, taskCount omitted or populated per spec shard) with no N+1 queries
- [ ] Board list stays ordered by `status`, then `position`

**Dependencies:** T-004, T-005
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - `labelId` Zod query validation + pass-through to repository
- src/db/task.ts - filtered board query + batched label hydration via `listByTaskIds`

**Technical Notes:**
- Filter with an EXISTS subquery on `task_labels` so pagination counts stay exact
- Keep the label hydration to one extra query per board request to protect the 300ms P95 filter round-trip NFR

---

## Frontend

### T-008: Author Label Management Dialog screen shard and update UI spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the screen shard for the new Label Management Dialog, add the LabelChip entry to the shared component inventory, and update the two modified screen shards and the UI index per Feature Brief Section 8.

**Rationale:**
Section 8 requires the new screen shard and inventory row before implementation; the shards give the frontend tasks their component→API mappings and state tables.

**Acceptance Criteria:**
- [ ] `screens/label-management-dialog.md` documents layout, component hierarchy, component→API mapping (all five label endpoints), all four states (Section 2.5 patterns), and interactions including the destructive delete confirmation with affected-task count
- [ ] `components.md` gains a LabelChip entry (inputs/outputs, variants for card vs picker use)
- [ ] `screens/project-board.md` documents chips on cards (max 3 + overflow), the toolbar label filter, the filtered-empty state with "Clear filter" CTA, and the deleted-while-filtered notice
- [ ] `screens/task-detail-panel.md` documents the Labels field with multi-select picker and the disable-at-10 tooltip
- [ ] `index.md` gains the Screen Inventory row and a Changelog entry

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/components.md - LabelChip inventory entry
- docs/ui-specification/screens/project-board.md - chips, filter dropdown, new states
- docs/ui-specification/screens/task-detail-panel.md - Labels field + picker
- docs/ui-specification/index.md - Screen Inventory row, Changelog

**Technical Notes:**
- The dialog is opened from the board toolbar and needs no new route; note the parent-layout relationship in the Screen Inventory row

---

### T-009: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create the reusable LabelChip component rendering a label's name on its accent-palette color, used by board cards, the task detail picker, and the Label Management Dialog.

**Rationale:**
Feature Brief Section 8 names LabelChip as a new shared component; centralizing it keeps chip contrast and truncation consistent across all three surfaces.

**Acceptance Criteria:**
- [ ] Renders the label name on the token's background with a per-token text color meeting WCAG 2.1 AA (4.5:1) for all 12 accent tokens
- [ ] Uses design tokens only (`caption` typography, `space-1` padding, accent CSS custom properties) — no hard-coded values
- [ ] Long names truncate with an ellipsis and expose the full name via `title`/aria-label
- [ ] Supports a compact variant for dense board cards

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component (CSS Modules)

**Technical Notes:**
- Map each accent token to a light or dark text color at build time (static lookup), since contrast is per-token by design
- Its visual treatment is approved via the Label Management Dialog mockup (T-010) before broad rollout

---

### T-010: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Implement the new Label Management Dialog screen — create, rename, recolor, and delete project labels — opened from the board toolbar. This adds a new user-facing screen: generate an HTML mockup of the Label Management Dialog for stakeholder approval first, per `.ai-framework/prompts/mockup-generation.md`, then implement against the approved mockup.

**Rationale:**
Implements the label-administration half of the feature (AC-1, AC-4, AC-5, AC-6 UI); Feature Brief Section 8 classifies work on this new screen as mockup-first.

**Acceptance Criteria:**
- [ ] Creating a label (name + swatch picker over the 12 accent tokens) shows it in the list immediately without a page reload
- [ ] A duplicate name shows an inline validation message next to the name field, driven by the API's 409 `conflict` response
- [ ] Rename/recolor persists and refreshes chips everywhere via TanStack Query invalidation of board and label queries
- [ ] Delete opens the shared `Dialog` in destructive mode stating the affected task count (from `taskCount`) and only deletes on explicit confirmation
- [ ] Loading, empty ("No labels yet" `EmptyState`), and error states follow index Section 2.5

**Dependencies:** T-006, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen (list, create form, edit, delete confirm)

**Technical Notes:**
- Color picker is swatch buttons over the existing accent tokens — no external color-picker dependency (Feature Brief Section 10)
- Reuse the shared `Dialog` component for both the container and the destructive delete confirmation

---

### T-011: Add Labels field with multi-select picker to Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to the Task Detail Panel with a multi-select picker showing LabelChip previews, saving via `PUT /api/v1/tasks/{id}/labels` and invalidating the board query so cards update without a reload.

**Rationale:**
Directly implements AC-2 (assign/remove from the panel, visible on the board without reload) and the Section 8 Task Detail Panel modification.

**Acceptance Criteria:**
- [ ] The picker lists the project's labels with chip previews; selecting/deselecting and applying persists the new set via `PUT /api/v1/tasks/{id}/labels`
- [ ] After saving, the board card behind the panel shows the updated chips without a page reload (query invalidation)
- [ ] With 10 labels assigned, further options are disabled and a tooltip explains the 10-label limit
- [ ] Save failures surface the standard inline error pattern with retry; the panel's existing fields are unaffected

**Dependencies:** T-006, T-008, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field, picker, mutation + invalidation

**Technical Notes:**
- Follows the panel's existing pattern of an approved layout (standard CRUD-style field addition), so no separate mockup is required
- Send the full label-id set on apply (replace semantics) rather than diffing add/remove calls

---

### T-012: Render label chips on task cards and add board label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to three LabelChips (plus a "+N" overflow indicator) on each TaskCard from the board response's `labels` array, and add a label filter dropdown to the BoardToolbar that refetches the board with `labelId`.

**Rationale:**
Implements AC-3 and the board half of AC-4; filtering stays server-side per Feature Brief Section 10 so results remain correct with pagination.

**Acceptance Criteria:**
- [ ] Task cards show up to 3 chips with a "+N" indicator when more are assigned; card data comes from the board response (no per-card fetches)
- [ ] Selecting a label in the toolbar dropdown refetches the board with `labelId` and shows only matching tasks; clearing the filter restores the full board
- [ ] A filter with zero matching tasks shows the standard `EmptyState` with a "Clear filter" action — never a blank board
- [ ] If the filtered label was deleted by another user, the refetch clears the filter and shows a notice
- [ ] Compact card variant stays single-line (chips hidden or collapsed per the updated screen shard)

**Dependencies:** T-007, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/components/task-card.tsx - chip row + overflow indicator
- src/ui/project-board.tsx - toolbar filter dropdown, filtered empty state, deleted-label notice

**Technical Notes:**
- Detect the deleted-filter case when the selected `labelId` no longer appears in the project's label list after a refetch
- Keep the filter in the board query key so TanStack Query caches filtered and unfiltered views separately, protecting the 300ms P95 filter round-trip

---

## Testing

### T-013: Write repository unit tests for label and task-label modules

**Type:** Testing
**Workflow:** standard

**Description:**
Add unit tests for the two new repository modules against the test database, covering uniqueness, the assignment rules, and cascade behavior.

**Rationale:**
CLAUDE.md requires a unit test per repository; these rules (AC-6, max-10, same-project, delete cascade) are the feature's core invariants.

**Acceptance Criteria:**
- [ ] Creating "urgent" when "Urgent" exists in the same project fails with the unique violation; the same name in another project succeeds
- [ ] `replaceForTask` rejects an 11-label set and a cross-project label without writing anything
- [ ] Deleting a label removes its `task_labels` rows and leaves tasks untouched; `assignedTaskCount` reflects assignments correctly
- [ ] `listByTaskIds` returns correct label sets for multiple tasks in one call

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - Label repository unit tests
- tests/db/task-label.test.ts (new) - TaskLabel repository unit tests

---

### T-014: Write API integration tests for label endpoints and board filter

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests for the labels router and extend the tasks endpoint tests for the `labelId` filter and the labels array in the board response.

**Rationale:**
CLAUDE.md requires a Supertest integration test per router; these tests verify the API-level behavior behind AC-1, AC-2, AC-3, AC-4, and AC-6.

**Acceptance Criteria:**
- [ ] All five label endpoints are covered happy-path with the correct envelope (`data`, plus `meta` on lists)
- [ ] Duplicate create/rename (including case-only variants) returns 409 `conflict`; invalid name length or non-palette color returns 400 `validation-error` with `fields`
- [ ] Replacing a task's labels with 11 ids or a cross-project id returns 400 `validation-error`; a valid set persists and is returned on the next fetch
- [ ] Board list with `labelId` returns only matching tasks with correct `meta.totalCount`; without it, the full board including each task's `labels` array
- [ ] Missing label/task ids return 404 `not-found`; missing token returns 401 `unauthorized`

**Dependencies:** T-006, T-007
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - `labelId` filter + labels-array assertions

---

### T-015: Write component tests for the label UI

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for the LabelChip, the Label Management Dialog, the panel picker, and the board filter behavior, with API calls mocked.

**Rationale:**
Verifies the UI halves of AC-1, AC-2, AC-3, and AC-5 (chips, picker limit, filter/empty state, delete confirmation) at the component level, mirroring `src/` per the test-location convention.

**Acceptance Criteria:**
- [ ] LabelChip renders name and token color for representative tokens and truncates long names
- [ ] Dialog: create shows the new label immediately; duplicate-name error renders inline; delete confirmation states the affected task count and calls DELETE only on confirm
- [ ] Panel picker disables selection at 10 labels with the explanatory tooltip and fires the replace mutation with the full set
- [ ] Board: filter selection renders only matching cards, clearing restores all; zero matches renders `EmptyState` with the "Clear filter" action

**Dependencies:** T-009, T-010, T-011, T-012
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/label-chip.test.tsx (new) - chip rendering + truncation
- tests/ui/label-management-dialog.test.tsx (new) - CRUD flows + delete confirmation
- tests/ui/task-detail-panel.test.tsx (new) - picker limit + mutation
- tests/ui/project-board.test.tsx (new) - filter, empty state, chips on cards

---

## Summary

**Feature:** FEAT-001 — Task Labels (TaskFlow v1.1)

**Total task count by type:**

| Type | Count | Tasks |
|------|-------|-------|
| Documentation | 3 | T-001, T-005, T-008 |
| Database | 1 | T-002 |
| Backend | 4 | T-003, T-004, T-006, T-007 |
| Frontend | 4 | T-009, T-010, T-011, T-012 |
| Testing | 3 | T-013, T-014, T-015 |
| **Total** | **15** | |

**Complexity distribution:** S: 2 (T-001, T-009) · M: 9 (T-002, T-003, T-004, T-005, T-007, T-008, T-011, T-013, T-015) · L: 4 (T-006, T-010, T-012, T-014) · XL: 0

**Critical path (longest dependency chain, 6 tasks):** T-001 → T-002 → T-003 → T-006 → T-010 → T-015. An equal-length parallel chain runs T-001 → T-002 → T-004 → T-007 → T-012 → T-015; spec tasks T-005/T-008 sit off the critical path and can proceed alongside T-002–T-004.

**Risks / open questions:**

- **Edit-rights enforcement** — label create/rename/delete is restricted to members with edit rights, but the auth service resolves rights externally; T-006 mirrors the existing `PATCH /api/v1/tasks/{id}` role handling. If that handling is coarser than expected, the restriction may need auth-service work outside this feature's scope.
- **`taskCount` on LabelDto** — the AC-5 confirmation needs the affected-task count *before* deletion; this plan sources it from the label list response (T-003/T-005). If label lists grow large this adds a GROUP BY to every list call — acceptable at current data volumes.
- **Concurrent edits** — renames are last-write-wins with no version checks, per Feature Brief Section 9; accepted, not mitigated.
- **Board payload growth** — including `labels` on every board task grows the response; the 300ms P95 filter NFR (Section 10) should be spot-checked on a 500-task board during T-007/T-012.

---

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label (name 1–30 chars + palette color); appears immediately in the project's label list | T-003, T-006, T-010, T-014 |
| AC-2: Assign/remove labels from the task detail panel; persists and shows on the board card without reload | T-004, T-006, T-011, T-014, T-015 |
| AC-3: Board filter by label shows only matching tasks; clearing restores the full board | T-007, T-012, T-014, T-015 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-006, T-010, T-012, T-014 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-003, T-006, T-010, T-015 |
| AC-6: Duplicate label name in the same project returns a validation error with an inline UI message | T-002, T-003, T-006, T-010, T-014 |
