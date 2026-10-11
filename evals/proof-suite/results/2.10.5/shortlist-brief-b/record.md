# shortlist / brief arm (b) on framework 2.10.5: in-scope rule, folded ledger, fold step

Second of the two brief runs of the matched set recorded in
[`../shortlist-brief-experiment.md`](../shortlist-brief-experiment.md).

| Field | Value |
|---|---|
| Framework version | 2.10.5 (bundled `.ai-framework/VERSION` 2.10.5; doctrine identical to 2.10.3) |
| Brief | shortlist v1 (seven files); seed commit `deab14a` (the 2.10.3 seed tree `d123bff` with the 2.10.5 bundle) |
| Arm / policy | default + `policies/shortlist-brief-fold.json` (as brief-a) |
| Runner | carestechs-pipeline-runner `68dfe6c` |
| Models (as reported) | sessions: sonnet 29, opus 10, haiku 1 (`model` on 40 of 89 events) |
| Started / finished | 2026-10-10T19:55-03:00 to 21:19, **84 min** (fold step 9 min), 42 steps, 40 sessions, 48 commits |
| Project checkout | `Repos/proof/shortlist-2.10.5-brief-b @ 138dfb5` |
| Exam | v2, run `374e26`, Release build on `--urls http://127.0.0.1:5188` (honoured) |

## Outcome

- Exam **19/19**. Baseline kill rate raw **86%** (48 killed, 8 survived, 15 invalid, 1 timeout of 72
  candidates); all 8 survivors equivalent (4 log lines, 4 cancellation checks): **0 real gaps, 100%
  adjusted**.
- 12 tasks (S 6, M 6; Testing 3, all M, all reviewed with the matrix). Task list approved first
  pass. Implementation review: 6 tasks, 8 rounds, 6 approve; first pass 4/6; two revises (T-008,
  T-009). Review-time matrices on T-009 to T-011 and on the fold in `review-kill-matrix-*.json`.
- Fold step: 18 open advisories offered; 17 applied (11 already done by the docs task T-012 under
  the in-scope rule, 6 test changes), 1 skipped with a reason; fold review **approve**, review-time
  matrix 100% (39 killed, 0 survived).
- Self-approval guard **0 firings**; 0 parks; closure by the pipeline. **131 tests**, 67
  declarations, at closure. 0 build files tracked. Listen port honoured (`app.Run()`).
- Brief inlined in 42 prompts, mean 3,497 chars (max 4,971); no advisory group dropped.
- Tokens 288,987; notional cost **$15.79**.

Findings and reading: see the experiment record. Raw: `events.ndjson` (89 events), `exam-v2.json`,
`report.md`, `review-kill-matrix-T-009..011.json`, `review-kill-matrix-fold.json`; baseline matrix
`examples/shortlist-2.10.5-brief-b.json` with the measuring tool.
