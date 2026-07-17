# Implementation Review: T-002 Label CRUD Endpoints

**Task:** T-002 (tasks/FEAT-001-tasks.md) · **Plan:** plans/plan-T-002-label-crud-endpoints.md
**Diff:** git diff main..feat/FEAT-001-T-002-labels (input/diff.md) · **Reviewed:** 2026-07-16
**Evidence (frozen, EVIDENCE.md):** tests NOT RUNNABLE (fixture has no package.json/dependencies; `tests/api/labels.test.ts` never executed — static reading only) · linters UNAVAILABLE (no lint config) · validate-specs.py over merged docs: **0 errors, 1 warning** — `docs/api-spec/index.md: WARN: existing shard endpoints/labels.md is not mentioned in this index`.

AC numbering below follows the plan's Acceptance Verification: AC-1 = standard envelope on all five operations, AC-2 = duplicate name returns the error-catalog error.

## Verdict

**revise** — R-1 is a CONFIRMED unmet acceptance criterion: no code path maps a duplicate label name to the catalog's 409 `conflict`, on create or on rename. R-2 is CONFIRMED out-of-scope contract surface (a CSV export endpoint neither the task nor the plan contains). R-3–R-5 are CONFIRMED medium findings (undocumented PUT-for-PATCH deviation, skipped index update flagged by the validator, happy-path-only tests) that independently require revision.

## Findings

| ID | Severity | Class | AC/Plan Ref | Finding | Required Change |
|----|----------|-------|-------------|---------|-----------------|
| R-1 | high | CONFIRMED | AC-2; Plan Steps 3–4, Edge Cases | AC-2 requires a duplicate name within a project to return the catalog error — index Section 2.5 maps uniqueness conflicts to 409 `conflict`. Neither handler implements it: `POST /projects/:projectId/labels` in src/api/labels.ts calls `labelRepo.create` with no duplicate check and no mapping of the repository's uniqueness violation, and `PUT /labels/:id` calls `labelRepo.replace` the same way — the plan's Edge Cases warn against exactly this ("never a raw driver error"). The new shard confirms the gap: its POST and PUT status-code lists have no 409. | Map the `(project_id, name)` uniqueness violation to `ApiError` 409 `conflict` (message naming `name`) in both the create and rename paths; add 409 `conflict` to the shard's POST and PUT status codes. |
| R-2 | high | CONFIRMED | — (scope, rubric 3); Plan Files Affected | `GET /api/v1/labels/export` (CSV dump) appears in src/api/labels.ts, in the shard's frontmatter `routes` and its own section, and in a test — but in neither the task's Files/ACs nor the plan; the plan's Edge Cases explicitly draw the scope boundary. It adds public contract surface and also bypasses the envelope (CLAUDE.md convention 2: every success response is `{ "data": ... }`) and pagination conventions, returning raw `text/csv` for up to 1000 unpaginated rows with no project-existence check. | Remove the export endpoint, its shard section and frontmatter route entry, and its test; if export is wanted, propose it as its own task. |
| R-3 | medium | CONFIRMED | Plan Step 4 | The plan specifies `PATCH /api/v1/labels/{id}` as a partial update (`name?`/`color?`, at least one required, empty body → `validation-error`), mirroring `PATCH /api/v1/tasks/{id}`. The diff implements `PUT` with both fields required (`labelReplaceSchema`, src/api/labels.ts) and documents PUT in the shard. Nothing in the diff records or justifies the deviation — an undocumented plan deviation (rubric 2), and it breaks the resource-consistency rationale the plan gave. | Implement PATCH partial update per Plan Step 4 (or surface and justify the deviation for approval); update the shard's method, request-body semantics, and the test accordingly. |
| R-4 | medium | CONFIRMED | Plan Step 8; rubric 5 (spec sync); index usage note 5 | `docs/api-spec/index.md` is untouched by the diff: no Endpoint Summary rows for the label routes and no Changelog entry, both required by Plan Step 8 and the index's usage note 5. Evidence: validate-specs.py warning quoted in the header — the new shard is unreachable from the index, which "doubles as the shard directory". | Add the label endpoints to index Section 4 (Endpoint Summary) pointing at `endpoints/labels.md`, and add a Changelog row for the addition. |
| R-5 | medium | CONFIRMED | AC-2; rubric 6 | tests/api/labels.test.ts covers only success paths (list envelope, create + name normalization, PUT, delete, CSV export). No test asserts the duplicate-name 409 (AC-2's behavior), nor any error path the shard documents (404 unknown project/label, 400 invalid body). Per EVIDENCE.md the suite has also never run. | Add error-path tests alongside the R-1 fix: duplicate name on create and on rename → 409 `conflict`; unknown project/label → 404; invalid body → 400 `validation-error`. |
| R-6 | low | CONFIRMED | Plan Step 7 | The shard's route sections omit the parameter tables and status-code tables Plan Step 7 specifies ("mirroring docs/api-spec/endpoints/tasks.md"), using one-line summaries instead. Content survives, so structure-only; the validator reports the shard itself as well-formed. | Expand the shard's route sections to the tasks.md table structure (auth/roles, path/query parameters, status-code tables). |

Rubric points examined: 1 (AC-1 envelope: met — all four implemented routes return `{ "data": ... }`, list adds `meta`, delete returns 200 with the deleted label per Plan Step 5; AC-2: unmet, R-1), 2 (R-3), 3 (R-2), 4 (clean apart from the envelope breach folded into R-2 — Zod schemas beside handlers, SQL only via `labelRepo`, `ApiError` + middleware, naming and test location all per CLAUDE.md), 5 (R-4), 6 (R-5).

## Required Changes Before Completion

- [ ] R-1: Return the catalog's 409 `conflict` for duplicate label names on both create and rename; document 409 in the shard's POST and PUT (or PATCH, per R-3) status codes.
- [ ] R-2: Remove `GET /api/v1/labels/export` (handler, shard frontmatter route + section, test); re-propose as a separate task if desired.
- [ ] R-3: Restore the planned PATCH partial-update contract (or document and justify the PUT deviation); align shard and test.
- [ ] R-4: Update docs/api-spec/index.md — Endpoint Summary rows for the label routes + Changelog entry — clearing the validate-specs.py warning.
- [ ] R-5: Add error-path tests: duplicate name → 409 on create and rename, unknown project/label → 404, invalid/empty body → 400.

R-6 is advisory (low) and does not block completion.
