# Task List — FEAT-001: Task Labels

**Source work item:** FEAT-001 (`docs/work-items/FEAT-001-task-labels.md`) · **Project:** TaskFlow · **Target version:** v1.1

## Generation Summary

- **15 tasks** generated from Feature Brief **FEAT-001**, covering all six acceptance criteria (AC-1 – AC-6), all six Section 9 edge cases, and all Section 10 constraints. Nothing from Section 4.2 (Excluded) is tasked: no cross-project labels, no automation, no custom hex colors, no multi-label filter combinations.
- **Ordering** follows the brief's Usage Notes: documentation for new entities/endpoints/screens first (T-001 – T-003, mandated by Sections 6–8), then data model (T-004 – T-007), then API (T-008 – T-010), then frontend (T-011 – T-014), then cross-cutting verification (T-015).
- **Workflow classification:** tasks building the new Label Management Dialog screen and the new LabelChip component are `mockup-first` per Section 8; all other tasks are `standard`.
- **Minimal-context assumptions** (this project has no spec documentation yet; the brief and CLAUDE.md are the only sources):
  - `docs/data-model/`, `docs/api-spec/`, and `docs/ui-specification/` do not exist. The brief's Sections 6–8 explicitly require the spec shards to be created before feature logic, so T-001 – T-003 create those files *and* their index files.
  - The 12-color accent palette referenced by Section 10 has no existing definition (`docs/ui-specification/index.md` does not exist). T-003 defines the tokens (with WCAG 2.1 AA-compliant chip text contrast) and T-005 encodes them as a shared TypeScript module so API validation and UI rendering share one source of truth.
  - `migrations/001-init.sql` is the only existing migration, so the new migration is numbered `002`.
  - Primary-key/column types for the new tables must match the existing `tasks` and `projects` tables in `001-init.sql`.

---

## Tasks

### T-001: Author data model documentation for Label and TaskLabel

- **Type:** documentation
- **Workflow:** standard
- **Description:** Create the data model spec shards for the two new entities required by the brief: `Label` (project-scoped, name + palette color) and `TaskLabel` (N:M join between tasks and labels). Since `docs/data-model/` does not exist yet, also create `docs/data-model/index.md` with Module Ownership and Relationships Overview entries for both entities.
- **Rationale:** Brief Section 6 mandates creating these shards before feature logic. They fix the business rules every later task depends on: case-insensitive name uniqueness per project, name length 1–30, color restricted to the 12 accent palette tokens, max 10 labels per task, same-project assignment rule, and delete cascading to assignments only (never to tasks).
- **Acceptance Criteria:**
  - `label.md` documents fields (id, projectId, name, color, timestamps) and all Label business rules from brief Section 6.
  - `task-label.md` documents the join (taskId, labelId), the max-10-per-task limit, and the same-project constraint.
  - `index.md` contains Module Ownership and Relationships Overview entries for both entities, including Project→Label (1:N, owning) and Task↔Label (N:M via TaskLabel).
  - Delete semantics are explicit: deleting a label removes its assignments; tasks are never deleted or modified.
- **Dependencies:** None
- **Complexity:** S
- **Files to Modify/Create:**
  - `docs/data-model/entities/label.md` (new)
  - `docs/data-model/entities/task-label.md` (new)
  - `docs/data-model/index.md` (new)

### T-002: Author API spec for label endpoints and the board `labelId` filter

