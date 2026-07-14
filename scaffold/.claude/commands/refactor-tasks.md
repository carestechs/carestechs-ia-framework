---
description: Generate refactoring tasks from an Improvement Proposal (writes tasks/IMP-XXX-tasks.md)
---

Read `.ai-framework/prompts/refactor-tasks.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "Refactoring" (plus any optional files relevant to this improvement).
2. `$ARGUMENTS` is the target Improvement Proposal — a work-item ID (e.g., `IMP-003`) or a path under `docs/work-items/`. If empty, ask which improvement to generate tasks for.
3. Generate the task list following the prompt template's structure and quality criteria.
4. Write the output file per the routing table's Output column: `tasks/IMP-XXX-tasks.md` — do not leave results only in chat.
5. After writing the task list, run `python .ai-framework/tools/validate-tasks.py tasks/IMP-XXX-tasks.md` and fix every error.
