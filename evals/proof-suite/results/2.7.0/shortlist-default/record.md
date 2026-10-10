# shortlist / default on framework 2.7.0

Reconstructed on 2026-10-09 from the preserved checkout, its event log and the runner's
hardening record; the exam was run retroactively against the preserved build. This is the
first full autonomous build the framework ever completed.

| Field | Value |
|---|---|
| Framework version | seeded on 2.6.0 (`36eca2b`), bundle upgraded in-run to 2.7.0 (`7eb1aff`, cut from this run's findings); `.ai-framework/VERSION` at HEAD = 2.7.0 |
| Brief | shortlist v1 (frozen 2026-10-09 from this run's commit `052f580`) |
| Arm / policy | default: `pipeline-runner/policy.json` (Sonnet workers, Opus task-list and implementation reviewers, Haiku closure) + `policies/testsys-shortlist.json` (`dotnet test`, no UI-spec bootstrap) |
| Runner | carestechs-pipeline-runner as of 2026-08-03 (nearest tracked commit `2d85c59`, 2026-08-04) |
| Models (as reported) | `model` field present on 4 of 88 events (sonnet 3, haiku 1); the policy is the record of the rest |
| Started / finished | 2026-08-03T00:05:38-03:00 (seed) to 2026-08-03T03:18:48-03:00 (`close(FEAT-001)`), 3 h 13 min; events 03:06:44Z to 06:18:48Z |
| Project checkout | `Repos/proof/testsys-shortlist @ ac57b5a` (63 commits) |

## Outcome

| Metric | Value |
|---|---|
| Exam | **16/16** (exam v1, run `b796e4`, 2026-10-09, Release build of `ac57b5a` on `http://localhost:5080`); **19/19** on exam v2, run `400c35`, 2026-10-10 (`exam-v2.json`) |
| Work items | FEAT-001 closed; 0 parked at close |
| Tasks | 11: S 3, M 7, L 1 (Backend 6, Testing 4, Documentation 1) |
| First-pass acceptance (event log) | task-list review 0/3; planning 11/11; implementation review 8/12 (67%): T-004, T-006 and T-009 revised, T-009 twice |
| Revise rounds | task list 3 (cap; accepted by hand via `task-review=accepted`); implementation max 2 (T-009) |
| Human triage | 1 park (T-011, "S-task completion blocked: tests red", later marked done); overlay marks T-001, T-002, T-011 done; task-list review accepted after the cap |
| Agents' own tests (AC-5) | 30 passed, 0 failed (`dotnet test`, re-run 2026-10-09); 28 `[Fact]`/`[Theory]` declarations; 20 `.cs` files |
| Tokens / notional cost | 355,939 logged (under-logged, see findings) / $29.75 |
| Current-verdict first-pass (`metrics-report.py`) | 8/9 (89%), versus 67% from the event log: re-reviews overwrote three revise files |
| Mutation kill rate (external measurement, `verify/mutation-kill-matrix@0.1.0`, 2026-10-10, 51 mutants) | raw **89%** (41 killed, 5 survived, 4 invalid, 1 timeout); adjusted 89% (no equivalent survivors). Real gaps: URL max-length boundary, generated-code collision retry loop. The strongest of the three Shortlist suites with the fewest tests |

## Findings

1. **Hard-coded listen address, uncaught.** `Program.cs` calls `UseUrls("http://localhost:5080")`,
   so `--urls` and `ASPNETCORE_URLS` are ignored; the stakeholder definition's constraint "no
   configuration beyond the listen port" implies the port is the one thing that must stay
   configurable. The all-Opus control honoured `--urls`. Attribution: worker-model deviation,
   but also a **review blind spot** that is framework-side: the implementation-review rubric
   (AC satisfaction, plan adherence, scope, conventions, spec sync, test adequacy) has no probe
   for stakeholder constraints, so an Opus reviewer passed it. Candidate rubric addition.
2. **The task-list review ratcheted**: three consecutive revise rounds with disjoint findings,
   reproduced in the control arm and the attended fixture. Framework-side; became v2.8.0
   (outcome-anchored verdicts). Also the measured reason the cap exists.
3. **Event log under-reports.** The runner of that day logged `model` on 4 events and tokens
   on a subset; cost is the runner's own notional figure. Later runner versions log every step
   (the control arm has `model` on 55 of 119). Records from this date lean on the policy file.
4. **Exam and self-grade agree (100% and green).** The exam's value is independence; here it
   confirms the product rather than contradicting the agents' tests. Its job is the future run
   where the two diverge.
5. **Current-verdict acceptance overstates by 22 points** (89% vs 67%). The event log is the
   number to record; the scorecard's current-verdict line is labelled as such but misleads
   when re-reviews overwrite files (same effect seen on Vision Lab: 100% vs 63%).

Raw: `events.ndjson` (88 events), `exam.json`.
