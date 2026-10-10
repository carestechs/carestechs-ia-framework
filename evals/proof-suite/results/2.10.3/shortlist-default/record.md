# shortlist / default on framework 2.10.3, with a review playbook injected

The second live run of the brief, and the first with an orchestrator-bound playbook: the
pipeline-runner injected `verify/mutation-kill-matrix@0.2.0` into every implementation-review
session for a Testing-type task. Everything else is identical to the 2.10.1 run (same seven
human inputs, same default policy, same seed procedure), so the 2.10.1 record is the control.

| Field | Value |
|---|---|
| Framework version | 2.10.3 (`main` at merge `63b4596`; bundled `.ai-framework/VERSION` 2.10.3) |
| Brief | shortlist v1 (seven files); seed commit `d123bff` (`CLAUDE.md` = brief's project sections + scaffold 2.10.3 Pre-Work Checklist and framework section; human-doc stamps set to the seed date) |
| Arm / policy | default (Sonnet workers, Opus reviewers, Haiku closure) + `policies/shortlist-kill-matrix.json`: `playbooks.root` = the playbooks checkout; binding `verify/mutation-kill-matrix@0.2.0` on `implementation-review` for `Type: Testing`, over `Shortlist.Api/**/*.cs`, `--skip-lines` for log calls and cancellation checks, budget 50, timeout 120 s |
| Runner | carestechs-pipeline-runner `1824c5b` (playbook registry: `inject_playbooks()`, `--add-dir`, provenance in the review event) |
| Models (as reported) | sessions: sonnet 32, opus 11, haiku 1 (`model` on 44 of 99 events) |
| Started / finished | 2026-10-10T02:59:11-03:00 to 2026-10-10T04:25:24-03:00, **86 min** |
| Project checkout | `Repos/proof/shortlist-2.10.3-default @ 485ffa9` |
| Exam | v2, run `f73fae`, Release build on `--urls http://127.0.0.1:5184` (honoured) |

## Outcome

| Metric | 2.10.3, tool injected | 2.10.1, control |
|---|---|---|
| Exam | **19/19** (v2) | 16/16 (v1), 19/19 (v2) |
| **Mutation kill rate** (baseline settings: all operators, no skip-lines, seed 1, 66 mutants) | raw **92%** (37 killed, 3 survived, 25 invalid, 1 timeout); **100% adjusted**: the 3 survivors are removed log lines, **0 real gaps** | raw 61%; 78% adjusted; 9 real gaps |
| Work items | FEAT-001 closed by the pipeline; 0 parked | FEAT-001 closed; BUG-001 filed and fixed |
| Tasks | 13: S 7, M 6 (Backend 6, Testing 5, DevOps 1, Documentation 1) | 13: S 5, M 7, L 1 (Testing 4) |
| First-pass acceptance (event log) | task-list review 1/2; planning 13/13; **implementation review 6/9 (67%)**: T-007 (before any injection), T-011 and T-012 revised once each, both matrix-driven | implementation review 8/10 (80%) |
| Revise rounds | task list 1; implementation max 1 | same |
| Human triage | **0** parks, 0 hand marks (7 overlay marks are the runner's S-task completions) | 0 |
| Guard | self-approval guard fired once (T-007 fix session rewrote its review) | once (T-006) |
| Agents' own tests (AC-5) | 53 passed; 39 `[Fact]`/`[Theory]` declarations (theories carry the new boundary rows); 18 `.cs` files | 55 passed; 43 declarations |
| Tokens / notional cost | 281,749 / **$17.55** (+1.4% tokens, +$1.66) | 277,992 / $15.89 |
| Wall-clock | 86 min (+30 min: six matrix runs inside review sessions) | 56 min |
| Current-verdict first-pass (`metrics-report.py`) | 9/9 (100%) vs 67% from events | 100% vs 80% |

Review-time matrices (the reviewers' own runs, `--skip-lines`, budget 50, archived here as
`review-kill-matrix-T-0xx.json`): T-009 **29%** (9 killed / 22 survived, all in endpoint code
owned by later tasks) → T-010 **61%** → T-011 **90%** (3 survivors owned by T-012) → T-012
**100%** (31 killed, 0 survived). The suite's strength is visible growing task by task.

## Findings

1. **The reviewers used the instrument as the runbook says, unprompted beyond the injected
   paragraph.** All four Testing-task reviews quote the matrix in their evidence header with
   `slug@version`, operators, seed and budget; every survivor is classified by ownership
   (in-scope: blocking; owned by a later task: advisory with the owner named; T-009's reviewer
   flagged one gap with **no owner in the task list**). Provenance landed in the event log
   (`playbooks=verify/mutation-kill-matrix@0.2.0` on the review events).
2. **Two matrix-driven revises produced exactly the tests the 2.10.1 record said were missing.**
   T-011: four surviving length-boundary mutants (`2048→2049`, `4→5`, `>`→`>=`) became R-1
   CONFIRMED → the fix added `UrlOfLength(2048)` accepted, `UrlOfLength(2049)` rejected, and the
   custom-code 4/32 edges → the re-review re-ran the matrix and showed all four killed. T-012:
   the reviewer read the runbook (via `--add-dir`) and **hand-mutated the route-constraint regex
   `{4,32}`**, which the tool's line-level operators cannot reach (five variants, all surviving)
   → R-1/R-2 CONFIRMED → the fix killed all five, verified by the re-review's manual pass.
   The playbook's "manual way first, script accelerates" rule worked for an autonomous reviewer.
3. **Product-level effect: every gap measured on 2.10.1 is closed.** URL length edge, custom-code
   length edges, collision retry loop (`InMemoryLinkStore`: 8 killed, 0 survived), reserved-code
   and host checks. Adjusted kill rate 78% → 100% on the same operators and seed; the exam
   stayed at full marks, so correctness did not pay for it.
4. **The habit costs wall-clock, not tokens.** +30 min for six matrix runs (about 5 min each inside
   Opus review sessions), +1.4% tokens, +10% notional cost. Reviews that ran the tool took 6 to 8
   minutes against 2 to 3.
5. **First-pass acceptance fell for the right reason.** 80% → 67% because the sensor got stricter:
   two of three revises are the tool's findings and each produced tests. Read first-pass together
   with what the revise rounds produced; a `revised` event whose fix adds tests is not the same
   signal as one that repairs a defect. Candidate: an event `detail` convention for that.
6. **A hygiene regression the tool has nothing to do with: no `.gitignore`.** T-001 ("Create
   solution skeleton", DevOps, S) did not create one; the 2.10.1 build's T-001 did. The runner's
   `git add -A` has therefore committed **456 build files** (`bin/`, `obj/`) since the first
   implementation commit, and S tasks skip review, so nothing could catch it. Attribution: worker
   variance on an unguarded path. Candidates: a sweep guard in the runner's `commit_all` that
   refuses `bin/`, `obj/`, `node_modules/`, `dist/` (the self-approval guard is the precedent); a
   skeleton convention in the scaffold's DevOps guidance; or a `git ls-files` sanity line in the
   S-task completion gate.
7. **The listen-port constraint was honoured this time** (`UseUrls` only when no `urls` setting
   is configured), where both earlier Sonnet builds hard-coded it. One data point against two;
   the rubric probe for stakeholder constraints remains a candidate.
8. **38% of mutants were invalid** (25 of 66), the highest of the four builds: nullable flow
   analysis on negated null checks, plus three in the `ILinkStore` interface file. The rate is
   unaffected, but budget-limited runs lose candidates to them; the runbook's advice to drop
   `negate` on `is null` lines stands.
9. **Pipeline hygiene otherwise held**: closure flipped the Status and wrote the project
   `CHANGELOG.md`; S tasks skipped review; every per-task artifact carried the work-item-qualified
   name.

## Reading

Same brief, same arm, one change: a playbook bound to the review of Testing tasks. The suite went
from killing 78% of meaningful mutants to 100%, the exam stayed at full marks, nobody touched the
computer, and it cost ten percent more and half an hour longer. The instrument is now a review
habit rather than a report. The regression it did not see (the missing `.gitignore`) is the
reminder that the next gap is always outside the current sensor.

Raw: `events.ndjson` (99 events), `exam-v2.json`, `report.md`, `review-kill-matrix-T-009..012.json`.
The baseline-settings matrix of the delivered build is archived with the measuring tool as
`examples/shortlist-2.10.3-default.json`.
