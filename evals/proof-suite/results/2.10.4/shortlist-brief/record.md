# shortlist / default + review playbook, on framework 2.10.4, with an orchestration brief

The third live run of the brief, and the first with the pipeline-runner's **orchestration brief**:
a one-page artifact the runner derives from the repository before every step and inlines at the
top of every session prompt (test command and last gate result, validator state, injected
playbooks, position and task states, every committed review's advisories with their verdict, this
run's revise rounds and parks, the last sessions' closing lines). Everything else is identical to
the 2.10.3 run (same seven human inputs, same seed procedure, same default policy with
`verify/mutation-kill-matrix@0.2.0` bound to Testing-task reviews), so the 2.10.3 record is the
control. The question was behavioural, not economic: Shortlist is too small for the re-derivation
cost the brief exists to remove, so the test is whether sessions use a ledger they are handed, and
what that does to their judgement.

| Field | Value |
|---|---|
| Framework version | 2.10.4 (`main` at merge `ce81163`; bundled `.ai-framework/VERSION` 2.10.4) |
| Brief | shortlist v1 (seven files); seed commit `6a2a422` (the 2.10.3 seed tree `d123bff` with the 2.10.4 bundle) |
| Arm / policy | default (Sonnet workers, Opus reviewers, Haiku closure) + `policies/shortlist-brief.json` = the 2.10.3 kill-matrix policy + `"brief": {"enabled": true, "max_chars": 6000}` |
| Runner | carestechs-pipeline-runner `84d6a8d` (orchestration brief: `render_brief`, `refresh_brief` before every step and commit, `BRIEF_INSTRUCTION`, `brief_chars` on `started` events) |
| Models (as reported) | sessions: sonnet 30, opus 9, haiku 1 (`model` on 40 of 93 events) |
| Started / finished | 2026-10-10T07:48-03:00 to 08:20 (killed, 25 sessions, 7/13 tasks) and 13:59 to 14:50 (resumed, 15 sessions): **83 min** of pipeline time; the resumed runner re-derived position from the repository and continued at T-008 |
| Project checkout | `Repos/proof/shortlist-2.10.4-brief @ 6d7d0e1` |
| Exam | v2, run `50ea78`, Release build on `--urls http://127.0.0.1:5184` (honoured) |

The interruption was external: Claude Code's low-memory reaper killed the background runner at
step 27 ("the system is running low on memory"). Fourteen `Shortlist.Api` servers left running by
earlier worker sessions (each had started the app on its own port to probe endpoints through a
detached Git Bash, and none stopped it) were holding about 1 GB. The partial T-008 diff was saved
as a patch, the one touched file reverted, and the same runner command resumed the run; the runner
committed the dead run's event log first ("chore: flush event log from previous run"), so
`events.ndjson` is one continuous record. During the resumed part an external watchdog checked
every 45 s for processes left by finished sessions and found none to stop.

## Outcome

