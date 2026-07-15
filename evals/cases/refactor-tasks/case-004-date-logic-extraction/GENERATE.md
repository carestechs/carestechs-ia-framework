# Case 004 — Generate Refactoring Tasks for IMP-001 (Extract Shared Date Logic)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/refactor-tasks/case-004-date-logic-extraction/`).

## Setup

- Treat `input/` as the project root: `input/CLAUDE.md` is the project's CLAUDE.md, `input/docs/` its documentation set, `input/src/` its source tree.
- Do not modify anything under `input/`.
- This fixture has no `stakeholder-definition.md` or persona documents.
- This is refactoring, not enhancement: the proposal's Section 8 constraints (no behavior changes, no new dependencies, incrementally deployable) bind every task.

## Context to Read

1. `input/CLAUDE.md`
2. `input/docs/work-items/IMP-001-extract-date-logic.md` — the improvement proposal
3. `input/docs/data-model/index.md` + the entity shards named by the proposal's Affected Entities table (Section 6)
4. `input/docs/api-spec/index.md` + the endpoint shards named by the same table
5. `input/docs/ui-specification/index.md` + the screen shards named by the same table + `input/docs/ui-specification/components.md`

The proposal's Section 6 table is the retrieval key — do **not** read whole spec directories. `src/lib/dates.ts` does not exist yet; the refactoring creates it.

## Procedure

1. Follow `../../../../prompts/refactor-tasks.md` **end-to-end** — Guidance, the five-phase safety structure (Phase 0 Preparation/safety net → Phase 1 Safe Parallel Implementation → Phase 2 Migration → Phase 3 Cleanup → Phase 4 Verification), Output Format (including the Summary Section), Constraints, and both Post-Generation checklists — using the canonical task schema from `../../../../prompts/base-template.md` (field list and order; `Type` enum delta: adds `Cleanup`).
2. Phase 0 comes first: establish the test-coverage baseline from the proposal's Section 10 and close the gaps **before** any restructuring task; every phase leaves the system in a working state; old code is removed only after both call sites have migrated.
3. In every task's **Files to Modify/Create**, write paths relative to the project root (`input/`), and suffix every file that does not yet exist under `input/` with `(new)` — e.g., `src/lib/dates.ts (new)`.

## Output

Write the complete task list to `output/tasks.md` (relative to this directory). The file **is** the deliverable — not chat output. The framework's usual `tasks/IMP-XXX-tasks.md` location does not apply inside the eval harness; `output/tasks.md` replaces it.

## Self-Check Before Finishing

Run, from this directory:

```
python ../../../../tools/validate-tasks.py output/tasks.md --root input
```

and fix every error it reports. (No `--work-item` — the improvement proposal defines success criteria, not an acceptance-criteria checklist.)
