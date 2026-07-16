# FEAT-001 — Task Labels: Implementation Task List

> **Work item:** `docs/work-items/FEAT-001-task-labels.md` (FEAT-001, target v1.1)
> **Schema:** canonical task schema from `prompts/base-template.md`; procedure per `prompts/feature-tasks.md`.
> All file paths are relative to the project root; files that do not exist yet are suffixed `(new)`.

---

## Foundation

### T-001: Author Label and TaskLabel data-model shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create entity shards for the new `Label` and `TaskLabel` entities following the data-model conventions (UUID `id` primary key, `created_at`/`updated_at` timestamptz, snake_case naming, explicit varchar limits). Update the data-model index's Module Ownership and Relationships Overview tables plus the Changelog, and add the new N:M relationship row to the existing Task shard so shard and index stay in sync.

**Rationale:**
Feature Brief Section 6 requires the new entity shards to exist before feature logic; the data-model index's usage notes require ownership and relationship entries for every new entity.

**Acceptance Criteria:**
- [ ] `entities/label.md` defines fields (`project_id` FK, `name` varchar(30), `color` restricted to the 12 accent tokens) and rules: per-project case-insensitive name uniqueness; deletion cascades to assignments only, never to tasks
- [ ] `entities/task-label.md` defines the join entity with the max-10-labels-per-task rule and the same-project assignment rule
- [ ] `docs/data-model/index.md` lists both new entities in Module Ownership and Relationships Overview, with a Changelog row
- [ ] `entities/task.md` Relationships table gains the N:M link to Label via `task_labels`

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity shard (fields, indexes, business rules)
- docs/data-model/entities/task-label.md (new) - TaskLabel join-entity shard
- docs/data-model/index.md - Module Ownership + Relationships Overview rows, Changelog entry
- docs/data-model/entities/task.md - add relationship row for labels

---

