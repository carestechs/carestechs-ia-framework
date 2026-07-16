# FEAT-001: Task Labels — Implementation Tasks

Generated from work item **FEAT-001** (`docs/work-items/FEAT-001-task-labels.md`). Paths are relative to the project root; files that do not exist yet are suffixed `(new)`. This project has no spec documentation yet — the shards named by the work item's impact tables are created by tasks in this list, before the feature logic that relies on them.

---

## Foundation

### T-001: Author data model spec shards for Label and TaskLabel

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the data model shards for the two new entities: Label (project-scoped, name + palette color) and TaskLabel (task-to-label N:M join). Because no spec documentation exists in this project yet, also create the data model index with Module Ownership and Relationships Overview entries for both entities.

**Rationale:**
Work item Section 6 requires the new-entity shards to exist before feature logic; the migration, repository, and API tasks all build against these definitions.

**Acceptance Criteria:**
- [ ] `docs/data-model/entities/label.md` defines fields (id, projectId, name 1–30 chars, color token, timestamps) and business rules: case-insensitive name uniqueness per project, color restricted to the 12 accent palette tokens, deletion cascades to assignments only — never to tasks
- [ ] `docs/data-model/entities/task-label.md` defines the join (taskId, labelId), the max-10-labels-per-task rule, and the same-project constraint for assignments
- [ ] `docs/data-model/index.md` contains Module Ownership and Relationships Overview entries for Label and TaskLabel
- [ ] Naming follows CLAUDE.md conventions: snake_case tables/columns, camelCase JSON keys

**Dependencies:** None
**Complexity:** S

**Files to Modify/Create:**
- docs/data-model/entities/label.md (new) - Label entity definition and business rules
- docs/data-model/entities/task-label.md (new) - TaskLabel join entity definition
- docs/data-model/index.md (new) - data model index with Module Ownership and Relationships Overview entries

### T-002: Create labels and task_labels database migration

**Type:** Database
**Workflow:** standard

**Description:**
Add migration `002-labels.sql` creating the `labels` table (id, project_id FK, name, color, timestamps) and the `task_labels` join table (task_id, label_id composite primary key). Enforce integrity at the schema level: case-insensitive unique label name per project and cascading deletes to assignments only.

**Rationale:**
The Label and TaskLabel entities from work item Section 6 need schema before the repository exists; database-level uniqueness backs the AC-6 duplicate rejection even under concurrent creates.

**Acceptance Criteria:**
- [ ] `labels` has a unique index on `(project_id, lower(name))` so "Urgent" vs "urgent" is rejected as a duplicate
- [ ] `color` is constrained to the 12 accent palette token values
- [ ] `task_labels` has composite primary key `(task_id, label_id)` with `ON DELETE CASCADE` from both `labels` and `tasks`, so deleting a label removes assignments but never tasks
- [ ] Migration applies cleanly on top of `migrations/001-init.sql`

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - labels and task_labels tables, constraints, indexes

**Technical Notes:**
- Follow the plain-SQL numbered migration convention (`NNN-description.sql`)
- Add an index on `task_labels(label_id)` to support the board label filter join

### T-003: Implement label repository module

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/db/label.ts` with the label data access: list labels for a project (with per-label assigned-task counts), create, rename/recolor, delete (returning the affected-task count), and atomically replace a task's label set. All SQL stays in this repository per CLAUDE.md convention 5.

**Rationale:**
CLAUDE.md mandates one repository module per entity with SQL confined to `src/db/`; every label endpoint depends on these queries.

**Acceptance Criteria:**
- [ ] `listByProject` returns labels with an assigned-task count per label (needed for the AC-5 delete confirmation)
- [ ] `deleteLabel` removes the label plus its assignments and returns how many tasks were affected
- [ ] `replaceTaskLabels` atomically replaces a task's label set, rejecting sets over 10 labels or containing labels from a different project
- [ ] Create/rename surface the unique-name violation distinctly so the router can map it to the `conflict` error code

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - label repository: CRUD, assignment replacement, task-count queries

**Technical Notes:**
- Run `replaceTaskLabels` inside a transaction (delete + insert) so the set change is atomic
- Detect the Postgres unique-violation error (code 23505) instead of pre-checking with a SELECT, to stay race-free

---

## Backend

### T-004: Author API spec shards for label endpoints

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/api-spec/endpoints/labels.md` documenting all five label endpoints from work item Section 7, and `docs/api-spec/endpoints/tasks.md` documenting the board list endpoint including the new `labelId` query parameter and embedded labels. Because no API spec exists yet, also create `docs/api-spec/index.md` with the Endpoint Summary rows and an Error Catalog covering every code these endpoints use.

