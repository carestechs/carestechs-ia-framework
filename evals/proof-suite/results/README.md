# Proof-suite results

One directory per framework version, one subdirectory per brief and arm, each holding
`record.md` (the fields in `../README.md` section 7), `exam.json`, `events.ndjson` and,
when the runner produced one, `report.md`. The table below is the index; keep it sorted by
version, newest first, and add a row per record.

| Framework | Brief | Arm | Exam | Impl. review first-pass (events) | Tasks | Human triage | Notional cost | Record |
|---|---|---|---|---|---|---|---|---|
| 2.10.1 | shortlist v1 | default (Sonnet workers) | 16/16 | 8/10 (80%) | 13 | 0 (task-list review approved after one round; pipeline filed and fixed its own BUG-001) | $15.89, 56 min | [record](2.10.1/shortlist-default/record.md) |
| 2.7.0 | shortlist v1 | default (Sonnet workers) | 16/16 | 8/12 (67%) | 11 | 1 park, 3 marks, review accepted at cap | $29.75, 3 h 13 min | [record](2.7.0/shortlist-default/record.md) |
| 2.7.0 | shortlist v1 | control (all-Opus) | 16/16 | 9/13 (69%) | 15 | 0 parks, 6 marks, review accepted at cap | $56.59 | [record](2.7.0/shortlist-control/record.md) |
| 2.7.0 | shortlist v1 | attended (`/orchestrate`) | n/a | n/a (stopped at task-list review cap) | 15 generated | human stopped after loop 2 | n/a | [record](2.7.0/shortlist-attended/record.md) |

The 2.7.0 rows are reconstructions: the runs happened on 2026-08-03 under the framework's
first autonomous-run version, and the exam was applied on 2026-10-09 to the preserved builds.
From 2.10.1 onward, records are written at run time per the procedure in `../README.md`.

Reading the table: the exam column is the correctness number; the first-pass column is the
pipeline's precision; cost is the denominator. A release that moves the first-pass column up
while the exam column stays at full marks has made the flow more precise at no cost to the
product, which is the claim this suite exists to test.
