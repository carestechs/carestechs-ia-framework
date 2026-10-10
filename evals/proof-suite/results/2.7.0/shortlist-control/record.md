# shortlist / control (all-Opus) on framework 2.7.0

Reconstructed on 2026-10-09 from the preserved checkout, its event log and the runner's
hardening record; the exam was run retroactively against the preserved build. Seeded from
the same five human inputs as the default arm (`testsys-shortlist @ 052f580`).

| Field | Value |
|---|---|
| Framework version | 2.7.0 (`7eb1aff`), seeded after the default arm's findings were released |
| Brief | shortlist v1 |
| Arm / policy | control: `pipeline-runner/policies/testsys-shortlist-opus.json` (every step on Opus; `dotnet test`; no UI-spec bootstrap) |
| Runner | carestechs-pipeline-runner as of 2026-08-03 (nearest tracked commit `2d85c59`, 2026-08-04) |
| Models (as reported) | `opus` on 55 of 119 events; remainder unlogged (policy: Opus everywhere) |
| Started / finished | 2026-08-03T11:54:10-03:00 (seed) to 2026-08-03T15:10:19-03:00 (`close(FEAT-001)`), 3 h 16 min; events 14:55:50Z to 18:10:18Z |
| Project checkout | `Repos/proof/testsys-shortlist-opus @ c671658` (99 commits) |

## Outcome

| Metric | Value |
|---|---|
| Exam | **16/16** (exam v1, run `79741e`, 2026-10-09, Release build of `c671658` started with `--urls http://127.0.0.1:5182`) |
| Work items | FEAT-001 closed; 0 parked |
| Tasks | 15: S 6, M 7, L 2 (Backend 10, Testing 3, DevOps 1, Documentation 1) |
| First-pass acceptance (event log) | task-list review 0/3; planning 15/15; implementation review 9/13 (69%): T-005, T-006, T-009, T-012 revised once each |
| Revise rounds | task list 3 (cap; accepted by hand); implementation max 1 |
| Human triage | 0 parks; overlay marks six S tasks done (T-002, T-003, T-004, T-010, T-014, T-015) and the task-list review accepted after the cap |
| Agents' own tests (AC-5) | 53 passed, 0 failed (`dotnet test`, re-run 2026-10-09); 42 `[Fact]`/`[Theory]` declarations; 22 `.cs` files |
| Tokens / notional cost | 465,767 logged / $56.59 (1.9x the default arm) |
| Current-verdict first-pass (`metrics-report.py`) | 9/10 (90%), versus 69% from the event log |

## Findings

1. **Same ratchet, same shape.** Three disjoint-finding revise rounds on the task list, as in
   the default arm: the loop is framework-side, not worker-model-side. This replication is the
   attribution the v2.8.0 change rests on.
2. **What Opus workers bought**: finer decomposition (15 tasks vs 11), a DevOps task the
   default arm did not produce, 53 tests vs 30, one revise round at most per task, and zero
   parks. Not fewer review loops on the task list. At 1.9x notional cost. This is the measured
   basis of the runner's standing policy: Sonnet workers, Opus reviewers.
3. **Honoured the listen-port constraint** (`--urls` works; `launchSettings.json` supplies the
   default), where the default arm hard-coded it. One data point, consistent with finding 1 of
   the default record.
4. **Exam and self-grade agree.** 16/16 against 53 green tests; see the default record.

Raw: `events.ndjson` (119 events), `exam.json`.
