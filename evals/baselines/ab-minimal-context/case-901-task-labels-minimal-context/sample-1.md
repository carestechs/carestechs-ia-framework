# Task List — FEAT-001: Task Labels

**Source work item:** `docs/work-items/FEAT-001-task-labels.md` (Feature Brief FEAT-001, target v1.1)

**Summary:** 13 tasks implementing project-scoped labels for TaskFlow: documentation shards for the two new entities and five new endpoints first (the project has no spec docs yet, so the referenced shard files are all new), then the database migration and repositories, then the Express API, then the React UI (mockup-first for the new Label Management Dialog and related frontend work). Scope is limited to Section 4.1 of the brief — no global labels, no automation, no custom hex colors, no multi-label filter combinations.

---

### TASK-001: Document the Label and TaskLabel entities

- **Type:** Documentation
- **Workflow:** standard
- **Description:** Create the data-model shards for the two new entities. `label.md` records fields (id, project_id, name 1–30 chars, color as one of the 12 accent palette tokens, timestamps) and business rules: name unique within a project (case-insensitive), color restricted to palette tokens, delete cascades to assignments only — never to tasks. `task-label.md` records the N:M join between tasks and labels, the max of 10 labels per task, and the rule that a label may only be assigned to a task in the same project. The project has no `docs/data-model/` directory yet, so also create `docs/data-model/index.md` with Module Ownership and Relationships Overview entries for both entities.
- **Rationale:** Work item Section 6 requires the new-entity shards to exist before feature logic is built; this project currently has no data-model documentation at all.
- **Acceptance Criteria:**
  - Both entity shards exist and state every business rule from Section 6 of the brief (case-insensitive uniqueness, palette-token color, cascade-to-assignments-only, max 10 per task, same-project assignment).
  - `docs/data-model/index.md` lists both entities with ownership and relationship entries.
- **Dependencies:** None
- **Complexity:** S
- **Files to Modify/Create:**
  - `docs/data-model/entities/label.md` (new)
  - `docs/data-model/entities/task-label.md` (new)
  - `docs/data-model/index.md` (new)

### TASK-002: Migration for `labels` and `task_labels` tables

- **Type:** Database
- **Workflow:** standard
- **Description:** Add `migrations/002-task-labels.sql`. `labels`: id primary key, `project_id` FK to projects (ON DELETE CASCADE), `name` (length 1–30 enforced by CHECK), `color` (CHECK constraint restricting to the 12 accent palette tokens), timestamps, and a unique index on `(project_id, lower(name))` for case-insensitive uniqueness. `task_labels`: `task_id` FK to tasks (ON DELETE CASCADE), `label_id` FK to labels (ON DELETE CASCADE), composite primary key `(task_id, label_id)`, plus an index on `label_id` to keep board filtering fast. The max-10-labels-per-task rule is enforced at the application layer (TASK-003), not in the schema. Tables and columns are snake_case per project conventions.
- **Rationale:** Section 6 introduces both entities. Enforcing uniqueness in the database (not just the API) makes the duplicate-name rule (AC-6) reliable under concurrent requests, and FK cascade from labels implements "deleting cascades to assignments only, never to tasks" (AC-5).
- **Acceptance Criteria:**
  - Migration applies cleanly on a database at `001-init.sql`.
  - Inserting two labels in one project whose names differ only by case ("Urgent" vs "urgent") violates the unique index.
  - Deleting a label removes its `task_labels` rows and leaves the tasks themselves untouched.
- **Dependencies:** TASK-001
- **Complexity:** M
- **Files to Modify/Create:**
  - `migrations/002-task-labels.sql` (new)

### TASK-003: Label repository module

- **Type:** Backend
- **Workflow:** standard
- **Description:** Create `src/db/label.ts` (one repository per entity; SQL lives only here). Functions: `listByProject` (each label including its assigned-task count, which the delete confirmation dialog needs), `create` (surfacing the unique-index violation as a detectable conflict error), `update` (rename/recolor), `remove` (returning the number of tasks that carried the label), and `replaceTaskLabels(taskId, labelIds)` which validates that every label belongs to the task's project and that the set contains at most 10 labels before replacing the assignments transactionally.
- **Rationale:** Convention 5 — routers never touch `pg` directly; all label SQL belongs in one repository module. Returning task counts from the repository is what makes AC-5's "states how many tasks are affected" possible without extra queries in the router.
- **Acceptance Criteria:**
  - Create/update/delete and `replaceTaskLabels` behave per the Section 6 business rules.
  - A case-insensitive duplicate name surfaces a conflict error the router can map to HTTP 409.
  - Assigning an 11th label or a label from another project is rejected.
  - `listByProject` returns each label with its assigned-task count.