- **Type:** documentation
- **Workflow:** standard
- **Description:** Create `docs/api-spec/endpoints/labels.md` covering all five label endpoints from brief Section 7 (list, create, rename/recolor, delete, replace task label set), and `docs/api-spec/endpoints/tasks.md` documenting the modified board list endpoint's optional `labelId` query parameter. Since `docs/api-spec/` does not exist yet, also create `docs/api-spec/index.md` with the Endpoint Summary rows and an Error Catalog containing every code this feature uses (`validation-error`, `conflict`, `not-found`).
- **Rationale:** Brief Section 7 mandates creating the endpoint shard and index rows before API work. CLAUDE.md forbids using an error code without a catalog row, and duplicate-name creation must return 409 `conflict` — so the catalog must exist before T-008.
- **Acceptance Criteria:**
  - All five label endpoints are specified with request/response shapes using the `{ "data": ... }` envelope and `meta` pagination block on the list response; label list items include a `taskCount` so the UI can populate the delete confirmation (AC-5).
  - Duplicate-name behavior is specified as 409 with error code `conflict`; validation failures (name length, invalid color token, >10 labels, cross-project assignment) map to `validation-error`.
  - `PUT /api/v1/tasks/{id}/labels` is specified as a full replace of the label set (array of label IDs, max 10).
  - `GET /api/v1/projects/{projectId}/tasks` documents the optional `labelId` parameter, its interaction with pagination, and that an unknown/deleted `labelId` yields an empty result page (not an error).
  - Concurrency semantics for rename/recolor are documented as last-write-wins (brief Section 9).
- **Dependencies:** T-001
- **Complexity:** M
- **Files to Modify/Create:**
  - `docs/api-spec/endpoints/labels.md` (new)
  - `docs/api-spec/endpoints/tasks.md` (new)
  - `docs/api-spec/index.md` (new)

### T-003: Author UI spec — accent palette, Label Management Dialog screen, LabelChip component

- **Type:** documentation
- **Workflow:** standard
- **Description:** Create the UI specification files required by brief Section 8. Since `docs/ui-specification/` does not exist yet, create `index.md` with a Screen Inventory and a Section 2.1 defining the fixed 12-color accent palette (token names + values + chip text color per token); create `screens/label-management-dialog.md` specifying the new dialog; create `components.md` with the LabelChip entry.
- **Rationale:** Brief Section 8 mandates these shards before frontend work, and Section 10 requires the palette tokens to come from `docs/ui-specification/index.md` Section 2.1 — which must therefore be authored first. Defining chip text contrast per token here is what makes the WCAG 2.1 AA (4.5:1) NFR verifiable later.
- **Acceptance Criteria:**
  - Section 2.1 defines exactly 12 accent palette tokens; each token's chip text/background pairing meets 4.5:1 contrast.
  - `label-management-dialog.md` specifies create/rename/recolor/delete flows, the palette swatch picker (no free hex input), inline duplicate-name error presentation (AC-6), and the delete confirmation stating the affected task count (AC-5).
  - `components.md` documents LabelChip (name + color, truncation for 30-char names, sizes for board card vs. picker usage).
  - `index.md` Screen Inventory gains the Label Management Dialog row; Project Board and Task Detail Panel entries note their label-related modifications.
- **Dependencies:** T-002
- **Complexity:** M
- **Files to Modify/Create:**
  - `docs/ui-specification/index.md` (new)
  - `docs/ui-specification/screens/label-management-dialog.md` (new)
  - `docs/ui-specification/components.md` (new)

### T-004: Migration — `labels` and `task_labels` tables

- **Type:** data-model
- **Workflow:** standard
- **Description:** Add `migrations/002-task-labels.sql` creating the `labels` table (id, project_id FK → projects ON DELETE CASCADE, name, color, timestamps) and the `task_labels` join table (task_id FK → tasks ON DELETE CASCADE, label_id FK → labels ON DELETE CASCADE, composite primary key). Key and column types must match the existing `tasks`/`projects` tables in `001-init.sql`.
- **Rationale:** Both new entities from brief Section 6 need schema before repositories can exist. FK cascade from `labels` to `task_labels` is what guarantees "deleting a label removes assignments only, never tasks" (AC-5) at the database level.
- **Acceptance Criteria:**
  - Case-insensitive uniqueness enforced by a unique index on `(project_id, lower(name))` — "Urgent" vs "urgent" is rejected (AC-6, Section 9 edge case).
  - `CHECK` constraint enforces name length 1–30.
  - `task_labels` has PK `(task_id, label_id)` (no duplicate assignments) plus an index on `label_id` for board filtering and delete-count queries.
  - Deleting a label row cascades only to `task_labels`; task rows are untouched. Deleting a task or project cleans up its labels/assignments.
  - Migration runs cleanly on top of `001-init.sql`.
