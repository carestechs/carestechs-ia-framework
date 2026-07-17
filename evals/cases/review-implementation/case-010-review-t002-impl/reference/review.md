<!-- Known-good reference output — not used by any judge check in this case; kept as
     the hand-written anchor showing a review that catches all five planted defects. -->

# Implementation Review: T-002 Label CRUD Endpoints

**Task:** T-002 (input/tasks/FEAT-001-tasks.md) · **Plan:** input/plans/plan-T-002-label-crud-endpoints.md
**Diff:** input/diff.md (git diff main..feat/FEAT-001-T-002-labels) · **Reviewed:** 2026-07-16
**Evidence (input/EVIDENCE.md, frozen):** tests NOT RUNNABLE (placeholder fixture — `tests/api/labels.test.ts` never executed; test adequacy judged statically) · linters UNAVAILABLE · validate-specs.py on the merged docs: 0 errors, 1 warning — `docs/api-spec/index.md: WARN: existing shard endpoints/labels.md is not mentioned in this index`

## Verdict

**revise** — R-1 is a CONFIRMED high-severity unmet acceptance criterion, and R-2, R-3, and R-4 are CONFIRMED medium findings against the plan and the task's scope. R-5 is advisory. All six rubric points were examined; the envelope criterion (AC-1: all five operations return the standard envelope) and the remaining convention checks passed.

## Findings

| ID | Severity | Class | AC/Plan Ref | Finding | Required Change |
|----|----------|-------|-------------|---------|-----------------|
| R-1 | high | CONFIRMED | AC-2 / Plan Step 3 | Duplicate label names are silently accepted. The `POST /projects/:projectId/labels` handler in `src/api/labels.ts` normalizes the name and inserts — no uniqueness check of any kind against the project's existing labels, and no Error Catalog 409 `conflict`, which AC-2 and Plan Step 3 both require; the replace path shares the gap (Plan Step 4 / Edge Cases: rename to an existing name must also map to `conflict`). `tests/api/labels.test.ts` conspicuously contains no duplicate-name test, so nothing would ever catch this (rubric point 6). | Add the duplicate-name check on create and rename, throw the catalog's 409 `conflict` with a message naming `name`, and add duplicate-name tests for both paths. |
| R-2 | medium | CONFIRMED | Plan Step 8 / api-spec index usage note 5 | Spec sync is incomplete: the diff adds `docs/api-spec/endpoints/labels.md` but never touches `docs/api-spec/index.md` — no Endpoint Summary rows for the new routes and no Changelog entry, both of which Plan Step 8 explicitly requires for a new resource. The frozen validate-specs run (header) confirms the new shard is unreferenced. | Update `docs/api-spec/index.md` in the same change set: Endpoint Summary rows for every route this task ships, plus a Changelog entry. |
| R-3 | medium | CONFIRMED | — (diff-level scope) | Scope creep: `GET /api/v1/labels/export` (CSV export) is implemented in `src/api/labels.ts`, documented in the new shard, and tested — but it appears in no acceptance criterion, no plan step, and T-002's Files to Modify/Create sanction no such capability (rubric point 3). | Remove the export endpoint, its shard section, and its test from this change set; raise it as its own task or work item if wanted. |
| R-4 | medium | CONFIRMED | Plan Step 4 / Plan Overview | Undocumented plan deviation: the plan prescribes `PATCH /api/v1/labels/{id}` (partial update, mirroring the tasks resource's PATCH pattern); the diff ships `PUT` with a full-replacement body requiring both fields (`labelReplaceSchema` and `labelsRouter.put` in `src/api/labels.ts`; the `PUT` section in the new shard). No deviation note exists in the diff, the shard, or the plan — a deviation is not automatically wrong, but an undocumented one is a finding (rubric point 2). | Either implement `PATCH` per the plan, or surface and justify the `PUT` deviation explicitly, then align the shard and tests with whichever contract is chosen. |
| R-5 | low | PLAUSIBLE | CLAUDE.md Conventions 4–5 | Business logic sits inline in the route handler module: `normalizeLabelName` (the stored-name business rule) and `parsePositiveInt` live in `src/api/labels.ts` rather than in the repository or a service module. Zod-next-to-handlers is sanctioned (Convention 4), and no SQL leaks into the router (Convention 5 holds), so this is a judgment call about where entity rules belong — flagged PLAUSIBLE, not CONFIRMED. | Consider moving name normalization into `src/db/label.ts` (or a label service) alongside the R-1 fix. |

## Required Changes Before Completion

- [ ] R-1: Reject duplicate label names on create and rename with the Error Catalog's 409 `conflict`; add duplicate-name tests for both paths.
- [ ] R-2: Update `docs/api-spec/index.md` in the same change set — Endpoint Summary rows for the new routes plus a Changelog entry.
- [ ] R-3: Remove the CSV export endpoint, its shard section, and its test; move that capability to its own task or work item.
- [ ] R-4: Implement `PATCH /api/v1/labels/{id}` per the plan, or document and justify the `PUT` deviation and align the shard and tests.