- **Dependencies:** TASK-002
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/db/label.ts` (new)

### TASK-004: Board query — embed labels and add optional label filter

- **Type:** Backend
- **Workflow:** standard
- **Description:** Modify `src/db/task.ts` so the board list query returns each task's labels aggregated in the same query (e.g., LEFT JOIN on `task_labels`/`labels` with `json_agg`) — labels ride along in the existing board tasks response rather than being fetched per card — and accepts an optional `labelId` parameter applied in SQL so filtering stays server-side and correct under pagination (filtered `totalCount` included).
- **Rationale:** Section 10 constraints: initial board load must not slow down (no per-card fetches) and filtering must remain server-side so paginated results stay correct.
- **Acceptance Criteria:**
  - One query returns board tasks with their labels; no N+1 per-card label queries.
  - Passing `labelId` returns only tasks carrying that label, with pagination metadata reflecting the filtered count.
  - With the `label_id` index from TASK-002, the filtered query supports the sub-300ms P95 round-trip target on boards up to 500 tasks.
- **Dependencies:** TASK-002
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/db/task.ts`

### TASK-005: API spec shards for the label endpoints

- **Type:** Documentation
- **Workflow:** standard
- **Description:** Create `docs/api-spec/endpoints/labels.md` documenting all five label endpoints from Section 7 (GET and POST `/api/v1/projects/{projectId}/labels`, PUT and DELETE `/api/v1/labels/{id}`, PUT `/api/v1/tasks/{id}/labels`) with request/response envelopes (`{ "data": ... }`, list `meta`) and error cases. The project has no `docs/api-spec/` directory yet, so also create `docs/api-spec/index.md` with Endpoint Summary rows for the five new endpoints plus the modified GET `/api/v1/projects/{projectId}/tasks` (`labelId` query parameter), and Error Catalog rows for every code the feature uses: `validation-error` (bad name length, non-palette color, 11th label, cross-project assignment) and `conflict` (409, duplicate label name).
- **Rationale:** Work item Section 7 requires the endpoint shard before frontend integration, and convention 3 forbids using an error code without a catalog row — the catalog must exist before TASK-006 returns `conflict`.
- **Acceptance Criteria:**
  - All six endpoint rows (five new, one modified) are documented with envelopes and error cases.
  - The Error Catalog defines `validation-error` and `conflict` before any router uses them.
- **Dependencies:** TASK-001
- **Complexity:** S
- **Files to Modify/Create:**
  - `docs/api-spec/endpoints/labels.md` (new)
  - `docs/api-spec/index.md` (new)

### TASK-006: Labels router

- **Type:** Backend
- **Workflow:** standard
- **Description:** Create `src/api/labels.ts` implementing the five endpoints from Section 7 and mount it in `src/api/index.ts`. Zod schemas defined next to the handlers validate: name 1–30 chars, color is one of the 12 palette tokens, and the PUT `/tasks/{id}/labels` body is an array of at most 10 unique label IDs. Success responses use the `{ "data": ... }` envelope (list adds `meta`); failures throw `ApiError` with catalog codes — duplicate name maps to 409 `conflict`, all validation failures to `validation-error`. PUT `/api/v1/labels/{id}` replaces name/color with no version check, giving last-write-wins semantics for concurrent renames (Section 9). GET returns each label with its assigned-task count (from TASK-003) so the UI can populate the delete confirmation.
- **Rationale:** Section 7 API surface, implemented per conventions 2–4 (envelope, error catalog, Zod validation). API tasks must precede frontend integration.
- **Acceptance Criteria:**
  - All five endpoints behave per the spec shard; responses never expose raw database rows.
  - Creating a duplicate name (case-insensitive) returns 409 with the `conflict` error envelope (AC-6).
  - Submitting 11 labels for a task returns `validation-error` (Section 9 edge case).
  - Deleting a label removes all its assignments and returns success; the label list reflects per-label task counts (AC-5 support).
- **Dependencies:** TASK-003, TASK-005
- **Complexity:** L
- **Files to Modify/Create:**
  - `src/api/labels.ts` (new)
  - `src/api/index.ts`

### TASK-007: Tasks router — `labelId` filter parameter

- **Type:** Backend
- **Workflow:** standard
- **Description:** Modify `src/api/tasks.ts`: extend the board list endpoint's query-parameter Zod schema with an optional `labelId`, pass it through to the repository (TASK-004), and serialize each task's embedded labels as camelCase JSON in the existing `{ data, meta }` envelope. `meta.totalCount` reflects the filtered count.
- **Rationale:** Section 7 marks GET `/api/v1/projects/{projectId}/tasks` as modified; server-side filtering is a Section 10 constraint.
- **Acceptance Criteria:**
  - `?labelId=` narrows results to tasks carrying that label; omitting it returns the full board (AC-3, server side).
  - An unknown or malformed `labelId` maps to `validation-error`.
  - Board tasks include their labels in the response without any extra request (Section 10).