- **Dependencies:** T-001
- **Complexity:** M
- **Files to Modify/Create:**
  - `migrations/002-task-labels.sql` (new)

### T-005: Shared accent palette module

- **Type:** data-model
- **Workflow:** standard
- **Description:** Encode the 12 accent palette tokens from the UI spec (T-003) as a typed constant module, e.g. an `as const` array plus a `LabelColor` union type, consumed by the API's Zod color validation (T-008) and the UI picker/chip rendering (T-011, T-012).
- **Rationale:** "Color must be one of the 12 accent palette tokens" is a business rule validated server-side and rendered client-side; a single module prevents the two lists from drifting. Keeping it plain TypeScript honors the Section 10 constraint of no new external dependencies for the color picker.
- **Acceptance Criteria:**
  - Module exports exactly the 12 token identifiers defined in T-003 and their display values (chip background + AA-compliant text color).
  - Importable from both `src/api/` and `src/ui/` code without circular dependencies.
  - Adding/removing a token is a single-file change (unit test asserts count and uniqueness of tokens).
- **Dependencies:** T-003
- **Complexity:** S
- **Files to Modify/Create:**
  - `src/shared/label-palette.ts` (new)
  - `tests/shared/label-palette.test.ts` (new)

### T-006: Label repository

- **Type:** data-model
- **Workflow:** standard
- **Description:** Create `src/db/label.ts` (one repository module per entity; SQL lives only here) with: `listByProject` (including per-label assigned-task counts), `create`, `update` (rename/recolor, last-write-wins), and `delete` (returning the number of assignments removed). Duplicate-name violations surface as a distinct, detectable error so the router can map them to the `conflict` catalog code.
- **Rationale:** CLAUDE.md requires routers never to touch `pg` directly. Task counts belong in the list query so the delete confirmation (AC-5) and board UI need no per-label follow-up queries.
- **Acceptance Criteria:**
  - `create` and `update` reject duplicate names case-insensitively within the same project (relying on the T-004 unique index) with a distinguishable error type.
  - `listByProject` returns labels with `taskCount` in a single query.
  - `delete` removes the label (assignments cascade) and reports the removed-assignment count; deleting a nonexistent label is detectable (returns nothing/0 rows).
  - Unit tests against the test database cover create/rename/recolor/delete, case-insensitive duplicates, and count correctness.
- **Dependencies:** T-004
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/db/label.ts` (new)
  - `tests/db/label.test.ts` (new)

### T-007: TaskLabel repository — assignment set replacement and batch lookup

- **Type:** data-model
- **Workflow:** standard
- **Description:** Create `src/db/task-label.ts` with: `replaceForTask(taskId, labelIds)` — a transactional full replace of a task's label set that verifies every label belongs to the task's project and enforces the max-10 rule — and `listForTasks(taskIds)` — a batch fetch of labels for a set of task IDs used to embed labels in the board response.
- **Rationale:** The PUT endpoint (T-009) replaces the whole set, so the repository operation must be atomic. Batch lookup is what lets the board include labels without per-card queries (Section 10 constraint on board load).
- **Acceptance Criteria:**
  - `replaceForTask` is transactional: on any violation (unknown label, cross-project label, >10 labels) nothing is written and a distinguishable error is raised.
  - Assigning an 11th label fails (Section 9 edge case); assigning exactly 10 succeeds.
  - `listForTasks` returns id/name/color for all assignments of the given tasks in one query.
  - Unit tests cover replace/clear semantics, the 10-label boundary, cross-project rejection, and batch lookup.
- **Dependencies:** T-004
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/db/task-label.ts` (new)
  - `tests/db/task-label.test.ts` (new)

### T-008: Labels router — CRUD endpoints

