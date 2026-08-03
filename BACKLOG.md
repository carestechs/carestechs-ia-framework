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
| 1 | ~~Task blocks have no `Status:` / `Assignee:` field — per-task state lives only in the orchestrator~~ **Resolved 2026-08-02 (v2.6.0)**, by derivation rather than the suggested in-file field: `tools/next-step.py` derives per-task state from artifacts (review verdicts, commit evidence, plan files) plus the `tasks/<WI>-progress.json` overlay for states artifacts can't express; task blocks stay Status-free by design (artifacts immutable after acceptance, one writer for state) | — | — |
| 2 | No implementation record — nothing links a completed task to its branch/commit/PR | Convention: implementing session appends `**Implemented in:** <ref>` to the task block | First time a review session has to hunt for the diff |
| 3 | ~~No implementation-review prompt~~ **Resolved 2026-07-16**: `prompts/review-implementation.md` written, wired (routing row, command, guides), and measured (case-010) | — | — |
| 4 | Closing documentation task is not mandated by the task prompts | Require a final Documentation task in every generated task list, with Files to Modify/Create derived from the work item's impact tables and `validate-specs.py` passing as its acceptance criterion | Batch-at-end docs updates start missing changes |
| 5 | No brief-closure checklist | Closure step in maintenance.md (+ optional `/close-brief` command): all tasks done, docs task done, validate-specs clean, work item Status → Completed with date, traceability updated | First brief reaches step 9 |

Cross-cutting recommendation recorded at the same time: make git commits the step
boundary — each session ends by committing its artifact, so handoffs are atomic and
the orchestrator can detect step completion from the repo.

## Other deferred items

- ~~**Approve-with-advisories verdict tier**~~ **Resolved 2026-08-03 (v2.8.0)** —
  trigger fired: the all-Opus control arm's third review round blocked on one
  medium with everything else explicitly advisory (ratchet replicated three times
  total across worker models and the /orchestrate fixture). Shipped as an
  outcome-anchored blocking bar in both review prompts' Step 4 (`revise` only for
  CONFIRMED wrong/unbuildable/unverified-as-written findings; severity alone no
  longer blocks) plus a structured `## Advisories` section with a
  never-silently-dropped disposition contract. The §2 verdict regex is unchanged.

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

- **compile-ddrs eval coverage — DORMANT**: no DDR repo exists in the organization yet (confirmed 2026-07-16). The prompt stays shipped but unmeasured; build its eval case the way case-009 froze the real ADR repo, when a DDR repo exists.