- **Dependencies:** TASK-004, TASK-005
- **Complexity:** S
- **Files to Modify/Create:**
  - `src/api/tasks.ts`

### TASK-008: Backend tests for labels

- **Type:** Testing
- **Workflow:** standard
- **Description:** Per convention 6, add `tests/db/label.test.ts` (repository unit tests against the test database: case-insensitive duplicate rejection, max-10 enforcement, same-project validation, delete removes assignments and reports affected count) and `tests/api/labels.test.ts` (Supertest integration: create + list flow, 409 `conflict` on duplicate, `validation-error` on 11th label and bad color, delete cascade leaves tasks intact). Extend `tests/api/tasks.test.ts` with `labelId` filter cases, including a label with zero matching tasks returning an empty list with correct `meta`.
- **Rationale:** Every router gets a Supertest integration test and every repository a unit test (convention 6); these tests pin the API-side behavior behind AC-1, AC-3, AC-5, and AC-6.
- **Acceptance Criteria:**
  - All Section 9 API-visible edge cases (case-insensitive duplicate, 11th label, delete-with-assignments, zero-match filter) have failing-first coverage.
  - Test files mirror the `src/` tree.
- **Dependencies:** TASK-006, TASK-007
- **Complexity:** M
- **Files to Modify/Create:**
  - `tests/db/label.test.ts` (new)
  - `tests/api/labels.test.ts` (new)
  - `tests/api/tasks.test.ts`

### TASK-009: UI spec shards — dialog screen, LabelChip, accent palette

- **Type:** Documentation
- **Workflow:** standard
- **Description:** The project has no `docs/ui-specification/` directory yet. Create `docs/ui-specification/screens/label-management-dialog.md` (layout and flows: create form with name + palette picker, rename/recolor in place, delete with confirmation stating the affected task count, inline duplicate-name error). Create `docs/ui-specification/components.md` with the LabelChip entry (renders label name on its palette color; used by board cards, detail panel picker, and the management dialog). Create `docs/ui-specification/index.md` with a Screen Inventory row for the dialog and a Section 2.1 defining the 12 accent palette tokens, each documented as meeting 4.5:1 contrast for chip text (Section 10 NFR).
- **Rationale:** Work item Section 8 requires the new screen shard and the LabelChip component entry; Section 10 pins the color picker to the Section 2.1 palette tokens, which must therefore be defined.
- **Acceptance Criteria:**
  - Dialog shard covers create, rename, recolor, and delete-with-confirmation flows including the inline duplicate-name message.
  - `components.md` documents LabelChip; `index.md` Section 2.1 lists exactly 12 accent tokens with the WCAG 2.1 AA contrast requirement.
- **Dependencies:** None
- **Complexity:** S
- **Files to Modify/Create:**
  - `docs/ui-specification/screens/label-management-dialog.md` (new)
  - `docs/ui-specification/components.md` (new)
  - `docs/ui-specification/index.md` (new)

### TASK-010: LabelChip shared component

- **Type:** Frontend
- **Workflow:** mockup-first
- **Description:** Create `src/ui/components/label-chip.tsx`: a function component rendering a label's name on its palette color, sized for board cards, the detail-panel picker, and the management dialog. Colors come from the 12 accent tokens (TASK-009) — no external color library (Section 10: no new dependencies). Chip text must meet WCAG 2.1 AA 4.5:1 contrast on every token.
- **Rationale:** Section 8 names LabelChip as a new shared component reused by three surfaces; building it first avoids three divergent chip implementations.
- **Acceptance Criteria:**
  - Chip renders name + color for any of the 12 tokens with AA-compliant text contrast.
  - Component is reused (not duplicated) by TASK-011, TASK-012, and TASK-013.
- **Dependencies:** TASK-009
- **Complexity:** S
- **Files to Modify/Create:**
  - `src/ui/components/label-chip.tsx` (new)

### TASK-011: Label Management Dialog

- **Type:** Frontend
- **Workflow:** mockup-first
- **Description:** Create `src/ui/label-management-dialog.tsx` on top of the shared `src/ui/components/dialog.tsx`, per the TASK-009 shard. Features: label list with chip previews (LabelChip); create form with name input and a 12-token palette picker; rename and recolor in place; delete guarded by a confirmation dialog stating how many tasks carry the label (count from the label list response). Mutations go through TanStack Query and invalidate both the project's label list and the board tasks query, so every card showing a renamed/recolored label updates without a reload (AC-4). A 409 `conflict` from create or rename renders as an inline message on the name field (AC-6).
- **Rationale:** Section 8 introduces this screen as new — hence mockup-first workflow; it is the management surface behind AC-1, AC-4, AC-5, and AC-6.
- **Acceptance Criteria:**
  - Creating a label shows it immediately in the project's label list (AC-1).
  - Rename/recolor updates every visible task card via query invalidation (AC-4).
  - Delete requires explicit confirmation stating the affected task count; confirming removes the label from all tasks and leaves tasks intact (AC-5).
  - Duplicate name (including case-only differences) shows an inline validation message without closing the dialog (AC-6).
