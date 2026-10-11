# shortlist / control arm on framework 2.10.5 (brief off)

The control of the matched set recorded in [`../shortlist-brief-experiment.md`](../shortlist-brief-experiment.md):
the 2.10.3 arm unchanged, built the same afternoon as the two brief runs from the same seed tree,
so the set has a same-day reference instead of the 2.10.3 record alone.

| Field | Value |
|---|---|
| Framework version | 2.10.5 (bundled `.ai-framework/VERSION` 2.10.5; doctrine identical to 2.10.3) |
| Brief | shortlist v1 (seven files); seed commit `1a8444d` (the 2.10.3 seed tree `d123bff` with the 2.10.5 bundle) |
| Arm / policy | default (Sonnet workers, Opus reviewers, Haiku closure) + `policies/shortlist-kill-matrix.json` (`verify/mutation-kill-matrix@0.2.0` on Testing-task reviews); no brief |
| Runner | carestechs-pipeline-runner `68dfe6c` (orphan sweep and PowerShell twins on; brief off) |
| Models (as reported) | sessions: sonnet 33, opus 17, haiku 1 (`model` on 51 of 106 events) |
| Started / finished | 2026-10-10T16:10-03:00 to 18:07, **118 min**, 46 steps, 51 sessions, 62 commits |
| Project checkout | `Repos/proof/shortlist-2.10.5-control @ c318729` |
| Exam | v2, run `961b35`, Release build; the build ignores `--urls` and listens on its pinned `http://localhost:5080` |

## Outcome

- Exam **19/19**. Baseline kill rate raw **77%** (36 killed, 11 survived, 8 invalid, 1 timeout of 56
  candidates); 8 equivalent survivors (3 log lines, 5 cancellation checks); **3 real gaps**, all in
  the collision retry loop bound (`MaxGenerationAttempts 100→101`, `<`→`<=`, loop start `0→1`):
  **92% adjusted**.
- 12 tasks (S 3, M 8, L 1; Testing 4, all M). Task list revise → approve. Implementation review:
  9 tasks, 15 rounds, 9 approve; first pass 4/9; six revises (T-006, T-007 twice, T-008 matrix-driven,
  T-009, T-010). Review-time matrices on T-008 to T-011 in `review-kill-matrix-T-0xx.json`.
- Self-approval guard fired **5 times** (every fix session rewrote its review); 0 parks; closure by
  the pipeline. 70 tests, 54 declarations, at closure. 0 build files tracked.
- Tokens 321,838; notional cost **$22.66**.
- Listen-port constraint **not honoured**: `app.Run("http://localhost:5080")`, as the generated task
  list specified and the T-001 reviewer accepted (R-3, advisory).

Findings and reading: see the experiment record. Raw: `events.ndjson` (106 events), `exam-v2.json`,
`report.md`, `review-kill-matrix-T-008..011.json`; baseline matrix `examples/shortlist-2.10.5-control.json`
with the measuring tool.
