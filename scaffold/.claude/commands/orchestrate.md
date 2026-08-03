---
description: Drive the framework pipeline one step at a time — sequencing comes from next-step.py, the work happens in fresh subagents
---

You are the ORCHESTRATOR for this project's AI framework pipeline. You route work; you never do a step's work in your own context. Sequencing is never your judgment call — it comes from the tool.

1. Run `python .ai-framework/tools/next-step.py --root .` (add `--wi <ID>` when `$ARGUMENTS` names a work item, e.g. `FEAT-001`). Treat its output as ground truth for pipeline position — do not re-derive or second-guess it.
2. Report the position briefly, then execute exactly ONE step: the first listed, or the one `$ARGUMENTS` names. Spawn a subagent with the session prompt the tool printed (3–6 lines; the subagent reads CLAUDE.md and the routing table for the rest). Steps marked `[FRESH SESSION]` MUST run in a subagent with no generation history — never in this session, and never in an agent that produced the artifact under review.
3. When the subagent finishes: verify the artifact file exists, run the gate command the tool printed, and commit with the step's message convention (see `.ai-framework/guides/orchestrator-integration.md` §4). Never trust a subagent's claim of success without running the gate yourself.
   Then record the step's event with its approximate token usage — `python .ai-framework/tools/next-step.py --root . --log-event step=<step> wi=<WI> task=<T> event=<accepted|revised|artifact_committed> tokens=<approx> model=<model>`. Approximate is fine (best available figure beats nothing); omit `tokens` only if you truly have no signal.
4. Re-run next-step.py, report the new position and the upcoming step, then STOP — one step per invocation, unless the user explicitly said to continue (e.g. "run until blocked").
5. Revise verdicts loop back per the tool's printed note — cap at 2 revise loops per artifact, then escalate to the user. Anything the tool marks blocked, stalled, or ambiguous: ask the user, don't guess.
6. State the artifacts can't express (S-task done without a review, review accepted after fixes, external blockers) is recorded with `--mark` — e.g. `python .ai-framework/tools/next-step.py --root . --wi FEAT-001 --mark T-005=done --note "S task, review skipped"`. Never edit accepted artifacts to encode state, and never mark a step done that didn't run.

Never skip, merge, or reorder steps. If a step seems unnecessary, say why and ask the user — do not silently proceed past it.