- **Dependencies:** TASK-006, TASK-009, TASK-010
- **Complexity:** L
- **Files to Modify/Create:**
  - `src/ui/label-management-dialog.tsx` (new)

### TASK-012: Task detail panel — labels field

- **Type:** Frontend
- **Workflow:** mockup-first
- **Description:** Modify `src/ui/task-detail-panel.tsx`: add a "Labels" field with a multi-select picker listing the project's labels as chip previews (LabelChip). Selecting/deselecting saves via PUT `/api/v1/tasks/{id}/labels` through a TanStack Query mutation that invalidates the board tasks query, so the task's card reflects the change without a page reload (AC-2). At 10 selected labels the picker disables further selection and shows an explanatory tooltip (Section 9).
- **Rationale:** Section 8 marks the Task Detail Panel as modified for this feature; classified mockup-first as frontend work tied to the new label UI.
- **Acceptance Criteria:**
  - Assigning and removing labels persists and appears on the board card without reload (AC-2).
  - The picker caps selection at 10 with a tooltip explaining the limit; the API rejection path (11th label) is never reachable from healthy UI state.
- **Dependencies:** TASK-006, TASK-010
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/ui/task-detail-panel.tsx`

### TASK-013: Project board — label chips and single-label filter

- **Type:** Frontend
- **Workflow:** mockup-first
- **Description:** Modify `src/ui/project-board.tsx` and `src/ui/components/task-card.tsx`. Cards render up to 3 label chips with a "+N" overflow indicator for the rest (labels come embedded in the board response — no per-card fetch). The board toolbar gains a single-select label filter dropdown and the button that opens the Label Management Dialog (TASK-011). Selecting a filter passes `labelId` to the board query (server-side, pagination-correct); clearing it restores the full board (AC-3). A filter with zero matching tasks renders the shared `src/ui/components/empty-state.tsx` with a "Clear filter" action — never a blank board. If a board refetch shows the filtered label no longer exists (deleted by another user), the filter clears automatically and a notice is shown; renamed/recolored labels appear on next refetch (last-write-wins, Section 9).
- **Rationale:** Section 8 marks the Project Board as modified; this is the surface behind AC-3 and the filter-related edge cases in Section 9.
- **Acceptance Criteria:**
  - Cards show up to 3 chips plus "+N" overflow (Section 8).
  - Filtering shows only tasks with the selected label; clearing restores the full board (AC-3).
  - Zero-match filter shows the empty state with "Clear filter" (Section 9).
  - Deleting the actively filtered label (by another user) clears the filter and shows a notice on refetch (Section 9).
  - Select-to-rendered round-trip stays under 300ms at P95 for 500-task boards (Section 10 NFR).
- **Dependencies:** TASK-007, TASK-010, TASK-011
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/ui/project-board.tsx`
  - `src/ui/components/task-card.tsx`

---

## Acceptance Criteria Coverage

| AC | Summary | Covered by |
|----|---------|------------|
| AC-1 | Create label (name 1–30 + palette color), appears in project label list | TASK-002, TASK-003, TASK-006, TASK-008, TASK-011 |
| AC-2 | Assign/remove labels from detail panel; persists and updates board card without reload | TASK-003, TASK-006, TASK-012 |
| AC-3 | Filter board by one label; clearing restores full board | TASK-004, TASK-007, TASK-008, TASK-013 |
| AC-4 | Rename/recolor updates every task card displaying the label | TASK-006, TASK-011, TASK-013 |
| AC-5 | Delete removes label from all tasks after confirmation stating affected task count | TASK-002, TASK-003, TASK-006, TASK-008, TASK-011 |
| AC-6 | Duplicate name in same project → validation error with inline UI message | TASK-002, TASK-006, TASK-008, TASK-011 |

## Edge Case Coverage (Section 9)

- Delete label assigned to tasks (confirmation with count; tasks untouched) — TASK-002, TASK-003, TASK-006, TASK-011
- Filter with zero matching tasks (empty state + "Clear filter") — TASK-008, TASK-013
- Assigning the 11th label (API validation error; picker disables at 10 with tooltip) — TASK-003, TASK-006, TASK-012
- Concurrent rename, last write wins; stale client updated on refetch — TASK-006, TASK-013
- Duplicate name differing only by case rejected — TASK-002, TASK-006, TASK-008
- Filtered label deleted by another user (clear filter + notice on refetch) — TASK-013
