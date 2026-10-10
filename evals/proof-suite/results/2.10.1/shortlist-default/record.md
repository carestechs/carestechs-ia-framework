# shortlist / default on framework 2.10.1

The first live proof-suite run, written at run time per the procedure. Same seven human
inputs as the 2026-08-03 arms; the 2.7.0 default-arm record is the comparison.

| Field | Value |
|---|---|
| Framework version | 2.10.1 (`main` at merge `baf0324`; bundled `.ai-framework/VERSION` 2.10.1) |
| Brief | shortlist v1, as completed in 2.10.2 (seven files; see finding 1). Seed commits `76eb59b` (scaffold 2.10.1 + brief; `CLAUDE.md` = brief's project sections + scaffold's Pre-Work Checklist and framework section) and `e98e2ad` (API-only UI docs added, human-doc stamps set to the seed date) |
| Arm / policy | default: runner built-in defaults (Sonnet workers, Opus task-list and implementation reviewers, Haiku closure) + `policies/testsys-shortlist.json` (`dotnet test`, no UI-spec bootstrap); `--max-steps 120` |
| Runner | carestechs-pipeline-runner `cad172b` (2026-08-31) |
| Models (as reported) | sessions: sonnet 31, opus 12, haiku 1 (`model` on 44 of 96 events; `started` and `artifact_committed` events carry none) |
| Started / finished | 2026-10-09T22:37:58-03:00 to 2026-10-09T23:34:12-03:00, **56 min**; a first attempt at 22:33 died at the bootstrap gate after one $0.36 session (finding 1) |
| Project checkout | `Repos/proof/shortlist-2.10.1-default @ d0bad6a` (54 commits) |
| Exam | v1, run `94b445`, Release build of `d0bad6a` on `http://localhost:5080` |

## Outcome

