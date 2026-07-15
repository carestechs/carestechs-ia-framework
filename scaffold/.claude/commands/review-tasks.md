---
description: Fresh-context adversarial review of a generated task list (writes tasks/<WORK-ITEM-ID>-review.md)
---

Read `.ai-framework/prompts/review-tasks.md` and follow it end-to-end.

**This command MUST run in a fresh session that did NOT generate the task list.** If this conversation produced it, stop and tell the user to re-run `/review-tasks` in a new session.

1. `$ARGUMENTS` is the task list under review — a file under `tasks/` or a work-item ID (e.g., `FEAT-001` → `tasks/FEAT-001-tasks.md`). If empty, ask which task list to review.
2. Read ONLY the context listed in the CLAUDE.md routing table row "Task list review": the task list, its work item, each spec's `index.md` + the shards named by the work item's impact tables, and `CLAUDE.md`. Never load the generator's transcript or rationale files.
3. FIRST run both validators and treat their output as ground truth: `python .ai-framework/tools/validate-tasks.py tasks/<file>.md --work-item docs/work-items/<file>.md` and `python .ai-framework/tools/validate-specs.py`.
4. Review against the prompt's rubric, then write the review per the routing table's Output column: `tasks/<WORK-ITEM-ID>-review.md` — do not leave results only in chat.
