# FEAT-001 — Task Labels: Implementation Task List

Generated from `docs/work-items/FEAT-001-task-labels.md` (FEAT-001, Target v1.1).

This project has no spec documentation yet; the shards named by the Feature Brief's impact tables (data model, API spec, UI specification) are created by the Documentation tasks below, before the feature logic that relies on them. All paths are relative to the project root; files that do not exist yet are marked `(new)`.

---

## Foundation

### T-001: Author data-model spec shards for Label and TaskLabel

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the data-model index and entity shards for the two new entities, Label and TaskLabel, since no `docs/data-model/` exists yet. Document fields, business rules, and relationships from Section 6 of the Feature Brief, and add Module Ownership and Relationships Overview entries for both entities to the index.

**Rationale:**
Section 6 of the brief requires the new-entity shards to exist before feature logic; downstream tasks and future work items retrieve these shards by path.

**Acceptance Criteria:**
- [ ] `label.md` defines id, projectId, name (1–30 chars, unique per project case-insensitively), color (one of the 12 accent palette tokens), and delete behavior (cascades to assignments only, never to tasks)
- [ ] `task-label.md` defines the N:M join (taskId, labelId), the max-10-labels-per-task rule, and the same-project assignment rule
- [ ] The index contains Module Ownership and Relationships Overview entries for both Label and TaskLabel

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- docs/data-model/index.md (new) - data-model conventions plus Module Ownership and Relationships Overview entries for Label and TaskLabel
- docs/data-model/entities/label.md (new) - Label entity shard
- docs/data-model/entities/task-label.md (new) - TaskLabel join-entity shard

**Technical Notes:**
- Follow CLAUDE.md naming: snake_case tables (`labels`, `task_labels`), camelCase JSON keys (`projectId`, `taskCount`)

### T-002: Create labels and task_labels migration

**Type:** Database
**Workflow:** standard

**Description:**
Add a plain SQL migration creating the project-scoped `labels` table (name + palette color) and the `task_labels` join table. Enforce case-insensitive per-project name uniqueness and referential integrity in the schema.

**Rationale:**
Label and TaskLabel are new entities (Section 6); the schema must exist before the repositories and endpoints that use it.

**Acceptance Criteria:**
- [ ] `labels` has id, project_id FK to projects, name (max 30 chars, not null), color (not null), and a unique index on (project_id, lower(name))
- [ ] `task_labels` has a composite primary key (task_id, label_id) with FKs to tasks and labels, both ON DELETE CASCADE
- [ ] Migration applies cleanly on top of 001-init.sql and follows the NNN-description.sql naming convention

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- migrations/002-labels.sql (new) - create labels and task_labels tables with constraints and indexes

**Technical Notes:**
- Index task_labels(label_id) to support the board filter within the 300ms P95 NFR at 500 tasks
- Deleting a label removes only task_labels rows via cascade — tasks are never touched (Section 6)
- The max-10 rule is enforced at the application layer (T-006), not as a DB trigger

## Backend

### T-003: Author API spec shard for label endpoints and error catalog

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the API spec index (Endpoint Summary + Error Catalog) and the labels endpoint shard covering all five label endpoints from Section 7, plus a tasks endpoint shard documenting the modified board list (optional `labelId` filter, labels embedded in each task row). Seed the Error Catalog with the codes these endpoints use.

**Rationale:**
Section 7 requires endpoint definitions before frontend integration, and CLAUDE.md forbids using an error code without an Error Catalog row — the catalog does not exist yet.

**Acceptance Criteria:**
- [ ] `labels.md` documents GET/POST `/api/v1/projects/{projectId}/labels`, PUT/DELETE `/api/v1/labels/{id}`, and PUT `/api/v1/tasks/{id}/labels` with request/response envelopes and error cases
- [ ] The index Endpoint Summary lists the five label endpoints and the modified board list endpoint
- [ ] The Error Catalog defines `validation-error`, `conflict` (duplicate name, HTTP 409), and `not-found` entries
- [ ] The board list is documented with the optional `labelId` query parameter and a labels array on each task row

**Dependencies:** T-001
**Complexity:** M

**Files to Modify/Create:**
- docs/api-spec/index.md (new) - endpoint summary and error catalog
- docs/api-spec/endpoints/labels.md (new) - contracts for all five label endpoints
- docs/api-spec/endpoints/tasks.md (new) - board list contract including labelId filter and embedded labels

