# FEAT-001: Task Labels — Implementation Tasks

> Generated from Feature Brief **FEAT-001** (`docs/work-items/FEAT-001-task-labels.md`, target v1.1) using the canonical task schema from `prompts/base-template.md` and the procedure in `prompts/feature-tasks.md`. Scope authority: Feature Brief Section 4 (this project keeps no separate stakeholder definition). All file paths are relative to the project root.

---

## Foundation

### T-001: Author Label and TaskLabel entity shards

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the data-model shards for the new Label entity and the TaskLabel join entity, and register both in the data-model index. Label carries a project-scoped name (varchar(30), case-insensitively unique per project) and one of the 12 accent-palette color tokens; TaskLabel connects tasks to labels N:M with a maximum of 10 labels per task.

**Rationale:**
Feature Brief Section 6 requires the new entity shards to exist before feature logic; the index's Module Ownership and Relationships tables double as the shard directory and must stay in sync.

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` defines fields (id, project_id, name, color, timestamps), the case-insensitive per-project name uniqueness rule, the 12-token color constraint, and cascade behavior (project delete removes labels; label delete removes assignments only, never tasks)
- [ ] `docs/data-model/entities/task-label.md` defines the join (task_id, label_id, composite PK), the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] `docs/data-model/index.md` gains Module Ownership rows for both entities, a Section 4.2 many-to-many entry (Task ↔ Label via `task_labels`), and a Changelog row

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- `docs/data-model/entities/label.md` (new) - Label entity shard (fields, rules, relationships)
- `docs/data-model/entities/task-label.md` (new) - TaskLabel join entity shard
- `docs/data-model/index.md` - Module Ownership rows, M:N relationship entry, ERD note, Changelog row

### T-002: Author labels API shard and update tasks endpoint spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` specifying all five label endpoints with DTOs, envelopes, roles, and status codes, reusing existing Error Catalog codes only. Update `docs/api-spec/endpoints/tasks.md` so the board list gains the optional `labelId` query parameter and `TaskDto` gains an embedded `labels` array, and add the new rows to the Endpoint Summary.

**Rationale:**
Feature Brief Section 7 requires the endpoint shard before frontend integration; embedding labels in the board response is mandated by the Section 10 board-load constraint.

