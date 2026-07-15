# Task List: FEAT-001 — Task Labels

**Feature Brief:** FEAT-001 (docs/work-items/FEAT-001-task-labels.md) · **Target Version:** v1.1 · **Priority:** High

**Summary:** 13 tasks implement project-scoped task labels for TaskFlow: specification shards first (this project has no spec documentation yet — the entity, API, and UI shards named by the brief's impact tables are created here), then the migration and repository, the five label endpoints plus the board-query filter, the frontend (classified `mockup-first` because the Label Management Dialog and LabelChip are new UI), and a closing edge-case test pass. Board filtering stays server-side and labels ship inside the existing board tasks response, per the brief's constraints.

## Group 1: Specification Shards

### T-001: Create data-model spec shards for Label and TaskLabel

**Type:** Documentation

**Workflow:** standard

**Description:** Author the entity shards for the two new entities and the data-model index. `label.md` defines fields (id, project_id, name, color, timestamps), name uniqueness within a project (case-insensitive), color restricted to the 12 accent palette tokens, and delete semantics (cascades to assignments only, never to tasks). `task-label.md` defines the N:M join (task_id, label_id), the 10-labels-per-task maximum, and the rule that task and label must belong to the same project. The index gets Module Ownership and Relationships Overview entries for both entities (Project 1—N Label, Task N—M Label via TaskLabel).

**Rationale:** Brief Section 6 requires the new entity shards to exist before feature logic; this project has no `docs/data-model/` yet, so the shards and index are created from scratch as the persistent contract for T-004/T-005.

**Acceptance Criteria:**
- [ ] `label.md` documents name length 1–30, case-insensitive per-project uniqueness, and the 12-token palette constraint
- [ ] `task-label.md` documents the max-10-per-task rule and the same-project invariant
- [ ] Delete semantics state that removing a label deletes its assignments but never modifies tasks
- [ ] `docs/data-model/index.md` lists both entities under Module Ownership and shows the Project/Task/Label relationships

**Dependencies:** None

**Complexity:** S

**Files to Modify/Create:**
- `docs/data-model/entities/label.md` (new)
- `docs/data-model/entities/task-label.md` (new)
- `docs/data-model/index.md` (new)

### T-002: Create API spec shards for label endpoints and board filter

**Type:** Documentation

**Workflow:** standard

**Description:** Author `endpoints/labels.md` covering all five label endpoints from brief Section 7 — GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, PUT `/api/v1/tasks/{id}/labels` — with request/response bodies in the `{ "data": ... }` envelope, Zod-validated inputs (name 1–30 chars, color token, label-ID array ≤ 10), and error responses. Author `endpoints/tasks.md` documenting the board list endpoint with its new optional `labelId` query parameter and the `labels` array embedded in each task of the response. Create `docs/api-spec/index.md` with the Endpoint Summary rows and an Error Catalog defining `validation-error` (400), `not-found` (404), and `conflict` (409, duplicate label name) — per CLAUDE.md, no error code may be used without a catalog row.

**Rationale:** Brief Section 7 requires the labels endpoint shard before API work; the project has no `docs/api-spec/` yet, so the index and Error Catalog must also be created for the `conflict` and `validation-error` codes the routers in T-006/T-007 will throw.

**Acceptance Criteria:**
- [ ] All five label endpoints are specified with methods, paths, request/response schemas, and envelope format
- [ ] The board list spec documents `labelId` filtering and the embedded `labels` array (no per-card fetch)
- [ ] The Error Catalog defines `validation-error`, `not-found`, and `conflict` with status codes
- [ ] Endpoint Summary in `docs/api-spec/index.md` lists every new/modified route

**Dependencies:** T-001

**Complexity:** M

**Files to Modify/Create:**
- `docs/api-spec/endpoints/labels.md` (new)
- `docs/api-spec/endpoints/tasks.md` (new)
- `docs/api-spec/index.md` (new)

### T-003: Create UI spec shards — palette tokens, screens, and LabelChip

**Type:** Documentation

**Workflow:** standard

**Description:** Create `docs/ui-specification/index.md` with the Screen Inventory and a Section 2.1 defining the fixed 12-color accent palette tokens (each token paired with a chip text color meeting WCAG 2.1 AA 4.5:1 contrast). Author screen shards: `label-management-dialog.md` (new screen — create/rename/recolor/delete flows, palette swatch picker, delete confirmation stating the affected task count, inline duplicate-name error), plus `project-board.md` and `task-detail-panel.md` (documenting the modified board — up to 3 chips + "+N" overflow, toolbar single-label filter dropdown — and the detail panel's Labels multi-select picker). Add LabelChip to `components.md` as a shared component rendering label name + color.

**Rationale:** Brief Section 8 names these shards as the retrieval keys for UI work and requires the new Label Management Dialog screen shard plus the LabelChip component entry; brief Section 10 requires the palette tokens to live in ui-specification index Section 2.1, which does not exist yet in this project.

**Acceptance Criteria:**
- [ ] Section 2.1 defines exactly 12 accent palette tokens with AA-compliant chip text contrast documented
- [ ] `label-management-dialog.md` specifies all four label operations, the delete confirmation with affected-task count, and the inline duplicate-name message
- [ ] Board and detail-panel shards document chip overflow (3 + "+N"), the single-label filter dropdown, and the ≤10 picker behavior
- [ ] LabelChip appears in the shared component inventory and the dialog appears in the Screen Inventory

**Dependencies:** None

**Complexity:** M

**Files to Modify/Create:**
- `docs/ui-specification/index.md` (new)
- `docs/ui-specification/screens/label-management-dialog.md` (new)
- `docs/ui-specification/screens/project-board.md` (new)
- `docs/ui-specification/screens/task-detail-panel.md` (new)
- `docs/ui-specification/components.md` (new)

## Group 2: Data Model and Persistence

### T-004: Migration — labels and task_labels tables

**Type:** Database

**Workflow:** standard

**Description:** Add `migrations/002-labels.sql` creating `labels` (id, project_id FK → projects ON DELETE CASCADE, name varchar(30) NOT NULL, color NOT NULL with a CHECK against the 12 palette token values, created_at/updated_at) and `task_labels` (task_id FK → tasks ON DELETE CASCADE, label_id FK → labels ON DELETE CASCADE, composite primary key). Enforce case-insensitive per-project name uniqueness with a unique index on `(project_id, lower(name))`, and index `task_labels.label_id` so the board's label filter stays fast at 500-task scale.

**Rationale:** Persists the Label and TaskLabel entities from T-001. The `lower(name)` unique index makes the "Urgent" vs "urgent" edge case (brief Section 9) a database guarantee, and ON DELETE CASCADE on `task_labels.label_id` implements "deleting cascades to assignments only, never to tasks". The label_id index supports the 300ms P95 filter NFR.

**Acceptance Criteria:**
- [ ] Migration applies cleanly on top of `001-init.sql` and follows the `NNN-description.sql` naming convention
- [ ] Duplicate label names differing only by case are rejected by the unique index
- [ ] Deleting a label row removes its `task_labels` rows and leaves `tasks` rows untouched
- [ ] Color values outside the 12 palette tokens are rejected by the CHECK constraint

**Dependencies:** T-001

**Complexity:** M

**Files to Modify/Create:**
- `migrations/002-labels.sql` (new)

### T-005: Label repository module

**Type:** Database

**Workflow:** standard

**Description:** Create `src/db/label.ts` — the single home for all label SQL per CLAUDE.md convention 5. Functions: `listByProject`, `create`, `update` (rename/recolor, last-write-wins with no optimistic locking), `remove` (returns the count of affected tasks so the API can report it), `countTasksForLabel`, `getTaskLabels`, and `replaceTaskLabels(taskId, labelIds)` which validates that all labels belong to the task's project and that the set size is ≤ 10 before replacing assignments in a transaction. Duplicate-name inserts/updates surface the unique-index violation so the router can map it to `conflict`. Add repository unit tests against the test database.

**Rationale:** Implements the business rules from T-001's entity shards (max 10, same-project invariant, cascade semantics) at the data-access layer; routers never touch `pg` directly, so every rule the API needs must be exposed here first.

**Acceptance Criteria:**
- [ ] All label CRUD and assignment operations run through this module with no SQL elsewhere
- [ ] `replaceTaskLabels` rejects sets larger than 10 and label IDs from a different project
- [ ] `remove` deletes assignments, leaves tasks untouched, and returns the affected-task count
- [ ] Unit tests cover create, case-insensitive duplicate detection, replace, and delete-with-count

**Dependencies:** T-004

**Complexity:** M

**Files to Modify/Create:**
- `src/db/label.ts` (new)
- `tests/db/label.test.ts` (new)

## Group 3: Backend API

### T-006: Labels router — CRUD endpoints

**Type:** Backend

**Workflow:** standard

**Description:** Create `src/api/labels.ts` and mount it in `src/api/index.ts`. Routes: GET `/api/v1/projects/{projectId}/labels` (list with `meta` envelope), POST `/api/v1/projects/{projectId}/labels` (create; Zod: name 1–30 chars, color one of the 12 tokens), PUT `/api/v1/labels/{id}` (rename/recolor, last-write-wins), DELETE `/api/v1/labels/{id}` (returns the removed-assignment/affected-task count in `data` so the UI confirmation can display it). Duplicate names (case-insensitive) throw `ApiError` with catalog code `conflict` (409); validation failures map to `validation-error`; unknown IDs to `not-found`. Add a Supertest integration test for the router.

**Rationale:** Implements the four label-management endpoints from brief Section 7 against the T-002 spec, enabling AC-1 (create + immediate list), AC-4 (rename/recolor), AC-5 (delete with affected count), and AC-6 (duplicate → validation error). Concurrent renames resolve last-write-wins per brief Section 9.

**Acceptance Criteria:**
- [ ] Create returns the new label in the `data` envelope and it appears in the subsequent project list
- [ ] Duplicate name in the same project (any casing) returns 409 with code `conflict`; same name in another project succeeds
- [ ] Delete responds with the affected-task count and removes all assignments
- [ ] Concurrent renames apply last-write-wins; the later request's name persists
- [ ] Integration tests cover all four routes, validation failures, and error codes

**Dependencies:** T-002, T-005

**Complexity:** M

**Files to Modify/Create:**
- `src/api/labels.ts` (new)
- `src/api/index.ts`
- `tests/api/labels.test.ts` (new)

### T-007: Task label assignment endpoint

**Type:** Backend

**Workflow:** standard

**Description:** Add PUT `/api/v1/tasks/{id}/labels` to `src/api/tasks.ts`: accepts `{ "labelIds": [...] }` (Zod-validated array of IDs, max length 10), calls `replaceTaskLabels`, and returns the task's updated label list in the `data` envelope. An 11th label or a label from another project returns 400 `validation-error` with a `fields` entry explaining the limit. Extend the tasks router integration test.

**Rationale:** Implements the replace-set endpoint from brief Section 7 that AC-2 (assign/remove from the detail panel) depends on, and enforces the max-10 edge case from brief Section 9 server-side rather than trusting the picker.

**Acceptance Criteria:**
- [ ] Replacing the label set persists and the response contains the updated labels
- [ ] Submitting 11 label IDs returns `validation-error` and changes nothing
- [ ] Submitting a label ID from a different project returns `validation-error`
- [ ] Integration tests cover replace, empty-set removal, over-limit, and cross-project rejection

**Dependencies:** T-002, T-005

**Complexity:** M

**Files to Modify/Create:**
- `src/api/tasks.ts`
- `src/db/label.ts` (new)
- `tests/api/tasks.test.ts`

### T-008: Board query — embedded labels and server-side labelId filter

**Type:** Backend

**Workflow:** standard

**Description:** Modify the board list query in `src/db/task.ts` to aggregate each task's labels into the row (single query — e.g. a lateral/aggregated join — so initial board load stays one round-trip), and accept an optional `labelId` filter applied in SQL so pagination and `meta.totalCount` stay correct. Extend GET `/api/v1/projects/{projectId}/tasks` in `src/api/tasks.ts` with a Zod-validated optional `labelId` query parameter; an unknown `labelId` simply yields zero tasks.

**Rationale:** Brief Section 10 requires labels inside the existing board response (never fetched per card) and server-side filtering for pagination correctness; this is the backend for AC-3 and feeds the chips AC-2/AC-4 render. The single aggregated query plus the T-004 index targets the 300ms P95 NFR at 500 tasks.

**Acceptance Criteria:**
- [ ] Board response embeds each task's labels; label data adds no additional queries per task
- [ ] With `labelId` set, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count
- [ ] Omitting `labelId` returns the full board unchanged (backwards compatible)
- [ ] Integration tests cover filtered, unfiltered, zero-match, and paginated-filtered responses

**Dependencies:** T-005

**Complexity:** M

**Files to Modify/Create:**
- `src/db/task.ts`
- `src/api/tasks.ts`
- `tests/api/tasks.test.ts`

## Group 4: Frontend

### T-009: LabelChip shared component

**Type:** Frontend

**Workflow:** mockup-first

**Description:** Build `src/ui/components/label-chip.tsx` per the T-003 component spec: renders the label name on its palette color with the AA-compliant text color for each of the 12 tokens, truncates long names, and supports the small variant used on board cards. No new dependencies — palette tokens come from the ui-specification Section 2.1 values.

**Rationale:** LabelChip is the shared building block brief Section 8 calls out for board cards, the detail-panel picker, and the management dialog; building it first (mockup-first, since it is new UI) lets every later frontend task reuse one contrast-checked implementation.

**Acceptance Criteria:**
- [ ] Chip renders name + color for all 12 palette tokens with 4.5:1 text contrast
- [ ] Component is reused by board cards, the picker, and the dialog with no duplicated chip markup
- [ ] No new external dependency is introduced

**Dependencies:** T-003

**Complexity:** S

**Files to Modify/Create:**
- `src/ui/components/label-chip.tsx` (new)
- `tests/ui/components/label-chip.test.tsx` (new)

### T-010: Label Management Dialog

**Type:** Frontend

**Workflow:** mockup-first

**Description:** Build `src/ui/label-management-dialog.tsx` (new screen per the T-003 shard), opened from the board toolbar and composed from the shared `dialog.tsx`. Lists the project's labels; supports create (name input + 12-swatch palette picker), rename, recolor, and delete. Delete first fetches the affected-task count and shows a confirmation dialog stating it before calling DELETE. A 409 `conflict` response renders as an inline "name already exists" message on the form rather than a toast. TanStack Query mutations invalidate the label list and board tasks queries so every visible chip updates without a reload.

**Rationale:** Delivers the management UI for AC-1 (create appears immediately), AC-4 (rename/recolor propagate to cards via invalidation), AC-5 (confirmed delete stating affected count), and AC-6 (inline duplicate message), following the mockup-first workflow the brief mandates for the new screen.

**Acceptance Criteria:**
- [ ] Creating a label shows it in the dialog list immediately (AC-1)
- [ ] Rename/recolor updates every board card chip showing that label without a page reload (AC-4)
- [ ] Delete shows a confirmation stating how many tasks are affected and only proceeds on confirm (AC-5)
- [ ] Duplicate name shows an inline validation message next to the name field (AC-6)
- [ ] Color choice is limited to the 12 palette swatches — no free-form color input

**Dependencies:** T-003, T-006, T-009

**Complexity:** L

**Files to Modify/Create:**
- `src/ui/label-management-dialog.tsx` (new)
- `tests/ui/label-management-dialog.test.tsx` (new)

### T-011: Task detail panel — label picker

**Type:** Frontend

**Workflow:** mockup-first

**Description:** Add the "Labels" field to `src/ui/task-detail-panel.tsx` per the T-003 shard: a multi-select picker listing the project's labels as chip previews, assigning/removing via PUT `/api/v1/tasks/{id}/labels`. At 10 selected labels the picker disables further selection and shows an explanatory tooltip. Mutations invalidate the board tasks query so the card's chips update without a page reload.

**Rationale:** Implements AC-2 (assign/remove from the detail panel, persisted and visible on the board card without reload) and the client half of the 11th-label edge case from brief Section 9 — the server already rejects it via T-007; the picker prevents it ergonomically.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists and the board card reflects the change without a reload (AC-2)
- [ ] Picker disables selection at 10 labels and shows a tooltip explaining the limit
- [ ] Picker options render as LabelChip previews with name and color

**Dependencies:** T-007, T-009

**Complexity:** M

**Files to Modify/Create:**
- `src/ui/task-detail-panel.tsx`
- `tests/ui/task-detail-panel.test.tsx` (new)

### T-012: Project board — chips, filter dropdown, and empty state

**Type:** Frontend

**Workflow:** mockup-first

**Description:** Render up to 3 LabelChips per card in `src/ui/components/task-card.tsx` with a "+N" overflow indicator, reading labels from the board response (no per-card fetching). Add a single-select label filter dropdown to the `src/ui/project-board.tsx` toolbar that sets the `labelId` query parameter on the board query (server-side filtering). A zero-match filter shows the standard `empty-state.tsx` with a "Clear filter" action instead of a blank board. If a board/label refetch reveals the filtered label was deleted (e.g. by another user), the filter clears automatically and a notice is shown.

**Rationale:** Completes AC-3 (filter + clear restores the full board) and the board half of AC-2/AC-4, and covers two Section 9 edge cases: zero-matching-tasks empty state and filtered-label-deleted-by-another-user. Classified mockup-first because the toolbar filter and chip row are new UI on the modified Project Board screen.

**Acceptance Criteria:**
- [ ] Cards show at most 3 chips plus a "+N" indicator when a task has more labels
- [ ] Selecting a label shows only matching tasks via the `labelId` parameter; clearing restores the full board (AC-3)
- [ ] Zero-match filter renders the empty state with a working "Clear filter" action
- [ ] When the active filter's label no longer exists after a refetch, the filter clears and a notice appears
- [ ] Chips come from the board response — no additional request per card

**Dependencies:** T-006, T-008, T-009

**Complexity:** L

**Files to Modify/Create:**
- `src/ui/project-board.tsx`
- `src/ui/components/task-card.tsx`
- `src/ui/components/empty-state.tsx`
- `tests/ui/project-board.test.tsx` (new)

## Group 5: Testing

### T-013: Edge-case and acceptance regression suite

**Type:** Testing

**Workflow:** standard

**Description:** Close the loop on the brief's Section 9 edge cases and Section 5 acceptance criteria with end-to-end API assertions: case-insensitive duplicate rejection ("Urgent" vs "urgent"), 11th-label rejection, delete-with-assignments returning the affected count while tasks survive, zero-match filtered board returning an empty page with correct `meta`, concurrent rename last-write-wins, and filtered list correctness under pagination. Verify the board response embeds labels in a single query (guard against per-card N+1) as a proxy for the 300ms P95 constraint.

**Rationale:** Brief Section 13 requires every edge case addressed and every AC covered; this suite pins the behaviors that span multiple tasks (repository + router + query) so regressions surface in CI rather than on the board.

**Acceptance Criteria:**
- [ ] Every Section 9 edge case has at least one automated test
- [ ] Tests assert AC-1 through AC-6 behaviors at the API level
- [ ] A test guards that board label data is fetched in the board query, not per task

**Dependencies:** T-006, T-007, T-008

**Complexity:** M

**Files to Modify/Create:**
- `tests/api/labels.test.ts` (new)
- `tests/api/tasks.test.ts`
- `tests/db/label.test.ts` (new)

## Acceptance Criteria Coverage

| AC-1 | T-005, T-006, T-010 |
| AC-2 | T-007, T-011, T-012 |
| AC-3 | T-008, T-012, T-013 |
| AC-4 | T-006, T-010, T-012 |
| AC-5 | T-005, T-006, T-010 |
| AC-6 | T-004, T-006, T-010 |