### T-004: Implement label repository

**Type:** Backend
**Workflow:** standard

**Description:**
Create the Label repository module with SQL for list-by-project (including a per-label assigned-task count), create, rename/recolor, and delete. Surface case-insensitive duplicate names distinctly, and return the number of affected task assignments on delete.

**Rationale:**
CLAUDE.md keeps SQL in one repository module per entity; the per-label task count feeds the delete confirmation dialog (AC-5).

**Acceptance Criteria:**
- [ ] listByProject returns each label with its assigned-task count
- [ ] create and update detect duplicate names case-insensitively within the project and signal a conflict distinctly from other failures
- [ ] delete removes the label (assignments removed via cascade) and returns the affected-task count; tasks themselves are untouched

**Dependencies:** T-002
**Complexity:** M

**Files to Modify/Create:**
- src/db/label.ts (new) - Label repository: list with task counts, create, update, delete

**Technical Notes:**
- Rely on the unique index for duplicate detection (catch pg error 23505) instead of a check-then-insert race

### T-005: Implement labels router

**Type:** Backend
**Workflow:** standard

**Description:**
Create the Express router for label CRUD — GET/POST `/api/v1/projects/{projectId}/labels` and PUT/DELETE `/api/v1/labels/{id}` — and mount it in the API index. Validate bodies with Zod (name 1–30 chars, color one of the 12 palette tokens) and map duplicate names to a 409 `conflict` ApiError.

**Rationale:**
Implements the new endpoints from Section 7 so label management has a contract to integrate against (AC-1, AC-4, AC-5, AC-6).

**Acceptance Criteria:**
- [ ] All four label CRUD endpoints return the `{ data }` envelope; the list response includes `meta` per convention and per-label task counts
- [ ] Creating or renaming to a duplicate name (case-insensitive) returns HTTP 409 with error code `conflict` (AC-6)
- [ ] Invalid name length or a non-palette color returns the `validation-error` catalog entry
- [ ] DELETE succeeds and its response carries the affected-task count for client messaging

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/api/labels.ts (new) - labels router with Zod schemas
- src/api/index.ts - mount the labels router

**Technical Notes:**
- Routers never touch pg directly — all SQL goes through src/db/label.ts; throw ApiError and let src/api/errors.ts serialize it
- Concurrent renames are last-write-wins with no version check (Section 9)
- Restrict create/rename/delete to members with edit rights by mirroring the authorization pattern used in src/api/tasks.ts (see Summary risk 3)

### T-006: Implement task label assignment endpoint

**Type:** Backend
**Workflow:** standard

**Description:**
Create the TaskLabel repository and add PUT `/api/v1/tasks/{id}/labels` to the tasks router, replacing the task's full label set from an array of label IDs. Enforce the max-10 rule and reject labels that do not belong to the task's project.

**Rationale:**
AC-2 needs persistent assignment; Section 6 fixes the business rules (max 10 per task, same project only) at the API boundary.

**Acceptance Criteria:**
- [ ] PUT replaces the label set atomically in one transaction and returns the updated label list in the `{ data }` envelope
- [ ] Submitting 11 or more labels returns the `validation-error` catalog entry (Section 9)
- [ ] Label IDs from another project or unknown IDs are rejected without partial writes

**Dependencies:** T-003, T-004
**Complexity:** M

**Files to Modify/Create:**
- src/db/task-label.ts (new) - TaskLabel repository: replace set for a task, same-project validation query
- src/api/tasks.ts - add PUT /api/v1/tasks/{id}/labels with a Zod schema

**Technical Notes:**
- Delete-then-insert inside one transaction keeps replace-set semantics simple
- Validate that all submitted labels belong to the task's project with a single join query

### T-007: Add labels and labelId filter to the board tasks query

**Type:** Backend
**Workflow:** standard

**Description:**
Extend the board tasks query so each returned task row embeds its labels, and add an optional `labelId` query parameter for server-side filtering. Keep pagination and `meta.totalCount` correct under the filter.

**Rationale:**
Section 10 requires labels inside the existing board response (no per-card fetches) and server-side filtering so results stay correct with pagination (AC-3).

**Acceptance Criteria:**
- [ ] GET `/api/v1/projects/{projectId}/tasks` embeds a labels array per task using a single query (no N+1)
- [ ] With `labelId`, only tasks carrying that label are returned and `meta.totalCount` reflects the filtered count
- [ ] Without `labelId`, the current response shape is preserved apart from the added labels array; an unknown labelId yields an empty list, not an error