**Rationale:**
Work item Section 7 requires the endpoint shard before implementation, and CLAUDE.md convention 3 forbids using an error code without an Error Catalog row.

**Acceptance Criteria:**
- [ ] All five label endpoints are documented with request/response shapes using the `{ "data": ... }` envelope and list `meta`
- [ ] The 409 `conflict` duplicate-name response and the max-10-labels `validation-error` are specified
- [ ] `docs/api-spec/endpoints/tasks.md` documents the optional `labelId` filter parameter and the labels array embedded in board task items
- [ ] Error Catalog rows exist in `docs/api-spec/index.md` for every code referenced by the new shards (`validation-error`, `conflict`, `not-found`)

**Dependencies:** T-001
**Complexity:** S

**Files to Modify/Create:**
- docs/api-spec/endpoints/labels.md (new) - all five label endpoints
- docs/api-spec/endpoints/tasks.md (new) - board tasks list endpoint including labelId filter and embedded labels
- docs/api-spec/index.md (new) - Endpoint Summary and Error Catalog

### T-005: Implement label CRUD router

**Type:** Backend
**Workflow:** standard

**Description:**
Create `src/api/labels.ts` implementing GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}`, and mount it in `src/api/index.ts`. Validate bodies with Zod (name 1–30 chars, color from the 12-token palette) and map duplicate names to a 409 `ApiError` with code `conflict`.

**Rationale:**
Implements the label management endpoints from work item Section 7 that AC-1, AC-4, AC-5, and AC-6 are built on.

**Acceptance Criteria:**
- [ ] POST returns the created label in the `{ "data": ... }` envelope; a duplicate name (case-insensitive) returns 409 `conflict`
- [ ] GET returns the project's labels with per-label task counts and list `meta`
- [ ] PUT renames/recolors with last-write-wins semantics (no version check), per the Section 9 concurrent-rename edge case
- [ ] DELETE removes the label plus all its assignments and reports the affected-task count in the response
- [ ] Invalid name length or non-palette color maps to `validation-error` via the error middleware

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - label router with Zod validation and ApiError mapping
- src/api/index.ts - mount the labels router

### T-006: Implement task label assignment endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Add PUT `/api/v1/tasks/{id}/labels` to `src/api/tasks.ts`, accepting an array of label IDs that replaces the task's label set via the repository. Reject arrays longer than 10 or containing labels from a different project with a `validation-error`.

**Rationale:**
Backs AC-2 (assign/remove from the detail panel) and the 11th-label edge case from work item Section 9.

**Acceptance Criteria:**
- [ ] PUT with a valid array replaces the set and returns the task's updated labels in the envelope
- [ ] An array of 11+ label IDs returns `validation-error` without modifying any assignments
- [ ] Label IDs that are nonexistent or belong to another project return `validation-error`
- [ ] An empty array is valid and clears all of the task's labels

**Dependencies:** T-003, T-004
**Complexity:** S

**Files to Modify/Create:**
- src/api/tasks.ts - add PUT /tasks/{id}/labels route with Zod schema

### T-007: Embed labels in board response and add labelId filter

**Type:** Backend
**Workflow:** standard

**Description:**
Extend the board tasks query in `src/db/task.ts` so each returned task includes its labels, and add an optional label filter applied in SQL. Wire a validated `labelId` query parameter through GET `/api/v1/projects/{projectId}/tasks` in `src/api/tasks.ts`.

**Rationale:**
Work item Section 10 requires labels inside the existing board response (no per-card fetches) and server-side filtering so results stay correct with pagination (AC-3).

**Acceptance Criteria:**
- [ ] Board response items include each task's labels without per-task queries (single aggregated query)
- [ ] `?labelId=` returns only tasks carrying that label, with pagination `meta.totalCount` reflecting the filtered set
- [ ] Omitting `labelId` returns the full board response unchanged
- [ ] A malformed `labelId` returns `validation-error`

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - board query aggregates labels per task and applies the optional label filter
- src/api/tasks.ts - accept and validate the labelId query parameter

**Technical Notes:**
- Aggregate labels with `json_agg` (or a lateral join) to keep board load a single round-trip, per the Section 10 performance constraint

---

## Frontend

### T-008: Author UI spec shards for label surfaces

**Type:** Documentation
**Workflow:** standard

**Description:**
Create `docs/ui-specification/screens/label-management-dialog.md` specifying the new dialog, `docs/ui-specification/components.md` with the LabelChip entry, and `docs/ui-specification/index.md` containing the Screen Inventory (including the dialog's row) and Section 2.1 with the accent palette. Since no UI spec exists in this project yet, Section 2.1 must define the 12 color tokens themselves.

**Rationale:**
Work item Section 8 requires the screen shard and component entry before frontend work; Section 10's color constraint points at `docs/ui-specification/index.md` Section 2.1, which does not exist yet and must be authored here.

**Acceptance Criteria:**
- [ ] The dialog shard covers create/rename/recolor/delete flows, the duplicate-name inline error, and the delete confirmation stating the affected task count
- [ ] `components.md` specifies LabelChip (name + color; used by board cards, detail panel, and picker) including the +N overflow treatment on cards
- [ ] Section 2.1 defines 12 accent palette tokens whose chip text contrast meets WCAG 2.1 AA (4.5:1)
- [ ] The Screen Inventory lists the Label Management Dialog

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/screens/label-management-dialog.md (new) - Label Management Dialog screen spec
- docs/ui-specification/components.md (new) - shared component inventory with the LabelChip entry
- docs/ui-specification/index.md (new) - Screen Inventory and Section 2.1 accent palette tokens

### T-009: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create `src/ui/components/label-chip.tsx`, a reusable chip rendering a label's name and palette color, usable on task cards, in the detail panel, and in the picker. Colors come exclusively from the accent palette tokens — no new dependencies.

**Rationale:**
Work item Section 8 defines LabelChip as the shared rendering primitive for every label surface; building it once keeps chips visually consistent.

**Acceptance Criteria:**
- [ ] Renders name and color for any of the 12 palette tokens with AA-contrast chip text per the T-008 token definitions
- [ ] Truncates long names (up to the 30-char max) gracefully at card size
- [ ] Introduces no new external dependencies

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared label chip component

### T-010: Build label management dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Create the Label Management Dialog — a new screen opened from the board toolbar — for creating, renaming, recoloring, and deleting project labels with a palette-token color picker. This new user-facing screen needs an HTML mockup for stakeholder approval before implementation; generate it per `.ai-framework/prompts/mockup-generation.md` against the T-008 screen spec.

**Rationale:**
Implements the label CRUD surface behind AC-1, AC-4, AC-5, and AC-6; work item Section 8 classifies new-screen frontend work as mockup-first.

**Acceptance Criteria:**
- [ ] Creating a label with a name and palette color shows it immediately in the project's label list (AC-1)
- [ ] A duplicate name (case-insensitive) shows an inline validation message without closing the dialog (AC-6)
- [ ] Deleting a label first shows a confirmation dialog stating how many tasks are affected (AC-5)
- [ ] Rename/recolor invalidates the label list and board queries so every visible chip updates (AC-4)
- [ ] The color picker offers exactly the 12 palette tokens — no custom colors

**Dependencies:** T-005, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen with label CRUD flows
- src/ui/project-board.tsx - toolbar entry point that opens the dialog

**Technical Notes:**
- Reuse `src/ui/components/dialog.tsx` for the dialog shell and the delete confirmation
- Use TanStack Query mutations invalidating the project's label list and board tasks queries
- Mockup approval gates implementation (see `.ai-framework/prompts/mockup-generation.md`)

### T-011: Add labels picker to task detail panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a "Labels" field to `src/ui/task-detail-panel.tsx` with a multi-select picker showing LabelChip previews of the project's labels, saving via PUT `/api/v1/tasks/{id}/labels`. Changes must appear on the task's board card without a page reload.

**Rationale:**
Implements AC-2 and the 10-label-cap picker behavior from work item Section 9.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists and the board card updates without a reload (TanStack Query invalidation) (AC-2)
- [ ] The picker disables further selection at 10 labels and shows an explanatory tooltip
- [ ] Picker options render LabelChip previews of every project label
- [ ] An API validation failure (e.g., 11th label submitted from a stale client) surfaces an error message and reverts the selection

**Dependencies:** T-006, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - add the Labels field with a multi-select picker

### T-012: Render label chips on board task cards

**Type:** Frontend
**Workflow:** standard

**Description:**
Update `src/ui/components/task-card.tsx` to render up to 3 LabelChips from the labels embedded in the board response, with a "+N" overflow indicator for additional labels. No per-card label fetching.

**Rationale:**
Implements the Project Board card changes from work item Section 8 within the Section 10 board-load constraint, and makes renames/recolors visible on every card (AC-4).

**Acceptance Criteria:**
- [ ] Cards show up to 3 chips with a "+N" overflow indicator when a task has more than 3 labels
- [ ] Chips reflect renames/recolors after a board query refetch, with no card-level fetches (AC-4)
- [ ] Cards without labels render exactly as before

**Dependencies:** T-007, T-009
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/task-card.tsx - render LabelChips with the overflow indicator

### T-013: Add board label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a single-select label filter dropdown to the board toolbar in `src/ui/project-board.tsx`, passing the selected `labelId` into the board query so filtering stays server-side. Handle the zero-match and deleted-while-filtered edge cases from work item Section 9.

**Rationale:**
Implements AC-3 and its edge cases; server-side filtering keeps results correct with pagination per Section 10.

**Acceptance Criteria:**
- [ ] Selecting a label shows only tasks carrying it; clearing the filter restores the full board (AC-3)
- [ ] Zero matching tasks shows the standard empty state with a "Clear filter" action — never a blank board
- [ ] If the filtered label no longer exists after a refetch, the filter clears automatically and a notice is shown
- [ ] The dropdown lists the project's labels as chip previews with a clear-filter option

**Dependencies:** T-005, T-007
**Complexity:** M

**Files to Modify/Create:**
- src/ui/project-board.tsx - toolbar filter dropdown; labelId included in the board query key
- src/ui/components/empty-state.tsx - support an action button for "Clear filter" (if not already supported)

---

## Testing

### T-014: Write label repository unit tests

**Type:** Testing
**Workflow:** standard

**Description:**
Create `tests/db/label.test.ts` covering the label repository against the test database, per CLAUDE.md convention 6. Focus on the business rules the schema and queries enforce.

**Rationale:**
CLAUDE.md requires a unit test per repository; uniqueness, the 10-label cap, and delete cascading are the riskiest logic in this feature.

**Acceptance Criteria:**
- [ ] A case-insensitive duplicate name within a project is rejected, while the same name in a different project succeeds
- [ ] `replaceTaskLabels` enforces the 10-label cap and the same-project rule atomically (no partial writes on failure)
- [ ] Deleting a label removes its assignments, leaves tasks intact, and reports the correct affected-task count
- [ ] `listByProject` returns correct per-label task counts

**Dependencies:** T-003
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - repository unit tests against the test database

### T-015: Write label API integration tests

**Type:** Testing
**Workflow:** standard

**Description:**
Create `tests/api/labels.test.ts` with Supertest coverage of the label router, and extend `tests/api/tasks.test.ts` for the label-assignment endpoint and the board `labelId` filter with embedded labels. Cover the response envelope, error codes, and the Section 9 edge cases end-to-end.

**Rationale:**
CLAUDE.md requires a Supertest integration test per router; these tests verify AC-1, AC-2, AC-3, AC-5, and AC-6 at the API level.

**Acceptance Criteria:**
- [ ] CRUD happy paths return the `{ "data": ... }` envelope, with `meta` on list responses (AC-1)
- [ ] A duplicate name returns 409 `conflict`; invalid name/color returns `validation-error` (AC-6)
- [ ] Assigning an 11th label or a cross-project label returns `validation-error` with no side effects
- [ ] `?labelId=` filters the board correctly and each board task embeds its labels (AC-3)
- [ ] DELETE removes assignments, leaves tasks intact, and reports the affected-task count (AC-5)

**Dependencies:** T-005, T-006, T-007
**Complexity:** M

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - Supertest integration tests for the label router
- tests/api/tasks.test.ts - tests for PUT /tasks/{id}/labels and the board labelId filter

---

## Summary

**Work item:** FEAT-001 — Task Labels (target v1.1).

**Total task count by type:**

| Type | Count | Tasks |
|------|-------|-------|
| Documentation | 3 | T-001, T-004, T-008 |
| Database | 1 | T-002 |
| Backend | 4 | T-003, T-005, T-006, T-007 |
| Frontend | 5 | T-009, T-010, T-011, T-012, T-013 |
| Testing | 2 | T-014, T-015 |

**Estimated complexity distribution:** S ×6 (T-001, T-002, T-004, T-006, T-009, T-012), M ×8 (T-003, T-005, T-007, T-008, T-011, T-013, T-014, T-015), L ×1 (T-010), XL ×0.

**Critical path:** T-001 → T-002 → T-003 → T-005 → T-010 (5 tasks). T-013 and T-015 share the same depth via T-005, but T-010 additionally carries the mockup-first approval gate, making it the schedule risk.

**Risks / open questions:**

- This project has no spec documentation at all, so T-001, T-004, and T-008 create `docs/data-model/index.md`, `docs/api-spec/index.md`, and `docs/ui-specification/index.md` from scratch with only the sections this feature needs. Entries for the existing Task and Project entities and endpoints will need backfilling later.
- Work item Section 10 references accent palette tokens in `docs/ui-specification/index.md` Section 2.1, but that file does not exist — T-008 must define the 12 token values themselves, and they need stakeholder confirmation plus WCAG 2.1 AA contrast validation.
- Work item Section 6 restricts label create/rename/delete to "members with edit rights", but the fixture source shows no authentication/authorization layer. The label router follows whatever pattern the existing routers use; if none exists, permission enforcement needs a decision outside this feature's scope.
- The concurrent-rename edge case is resolved as last-write-wins (Section 9), so no optimistic-locking column is added; stale clients converge on the next board refetch.
- The NFR of a sub-300ms P95 filter round-trip on 500-task boards is untested until real data exists; the `task_labels(label_id)` index and single aggregated board query (T-002, T-007) are the mitigations.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: A project member can create a label with a name (1–30 chars) and a palette color; it immediately appears in the project's label list | T-002, T-005, T-010, T-015 |
| AC-2: A user can assign and remove labels on a task from the task detail panel; changes persist and appear on the board card without a page reload | T-006, T-011, T-012, T-015 |
| AC-3: Selecting a label in the board filter shows only tasks carrying that label; clearing the filter restores the full board | T-007, T-013, T-015 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-005, T-010, T-012 |
| AC-5: Deleting a label removes it from all tasks after an explicit confirmation dialog stating how many tasks are affected | T-003, T-005, T-010, T-015 |
| AC-6: Attempting to create a duplicate label name within the same project returns a validation error and the UI shows an inline message | T-002, T-005, T-010, T-014, T-015 |