- **Type:** api
- **Workflow:** standard
- **Description:** Create `src/api/labels.ts` implementing `GET/POST /api/v1/projects/{projectId}/labels` and `PUT/DELETE /api/v1/labels/{id}` per the T-002 spec, and mount it in `src/api/index.ts`. Request bodies are validated with Zod schemas defined next to the handlers: name (1–30 chars after trimming), color (enum derived from the T-005 palette module). Errors are thrown as `ApiError` with catalog codes and serialized by the existing middleware.
- **Rationale:** These are four of the five new endpoints from brief Section 7 and the API surface behind AC-1, AC-4, AC-5, and AC-6. Deriving the Zod color enum from the shared palette module keeps validation and UI in lockstep.
- **Acceptance Criteria:**
  - POST creates a label and the list response immediately includes it (AC-1); duplicate name (case-insensitive) returns 409 with code `conflict` and a field-level message (AC-6).
  - Invalid name length or non-palette color returns `validation-error`.
  - PUT renames/recolors with last-write-wins semantics (no version check — Section 9 concurrency edge case); unknown id returns `not-found`.
  - DELETE removes the label and all its assignments, never tasks, and the response reports the removed-assignment count; GET list includes `taskCount` per label so the client can build the AC-5 confirmation.
  - All responses use the `{ "data": ... }` envelope; the list adds `meta` (`totalCount`, `page`, `pageSize`). Supertest integration tests cover every endpoint including both error paths.
- **Dependencies:** T-002, T-005, T-006
- **Complexity:** L
- **Files to Modify/Create:**
  - `src/api/labels.ts` (new)
  - `src/api/index.ts`
  - `tests/api/labels.test.ts` (new)

### T-009: Task label assignment endpoint — `PUT /api/v1/tasks/{id}/labels`

- **Type:** api
- **Workflow:** standard
- **Description:** Add the label-set replacement endpoint to the existing tasks router. The Zod schema validates an array of label IDs with `max(10)`; the handler delegates to `replaceForTask` (T-007) and maps repository violations to catalog error codes.
- **Rationale:** This is the persistence path for AC-2 (assign/remove from the task detail panel) and the API-side enforcement of the 11th-label edge case.
- **Acceptance Criteria:**
  - Replacing the set persists and the response returns the task's updated labels in the `data` envelope.
  - An 11-item array returns `validation-error` (Section 9 edge case); an empty array clears all labels.
  - Label IDs from another project or unknown IDs return `validation-error`/`not-found` without partial writes.
  - Supertest tests cover success, boundary (10 vs 11), cross-project rejection, and unknown task id.
- **Dependencies:** T-002, T-007
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/api/tasks.ts`
  - `tests/api/tasks.test.ts`

### T-010: Board tasks endpoint — `labelId` filter and embedded labels

- **Type:** api
- **Workflow:** standard
- **Description:** Extend `GET /api/v1/projects/{projectId}/tasks`: validate an optional `labelId` query parameter with Zod, filter server-side in the task repository's board query, and embed each task's labels (id/name/color) in the response using the T-007 batch lookup — one aggregate query, no per-card fetching.
- **Rationale:** Server-side filtering keeps results correct under pagination (Section 10 constraint), and embedding labels in the existing board response is the Section 10 requirement that protects initial board load time. This is the API side of AC-3.
- **Acceptance Criteria:**
  - With `labelId`, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count; without it, behavior is unchanged (AC-3).
  - Every board task includes a `labels` array; the implementation issues no per-task label queries (single filtered query plus at most one batch label query).
  - An unknown or deleted `labelId` returns an empty page (200), per the T-002 spec, so a stale client filter degrades gracefully.
  - Supertest tests cover filtered/unfiltered results, pagination with filter, embedded label shape, and the unknown-`labelId` case.
- **Dependencies:** T-002, T-007
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/api/tasks.ts`
  - `src/db/task.ts`
  - `tests/api/tasks.test.ts`

### T-011: LabelChip shared component

- **Type:** frontend
- **Workflow:** mockup-first
- **Description:** Create the reusable `LabelChip` component per the T-003 component spec: renders a label's name on its palette color, with text color taken from the palette module's AA-compliant pairing, and truncates long names. Used by board cards (T-014), the detail panel picker (T-013), and the management dialog (T-012).
- **Rationale:** Brief Section 8 names LabelChip as a new shared component; building it first (mockup-first) lets all three consuming surfaces render labels identically and makes the WCAG contrast NFR a single-component concern.
- **Acceptance Criteria:**
  - Renders name + color for any of the 12 palette tokens; component test asserts the text/background pairing for every token meets 4.5:1 contrast (NFR).
  - Handles 30-character names with truncation and a title/tooltip for the full name.
  - Static mockup states (all 12 tokens, long name, compact board-card size vs. picker size) reviewed before wiring into screens.