**Dependencies:** T-002, T-003
**Complexity:** M

**Files to Modify/Create:**
- src/db/task.ts - aggregate labels per task and apply the optional label filter
- src/api/tasks.ts - Zod-validated optional labelId query parameter on the board list

**Technical Notes:**
- Aggregate with json_agg over a LEFT JOIN (or a lateral subquery); filter with an EXISTS subquery on task_labels so pagination is unaffected
- The task_labels(label_id) index from T-002 supports the 300ms P95 filter NFR

## Frontend

### T-008: Author UI specification shards for labels

**Type:** Documentation
**Workflow:** standard

**Description:**
Create the UI spec index with the design-system section — including the Section 2.1 twelve-color accent palette the brief references — plus a Screen Inventory, the Label Management Dialog screen shard, and the shared-components inventory with LabelChip. Verify every palette token gives at least 4.5:1 contrast for chip text.

**Rationale:**
Section 8 requires the new screen shard and the LabelChip component entry; the palette tokens are referenced by Section 10 but defined nowhere in this project yet, so this shard is the prerequisite for all frontend work.

**Acceptance Criteria:**
- [ ] Index Section 2.1 defines exactly 12 named accent palette tokens whose chip text contrast meets WCAG 2.1 AA (4.5:1)
- [ ] The Screen Inventory gains a Label Management Dialog row, and `label-management-dialog.md` specifies the create/rename/recolor/delete flows, the palette picker, and the delete confirmation stating the affected-task count
- [ ] `components.md` documents LabelChip (name + color rendering; used by board cards, detail panel, and picker) alongside the existing shared components (dialog, empty-state, task-card)

**Dependencies:** None
**Complexity:** M

**Files to Modify/Create:**
- docs/ui-specification/index.md (new) - design system including the Section 2.1 accent palette, plus the Screen Inventory
- docs/ui-specification/screens/label-management-dialog.md (new) - new screen specification
- docs/ui-specification/components.md (new) - shared component inventory including LabelChip

**Technical Notes:**
- CLAUDE.md already points to docs/ui-specification/components.md as the component inventory, so match that expectation

### T-009: Build LabelChip shared component

**Type:** Frontend
**Workflow:** standard

**Description:**
Create the reusable LabelChip component that renders a label's name on its palette color, shared by board cards, the detail-panel picker, and the management dialog.

**Rationale:**
Section 8 defines LabelChip as a shared component so chip rendering stays consistent across all three surfaces (AC-2, AC-4).

**Acceptance Criteria:**
- [ ] Renders the label name and palette token color per the components.md spec, with text color meeting AA contrast on every token
- [ ] Supports a compact board-card variant and an optional remove affordance for picker use

**Dependencies:** T-008
**Complexity:** S

**Files to Modify/Create:**
- src/ui/components/label-chip.tsx (new) - shared chip component

### T-010: Build the Label Management Dialog

**Type:** Frontend
**Workflow:** mockup-first

**Description:**
Build the new Label Management Dialog — list, create, rename, recolor, and delete project labels with a 12-token palette picker — opened from the board toolbar. This adds a new user-facing screen: generate an HTML mockup per `.ai-framework/prompts/mockup-generation.md` and obtain approval before implementing. Wire mutations through TanStack Query against the T-005 endpoints.

**Rationale:**
Covers the label lifecycle management surface (AC-1, AC-4, AC-5, AC-6) as the new screen defined in Section 8, which mandates mockup-first classification.

**Acceptance Criteria:**
- [ ] Creating a label makes it appear in the project's label list immediately (AC-1)
- [ ] A duplicate name shows the server's `conflict` error as an inline field message (AC-6)
- [ ] Delete shows a confirmation dialog stating how many tasks are affected before executing (AC-5)
- [ ] Rename/recolor invalidates the label and board task queries so every displayed card updates (AC-4)

**Dependencies:** T-005, T-008, T-009
**Complexity:** L

**Files to Modify/Create:**
- src/ui/label-management-dialog.tsx (new) - dialog screen with palette picker

**Technical Notes:**
- Build on the shared src/ui/components/dialog.tsx
- No new dependencies for the color picker (Section 10) — render the 12 palette tokens as swatch buttons

### T-011: Add labels picker to the Task Detail Panel

**Type:** Frontend
**Workflow:** standard

