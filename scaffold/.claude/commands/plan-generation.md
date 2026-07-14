---
description: Generate an implementation plan for a task (writes plans/plan-T-XXX-short-title.md)
---

Read `.ai-framework/prompts/plan-generation.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "Task implementation plan" — `CLAUDE.md`, the task definition, and the files listed in the task's "Files to Modify/Create".
2. `$ARGUMENTS` is the target task ID (e.g., `T-035`) from a task list under `tasks/`. If empty, ask which task to plan.
3. Check the task's Workflow field and follow the Workflow Enforcement rules in CLAUDE.md before planning.
4. Write the output file per the routing table's Output column: `plans/plan-T-XXX-short-title.md` — do not leave results only in chat.