- **Dependencies:** T-003, T-005
- **Complexity:** S
- **Files to Modify/Create:**
  - `src/ui/components/label-chip.tsx` (new)
  - `tests/ui/components/label-chip.test.tsx` (new)

### T-012: Label Management Dialog

- **Type:** frontend
- **Workflow:** mockup-first
- **Description:** Create the Label Management Dialog screen per the T-003 screen spec, reusing the existing shared `dialog.tsx` component: list the project's labels with edit/delete affordances, create/rename forms with a 12-swatch palette picker (no new dependencies, no free hex input), and delete confirmation. Server state via TanStack Query; label mutations invalidate both the label-list query and the board tasks query so every card reflects renames/recolors (AC-4).
- **Rationale:** This is the new screen from brief Section 8 (hence `mockup-first`) and the UI for label CRUD (AC-1), rename propagation (AC-4), guarded deletion (AC-5), and inline duplicate-name feedback (AC-6).
- **Acceptance Criteria:**
  - Creating a label shows it in the list immediately without a page reload (AC-1).
  - A 409 `conflict` response renders as an inline field error on the name input, preserving user input (AC-6).
  - Delete requires an explicit confirmation dialog stating how many tasks are affected, using the `taskCount` from the list response (AC-5, Section 9 edge case); confirming removes the label everywhere.
  - Rename/recolor updates chips on all visible board cards after mutation-triggered refetch (AC-4).
  - Static mockup of the dialog (list, create form, picker, confirmation state) reviewed before wiring mutations.
- **Dependencies:** T-008, T-011
- **Complexity:** L
- **Files to Modify/Create:**
  - `src/ui/label-management-dialog.tsx` (new)
  - `tests/ui/label-management-dialog.test.tsx` (new)

### T-013: Task Detail Panel — labels field with multi-select picker

- **Type:** frontend
- **Workflow:** standard
- **Description:** Add a "Labels" field to the existing task detail panel: a multi-select picker listing the project's labels as chip previews (LabelChip), persisting changes through `PUT /api/v1/tasks/{id}/labels`, and invalidating the board tasks query so the card updates without a page reload.
- **Rationale:** This is the assignment surface for AC-2 and the UI-side enforcement of the max-10 rule from Section 9.
- **Acceptance Criteria:**
  - Assigning and removing labels persists and is reflected on the board card without a page reload (AC-2).
  - At 10 selected labels the picker disables further selection and shows an explanatory tooltip (Section 9 edge case); the API's `validation-error` for an 11th label is still handled gracefully if it occurs.
  - Picker options come from the project's label list query and render as LabelChip previews.
  - Component tests cover selection persistence wiring, the 10-label disable state, and removal.
- **Dependencies:** T-008, T-009, T-011
- **Complexity:** M
- **Files to Modify/Create:**
  - `src/ui/task-detail-panel.tsx`
  - `tests/ui/task-detail-panel.test.tsx` (new)

### T-014: Project Board — label chips, filter dropdown, empty state

- **Type:** frontend
- **Workflow:** standard
- **Description:** Extend the project board and its task card component: cards render up to 3 label chips with a "+N" overflow indicator from the labels embedded in the board response (no extra fetches); the toolbar gains a single-select label filter dropdown and the entry point that opens the Label Management Dialog (T-012). The filter sets the `labelId` parameter on the board query so filtering stays server-side.
- **Rationale:** This delivers the board half of AC-2/AC-3/AC-4 and three Section 9 edge cases (zero-match filter, deleted-while-filtered, stale rename), while honoring the Section 10 constraints on board load and server-side filtering.
- **Acceptance Criteria:**
  - Cards show ≤3 chips plus "+N" when a task has more; chips come from the embedded `labels` array (no per-card requests).
  - Selecting a label shows only matching tasks; clearing restores the full board (AC-3).
  - A filter with zero matches renders the existing `empty-state.tsx` with a "Clear filter" action, never a blank board (Section 9 edge case).
  - If the active filter's label disappears from the label-list refetch (deleted by another user), the board clears the filter and shows a notice (Section 9 edge case).
  - Renames/recolors by other users appear on next board refetch (last-write-wins, Section 9 edge case; AC-4).
  - Component tests cover chip overflow, filter apply/clear, empty state, and deleted-filter recovery.