**Description:**
Add a Labels field to the task detail panel with a multi-select picker showing chip previews; save via PUT `/api/v1/tasks/{id}/labels` and invalidate the board query so the card updates without a page reload.

**Rationale:**
AC-2 requires assigning and removing labels from the detail panel with changes visible on the board immediately.

**Acceptance Criteria:**
- [ ] Assigning and removing labels persists via the replace-set endpoint and survives a reload (AC-2)
- [ ] Board card chips update without a page reload after saving (AC-2)
- [ ] The picker disables further selection at 10 labels and shows an explanatory tooltip (Section 9)

**Dependencies:** T-006, T-008, T-009
**Complexity:** M

**Files to Modify/Create:**
- src/ui/task-detail-panel.tsx - add the Labels field with a multi-select picker and chip previews

**Technical Notes:**
- Invalidate the board tasks query on mutation success (TanStack Query)
- Standard form-field addition to an existing panel — the mockup-first exception for standard form patterns applies

### T-012: Render label chips on board cards and add the label filter

**Type:** Frontend
**Workflow:** standard

**Description:**
Render up to 3 label chips with a "+N" overflow indicator on each board task card, add a single-select label filter dropdown and a Manage-labels entry point to the board toolbar, and drive filtering through the `labelId` query parameter.

**Rationale:**
AC-3 and AC-4 surface labels on the board; Section 10 mandates server-side filtering and forbids extra per-card requests.

**Acceptance Criteria:**
- [ ] Cards show up to 3 chips plus a "+N" indicator using the labels embedded in the board response — no additional requests (Section 10)
- [ ] Selecting a label refetches with `labelId` and shows only matching tasks; clearing the filter restores the full board (AC-3)
- [ ] A zero-match filter shows the standard empty state with a Clear filter action (Section 9)
- [ ] If the filtered label was deleted by another user, the next refetch clears the filter and shows a notice (Section 9)

**Dependencies:** T-007, T-009, T-010
**Complexity:** L

**Files to Modify/Create:**
- src/ui/components/task-card.tsx - render the LabelChip row with the overflow indicator
- src/ui/project-board.tsx - toolbar filter dropdown and Manage-labels entry, filtered refetch, empty state handling

**Technical Notes:**
- Reuse src/ui/components/empty-state.tsx for the zero-match state
- Board refetches also pick up renamed/recolored labels — last-write-wins per Section 9
- Modifies an existing screen following the chip pattern approved via the T-010 mockup, so workflow stays standard

## Testing

### T-013: Write repository unit tests for label data access

**Type:** Testing
**Workflow:** standard

**Description:**
Add unit tests against the test database for the label and task-label repositories and the extended board query, per the CLAUDE.md rule that every repository gets a unit test.

**Rationale:**
Locks in the business rules that live in SQL: case-insensitive uniqueness, delete cascades, the max-10 rule, and filter correctness.

**Acceptance Criteria:**
- [ ] Duplicate names differing only by case are rejected (Section 9)
- [ ] Deleting an assigned label removes only task_labels rows and reports the affected count; tasks remain (AC-5)
- [ ] Replace-set enforces max 10 labels and rejects cross-project labels
- [ ] The board query embeds labels per task and filters by label with a correct total count

**Dependencies:** T-004, T-006, T-007
**Complexity:** M

**Files to Modify/Create:**
- tests/db/label.test.ts (new) - label repository unit tests
- tests/db/task-label.test.ts (new) - task-label repository unit tests
- tests/db/task.test.ts (new) - board query label aggregation and filter cases

### T-014: Write API integration tests for label endpoints

**Type:** Testing
**Workflow:** standard

**Description:**
Add Supertest integration tests for the labels router and extend the tasks router tests to cover label assignment and board filtering, per the CLAUDE.md rule that every router gets an integration test.

**Rationale:**
Verifies every acceptance criterion at the API boundary, including error-catalog codes and response envelopes.

**Acceptance Criteria:**
- [ ] Label CRUD happy paths return `{ data }` envelopes; the list includes `meta` and per-label task counts (AC-1)
- [ ] Duplicate create/rename returns 409 `conflict`, including a duplicate differing only by case (AC-6, Section 9)
- [ ] PUT task labels persists the set, rejects an 11th label with `validation-error`, and rejects cross-project labels (AC-2, Section 9)
- [ ] DELETE removes assignments from tasks (AC-5); the `labelId` filter returns only matching tasks and clearing it restores the full list (AC-3)