**Acceptance Criteria:**
- [ ] `labels.md` specifies GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` with request/response schemas using the standard envelope
- [ ] Duplicate name maps to 409 `conflict`; invalid name/color, an 11th label, and cross-project assignment map to 400 `validation-error` — no new Error Catalog codes introduced
- [ ] `LabelDto` on the project list includes `taskCount` so the delete confirmation can state how many tasks are affected
- [ ] `tasks.md` documents the optional `labelId` filter on the board list and the embedded `labels` array on `TaskDto` (list and single-task responses)
- [ ] `docs/api-spec/index.md` Endpoint Summary gains the five new rows plus a Changelog entry

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- `docs/api-spec/endpoints/labels.md` (new) - all five label endpoints, LabelDto, error mapping
- `docs/api-spec/endpoints/tasks.md` - `labelId` query parameter + `labels` array on TaskDto
- `docs/api-spec/index.md` - Endpoint Summary rows, Changelog row

### T-003: Author Label Management Dialog screen shard and update UI spec

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the screen shard for the new Label Management Dialog (layout, component hierarchy, component→API mapping, all four states, delete confirmation interaction) and add its Screen Inventory row. Document the LabelChip shared component in `components.md`, and update the Project Board and Task Detail Panel shards with label chips, the single-label filter, and the Labels picker field.

**Rationale:**
Feature Brief Section 8 requires the new screen shard and inventory row before frontend work; modified screens must keep their shards in sync per the UI index usage notes.

**Acceptance Criteria:**
- [ ] `docs/ui-specification/screens/label-management-dialog.md` covers layout, component→API mapping, default/loading/empty/error states, and the destructive delete confirmation stating the affected task count
- [ ] `docs/ui-specification/components.md` gains a LabelChip entry (inputs/outputs, variants, per-token AA-contrast text color rule)
- [ ] `docs/ui-specification/index.md` Screen Inventory gains the dialog row and the Changelog records the change
- [ ] `project-board.md` and `task-detail-panel.md` reflect chips (max 3 + "+N" overflow), the toolbar filter dropdown and manage-labels entry point, and the Labels multi-select picker

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- `docs/ui-specification/screens/label-management-dialog.md` (new) - new screen shard
- `docs/ui-specification/index.md` - Screen Inventory row, Changelog row
- `docs/ui-specification/components.md` - LabelChip shared component entry
- `docs/ui-specification/screens/project-board.md` - chips, filter dropdown, dialog entry point
- `docs/ui-specification/screens/task-detail-panel.md` - Labels picker field

### T-004: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add `migrations/002-labels.sql` creating the `labels` table (UUID `id` PK, `project_id` FK cascading on project delete, `name` varchar(30), `color` token, `created_at`/`updated_at`) and the `task_labels` join table (composite PK on `task_id` + `label_id`, FKs cascading on task and label delete). Enforce case-insensitive per-project name uniqueness with a unique index on `(project_id, lower(name))` and index `task_labels.label_id` for board filtering.

**Rationale:**
The new Section 6 entities need schema before repositories exist; DB-level uniqueness backs the duplicate-name edge case ("Urgent" vs "urgent") independently of application code.

**Acceptance Criteria:**
- [ ] Migration applies cleanly after `001-init.sql` and follows the snake_case, UUID-PK, and timestamptz conventions from the data-model index
- [ ] Unique index on `(project_id, lower(name))` rejects same-project duplicates differing only by case, while identical names in different projects are allowed
- [ ] Deleting a label cascades to `task_labels` rows only; deleting a task or project removes its dependent rows; label operations never delete tasks
- [ ] `color` is constrained (CHECK) to the 12 accent-palette tokens

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- `migrations/002-labels.sql` (new) - `labels` + `task_labels` tables, unique and filter indexes, color CHECK

---

## Backend

### T-005: Implement label and task-label repositories

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` (list with task counts, create, rename/recolor, delete returning affected-task count) and `src/db/task-label.ts` (fetch labels for tasks, replace a task's label set in one transaction). The replace operation enforces the max-10 rule and that every label belongs to the task's project; all SQL stays in these modules per CLAUDE.md convention 5.

**Rationale:**
The data-access convention requires one repository module per entity, and routers never touch `pg` directly.

**Acceptance Criteria:**
- [ ] `listByProject` returns labels with `taskCount`; unique-constraint violations on create/rename surface as a typed conflict the router can map to 409
- [ ] `replaceForTask` atomically replaces assignments and rejects sets larger than 10 or containing labels from another project
- [ ] Deleting a label removes its assignments in the same transaction and reports how many tasks were affected

**Dependencies:** T-004
**Complexity:** M

**Files to Modify/Create:**
- `src/db/label.ts` (new) - label repository (CRUD + task counts)
- `src/db/task-label.ts` (new) - assignment repository (replace-set, lookups for board embedding)

### T-006: Implement label CRUD endpoints

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}` with Zod validation (trimmed name 1–30 chars, color one of the 12 accent tokens), and mount the router in `src/api/index.ts`. Responses use the standard envelope; errors are thrown as `ApiError` with existing catalog codes.

**Rationale:**
Section 7's new endpoints must exist before frontend integration; this router delivers the API side of AC-1, AC-4, AC-5, and AC-6.

**Acceptance Criteria:**
- [ ] POST creates the label and returns it in the `{ data }` envelope; it appears in a subsequent GET list (AC-1)
- [ ] Duplicate name within a project — including case variants like "Urgent" vs "urgent" — returns 409 `conflict`; invalid name/color returns 400 `validation-error` with `fields`
- [ ] PUT renames/recolors with last-write-wins semantics (no version check); a stale client receives the stored state on its next fetch
- [ ] DELETE removes the label and all its assignments (never tasks) and returns the affected-task count for the UI notice
- [ ] GET list uses the list envelope with `meta` per index Section 2.4 and includes `taskCount` per label

**Dependencies:** T-002, T-005
**Complexity:** L

**Files to Modify/Create:**
- `src/api/labels.ts` (new) - labels router (list/create/rename/recolor/delete) with Zod schemas
- `src/api/index.ts` - mount the labels router

**Technical Notes:** (optional)
- List is visible to any project member; create/rename/delete require edit rights, mirroring the role checks in `src/api/tasks.ts`
- Map the Postgres unique-violation from T-005 to `ApiError('conflict')` — do not pre-check with a SELECT (race-prone)

### T-007: Implement task label assignment endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Add PUT `/api/v1/tasks/{id}/labels` to `src/api/labels.ts`, accepting an array of label IDs and replacing the task's label set via the task-label repository. Enforce the max-10 and same-project rules as 400 `validation-error` and respond with the task's updated label set in the standard envelope.

**Rationale:**
AC-2 requires persisted assign/remove from the detail panel, and the Section 9 edge case requires the 11th label to be rejected server-side.

**Acceptance Criteria:**
- [ ] A valid request atomically replaces the set and returns the task's updated labels
- [ ] An 11th label returns 400 `validation-error` with a message naming the 10-label limit
- [ ] An unknown task returns 404 `not-found`; label IDs from another project or unknown label IDs return 400 `validation-error`

**Dependencies:** T-006
**Complexity:** M

**Files to Modify/Create:**
- `src/api/labels.ts` (new) - add the PUT `/api/v1/tasks/{id}/labels` handler (file created in T-006)

### T-008: Add label filter and embedded labels to task queries

**Type:** Backend
**Workflow:** standard

**Description:**
Extend `src/db/task.ts` so the board list query and the single-task fetch return each task's labels via a single join-aggregate (no per-card fetches), and accept an optional `labelId` filter applied server-side. Add the `labelId` query parameter (UUID, Zod-validated) to GET `/api/v1/projects/{projectId}/tasks` in `src/api/tasks.ts`.

**Rationale:**
Section 10 requires labels to ride in the existing board response and filtering to stay server-side so results remain correct under pagination (AC-3).

**Acceptance Criteria:**
- [ ] Board response `TaskDto` items include a `labels` array produced by one aggregated query — query count does not grow with task count
- [ ] With `labelId`, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered total under pagination
- [ ] Without `labelId`, the response is unchanged except for the added `labels` array; an invalid `labelId` returns 400 `validation-error`
- [ ] GET `/api/v1/tasks/{id}` includes the task's labels for the detail panel

**Dependencies:** T-002, T-005
**Complexity:** M

**Files to Modify/Create:**
- `src/db/task.ts` - join/aggregate labels into board and single-task queries, optional `labelId` filter
- `src/api/tasks.ts` - `labelId` query parameter in the Zod schema

---

## Frontend

### T-009: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create `src/ui/components/label-chip.tsx` rendering a label's name on its accent-token background with a per-token text color meeting WCAG 2.1 AA (4.5:1), caption typography, and `space-1` padding. It is the single chip rendering used by board cards, the detail-panel picker, and the management dialog.

**Rationale:**
Section 8 defines LabelChip as a shared component so all three surfaces render labels identically; Section 10's NFR requires AA contrast on every palette color.

**Acceptance Criteria:**
- [ ] Chip renders name and color from a `LabelDto` using accent-palette CSS custom properties — no hard-coded hex values
- [ ] Text color per token meets 4.5:1 contrast on all 12 accent tokens
- [ ] Long names truncate with an ellipsis and expose the full name via a `title`/aria-label

**Dependencies:** T-003
**Complexity:** S

**Files to Modify/Create:**
- `src/ui/components/label-chip.tsx` (new) - shared chip (name + accent color, AA text contrast)

### T-010: Build Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Create the Label Management Dialog screen (`src/ui/label-management-dialog.tsx`) for creating, renaming, recoloring, and deleting project labels, using the shared `Dialog` component and a 12-swatch accent-palette picker with no new dependencies. This adds a new user-facing screen — generate an HTML mockup of the Label Management Dialog for stakeholder approval before implementing, per `.ai-framework/prompts/mockup-generation.md`.

**Rationale:**
Section 8's new screen delivers label management end to end: AC-1 (create), AC-4 (rename/recolor), AC-5 (delete confirmation), and AC-6 (inline duplicate error).

**Acceptance Criteria:**
- [ ] Creating a label shows it in the dialog's list immediately via TanStack Query invalidation — no page reload (AC-1)
- [ ] A duplicate-name 409 renders an inline message on the name field (AC-6)
- [ ] Delete opens a destructive-variant confirmation stating the affected task count (from `taskCount`) before calling DELETE (AC-5)
- [ ] Rename/recolor mutations invalidate the board query so every visible card chip updates (AC-4)
- [ ] All four states handled per UI index Section 2.5: loading skeleton, `EmptyState` ("No labels yet" + create CTA), inline error banner with retry

**Dependencies:** T-003, T-006, T-009
**Complexity:** L

**Files to Modify/Create:**
- `src/ui/label-management-dialog.tsx` (new) - dialog screen (list, create form, rename/recolor, delete confirmation)

**Technical Notes:** (optional)
- Palette picker is a static grid of the 12 accent tokens from UI index Section 2.1 — no external color-picker dependency (Section 10 constraint)

### T-011: Add label chips and single-label filter to the Project Board

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 LabelChips per `TaskCard` with a "+N" overflow indicator, and add a single-select label filter dropdown plus a "Manage labels" entry point to the BoardToolbar. The filter passes `labelId` to the board query (server-side) and offers a clear action that restores the full board.

**Rationale:**
Delivers AC-3 and the board-side rendering behind AC-2/AC-4; Section 10 requires filtering to remain a server-side query parameter, and Section 4.2 excludes multi-label filter combinations.

**Acceptance Criteria:**
- [ ] Cards show at most 3 chips plus a "+N" indicator when a task has more; unlabeled boards render unchanged
- [ ] Selecting a label refetches with `labelId` and shows only matching tasks; "Clear filter" restores the full board (AC-3)
- [ ] A zero-match filter shows the standard `EmptyState` with a "Clear filter" CTA — never a blank board
- [ ] If a refetch reveals the filtered label was deleted (e.g., by another user), the filter clears automatically and a notice is shown
- [ ] The toolbar entry point opens the Label Management Dialog

**Dependencies:** T-008, T-009, T-010
**Complexity:** L

**Files to Modify/Create:**
- `src/ui/project-board.tsx` - filter dropdown, manage-labels entry point, empty-filter state, deleted-label handling
- `src/ui/components/task-card.tsx` - render up to 3 LabelChips + overflow indicator

### T-012: Add Labels picker to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to `src/ui/task-detail-panel.tsx` with a multi-select picker that shows chip previews of the project's labels and marks the task's current assignments. Selection changes call PUT `/api/v1/tasks/{id}/labels` and invalidate the board query so the card updates without a reload; the picker disables further selection at 10 labels with an explanatory tooltip.

**Rationale:**
Delivers AC-2 and the picker half of the Section 9 11th-label edge case.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists via the replace-set endpoint and updates both the panel and the board card without a page reload (AC-2)
- [ ] With 10 labels selected, remaining options are disabled and a tooltip explains the 10-label limit
- [ ] The picker loads the project's labels with chip previews; loading and error states follow UI index Section 2.5

**Dependencies:** T-007, T-008, T-009
**Complexity:** M

**Files to Modify/Create:**
- `src/ui/task-detail-panel.tsx` - Labels field, multi-select picker, mutation + query invalidation

---

## Testing

### T-013: Write repository unit tests for labels

**Type:** Testing
**Workflow:** standard

**Description:**
Unit-test `src/db/label.ts` and `src/db/task-label.ts` against the test database, per CLAUDE.md convention 6. Cover CRUD, case-insensitive uniqueness, cascade behavior, and replace-set validation.

**Rationale:**
Every repository gets a unit test; the DB-level rules (uniqueness, cascades, max-10, same-project) underpin AC-5 and AC-6.

**Acceptance Criteria:**
- [ ] Duplicate names in the same project (including case variants) are rejected; the same name in different projects is allowed
- [ ] `replaceForTask` rejects an 11th label and cross-project labels; a valid replace is atomic
- [ ] Deleting a label removes its assignments and returns the affected-task count while tasks remain intact

**Dependencies:** T-005
**Complexity:** M

**Files to Modify/Create:**
- `tests/db/label.test.ts` (new) - label repository tests
- `tests/db/task-label.test.ts` (new) - assignment repository tests

### T-014: Write API integration tests for label endpoints and board filter

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest coverage for all five label endpoints in `tests/api/labels.test.ts`, and extend `tests/api/tasks.test.ts` for the `labelId` filter and the embedded `labels` array. Assert envelope shape, error codes, and `meta` correctness under filtering.

**Rationale:**
Every router gets a Supertest integration test per CLAUDE.md convention 6; this verifies AC-1, AC-3, AC-5, and AC-6 at the API level.

**Acceptance Criteria:**
- [ ] Happy paths for list/create/rename/recolor/delete/replace-set assert the `{ data }` envelope (plus `meta` on lists)
- [ ] Duplicate create/rename returns 409 `conflict`; an 11th label or invalid color returns 400 `validation-error`; unknown IDs return 404 `not-found`
- [ ] Board list with `labelId` returns only matching tasks with correct `meta.totalCount`; without it, the response is unchanged apart from the `labels` array
- [ ] Deleting a label then listing board tasks shows the assignments gone and the tasks still present

**Dependencies:** T-006, T-007, T-008
**Complexity:** M

**Files to Modify/Create:**
- `tests/api/labels.test.ts` (new) - integration tests for the labels router
- `tests/api/tasks.test.ts` - `labelId` filter and embedded-labels cases

### T-015: Write frontend component tests for label UI

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for LabelChip, the Label Management Dialog, the board chips/filter, and the panel picker, mocking API responses behind TanStack Query. Focus on the UI edge cases from Feature Brief Section 9.

**Rationale:**
Verifies the UI halves of AC-2 through AC-6 — inline duplicate error, delete-confirmation count, empty filter state, and the max-10 tooltip.

**Acceptance Criteria:**
- [ ] LabelChip applies the expected AA-contrast text color for each of the 12 accent tokens and truncates long names
- [ ] Dialog shows the inline duplicate-name error on 409 and the affected-count confirmation before delete
- [ ] Board tests cover chip overflow at 3 ("+N"), the zero-match `EmptyState` with "Clear filter", and the deleted-filtered-label refetch clearing the filter with a notice
- [ ] Picker disables further selection at 10 labels and shows the explanatory tooltip

**Dependencies:** T-010, T-011, T-012
**Complexity:** M

**Files to Modify/Create:**
- `tests/ui/components/label-chip.test.tsx` (new) - chip rendering and contrast mapping
- `tests/ui/label-management-dialog.test.tsx` (new) - dialog CRUD, inline error, delete confirmation
- `tests/ui/project-board.test.tsx` (new) - chips, filter, empty and deleted-label states
- `tests/ui/task-detail-panel.test.tsx` (new) - picker behavior and max-10 handling

---

## Summary

**Feature Brief:** FEAT-001 — Task Labels (v1.1)

**Total task count by type:**

| Type | Count |
|------|-------|
| Documentation | 3 (T-001, T-002, T-003) |
| Database | 1 (T-004) |
| Backend | 4 (T-005–T-008) |
| Frontend | 4 (T-009–T-012) |
| Testing | 3 (T-013–T-015) |
| **Total** | **15** |

**Estimated complexity distribution:** S ×3 (T-001, T-004, T-009) · M ×9 (T-002, T-003, T-005, T-007, T-008, T-012, T-013, T-014, T-015) · L ×3 (T-006, T-010, T-011) · XL ×0 — no task warrants XL; the feature decomposes cleanly along the entity/API/UI seams.

**Critical path (7 tasks):** T-001 → T-004 → T-005 → T-006 → T-010 → T-011 → T-015. (An equal-length parallel chain runs T-001 → T-002 → T-003 → T-009 → T-010; documentation and schema work can proceed concurrently.)

**Risks / open questions:**

- The project has no e2e harness (Vitest + Supertest only), so AC verification tops out at API integration plus component tests; adding an e2e framework was deliberately not tasked to avoid new dependencies and over-engineering.
- The <300ms P95 filter round-trip NFR (boards up to 500 tasks) is addressed structurally (single aggregated query, `task_labels.label_id` index, server-side filter in T-004/T-008) but is not load-tested; profile during T-014 if boards approach that size.
- Per-token AA-contrast text colors for the 12 accent tokens are asserted in T-009/T-015, but final visual confirmation should happen during the T-010 mockup approval.
- Edit-rights enforcement depends on the external auth service's role resolution; the labels router mirrors the tasks router's checks (spec'd in T-002) — confirm no additional permission model is expected for label management.

---

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label (name 1–30 chars + palette color); it immediately appears in the project's label list | T-006, T-010, T-014 |
| AC-2: Assign/remove labels from the task detail panel; changes persist and appear on the board card without a reload | T-007, T-012, T-015 |
| AC-3: Selecting a label in the board filter shows only matching tasks; clearing restores the full board | T-008, T-011, T-014 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-006, T-010, T-011 |
| AC-5: Deleting a label removes it from all tasks after a confirmation stating the affected task count | T-005, T-006, T-010, T-014 |
| AC-6: Duplicate label name within a project returns a validation error and the UI shows an inline message | T-004, T-006, T-010, T-014 |
