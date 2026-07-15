# Case 901 — Generate Feature Tasks for FEAT-001 WITHOUT Spec Docs (experimental arm)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/feature-tasks/case-901-task-labels-minimal-context/`).

> **Experimental arm.** This case is the "without spec docs" arm of the context A/B
> experiment: identical to case-001-task-labels except the fixture contains no spec
> documentation. That is intentional — do not attempt to locate or reconstruct spec
> shards before generating.

## Setup

- Treat `input/` as the project root: `input/CLAUDE.md` is the project's CLAUDE.md, `input/docs/` its documentation set, `input/src/` its source tree.
- Do not modify anything under `input/`.
- This fixture has no `stakeholder-definition.md` or persona documents — the work item's Feature Scope (Section 4) is the scope authority.
- This project has **no spec documentation**: there is no `docs/data-model/`, `docs/api-spec/`, or `docs/ui-specification/`. The work item and CLAUDE.md are the only documentation.

## Context to Read

1. `input/CLAUDE.md`
2. `input/docs/work-items/FEAT-001-task-labels.md` — the work item

That is the complete context. The shard paths named by the work item's impact tables (Sections 6–8) do not exist yet; the feature's tasks create them.

## Procedure

1. Follow `../../../../prompts/feature-tasks.md` **end-to-end** — Guidance (including Workflow Classification), Output Format, Constraints, and Post-Generation Checklist — using the canonical task schema from `../../../../prompts/base-template.md` (field list and order, Type/Workflow/Complexity enums, grouping scheme).
2. In every task's **Files to Modify/Create**, write paths relative to the project root (`input/`), and suffix every file that does not yet exist under `input/` with `(new)` — code files, migrations, tests, and new spec shards alike (e.g., `docs/data-model/entities/label.md (new)`).
3. End the task list with the mandatory `## Acceptance Criteria Coverage` table mapping every acceptance criterion (AC-1 … AC-6) to the task IDs that cover it.

## Output

Write the complete task list to `output/tasks.md` (relative to this directory). The file **is** the deliverable — not chat output. The framework's usual `tasks/FEAT-XXX-tasks.md` location does not apply inside the eval harness; `output/tasks.md` replaces it.

## Self-Check Before Finishing

Run, from this directory:

```
python ../../../../tools/validate-tasks.py output/tasks.md --work-item input/docs/work-items/FEAT-001-task-labels.md --root input
```

and fix every error it reports.