**Dependencies:** T-005, T-006, T-007
**Complexity:** L

**Files to Modify/Create:**
- tests/api/labels.test.ts (new) - labels router integration tests
- tests/api/tasks.test.ts - assignment endpoint and labelId filter cases

### T-015: Write UI component tests for label interactions

**Type:** Testing
**Workflow:** standard

**Description:**
Add Vitest component tests for LabelChip, the management dialog, the detail-panel picker, and the board chips/filter, mirroring `src/` per the test-location convention.

**Rationale:**
Covers the UI halves of AC-2 through AC-6 that API tests cannot observe: inline errors, the confirmation dialog, the max-10 tooltip, and the empty state.

**Acceptance Criteria:**
- [ ] The dialog shows the inline duplicate-name message (AC-6) and the delete confirmation with the affected-task count (AC-5)
- [ ] The picker disables at 10 labels with a tooltip; removing a label updates the chips (AC-2)
- [ ] Board cards render at most 3 chips with a "+N" overflow; a zero-match filter shows the empty state with Clear filter (AC-3)
- [ ] A chip re-renders with the new name/color after a label is renamed or recolored (AC-4)

**Dependencies:** T-009, T-010, T-011, T-012
**Complexity:** M

**Files to Modify/Create:**
- tests/ui/components/label-chip.test.tsx (new) - chip rendering and contrast variant tests
- tests/ui/label-management-dialog.test.tsx (new) - dialog flow tests
- tests/ui/task-detail-panel.test.tsx (new) - picker behavior tests
- tests/ui/project-board.test.tsx (new) - chips, filter, and empty-state tests

---

## Summary

Feature Brief: **FEAT-001 — Task Labels** (`docs/work-items/FEAT-001-task-labels.md`).

**Total task count by type:**

| Type | Count | Tasks |
|------|-------|-------|
| Documentation | 3 | T-001, T-003, T-008 |
| Database | 1 | T-002 |
| Backend | 4 | T-004, T-005, T-006, T-007 |
| Frontend | 4 | T-009, T-010, T-011, T-012 |
| Testing | 3 | T-013, T-014, T-015 |
| **Total** | **15** | |

**Complexity distribution:** S: 1 (T-009) · M: 11 · L: 3 (T-010, T-012, T-014) · XL: 0

**Critical path (7 tasks):** T-001 → T-002 → T-004 → T-005 → T-010 → T-012 → T-015

**Risks and open questions:**

1. **Accent palette undefined.** Section 10 points at `docs/ui-specification/index.md` Section 2.1 for the 12 palette tokens, but no UI specification exists in this project. T-008 must define the tokens (with verified WCAG AA chip contrast) and the choice should be confirmed with stakeholders via the T-010 mockup.
2. **Error catalog does not exist yet.** CLAUDE.md forbids using an error code without a catalog row; T-003 seeds the catalog (`validation-error`, `conflict`, `not-found`) before T-005/T-006 can reference the codes.
3. **Edit-rights enforcement is unspecified.** Section 6 restricts label create/rename/delete to members with edit rights, but the project's existing authorization mechanism is not documented. T-005 should mirror whatever pattern `src/api/tasks.ts` uses; if none exists, raise this before implementing rather than inventing an auth scheme (scope risk).
4. **Max-10 enforced at the application layer** (T-006 transaction), not by a database constraint — simple and sufficient at this scale; concurrent replace-set writes serialize on the transaction.

## Acceptance Criteria Coverage

| Work Item AC | Covered By |
|--------------|------------|
| AC-1: Create a label with a name (1–30 chars) and palette color; it immediately appears in the project's label list | T-002, T-004, T-005, T-010, T-014 |
| AC-2: Assign and remove labels on a task from the detail panel; changes persist and appear on the board card without a page reload | T-006, T-011, T-014, T-015 |
| AC-3: Selecting a label in the board filter shows only tasks carrying that label; clearing the filter restores the full board | T-007, T-012, T-014, T-015 |
| AC-4: Renaming or recoloring a label updates every task card that displays it | T-005, T-010, T-012, T-015 |
| AC-5: Deleting a label removes it from all tasks after an explicit confirmation stating how many tasks are affected | T-004, T-005, T-010, T-013, T-014, T-015 |
| AC-6: Creating a duplicate label name in the same project returns a validation error and the UI shows an inline message | T-002, T-005, T-010, T-014, T-015 |
