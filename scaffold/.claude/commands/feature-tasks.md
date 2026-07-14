---
description: Generate a feature task list from a Feature Brief (writes tasks/FEAT-XXX-tasks.md)
---

Read `.ai-framework/prompts/feature-tasks.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "New feature" (plus any optional files relevant to this feature).
2. `$ARGUMENTS` is the target Feature Brief — a work-item ID (e.g., `FEAT-001`) or a path under `docs/work-items/`. If empty, ask which feature to generate tasks for.
3. Generate the task list following the prompt template's structure and quality criteria.
4. Write the output file per the routing table's Output column: `tasks/FEAT-XXX-tasks.md` — do not leave results only in chat.
