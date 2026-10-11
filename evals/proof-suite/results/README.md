# Proof-suite results

One directory per framework version, one subdirectory per brief and arm, each holding
`record.md` (the fields in `../README.md` section 7), `exam.json`, `events.ndjson` and,
when the runner produced one, `report.md`. The table below is the index; keep it sorted by
version, newest first, and add a row per record.

| Framework | Brief | Arm | Exam | Kill rate (adjusted) | Impl. review first-pass (events) | Tasks | Human triage | Notional cost | Record |
|---|---|---|---|---|---|---|---|---|---|
| 2.10.5 | shortlist v1 | brief-b: default + kill-matrix playbook + **brief with the in-scope rule, folded ledger and fold step** | v2 19/19 | **100%** (raw 86%; 0 real gaps) | 6/8 rounds (75%) | 12 | 0 | $15.79, 84 min | [record](2.10.5/shortlist-brief-b/record.md) |
| 2.10.5 | shortlist v1 | brief-a: same arm as brief-b | v2 19/19 | **100%** (raw 81%; 0 real gaps) | 8/13 rounds (62%) | 13 | 0 | $20.24, 108 min | [record](2.10.5/shortlist-brief-a/record.md) |
| 2.10.5 | shortlist v1 | control: default + kill-matrix playbook, no brief (same-day reference for the set) | v2 19/19 | 92% (raw 77%; 3 real gaps, the collision-loop bound) | 9/15 rounds (60%) | 12 | 0 | $22.66, 118 min | [record](2.10.5/shortlist-control/record.md) |
| 2.10.4 | shortlist v1 | default + kill-matrix playbook + **orchestration brief** (runner-maintained page inlined in every session prompt) | v2 19/19 | 86% (raw 79%; all 6 real gaps were ledger advisories no step acted on) | 6/7 rounds (86%; no matrix-driven revise) | 13 | 0 | $15.31, 83 min (one external interruption, resumed from the repository) | [record](2.10.4/shortlist-brief/record.md) |
| 2.10.3 | shortlist v1 | default + `verify/mutation-kill-matrix@0.2.0` injected into Testing-task reviews | v2 19/19 | **100%** (raw 92%) | 6/9 (67%; 2 of 3 revises matrix-driven, each adding boundary tests) | 13 | 0 | $17.55, 86 min | [record](2.10.3/shortlist-default/record.md) |
| 2.10.1 | shortlist v1 | default (Sonnet workers) | v1 16/16, v2 19/19 | 78% (raw 61%) | 8/10 (80%) | 13 | 0 (task-list review approved after one round; pipeline filed and fixed its own BUG-001) | $15.89, 56 min | [record](2.10.1/shortlist-default/record.md) |
| 2.7.0 | shortlist v1 | default (Sonnet workers) | v1 16/16, v2 19/19 | 89% (raw 89%) | 8/12 (67%) | 11 | 1 park, 3 marks, review accepted at cap | $29.75, 3 h 13 min | [record](2.7.0/shortlist-default/record.md) |
| 2.7.0 | shortlist v1 | control (all-Opus) | v1 16/16, v2 19/19 | 80% (raw 69%) | 9/13 (69%) | 15 | 0 parks, 6 marks, review accepted at cap | $56.59 | [record](2.7.0/shortlist-control/record.md) |
| 2.7.0 | shortlist v1 | attended (`/orchestrate`) | n/a | n/a | n/a (stopped at task-list review cap) | 15 generated | human stopped after loop 2 | n/a | [record](2.7.0/shortlist-attended/record.md) |

The three 2.10.5 rows are one experiment, compared in
[`2.10.5/shortlist-brief-experiment.md`](2.10.5/shortlist-brief-experiment.md): a same-day control
and two runs of the brief arm, which settled the question the 2.10.4 record left open.

The kill rate is the share of meaningful mutants the agents' own tests catch, measured with the
`verify/mutation-kill-matrix` playbook (its matrices are archived with the playbook); "adjusted"
excludes equivalent mutants such as removed log lines. It is the product-level test-strength
number next to the exam's correctness number.

The 2.7.0 rows are reconstructions: the runs happened on 2026-08-03 under the framework's
first autonomous-run version, and the exam was applied on 2026-10-09 to the preserved builds.
From 2.10.1 onward, records are written at run time per the procedure in `../README.md`.

Reading the table: the exam column is the correctness number; the first-pass column is the
pipeline's precision; cost is the denominator. A release that moves the first-pass column up
while the exam column stays at full marks has made the flow more precise at no cost to the
product, which is the claim this suite exists to test.
