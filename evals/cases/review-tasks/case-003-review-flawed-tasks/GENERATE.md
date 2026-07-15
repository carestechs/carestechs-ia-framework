# Case 003 — Fresh-Context Review of the FEAT-001 Task List

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/review-tasks/case-003-review-flawed-tasks/`).

## Setup

- Treat `input/` as the project root: `input/CLAUDE.md` is the project's CLAUDE.md, `input/docs/` its documentation set, `input/tasks/` its generated task lists.
- Do not modify anything under `input/`.
- You are the **reviewer**, not the generator. You have no generation transcript for this task list — that is the point (`prompts/review-tasks.md`, fresh-context mandate). Do not regenerate or edit the task list; the review file is the deliverable.

## Context to Read

Load **only** (per the review prompt's Required Context):

1. `input/tasks/FEAT-001-tasks.md` — the task list under review
2. `input/docs/work-items/FEAT-001-task-labels.md` — the work item it was generated from
3. Each spec's index plus **only** the shards named by the work item's impact tables (Sections 6–8): `input/docs/data-model/index.md` + named entity shards, `input/docs/api-spec/index.md` + named endpoint shards, `input/docs/ui-specification/index.md` + named screen shards + `input/docs/ui-specification/components.md`. Shards the impact tables mark `(new)` do not exist yet.
4. `input/CLAUDE.md`

Do not read whole spec directories, `docs/rationale/` files, or anything else.

## Procedure

1. **Run both external tools FIRST** and record their output — from this directory:

   ```
   python ../../../../tools/validate-tasks.py input/tasks/FEAT-001-tasks.md --work-item input/docs/work-items/FEAT-001-task-labels.md --root input
   python ../../../../tools/validate-specs.py --root input
   ```

   Treat tool output as ground truth: every error becomes a CONFIRMED finding; warnings qualify the affected findings.
2. Follow `../../../../prompts/review-tasks.md` **end-to-end** — the six-point rubric (AC completeness, scope fidelity, reference reality, dependency logic, sizing, workflow correctness), CONFIRMED/PLAUSIBLE classification with high/medium/low severity, the Step 4 verdict rules, and the Output Format (header with tool results, `## Verdict`, `## Findings` table, `## Required Changes Before Implementation` when the verdict is revise).

## Output

Write the complete review to `output/review.md` (relative to this directory). The file **is** the deliverable — not chat output. The framework's usual `tasks/FEAT-001-review.md` location does not apply inside the eval harness; `output/review.md` replaces it.
