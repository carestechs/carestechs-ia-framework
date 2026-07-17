# Implementation Review: T-002 Label CRUD Endpoints

**Task:** T-002 (input/tasks/FEAT-001-tasks.md) · **Plan:** input/plans/plan-T-002-label-crud-endpoints.md
**Diff:** git diff main..feat/FEAT-001-T-002-labels (input/diff.md) · **Reviewed:** 2026-07-16
**Evidence (see input/EVIDENCE.md):** tests NOT RUNNABLE (fixture has no package.json/deps; `tests/api/labels.test.ts` never executed) · linters UNAVAILABLE (no config) · validate-specs 0 errors / 1 warning (`docs/api-spec/index.md`: existing shard `endpoints/labels.md` is not mentioned in this index).

## Verdict

**revise** — R-1 is a CONFIRMED unmet acceptance criterion: duplicate label names are never mapped to the catalog's 409 `conflict` on either create or rename. R-2 ships an out-of-scope public endpoint (`GET /labels/export`). R-3 (PUT vs. planned PATCH), R-4 (index not synced), and R-5 (no error-path tests) also block completion.

## Findings

| ID | Severity | Class | AC/Plan Ref | Finding | Required Change |
|----|----------|-------|-------------|---------|-----------------|
| R-1 | high | CONFIRMED | AC-2 / plan Step 3–4 | The task's second AC and plan Steps 3–4 + Edge Cases require a duplicate name within a project to return the Error Catalog's 409 `conflict` (index §2.5). In `src/api/labels.ts` the POST create handler calls `labelRepo.create(...)` and returns 201 with no duplicate check, and the PUT replace handler calls `labelRepo.replace(...)` with none either — neither catches the repository's uniqueness violation, so a duplicate surfaces as a raw 500, not 409. The new shard's POST/PUT Status Codes tables also omit 409 `conflict`. | Catch the repository uniqueness violation in both create and replace, throw `ApiError` 409 `conflict` with a message naming `name`; add the 409 row to the shard's POST and PUT status codes. |
| R-2 | high | CONFIRMED | — (scope) / plan Files Affected | `GET /api/v1/labels/export` (CSV dump handler in `src/api/labels.ts`) is a sixth endpoint. The task defines five endpoints and the plan four routes across `src/api/labels.ts`, `src/api/index.ts`, and the two docs; export appears in none. It also returns raw `text/csv`, bypassing the `{ "data": ... }` envelope (CLAUDE.md convention 2 / index §2.1), and was smuggled into the shard frontmatter `routes`, a shard section, and a test. | Remove the export route, its shard `routes` entry + section, and its test; if wanted, file it as its own task. |
| R-3 | medium | CONFIRMED | plan Step 4 | Plan Step 4 specifies `PATCH /api/v1/labels/{id}` as a partial update (`name?`, `color?`, at least one required), mirroring `PATCH /api/v1/tasks/{id}`. The diff instead implements `PUT /labels/:id` with `labelReplaceSchema` requiring both `name` and `color`, so recolor-only and rename-only are impossible without resupplying the other field. This is an undocumented deviation (the plan gives no PUT rationale); the shard documents PUT to match. | Implement `PATCH` partial update per the plan (or add a documented, justified deviation note) and realign the shard route/section. |
| R-4 | medium | CONFIRMED | plan Step 8 / spec sync | Plan Step 8 and index usage note 5 require new resources to be added to the Endpoint Summary (§4) with a Changelog row. The diff never touches `docs/api-spec/index.md`, leaving the new shard orphaned. Evidence: validate-specs WARN "existing shard `endpoints/labels.md` is not mentioned in this index". | Add the `/projects/{projectId}/labels` and `/labels/{id}` rows to Endpoint Summary §4 pointing at `endpoints/labels.md`, and add a Changelog entry. |
| R-5 | medium | CONFIRMED | rubric 6 / AC-2 | The added `tests/api/labels.test.ts` asserts only happy paths (list, create, replace, delete) plus the out-of-scope export; no test covers the duplicate-name `conflict`, `not-found`, or `validation-error` paths the ACs name, so the R-1 gap would ship untested even once the suite runs. | Add a duplicate-name → 409 `conflict` test (create and rename) and not-found/validation cases alongside the R-1 fix. |

## Required Changes Before Completion

- [ ] R-1: Map the repository's uniqueness violation to `ApiError` 409 `conflict` (naming `name`) in both create and rename; add 409 to the shard's POST/PUT status codes.
- [ ] R-2: Remove the out-of-scope `GET /api/v1/labels/export` endpoint, its shard route/section, and its test.
- [ ] R-3: Replace `PUT` full-replace with the planned `PATCH` partial update (or document and justify the deviation) and align the shard.
- [ ] R-4: Add the label routes to `docs/api-spec/index.md` Endpoint Summary (§4) and a Changelog entry.
- [ ] R-5: Add duplicate-name 409, not-found, and validation-error tests to `tests/api/labels.test.ts`.
