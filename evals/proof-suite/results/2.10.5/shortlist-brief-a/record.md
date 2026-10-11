# shortlist / brief arm (a) on framework 2.10.5: in-scope rule, folded ledger, fold step

First of the two brief runs of the matched set recorded in
[`../shortlist-brief-experiment.md`](../shortlist-brief-experiment.md).

| Field | Value |
|---|---|
| Framework version | 2.10.5 (bundled `.ai-framework/VERSION` 2.10.5; doctrine identical to 2.10.3) |
| Brief | shortlist v1 (seven files); seed commit `b51185f` (the 2.10.3 seed tree `d123bff` with the 2.10.5 bundle) |
| Arm / policy | default + `policies/shortlist-brief-fold.json`: the kill-matrix binding on Testing-task reviews and on the fold review, `"brief": {"enabled": true, "max_chars": 6000, "full_groups": 2, "fold": true, "fold_review": true}` |
| Runner | carestechs-pipeline-runner `68dfe6c` (in-scope rule in `BRIEF_INSTRUCTION`, ledger folding by status, fold step, orphan sweep, PowerShell twins) |
| Models (as reported) | sessions: sonnet 34, opus 15, haiku 1 (`model` on 50 of 104 events) |
| Started / finished | 2026-10-10T18:07-03:00 to 19:55, **108 min** (fold step 10 min), 48 steps, 50 sessions, 57 commits |
| Project checkout | `Repos/proof/shortlist-2.10.5-brief-a @ 5092647` |
| Exam | v2, run `1a02a4`, Release build on `--urls http://127.0.0.1:5187` (honoured) |

## Outcome

- Exam **19/19**. Baseline kill rate raw **81%** (35 killed, 8 survived, 11 invalid, 1 timeout of 55
  candidates); all 8 survivors equivalent (3 log lines, 5 cancellation checks): **0 real gaps, 100%
  adjusted**.
- 13 tasks (S 5, M 7, L 1; Testing 4: T-009 sized S and therefore unreviewed, T-010 to T-012 M).
  Task list approved first pass. Implementation review: 8 tasks, 13 rounds, 8 approve; first pass
  3/8; five revises (T-001, T-004, T-008, T-010, T-012). Review-time matrices on T-010 to T-012 and
  on the fold in `review-kill-matrix-*.json`.
- Fold step: 14 open advisories offered; 12 applied (8 already satisfied by later tasks, which is
  the in-scope rule at work), 2 skipped with reasons; four edits (two task-list lines, two test
  files); fold review **approve**, review-time matrix 100% (34 killed, 0 survived).
- Self-approval guard **0 firings**; 0 parks; closure by the pipeline. **118 tests**, 83
  declarations, at closure. 0 build files tracked. Listen port honoured (`app.Run()`).
- Brief inlined in 48 prompts, mean 3,926 chars (max 5,176); no advisory group dropped.
- Tokens 350,673; notional cost **$20.24**.

Findings and reading: see the experiment record. Raw: `events.ndjson` (104 events), `exam-v2.json`,
`report.md`, `review-kill-matrix-T-010..012.json`, `review-kill-matrix-fold.json`; baseline matrix
`examples/shortlist-2.10.5-brief-a.json` with the measuring tool.