- **Dependencies:** T-008, T-010, T-011, T-012
- **Complexity:** L
- **Files to Modify/Create:**
  - `src/ui/project-board.tsx`
  - `src/ui/components/task-card.tsx`
  - `tests/ui/project-board.test.tsx` (new)

### T-015: End-to-end acceptance flow and NFR verification

- **Type:** testing
- **Workflow:** standard
- **Description:** Add an API-level end-to-end flow test exercising the full label lifecycle (create → assign → filter board → rename → delete with assignment cleanup) against a seeded test database, plus an NFR check: with a 500-task board, the filtered board query round-trip stays under the 300ms P95 budget from brief Section 10.
- **Rationale:** Per-task tests verify slices; this task verifies the acceptance criteria end-to-end across router + repository + schema and pins the performance constraint so regressions are caught, not discovered by pilot teams.
- **Acceptance Criteria:**
  - Flow test covers AC-1 → AC-5 sequentially against the running Express app (Supertest), including the delete cascade leaving tasks intact.
  - Duplicate-name (case-insensitive) and 11th-label rejections are asserted in the flow (AC-6, Section 9).
  - Seeded 500-task board: filtered list request completes within the 300ms P95 budget in the test environment; the assertion documents the budget's origin (FEAT-001 Section 10).
  - Palette contrast NFR is verified by the T-011 component test; this task confirms the suite runs green as a whole.
- **Dependencies:** T-012, T-013, T-014
- **Complexity:** M
- **Files to Modify/Create:**
  - `tests/api/label-board-flow.test.ts` (new)

---

## Acceptance Criteria Coverage

| Acceptance Criterion | Summary | Covered by |
|---|---|---|
| AC-1 | Create label (name 1–30 + palette color); appears in project label list immediately | T-004, T-006, T-008, T-012 |
| AC-2 | Assign/remove labels from task detail panel; persists and updates board card without reload | T-007, T-009, T-013 |
| AC-3 | Board filter by label shows only matching tasks; clearing restores full board | T-010, T-014 |
| AC-4 | Rename/recolor updates every task card displaying the label | T-006, T-008, T-012, T-014 |
| AC-5 | Delete removes label from all tasks after confirmation stating affected task count | T-004, T-006, T-008, T-012 |
| AC-6 | Duplicate name in same project → validation error + inline UI message | T-004, T-006, T-008, T-012 |

## Edge Case Coverage (Brief Section 9)

| Edge case | Covered by |
|---|---|
| Deleting an assigned label — confirmation states affected count; tasks untouched | T-004, T-006, T-008, T-012 |
| Filtering by a label with zero matches — empty state with "Clear filter" | T-014 |
| Assigning an 11th label — API validation error; picker disables at 10 with tooltip | T-007, T-009, T-013 |
| Concurrent rename — last write wins; stale client updated on next refresh | T-008, T-014 |
| Duplicate name differing only by case — rejected (case-insensitive uniqueness) | T-004, T-006, T-008 |
| Active filter label deleted by another user — refetch clears filter and shows notice | T-010, T-014 |

## Constraint Coverage (Brief Section 10)

| Constraint | Covered by |
|---|---|
| Labels embedded in board response — no per-card fetches, board load protected | T-007, T-010, T-014 |
| No new dependencies for color picker; fixed 12-token accent palette | T-003, T-005, T-011, T-012 |
| Server-side board filtering (query parameter), correct under pagination | T-010, T-014 |
| NFR: filter round-trip < 300ms P95 at 500 tasks | T-015 |
| NFR: chip text meets WCAG 2.1 AA (4.5:1) on all palette colors | T-003, T-005, T-011 |
