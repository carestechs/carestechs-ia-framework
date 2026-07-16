# Case 006 — Generate an Implementation Plan for T-002 (Label CRUD Endpoints)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/plan-generation/case-006-plan-label-endpoints/`).

## Setup

- Treat `../../feature-tasks/case-001-task-labels/input/` as the project root: its `CLAUDE.md` is the project's CLAUDE.md, its `docs/` the documentation set, its `src/` the source tree.
- The accepted task list for FEAT-001 lives at `input/tasks/FEAT-001-tasks.md` (in **this** case directory) — it stands in for the framework's `tasks/FEAT-001-tasks.md`.
- The target task is **T-002: Label CRUD endpoints** from that task list.
- Treat T-002's dependency T-001 as complete: its migration, entity shards, and label repository are already delivered.
- Do not modify anything under the project root.

## Context to Read

1. `input/tasks/FEAT-001-tasks.md` — locate T-002 (the task being planned) and its dependency T-001 (what it already delivered).
2. `../../feature-tasks/case-001-task-labels/input/CLAUDE.md` — project conventions.
3. The files named by T-002's **Files to Modify/Create** that exist under the project root: `src/api/index.ts`. (`src/api/labels.ts` and `docs/api-spec/endpoints/labels.md` are `(new)` — created by this very task, so there is nothing to read yet.)
4. Conditional spec context for a Backend task, per the prompt's Required Context: `../../feature-tasks/case-001-task-labels/input/docs/api-spec/index.md` (envelope, error catalog, pagination, endpoint summary) and `../../feature-tasks/case-001-task-labels/input/docs/api-spec/endpoints/tasks.md` (the existing resource shard whose structure the new labels shard mirrors). `endpoints/labels.md` is `(new)` — this task creates it.

## Procedure

1. Follow `../../../../prompts/plan-generation.md` **end-to-end** — its Required Context, Guidance (Plan Generation Rules and Workflow), **Output Format**, and Constraints.
2. Plan exactly one task: T-002. Do not plan, merge, or anticipate work owned by other tasks (T-001's schema and repository, T-003's assignment endpoints, T-004–T-006's UI, T-007's tests).
3. Respect the plan budget: ≤ ~150 lines and ≤ 10 implementation steps, each step naming concrete files and changes (Create / Modify / Delete).
4. Every file in T-002's **Files to Modify/Create** must be covered by at least one step.

## Output

Write the plan to `output/plan.md` (relative to this directory). It replaces the framework's `plans/plan-T-002-label-crud-endpoints.md` inside the harness — the file **is** the deliverable, not chat output.

## Self-Check Before Finishing

There is no validator script for plans. Instead, re-read your plan against the **Post-Generation Checklist** in `../../../../prompts/plan-generation.md` and fix every item that does not hold before finishing.
