---
description: Generate investigation and fix tasks from a Bug Report (writes tasks/BUG-XXX-tasks.md)
---

Read `.ai-framework/prompts/bugfix-tasks.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "Bug fix" (plus any optional files relevant to this bug).
2. `$ARGUMENTS` is the target Bug Report — a work-item ID (e.g., `BUG-002`) or a path under `docs/work-items/`. If empty, ask which bug to generate tasks for.
3. Generate the task list following the prompt template's structure and quality criteria.
4. Write the output file per the routing table's Output column: `tasks/BUG-XXX-tasks.md` — do not leave results only in chat.
5. After writing the task list, run `python .ai-framework/tools/validate-tasks.py tasks/BUG-XXX-tasks.md` and fix every error.
