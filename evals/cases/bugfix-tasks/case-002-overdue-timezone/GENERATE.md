# Case 002 — Generate Bug Fix Tasks for BUG-001 (Overdue Filter Timezone)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/bugfix-tasks/case-002-overdue-timezone/`).

## Setup

- Treat `input/` as the project root: `input/CLAUDE.md` is the project's CLAUDE.md, `input/docs/` its documentation set, `input/src/` its source tree.
- Do not modify anything under `input/`.
- This fixture has no `stakeholder-definition.md` or persona documents.
- The bug's Status is **Reported** and its Root Cause & Resolution section (Section 10) is deliberately unfilled — the investigation has not happened yet. The generated tasks perform it; do not treat the Section 6 hypothesis as an established root cause.

## Context to Read

1. `input/CLAUDE.md`
2. `input/docs/work-items/BUG-001-overdue-filter-timezone.md` — the bug report
3. `input/docs/data-model/index.md` + the entity shards named by the bug report's Affected Entities table (Section 7)
4. `input/docs/api-spec/index.md` + the endpoint shards named by the same table
5. `input/docs/ui-specification/index.md` + the screen shards named by the same table

The bug report's Section 7 retrieval key is the shard list — do **not** read whole spec directories.

## Procedure

1. Follow `../../../../prompts/bugfix-tasks.md` **end-to-end** — Guidance, the three-phase structure (Phase 1 Investigation → Phase 2 Implementation → Phase 3 Verification & Prevention, enforced through Dependencies), Output Format (including the Summary Section), Constraints, and Post-Generation Checklist — using the canonical task schema from `../../../../prompts/base-template.md` (field list and order; `Type` enum delta: adds `Investigation`).
2. In every task's **Files to Modify/Create**, write paths relative to the project root (`input/`), and suffix every file that does not yet exist under `input/` with `(new)` — code files, tests, and spec shards alike.
3. Investigation tasks come first and identify the root cause; fix tasks address the root cause, not the symptom; verification tasks include a test that would have caught this exact bug plus boundary conditions.

## Output

Write the complete task list to `output/tasks.md` (relative to this directory). The file **is** the deliverable — not chat output. The framework's usual `tasks/BUG-XXX-tasks.md` location does not apply inside the eval harness; `output/tasks.md` replaces it.

## Self-Check Before Finishing

Run, from this directory:

```
python ../../../../tools/validate-tasks.py output/tasks.md --root input
```

and fix every error it reports. (No `--work-item` — the bug report defines no acceptance-criteria checklist to cross-check.)
