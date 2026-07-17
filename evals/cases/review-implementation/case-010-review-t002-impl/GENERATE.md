# Case 010 — Fresh-Context Review of the T-002 Implementation

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/review-implementation/case-010-review-t002-impl/`).

## Setup

- Treat `../../feature-tasks/case-001-task-labels/input/` as the project root: its `CLAUDE.md` is the project's CLAUDE.md, its `docs/` the documentation set, its `src/` the source tree. It is **read-only** — do not modify anything under it.
- The artifacts under review live in **this** case's `input/`:
  - `input/tasks/FEAT-001-tasks.md` — the accepted task list (stands in for the framework's `tasks/FEAT-001-tasks.md`);
  - `input/plans/plan-T-002-label-crud-endpoints.md` — the accepted implementation plan (stands in for `plans/plan-T-002-label-crud-endpoints.md`);
  - `input/diff.md` — the implementation diff under review (stands in for `git diff main..feat/FEAT-001-T-002-labels`);
  - `input/EVIDENCE.md` — the frozen Step-1 evidence record (see Evidence below).
- Treat T-002's dependency T-001 as complete on the diff's base branch: its migration, entity shards, and label repository (`src/db/label.ts`) are already delivered there. They are not visible in the fixture project root — that is a fixture limitation, not a finding.
- You are the **reviewer**, not the implementer. You have no implementation transcript — that is the point (`prompts/review-implementation.md`, fresh-session mandate). Do not fix the code, the specs, or the task list; the review file is the deliverable.

## Context to Read

Load **only** (per the review prompt's Required Context):

1. The **T-002 task block** from `input/tasks/FEAT-001-tasks.md` — the single task under review, not the whole list.
2. `input/plans/plan-T-002-label-crud-endpoints.md` — the plan the implementation was supposed to follow.
3. `input/diff.md` — the implementation diff (the object under review).
4. `../../feature-tasks/case-001-task-labels/input/CLAUDE.md` — project conventions.
5. The spec shards T-002 references: `../../feature-tasks/case-001-task-labels/input/docs/api-spec/index.md` (envelope, Error Catalog, pagination, Endpoint Summary) and `../../feature-tasks/case-001-task-labels/input/docs/api-spec/endpoints/tasks.md` (the existing resource shard the labels work mirrors). `docs/api-spec/endpoints/labels.md` is created **by the diff itself** — read it inside `input/diff.md`; it does not exist in the project root.

Do not read whole spec directories, `docs/rationale/` files, or anything else.

## Evidence (Step 1)

`input/EVIDENCE.md` **is** the Step-1 external evidence — the frozen record standing in for tools this placeholder fixture cannot run. Read it FIRST and treat it as ground truth:

- The fixture has **no runnable test suite** and **no linters** — do not attempt `npm test` or `npm run lint`. Recording "tests not runnable / linters unavailable — see EVIDENCE.md" in the review header is itself the correct Step-1 behavior, not a gap to paper over.
- The frozen `validate-specs.py` result over the merged docs is quoted there; use it exactly as you would a live run's output.

## Procedure

Follow `../../../../prompts/review-implementation.md` **end-to-end** — Required Context, Step 1 (evidence, per the substitution above), the six-point rubric (AC satisfaction, plan adherence, scope fidelity, convention compliance, spec sync, test adequacy), Step-3 CONFIRMED/PLAUSIBLE classification with high/medium/low severity, the Step-4 verdict rules, the Output Format (header with evidence summary, `## Verdict`, `## Findings` table, `## Required Changes Before Completion` when the verdict is revise), and the ≤ ~120-line output budget.

## Output

Write the complete review to `output/review.md` (relative to this directory). The file **is** the deliverable — not chat output. The framework's usual `tasks/T-002-implementation-review.md` location does not apply inside the eval harness; `output/review.md` replaces it.