### T-002: Author labels API spec shard and update endpoint summary

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `endpoints/labels.md` specifying the five label endpoints from Feature Brief Section 7 — GET/POST `/api/v1/projects/{projectId}/labels`, PUT and DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` (replace set) — with LabelDto, response envelopes, and Error Catalog codes. Add the new rows to the index's Endpoint Summary, and document the new optional `labelId` query parameter and embedded `labels` array in the tasks shard.

**Rationale:**
Section 7 requires the endpoint shard before API implementation, and the API index's Endpoint Summary doubles as the shard directory, so it must gain a row per new endpoint.

**Acceptance Criteria:**
- [ ] `endpoints/labels.md` documents all five endpoints with request/response bodies and status codes from the Error Catalog (409 `conflict` on duplicate name; 400 `validation-error` for bad name/color or >10 labels)
- [ ] LabelDto includes a per-label assigned-task count so the delete confirmation can state how many tasks are affected
- [ ] `docs/api-spec/index.md` Endpoint Summary gains one row per new endpoint plus a Changelog entry
- [ ] `endpoints/tasks.md` documents the optional `labelId` query parameter and the `labels: LabelDto[]` field on TaskDto

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - label resource shard (all five endpoints)
- docs/api-spec/index.md - Endpoint Summary rows, Changelog entry
- docs/api-spec/endpoints/tasks.md - labelId parameter + labels array on TaskDto

---

### T-003: Author Label Management Dialog UI spec and update UI inventory

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the screen shard for the new Label Management Dialog (layout sketch, component hierarchy, component→API mapping, all four states, interactions) and add its Screen Inventory row and Changelog entry to the UI index. Document the shared LabelChip component in `components.md`, and update the Project Board and Task Detail Panel shards to reflect card chips, the label filter, and the labels picker.

**Rationale:**
Feature Brief Section 8 requires the new screen shard, its inventory row, and the LabelChip inventory entry before frontend work; the UI index's usage notes require modified screens' shards to stay current.

**Acceptance Criteria:**
- [ ] `screens/label-management-dialog.md` covers create/rename/recolor/delete flows, the duplicate-name inline error, and the destructive delete confirmation stating the affected task count
- [ ] `components.md` documents LabelChip (inputs/outputs, variants, accent-token coloring with WCAG 2.1 AA text contrast)
- [ ] `screens/project-board.md` reflects card chips (max 3 + overflow), the toolbar filter dropdown, and the filtered empty state; `screens/task-detail-panel.md` reflects the Labels picker field
- [ ] `docs/ui-specification/index.md` gains the Screen Inventory row and a Changelog entry

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen shard
- docs/ui-specification/index.md - Screen Inventory row, Changelog entry
- docs/ui-specification/components.md - LabelChip inventory entry
- docs/ui-specification/screens/project-board.md - chips, filter dropdown, filtered states
- docs/ui-specification/screens/task-detail-panel.md - Labels picker field

---

### T-004: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Write `migrations/002-labels.sql` creating `labels` (`id` UUID PK, `project_id` FK → projects ON DELETE CASCADE, `name` varchar(30) NOT NULL, `color` varchar(16) NOT NULL, timestamps) and `task_labels` (`id` UUID PK, `task_id` and `label_id` FKs with ON DELETE CASCADE, timestamps). Add the uniqueness and filtering indexes required by the business rules and the board filter.

**Rationale:**
The Label and TaskLabel entities from Feature Brief Section 6 need persistent storage before any repository or API work, following the plain-SQL migration convention.

**Acceptance Criteria:**
- [ ] Tables follow database conventions: snake_case plural names, UUID `id` PK, `created_at`/`updated_at` timestamptz, explicit varchar limits
- [ ] Unique index on `(project_id, lower(name))` enforces case-insensitive per-project label-name uniqueness
- [ ] `task_labels` has a UNIQUE constraint on `(task_id, label_id)` and an index on `label_id` to support the board filter join
- [ ] Deleting a project cascades to its labels; deleting a task or a label cascades to `task_labels` rows only — tasks are never deleted by label operations

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - labels + task_labels tables, indexes, FKs

**Technical Notes:**
- CHECK constraint restricting `color` to the 12 accent-palette tokens keeps invalid values out even outside the API path
- The max-10-labels-per-task rule cannot be a simple CHECK; it is enforced transactionally in the repository (T-005)

---

### T-005: Implement label and task-label repository modules

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` (list with per-label task counts, create, rename/recolor, delete) and `src/db/task-label.ts` (replace a task's label set, fetch labels for a set of task ids) — one repository module per entity, with all SQL confined to `src/db/`. The replace operation runs in a single transaction and enforces the max-10 and same-project rules.

**Rationale:**
The data-access convention requires SQL to live only in repository modules; the routers in T-006/T-007/T-008 build on these functions.

**Acceptance Criteria:**
- [ ] Label list query returns each label with its assigned-task count (drives the AC-5 confirmation copy)
- [ ] Create and rename surface the unique-violation on `(project_id, lower(name))` distinctly so routers can map it to 409 `conflict`
- [ ] Replace-set rejects more than 10 labels and label ids that do not belong to the task's project, atomically
- [ ] No router touches `pg` directly — these modules own all label SQL

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - Label repository (CRUD + counts)
- src/db/task-label.ts (new) - assignment repository (transactional replace-set, batch fetch)

---

## Backend

### T-006: Build label CRUD router

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET and POST `/api/v1/projects/{projectId}/labels`, PUT `/api/v1/labels/{id}`, and DELETE `/api/v1/labels/{id}` per the labels spec shard, and mount it in `src/api/index.ts`. Validate bodies with Zod (name 1–30 chars after trimming; color one of the 12 accent tokens) and wrap every response in the standard envelope.

**Rationale:**
Feature Brief Section 7 defines these endpoints as the backend surface for label management (AC-1, AC-4, AC-5, AC-6).

**Acceptance Criteria:**
- [ ] POST returns the created label; a duplicate name in the same project (case-insensitive, e.g. "Urgent" vs "urgent") returns 409 `conflict` naming the `name` field
- [ ] PUT renames/recolors and returns the updated label; concurrent renames resolve last-write-wins, stale clients pick up the new name on next refetch
- [ ] DELETE removes the label and all its assignments (cascade) without touching tasks, and returns a success envelope
- [ ] Invalid name/color/UUID returns 400 `validation-error` with `fields`; unknown label or project returns 404 `not-found`; list responses include `meta`
- [ ] List is visible to any project member; create/rename/recolor/delete require edit rights, mirroring the existing PATCH task authorization

**Dependencies:** T-002, T-005
**Complexity:** L

**Files to Modify/Create:**
- src/api/labels.ts (new) - label router (4 routes + Zod schemas + ApiError mapping)
- src/api/index.ts - mount the labels router

**Technical Notes:**
- GET list includes per-label task counts so the delete confirmation (AC-5) needs no extra round-trip
- Throw `ApiError` and let `src/api/errors.ts` serialize; never invent codes outside the Error Catalog

---

### T-007: Add replace-labels endpoint on tasks

**Type:** Backend
**Workflow:** standard

**Description:**
Add PUT `/api/v1/tasks/{id}/labels` to `src/api/tasks.ts`, accepting `{ labelIds: UUID[] }` and replacing the task's label set via the transactional repository operation from T-005. Return the updated task with its embedded labels in the standard envelope.

**Rationale:**
Feature Brief Section 7 specifies replace-set semantics for task label assignment, backing the detail-panel picker (AC-2).

**Acceptance Criteria:**
- [ ] A valid request atomically replaces the set and returns the TaskDto including `labels`
- [ ] More than 10 label ids returns 400 `validation-error` (11th-label edge case); label ids from another project return 400 `validation-error`
- [ ] Unknown task id returns 404 `not-found`; an empty array is valid and clears all labels

**Dependencies:** T-002, T-005
**Complexity:** M

**Files to Modify/Create:**
- src/api/tasks.ts - add PUT /api/v1/tasks/{id}/labels route with Zod schema

---

### T-008: Embed labels in board response and add labelId filter

**Type:** Backend
**Workflow:** standard

**Description:**
Extend the board list query in `src/db/task.ts` to aggregate each task's labels in a single round-trip (no per-card fetches) and accept an optional label filter applied before pagination. Extend GET `/api/v1/projects/{projectId}/tasks` in `src/api/tasks.ts` with a Zod-validated optional `labelId` query parameter, and include `labels` on TaskDto for both the list and single-task endpoints.

**Rationale:**
Section 10 constraints require labels in the existing board response (initial load must not slow down) and server-side filtering so results stay correct with pagination (AC-3).

**Acceptance Criteria:**
- [ ] Board response embeds `labels: LabelDto[]` per task with no N+1 queries
- [ ] With `labelId`, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count; omitting the parameter restores the full board
- [ ] A malformed `labelId` returns 400 `validation-error`; a valid-but-unknown `labelId` returns an empty page, not an error
- [ ] The filtered query uses the `task_labels.label_id` index; filter round-trip stays under the 300ms P95 NFR for 500-task boards

**Dependencies:** T-002, T-005
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - label aggregation join + optional label filter
- src/api/tasks.ts - labelId query parameter, labels field in DTO mapping

**Technical Notes:**
- Aggregate labels via LEFT JOIN + `json_agg` (or one batched IN-list query) — keep board load a single round-trip
- Filter with EXISTS on `task_labels` so pagination and `totalCount` stay correct server-side

---

## Frontend

### T-009: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create `src/ui/components/label-chip.tsx` rendering a label's name on its accent-token background, with a compact variant for dense contexts and a removable variant (accessible remove button) for the picker. Use design-token CSS custom properties only — no hard-coded colors and no new dependencies.

**Rationale:**
Feature Brief Section 8 defines LabelChip as a new shared component reused by board cards, the detail panel picker, and the management dialog.

**Acceptance Criteria:**
- [ ] Renders name + color for each of the 12 accent tokens with per-token text color meeting WCAG 2.1 AA contrast (4.5:1)
- [ ] Uses caption typography and `space-1` padding per the design system; long names truncate with ellipsis and expose the full name via an accessible label
- [ ] Removable variant fires an `onRemove` output and is keyboard-operable

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component (default, compact, removable variants)

---

### T-010: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
New user-facing screen — the Label Management Dialog needs an HTML mockup generated per `.ai-framework/prompts/mockup-generation.md` and stakeholder approval before implementation. Then build `src/ui/label-management-dialog.tsx` on the shared `Dialog` component: list labels with chip previews and task counts, create with name input plus 12-token palette picker, inline rename, recolor, and delete; open it from a new board-toolbar button.

**Rationale:**
Feature Brief Section 8 lists the Label Management Dialog as a new screen and directs that related frontend tasks be classified `mockup-first` (AC-1, AC-4, AC-5, AC-6).

**Acceptance Criteria:**
- [ ] Creating a label makes it appear in the list immediately (AC-1); a duplicate name shows the 409 `conflict` response as an inline message next to the name field (AC-6)
- [ ] Rename and recolor persist via PUT and invalidate the labels and board queries so every visible card updates (AC-4)
- [ ] Delete uses the destructive Dialog variant and states the affected task count before confirming; confirming removes the label everywhere without touching tasks (AC-5)
- [ ] All four states handled per the design system: loading skeleton, "No labels yet" EmptyState with create CTA, inline error banner with retry

**Dependencies:** T-003, T-006, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen (list, create, rename, recolor, delete)
- src/ui/project-board.tsx - toolbar button that opens the dialog

**Technical Notes:**
- Mockup must cover the list, create form, palette picker, rename-in-place, and delete confirmation before any code is written
- Color picker is built from the accent tokens in `docs/ui-specification/index.md` Section 2.1 — no external color-picker dependency

---

### T-011: Add labels picker to Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to `src/ui/task-detail-panel.tsx` with a multi-select picker showing chip previews; every selection change calls PUT `/api/v1/tasks/{id}/labels` with the full set. Invalidate the board tasks query so card chips update without a page reload. This extends an existing form screen following its established field pattern, so no mockup is required.

**Rationale:**
Feature Brief Section 8 adds label assignment to the Task Detail Panel; AC-2 requires changes to persist and appear on the board card without reload.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists and is reflected on the board card without a page reload (AC-2)
- [ ] The picker disables further selection at 10 labels and shows an explanatory tooltip (11th-label edge case)
- [ ] Options come from the project labels query and render as LabelChips; loading and error states follow the design-system state patterns

**Dependencies:** T-007, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - Labels field with multi-select chip picker wired to PUT

---

### T-012: Render board label chips and filter dropdown

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 LabelChips per card with a "+N" overflow indicator in `src/ui/components/task-card.tsx`, and add a single-select label filter dropdown to the board toolbar in `src/ui/project-board.tsx` that passes `labelId` to the board query. Handle the filtered-empty and filtered-label-deleted cases. Chips reuse the approved TaskCard pattern and design-system tokens, so this stays `standard` rather than `mockup-first`.

**Rationale:**
Feature Brief Section 8 modifies the Project Board with chips and a filter; AC-3 requires single-label server-side filtering with a clear-filter path.

**Acceptance Criteria:**
- [ ] Default card variant shows up to 3 chips plus a "+N" indicator when more are assigned; the compact variant remains title-only
- [ ] Selecting a label filters the board via the server-side `labelId` parameter; clearing the filter restores the full board (AC-3)
- [ ] A filter with zero matching tasks shows the EmptyState with a "Clear filter" action — never a blank board
- [ ] If the filtered label was deleted by another user, the board refetch clears the filter and shows a notice

**Dependencies:** T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/components/task-card.tsx - chip row with overflow indicator
- src/ui/project-board.tsx - filter dropdown, labelId in board query, filtered empty/notice states

---

## Testing

### T-013: Write repository unit tests for labels

**Type:** Testing
**Workflow:** standard

**Description:**
Unit-test the new repository modules and the extended board query against the test database, mirroring `src/` under `tests/` per the test-location convention.

**Rationale:**
The conventions require a unit test per repository; the label business rules (uniqueness, max-10, same-project, cascades) live in this layer.

**Acceptance Criteria:**
- [ ] `label.ts`: create, list-with-counts, rename, recolor, delete; case-insensitive duplicate ("Urgent" vs "urgent") is rejected
- [ ] `task-label.ts`: replace-set is atomic; max-10 and cross-project violations are rejected; deleting a task or label removes only assignment rows
- [ ] `task.ts` board query: labels aggregate correctly per task; `labelId` filtering with pagination returns correct rows and counts

**Dependencies:** T-005, T-008
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - assignment repository unit tests
- tests/db/task.test.ts (new) - board query aggregation + filter tests

---

### T-014: Write API integration tests for label endpoints

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration coverage for the labels router, the replace-labels endpoint, and the filtered board list, extending the existing tasks API test file for the modified endpoints.

**Rationale:**
Every router gets a Supertest integration test per the conventions; these tests verify the API halves of AC-1 through AC-6 including error paths.

**Acceptance Criteria:**
- [ ] Label CRUD happy paths return enveloped responses; the list includes `meta` and per-label task counts (AC-1)
- [ ] Duplicate name returns 409 `conflict`; invalid name/color returns 400 `validation-error` with `fields`; unknown ids return 404 (AC-6)
- [ ] PUT replace-labels persists and returns embedded labels (AC-2); 11 labels and cross-project labels return 400
- [ ] Board GET with `labelId` returns only matching tasks with correct `totalCount`, and the full board without it (AC-3); after label rename or delete, subsequent board responses reflect it (AC-4, AC-5)

**Dependencies:** T-006, T-007, T-008
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - replace-labels and labelId filter cases

---

### T-015: Write UI component tests for label flows

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for the new label UI, mirroring `src/ui/` under `tests/ui/`, covering the chip, the management dialog, the panel picker, and the board filter behaviors.

**Rationale:**
The UI carries the user-visible halves of AC-2, AC-3, AC-5, and AC-6 plus several Section 9 edge cases; component tests are the project's frontend verification level (no e2e harness exists).

**Acceptance Criteria:**
- [ ] LabelChip renders all 12 accent tokens with the AA-contrast text-color mapping; TaskCard shows at most 3 chips plus a correct "+N" overflow
- [ ] Dialog flows: create, inline duplicate-name error (AC-6), and delete confirmation stating the affected task count (AC-5)
- [ ] Panel picker disables at 10 labels with a tooltip and triggers board-query invalidation on change (AC-2)
- [ ] Board filter: zero-match state shows "Clear filter" EmptyState; deleted-filtered-label path clears the filter and shows a notice (AC-3)

**Dependencies:** T-010, T-011, T-012
**Complexity:** L

**Files to Modify/Create:**
- tests/ui/label-chip.test.tsx (new) - chip rendering + contrast mapping tests
- tests/ui/label-management-dialog.test.tsx (new) - dialog flow tests
- tests/ui/task-detail-panel.test.tsx (new) - picker behavior tests
- tests/ui/project-board.test.tsx (new) - chips, filter, empty/notice state tests

---

## Summary

**Feature:** FEAT-001 — Task Labels (Feature Brief: `docs/work-items/FEAT-001-task-labels.md`).

**Task count by type:** Documentation 3 (T-001–T-003) · Database 1 (T-004) · Backend 4 (T-005–T-008) · Frontend 4 (T-009–T-012) · Testing 3 (T-013–T-015) — **15 tasks total**.

**Complexity distribution:** S ×3 (T-001, T-002, T-009) · M ×7 (T-003, T-004, T-005, T-007, T-008, T-011, T-013) · L ×5 (T-006, T-010, T-012, T-014, T-015) · XL ×0.

**Critical path:** T-001 → T-004 → T-005 → T-006 → T-010 → T-015 (6 tasks; the parallel chain T-001 → T-004 → T-005 → T-008 → T-012 → T-015 is equally long — the mockup approval loop in T-010 is the schedule risk).

**Risks / open questions:**

- The project has no e2e test harness (Vitest + Supertest only). Acceptance criteria are verified via API integration plus component tests; introducing an e2e framework would add a new dependency beyond the brief's requirements, so it is flagged here rather than added.
- AC-6 calls a duplicate name a "validation error" while the API impact table and Error Catalog specify 409 `conflict`. Tasks follow the Error Catalog (409), with the UI presenting it as an inline validation message — confirm this reading at review.
- `task_labels` is specified with a UUID `id` primary key plus a UNIQUE `(task_id, label_id)` constraint to honor the "PK column named `id`" convention; if a composite PK is preferred for the join table, adjust T-004 before implementation.
- Edit-rights enforcement for label mutations relies on the external auth service's role resolution, mirroring the existing PATCH `/api/v1/tasks/{id}` behavior — no new permission model is introduced.

---

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label (name 1–30 chars + palette color); it immediately appears in the project's label list | T-006, T-010, T-014 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and appear on the board card without reload | T-007, T-011, T-014, T-015 |
| AC-3: Selecting a label in the board filter shows only matching tasks; clearing restores the full board | T-008, T-012, T-014, T-015 |
| AC-4: Renaming or recoloring a label updates every task card displaying it | T-006, T-010, T-012, T-014 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-005, T-006, T-010, T-014, T-015 |
| AC-6: Duplicate label name within a project returns a validation error with an inline UI message | T-006, T-010, T-014, T-015 |