| Metric | 2.10.4, brief on | 2.10.3, control (tool injected, no brief) |
|---|---|---|
| Exam | **19/19** (v2) | 19/19 (v2) |
| **Mutation kill rate** (baseline settings: all operators, no skip-lines, seed 1) | raw **79%** (37 killed, 10 survived, 25 invalid, 3 timeouts of 75); **86% adjusted**: 4 equivalent survivors (three log lines, a `stackalloc` size), **6 real gaps**, all six already in the ledger as advisories (T-010 R-1, T-009 R-1, T-009 R-2) | raw 92% (37 killed, 3 survived, 25 invalid, 1 timeout of 66); 100% adjusted; 0 real gaps |
| Work items | FEAT-001 closed by the pipeline; 0 parked | FEAT-001 closed; 0 parked |
| Tasks | 13: S 7, M 6 (Backend 7, Testing 4, DevOps 1, Documentation 1); **T-012 (Testing) sized S, so it skipped review and the playbook** | 13: S 7, M 6 (Backend 6, Testing 5, DevOps 1, Documentation 1) |
| First-pass acceptance (event log) | task-list review 1/2; planning 13/13; **implementation review 6/7 rounds (86%)**, per task 5/6: T-007 revised once (before any Testing task); T-009, T-010, T-011 approved first pass with the matrix | implementation review 6/9 rounds (67%), per task 3/6: T-007, T-011, T-012 revised once each |
| Revise rounds | task list 1; implementation max 1 | same |
| Human triage | **0** parks, 0 hand marks (7 overlay marks are the runner's S-task completions) | 0 |
| Guard | self-approval guard: 0 firings | fired once (T-007 fix session rewrote its review) |
| Agents' own tests (AC-5) | **69 passed**; 55 `[Fact]`/`[Theory]` declarations; 16 `.cs` files | 53 passed; 39 declarations; 18 files |
| Tokens / notional cost | 285,510 / **$15.31** (+1.3% tokens, **-$2.24**: two fewer Opus review rounds) | 281,749 / $17.55 |
| Wall-clock | 83 min of pipeline time (32 + 51 across the interruption) | 86 min |
| Brief overhead | inlined in 45 of 46 session prompts: 1,104 to 5,735 chars, **mean 4,250** (about 1.1k tokens per prompt) | none |
| Build hygiene | `.gitignore` created by T-001; **0** build files tracked (121 tracked files) | no `.gitignore`; 456 build files tracked |

Review-time matrices (the reviewers' own runs, `--skip-lines`, budget 50, archived here as
`review-kill-matrix-T-0xx.json`): T-009 **39%** whole tree, 81% on the two files it owns →
T-010 **85%** (14/14 on the files it targets) → T-011 **88%**. No matrix ran after T-012's
list/detail/delete tests, because T-012 was an S task; the baseline matrix kills all four
route-registration mutants, so those tests covered the routes anyway.

The three timeouts of the baseline matrix are all endless loops the suite hangs on instead of
failing: `TryUpdate` negated in the click compare-and-swap (the same mutant as every earlier
build), and two new ones in the generator (`filled < CodeLength` negated; `RandomNumberGenerator.Fill`
removed, which makes every code the same and the collision loop endless). T-011's reviewer had
named the second shape in advance (T-009 R-4).

## Findings

1. **Sessions used the ledger instead of re-deriving it.** Every review written with the brief
   (task-list re-review, T-004, T-006, T-007, T-009, T-010, T-011) ends with a "standing advisories"
   section that cites earlier IDs and gives each a status: *resolved by this task* (T-009 closes
   T-004 R-1 and task-list R-4; T-011 closes T-007 R-4 and task-list R-8), *still holds*, *partly
   reduced*, *respected*, or *untouched by this diff; not re-examined*. T-010's reviewer wrote that
   T-006 R-5 "still holds, and is now confirmed by a surviving mutant"; T-011's that T-007 R-8
   "needs an owner (T-012 or T-013)". The task-list re-review stated outright that R-2 to R-8 were
   the previous round's advisories listed with status, not re-raised. No review re-raised a
   recorded advisory as a new finding. The ledger became a cross-session memory with status
   tracking that nobody maintains by hand.
2. **The ledger recorded every gap, and nothing acted on them: adjusted kill rate 100% → 86%.**
   The six real survivors of the delivered build are, exactly, T-010 R-1 (the 2048 URL cap: both
   `2048→2049` and `>`→`>=` survive), T-009 R-1 (the modulo-bias guard: `248→249`, `>=`→`>`) and
   T-009 R-2 (two constructor null guards). Each was written up with a precise required change,
   each marked "cheap to fold in", each left as an advisory because "no AC names it", and no later
   step consumes advisories: the next task's plan did not pick them up, T-013's docs task did not,
   closure did not. In 2.10.3 the comparable survivors (T-011's length-boundary mutants) came back
   as `revise` with the finding CONFIRMED and the fix added the exact-edge tests; the same rubric
   point 6 asks for both sides of every length constraint in both builds. Two readings fit. Reviewer
   variance in treating rubric 6 as blocking: T-010's reviewer reasoned from the task's ACs, 2.10.3
   T-011's from the rubric. Or the brief's framing: the ledger already carried task-list R-2 ("URL
   > 2048 ... untested; extend T-010"), and a reviewer told that recorded advisories are to be cited
   with a status, not raised again, filed the gap that was now inside T-010's own scope as one more
   status line. The instruction cannot tell the two apart; the fix can. Candidates: the brief's
   instruction states that a standing advisory whose subject falls inside the current task's scope
   is a required change, not a status update; and a closure-time fold step (one fix session over
   the open advisories marked cheap, gated by the matrix) so that a ledger has an actor.
3. **The ledger outgrew the page.** Reviews under this rubric carry long `## Advisories` bullets
   (equivalent-mutant adjudications included), so the 6,000-character cap started dropping the
   oldest group at the T-007 review (step 24) and had dropped four of seven groups by the T-011
   review; the omission note ("see `tasks/FEAT-001-*review.md`") sent reviewers to the files, and
   T-011's reviewer still cited T-004 R-2 and task-list R-8 correctly from them. The behaviour held
   through the cap, but the brief's point is to spare that reading. Candidate: fold instead of
   drop. One line per advisory (ID, severity, first clause), and a group older than two tasks
   collapses to its open IDs only ("T-004: R-2 open (T-013); R-1 resolved by T-009"), which needs
   the runner to parse the status words later reviews already use. Harvest only advisory bullets,
   not the equivalence notes that share the heading.
4. **The reviewers probed further than the tool, in every Testing review.** All three quote the
   matrix (whole tree and the task's own files), then add hand-written mutants "in a throwaway copy
   outside the repository" (5, 14 and 16 probes), because the operators do not produce ordering,
   comparer, atomicity, "drop one alternative" or "widen a constant" mutants. The probes found the
   real gaps of finding 2 and classified four equivalents with reasons. Reviews took 10 to 13.5
   minutes against 6 to 8 in 2.10.3; the probes' cost. The runbook's manual path is now the
   reviewers' habit, not an exception; the open operator follow-ups (regex quantifiers, `is null`
   negation) have company: constant widening and alternative dropping.
5. **An S-sized Testing task escaped the playbook.** The task generator sized T-012 S this time
   (M in 2.10.3), so it was completed on green tests with no review and no matrix, right after
   T-011's reviewer wrote "T-012 must kill this mutant; its review should re-run the matrix". The
   binding is by step and task type; size decides whether the step happens at all. No harm this
   time (the routes are covered), by luck. Candidate: Testing-type tasks are never S for review
   purposes, or the task-completion gate runs the bound playbook when a Testing task skips review.
6. **Cost went down because the sensor was softer.** -$2.24 and +1.3% tokens against the control
   come from two fewer Opus review rounds, which is finding 2 seen from the invoice. The 45 inlined
   pages cost about 1.1k tokens each and are invisible in the total. On a project this size the
   brief is close to free either way; the economic case rests on the ChatLens-scale re-derivation
   it was built against, which this suite cannot measure.
7. **Worker variance on an unguarded path, again, in the other direction.** This build's T-001
   created a `.gitignore` and nothing under `bin/` or `obj/` was committed; the 2.10.3 build's T-001
   did not and 456 build files were. Same prompt, same model, same S task without review. The
   runner sweep guard proposed in the 2.10.3 record stands.
8. **One worker skipped its own verification on a false premise.** The first session after the
   resume (T-008) reported that its PowerShell calls were refused (true: workers are allowed `Bash`
   only) and that `dotnet` was "not on the Bash PATH" (false: a headless probe found it, and the
   next worker ran the suite). It shipped the endpoints unbuilt; the gate built and tested them and
   they were right. Across both attempts 9 of 40 sessions tried PowerShell first and were denied.
   Candidate for the runner on Windows: allow PowerShell for implementation steps or tell sessions
   in the prompt which shell is allowed.
9. **Pipeline hygiene otherwise held**: the listen-port constraint was honoured (second build in a
   row), closure flipped the Status and wrote the project `CHANGELOG.md`, S tasks skipped review,
   every per-task artifact carried the work-item-qualified name, and the brief file never reached a
   commit in a session-edited form (the runner rewrites it before `git add`).

## Reading

Same brief, same arm, one change: every session opened with a page the orchestrator wrote from the
repository. Sessions read it. Reviews stopped re-deriving the advisory history and started
maintaining it, with statuses, at no token cost worth measuring; the exam stayed at full marks and
nobody touched the computer. Then the suite's own warning sign showed: the first-pass column went
up and the cost went down while the kill-rate column went down, which is precision bought with a
softer sensor. The ledger remembered every gap and nobody owned them. A memory needs an actor, and
the page needs to fold by status rather than drop by age; both are runner work, measurable on the
next build the same way.

Raw: `events.ndjson` (93 events, both attempts), `exam-v2.json`, `report.md` (the resumed runner's
report; the killed runner wrote none, its 25 session logs are in the runner's `runs/` directory),
`review-kill-matrix-T-009..011.json`. The baseline-settings matrix of the delivered build is archived
with the measuring tool as `examples/shortlist-2.10.4-brief.json`.
