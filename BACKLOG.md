# Framework Backlog

Deferred improvements, documented for future review. Not scheduled; revisit when the
trigger condition appears.

## Pipeline lifecycle gaps (from the manual-steps / independent-sessions review, 2026-07-14)

Context: each pipeline step (brief → tasks → plans → assignment → implementation →
review → completion → docs update → brief merge) runs as an independent session with
only prior artifacts available. Steps 1–3 and 5 are fully covered today; these gaps
are all in the state/lifecycle layer.

| # | Gap | Suggested shape | Revisit when |
|---|-----|-----------------|--------------|
| 1 | Task blocks have no `Status:` / `Assignee:` field — per-task state lives only in the orchestrator | Optional `Status: pending \| planned \| in-progress \| implemented \| reviewed \| done` in the canonical schema; each step's session updates it as its last action; orchestrator stays authoritative, file is the human-readable mirror; validator checks the enum | State drift between orchestrator and files causes a real mistake, or a human can't tell pipeline position from artifacts |
| 2 | No implementation record — nothing links a completed task to its branch/commit/PR | Convention: implementing session appends `**Implemented in:** <ref>` to the task block | First time a review session has to hunt for the diff |
| 3 | No implementation-review prompt — `review-tasks.md` reviews task lists pre-implementation, not code | Sibling prompt `review-implementation.md`: fresh session, input = task block + plan + diff + ACs + CLAUDE.md; run tests/validators first; verdict to `tasks/T-XXX-implementation-review.md` | Step 6 of the pipeline starts running regularly |
| 4 | Closing documentation task is not mandated by the task prompts | Require a final Documentation task in every generated task list, with Files to Modify/Create derived from the work item's impact tables and `validate-specs.py` passing as its acceptance criterion | Batch-at-end docs updates start missing changes |
| 5 | No brief-closure checklist | Closure step in maintenance.md (+ optional `/close-brief` command): all tasks done, docs task done, validate-specs clean, work item Status → Completed with date, traceability updated | First brief reaches step 9 |

Cross-cutting recommendation recorded at the same time: make git commits the step
boundary — each session ends by committing its artifact, so handoffs are atomic and
the orchestrator can detect step completion from the repo.

## Other deferred items

- **LICENSE** — needs an owner decision (proprietary vs open source).
- **Team-scale items** (deferred 2026-07-14): AGENTS.md canonicalization for mixed-tool
  teams, CODEOWNERS per doc layer, CI enforcement of sync/changelog/schema, tracker-first
  work items via MCP, doc-drift detection action. Revisit when a second regular
  contributor joins.
- **Prompt refinements** (research-backed, not yet applied): contrastive (bad) examples
  in task prompts; output budgets on generated artifacts. (U-curve context
  ordering: resolved by EXP-003 — no measurable effect for agentic sessions;
  chat-assembly note added to context-compilation.md.)
- **Best-of-N generation** — orchestrator-side: sample N task lists, discard validator
  failures, fresh-context review the survivors, pick/synthesize. Documented in
  `prompts/review-tasks.md`.

- **`judge_samples` key for run-evals.py** (from EXP-001 addendum 2): judge scores
  within ±1 of `min_score` are noisy (same sample scored 6 and 8 across passes).
  Automate median-of-N judging for gating decisions. Revisit when a judge score
  gates a real decision.
