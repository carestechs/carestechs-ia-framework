# Case 903 — Generate Feature Tasks for FEAT-001 with INVERTED Read Order (experimental arm)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/feature-tasks/case-903-read-order-inverted/`).

> **Experimental arm (EXP-003).** Identical to case-001-task-labels in fixture, prompt,
> and procedure. The single variable is the ORDER in which you read the context: spec
> documents first, conventions second, the work item LAST. Read each file exactly once,
> in exactly the order below, before generating.

## Setup

- Treat `../case-001-task-labels/input/` as the project root: its `CLAUDE.md` is the project's CLAUDE.md, its `docs/` the documentation set, its `src/` the source tree.
- Do not modify anything under `../case-001-task-labels/input/`.
- This fixture has no `stakeholder-definition.md` or persona documents — the work item's Feature Scope (Section 4) is the scope authority.

## Context to Read — in exactly this order

1. `../case-001-task-labels/input/docs/data-model/index.md` + the entity shards `entities/task.md` and `entities/project.md`
2. `../case-001-task-labels/input/docs/api-spec/index.md` + the endpoint shard `endpoints/tasks.md`
3. `../case-001-task-labels/input/docs/ui-specification/index.md` + the screen shards `screens/project-board.md` and `screens/task-detail-panel.md` + `components.md`
4. `../case-001-task-labels/input/CLAUDE.md`
5. `../case-001-task-labels/input/docs/work-items/FEAT-001-task-labels.md` — the work item, read LAST

(These are the same files case-001 reads — its impact-table retrieval keys resolved to explicit paths so the order is fully specified. Shards the work item marks `(new)` do not exist yet; the feature's tasks create them.)

## Procedure

1. Follow `../../../../prompts/feature-tasks.md` **end-to-end** — Guidance (including Workflow Classification), Output Format, Constraints, and Post-Generation Checklist — using the canonical task schema from `../../../../prompts/base-template.md` (field list and order, Type/Workflow/Complexity enums, grouping scheme).
2. In every task's **Files to Modify/Create**, write paths relative to the project root (`../case-001-task-labels/input/`), and suffix every file that does not yet exist there with `(new)` — code files, migrations, tests, and new spec shards alike (e.g., `docs/data-model/entities/label.md (new)`).
3. End the task list with the mandatory `## Acceptance Criteria Coverage` table mapping every acceptance criterion (AC-1 … AC-6) to the task IDs that cover it.

## Output

Write the complete task list to `output/tasks.md` (relative to this directory). The file **is** the deliverable — not chat output.

## Self-Check Before Finishing

Run, from this directory:

```
python ../../../../tools/validate-tasks.py output/tasks.md --work-item ../case-001-task-labels/input/docs/work-items/FEAT-001-task-labels.md --root ../case-001-task-labels/input
```

and fix every error it reports.