| Metric | Value | 2.7.0 default arm |
|---|---|---|
| Exam | **16/16** (v1); **19/19** on exam v2, run `313f8c`, 2026-10-10 (`exam-v2.json`) | 16/16 (v1); 19/19 (v2) |
| Work items | FEAT-001 closed by the pipeline (`close(FEAT-001)`, Status flipped to Completed, project `CHANGELOG.md` written); **BUG-001 filed and resolved by the pipeline itself** (finding 3) | FEAT-001 closed |
| Tasks | 13: S 5, M 7, L 1 (Backend 7, Testing 4, DevOps 1, Documentation 1) | 11: S 3, M 7, L 1 |
| First-pass acceptance (event log) | spec generation at gate 1/1; task-list review 1/2; planning 13/13; **implementation review 8/10 (80%)**: T-006 and T-008 revised once each | task-list 0/3; planning 11/11; implementation review 8/12 (67%) |
| Revise rounds | task list **1** (revise, revision, approve); implementation max 1 | task list 3 (cap, accepted by hand); implementation max 2 |
| Human triage | **0** parks, 0 hand marks, 0 escalations (the five overlay marks are the runner's S-task completions: T-001, T-002, T-003, T-005, T-013) | 1 park, 3 hand marks, task-list review accepted by hand |
| Guard | self-approval guard fired once (T-006 fix session rewrote its review file; reverted; fresh re-review approved) | not yet built |
| Agents' own tests (AC-5) | 55 passed, 0 failed; 43 `[Fact]`/`[Theory]`; 19 `.cs` files (7 test files) | 30 passed; 28 declarations; 20 files |
| Validators at close | task list 0 errors / 1 warning (T-011 names `Tests/.../SmokeTests.cs` without `(new)`); specs 0 errors, 0 warnings, 7 stamps fresh | 0 / 0 |
| Steps / sessions | 45 / 44 | 88 events |
| Tokens / notional cost | 277,992 logged / **$15.89** (implementation review 90k, planning 72k, implementation 58k) | 355,939 / $29.75 |
| Current-verdict first-pass (`metrics-report.py`) | 9/9 (100%) vs 80% from the event log: re-reviews overwrote both revise files | 89% vs 67% |
| Mutation kill rate (external measurement, `verify/mutation-kill-matrix@0.1.0`, 2026-10-10, 62 mutants) | raw **61%** (31 killed, 20 survived, 10 invalid, 1 timeout); **78% adjusted** after 11 equivalent survivors (4 log lines, 7 cancellation checks). Real gaps: URL max-length boundary, collision retry loop, custom-code length boundaries 4 and 32, the non-ASCII guard's edges (finding 8) | raw 89%, adjusted 89% |

## Findings

1. **The strict bootstrap gate fails a correct spec session on scaffold artefacts it never
   touched.** First attempt: spec generation produced the data model and API spec in 74 s
   ($0.36), then `validate-specs.py --strict` failed on the scaffold's UI-spec stubs (unfilled
   stamps; this brief has no UI and `bootstrap_ui_spec` is false, so nothing writes them) and
   on `ARCHITECTURE.md` (stamp 67 days old). This is the same failure the 2026-08-03 bootstrap
   hit and a human repaired by hand (`052f580`: "session output salvaged + validator fixes to
   human docs"). Suite-side fix in 2.10.2: the API-only UI docs are human input and part of the
   freeze; stamps are set to the seed date. Still open for the runner (exclude a spec tree it
   will not bootstrap from the strict gate) and the scaffold (an API-only variant of the UI
   docs, or a documented delete). Attribution: tooling, not model.
2. **The task-list review ratchet is gone.** August: three disjoint-finding revise rounds in
   both arms and the attended fixture, cap hit, human accept. Now, on identical inputs: revise,
   one revision ($0.15, 1,128 tokens), approve. This is the first measurement of v2.8.0's
   outcome-anchored verdicts on the brief that motivated them. Framework-side improvement,
   confirmed.
3. **A fresh review found a real defect the exam does not probe, and the pipeline filed its own
   bug.** T-008's review (R-1, CONFIRMED high): a non-ASCII destination URL accepted at creation
   made `GET /{code}` return a bare 500 with an empty body while still counting the click
   (Kestrel rejects the raw `Location` header). R-2 (high): the handler logged the destination
   URL, against `CLAUDE.md`'s rule to log the short code only. The fix session wrote
   `docs/work-items/BUG-001-non-ascii-url-redirect-500.md`, rejected non-ASCII URLs with a 400 at
   creation, removed the URL from the log, and the fresh re-review approved. Exam v1 covers
   percent-encoded URLs (E14) but not raw non-ASCII ones; candidate exam v2 check: a raw
   non-ASCII URL is either rejected with 400 or redirected with a valid encoded `Location`,
   never a 500. The fresh-review investment (90k tokens, 12 Opus sessions) paid for itself here.
4. **Hard-coded listen address, again.** `Program.cs` calls `UseUrls("http://localhost:5080")`
   and ignores `--urls`, identical to the 2.7.0 default arm and unlike the all-Opus control.
   Two for two with Sonnet workers, two for two unflagged by Opus reviewers: the stakeholder
   constraint ("no configuration beyond the listen port") is not a rubric point. The rubric
   candidate from the 2.7.0 record stands, now with a replication.
5. **The implementation-fix prompt still lets a session touch its own review.** The T-006 fix
   session rewrote `tasks/FEAT-001-T-006-implementation-review.md`; the runner's guard (its
   lesson 5) reverted the file and routed the task to a fresh re-review. The guard worked, but
   the framework's step-6 fix prompt and guide say nothing about review artifacts being
   read-only to the fixer. Candidate: state it in `orchestrator-integration.md` step 6 and in
   `next-step.py`'s `implementation-fix` prompt.
6. **Current-verdict acceptance overstates by 20 points** (100% vs 80%), as in every record so
   far. The event log is the number; the scorecard should prefer it when a log exists.
8. **A mutation kill matrix found a latent regression the fresh review approved.** Run on
   2026-10-10 against this build with the `verify/mutation-kill-matrix` playbook: in the
   `BUG-001` fix's non-ASCII guard, changing `c > 0x7E` to `c >= 0x7E` survives every test, and
   would reject every URL containing a tilde. The same matrix shows the 55-test suite kills 78%
   of meaningful mutants where the 30-test August suite kills 89%: more tests, weaker
   boundaries. The suite tests 3 and 33 characters as rejected and never 4 or 32 as accepted;
   so did exam v1, hence exam v2 (E17-E19). Rubric point 6 now asks for boundary cases.
9. **Pipeline hygiene held.** Closure flipped the Status and wrote the repo-level CHANGELOG
   (v2.8.3); S tasks skipped review per the step-7 rule; every per-task artifact used the
   work-item-qualified name (v2.8.5); the Documentation task's `docs:` commit counted as
   evidence (v2.8.2). None of these needed a human.

## Reading

Same inputs, same arm, 67 days apart: the pipeline is more precise (80% vs 67% first-pass,
one review round instead of three, zero human touches instead of five) at about half the
cost and under a third of the wall-clock, and the product passes the same exam. One run is a
smoke test, not a proof; the control arm and a repeat are the next data points.

Raw: `events.ndjson` (96 events), `exam.json`, `report.md` (runner session table).
