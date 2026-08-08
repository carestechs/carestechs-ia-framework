---
description: Fresh-session adversarial review of an implemented task against its ACs, plan, and conventions (writes tasks/<WORK-ITEM-ID>-<TASK-ID>-implementation-review.md)
---

Read `.ai-framework/prompts/review-implementation.md` and follow it end-to-end.

**This command MUST run in a fresh session that did NOT implement the task.** If this conversation produced the implementation, stop and tell the user to re-run `/review-implementation` in a new session.

1. `$ARGUMENTS` is the task ID to review (e.g., `T-002`), optionally followed by a git ref/range for the diff (e.g., `T-002 main..feat/labels`). If empty, ask which task and which diff/changed files to review.
2. Read ONLY the context listed in the CLAUDE.md routing table row "Implementation review": the task block, its plan (`plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md`), the diff/changed files, `CLAUDE.md`, and the spec shards the task references. Never load the implementer's transcript or rationale files.
3. FIRST gather external evidence and treat it as ground truth: run the project's test suite and linters, plus `python .ai-framework/tools/validate-specs.py` when the task touched spec shards.
4. Review against the prompt's six-point rubric, then write the review per the routing table's Output column: `tasks/<WORK-ITEM-ID>-<TASK-ID>-implementation-review.md` — do not leave results only in chat.
