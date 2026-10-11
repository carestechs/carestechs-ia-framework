# shortlist on 2.10.5: the orchestration brief, matched set (one control, two brief runs)

The 2.10.4 record ended with a question a single run could not answer: the pipeline-runner's
orchestration brief made reviews maintain an advisory ledger instead of re-deriving it, and the
delivered build's adjusted kill rate fell from 100% to 86% with every surviving gap sitting in that
ledger as an advisory nobody acted on. Reviewer variance or the brief's framing? This set answers
it with three fresh builds of the same brief, on the same day, from the same seed tree (the 2.10.3
seed with the 2.10.5 bundle, which differs from 2.10.3 doctrine only in records), all driven by the
same runner commit (`68dfe6c`):

- **control**: the 2.10.3 arm unchanged (`policies/shortlist-kill-matrix.json`): Sonnet workers,
  Opus reviewers, `verify/mutation-kill-matrix@0.2.0` bound to Testing-task reviews, no brief;
- **brief-a** and **brief-b**: the same plus `policies/shortlist-brief-fold.json`: the brief with
  the **in-scope rule** (an advisory inside the current task's scope is a required change: the
  planner plans it, the reviewer returns revise if it is not done), a ledger that **folds by status**
  (one line per advisory with the status later reviews gave it; older groups collapse to open IDs),
  and the **fold step** before closure (one gated session applies what is still open, a fresh
  review with the matrix checks it).

Two runner changes apply to all three arms and are not under test: an orphan sweep after every
session (the 2.10.4 run was killed by the host's memory reaper under fourteen leftover app servers)
and PowerShell twins for the Windows workers' Bash rules (9 of 40 sessions had been denied). Every
measurement below was taken the same way: exam v2 against a Release build at the address the
server reports, and the baseline matrix with the settings of every earlier record (all operators,
no skip-lines, seed 1, `Program.cs` excluded). Per-build fields and raw files are in the three
subdirectories; this file is the comparison.

## Outcome

| Metric | control | brief-a | brief-b |
|---|---|---|---|
| Exam (v2) | 19/19 | 19/19 | 19/19 |
| **Adjusted kill rate** (baseline matrix) | **92%**: raw 77% (36 killed, 11 survived, 8 invalid, 1 timeout of 56); 8 equivalent, **3 real gaps** (the collision-loop bound: `100→101`, `<`→`<=`, `0→1`) | **100%**: raw 81% (35/8/11/1 of 55); 8 equivalent (3 log lines, 5 cancellation checks), **0 real gaps** | **100%**: raw 86% (48/8/15/1 of 72); 8 equivalent (4 log lines, 4 cancellation checks), **0 real gaps** |
| Tasks | 12: S 3, M 8, L 1; Testing 4, all M, all reviewed with the matrix | 13: S 5, M 7, L 1; Testing 4: **T-009 sized S, skipped review**, T-010 to T-012 M | 12: S 6, M 6; Testing 3, all M, all reviewed |
| Task-list review | revise → approve | approve first pass | approve first pass |
| Implementation review (event log) | 9 tasks, 15 rounds, 9 approve (60%); first pass 4/9; 6 revises (T-007 twice; T-008 matrix-driven) | 8 tasks, 13 rounds, 8 approve (62%); first pass 3/8; 5 revises | 6 tasks, 8 rounds, 6 approve (75%); first pass 4/6; 2 revises |
| Self-approval guard | **5 firings** (T-006, T-007 ×2, T-008, T-010: every fix session rewrote its review) | 0 | 0 |
| Human triage | 0 parks, 0 marks | 0 | 0 |
| Fold step | none | 14 open advisories offered; 12 applied (8 already satisfied by later tasks), 2 skipped with reasons; review **approve**, review-time matrix 100% (34/0/11/1) | 18 offered; 17 applied (11 already done by the docs task T-012, 6 test changes), 1 skipped; review **approve**, matrix 100% (39/0/10/1) |
| Agents' tests at closure | 70 passed; 54 declarations | **118** passed; 83 declarations | **131** passed; 67 declarations |
| Tokens / notional cost | 321,838 / **$22.66** | 350,673 / $20.24 | 288,987 / $15.79 |
| Pipeline time | 118 min | 108 min (fold 10) | 84 min (fold 9) |
| Brief overhead | none | 48 prompts, mean 3,926 chars, max 5,176; no group ever dropped | 42 prompts, mean 3,497, max 4,971; none dropped |
| Listen-port constraint | **not honoured**: `app.Run("http://localhost:5080")`, specified by the generated task list, accepted by the T-001 reviewer as an advisory | honoured (`app.Run()`) | honoured |
| Build hygiene | 0 build files tracked | 0 | 0 |

Review-time matrices (the reviewers' own runs, `--skip-lines`, budget 50): control T-008 **56%** →
T-009 85% → T-010 85% → T-011 **92%**; brief-a T-010 74% → T-011 97% → T-012 **100%** → fold 100%;
brief-b T-009 79% → T-010 95% → T-011 **100%** → fold 100%. Both brief arms reached a clean matrix
before the fold ran; the control never did.

With the two earlier records on the same brief and arm: 2.10.3 control 100% adjusted (0 gaps),
2.10.4 brief without the rule 86% (6 gaps, all ledger advisories), 2.10.5 control 92% (3 gaps),
2.10.5 brief-a 100%, brief-b 100%. The one timeout in every build is the same mutant, `TryUpdate`
negated in the click compare-and-swap loop: detected by a hung suite, not a gap.

## Findings

1. **The brief with the in-scope rule beats the control on the sensor that fell last time.** Both
   brief builds end with no real surviving mutant; the control, built the same afternoon with no
   brief, keeps three. The 2.10.4 result was not reviewer noise around a neutral page: the page's
   wording decides whether a recorded gap becomes a status line or a required change. With the
   rule, it became work.
2. **Most of the folding happened before the fold.** Plans in the brief arms carry a "standing
   advisories in scope" section, reviews mark the ones in scope *resolved* per task (brief-a's T-005
   closed task-list R-2, T-006 closed four, T-012 closed T-008 R-27; brief-b's docs task T-012
   closed eleven), and the fold session found 8 of its 12 applied items in brief-a and 11 of 17 in
   brief-b already done. The fold's own changes were small: four edits (two task-list lines, two
   test files) in brief-a, six test changes in brief-b, both approved on the first review with a
   100% review-time kill rate. The rule is the mechanism; the fold is the backstop, and a cheap one
   (9 to 10 minutes, about $1.30 with its review).
3. **Cost did not rise.** brief-a spent 9% more tokens than the control and $2.42 less, brief-b 10%
   fewer tokens and $6.87 less, both in less pipeline time (108 and 84 minutes against 118). The
   control's six revise rounds and five guard firings were the expensive part. The inlined page
   (about 1k tokens per prompt, mean 3.5k to 3.9k characters) is invisible in the totals.
4. **The folded ledger fit.** No advisory group was ever dropped in either brief run (max 5,176
   characters of a 6,000 cap), where the 2.10.4 run had lost four of seven groups by its seventh
   review. The reviewers in both brief arms also numbered advisories in one shared sequence across
   reviews (brief-a reached R-44), which the ledger did not ask for and makes citation unambiguous.
5. **Zero guard firings with the brief, five without.** Every control fix session rewrote its own
   review file and was reverted; no brief-arm fix session did. The brief's "never edit the brief
   file" line and its listing of the review as a committed artifact are the only differences on
   that path. Two runs are not proof, but it is the same direction as 2.10.4 (one firing in the
   2.10.3 control, none with the brief).
6. **An S-sized Testing task escaped the playbook again** (brief-a's T-009, "unit-test code
   generation and request validation"). Its tests were later checked by the T-010 to T-012 reviews
   and the fold review (the validator mutants were all killed), so no harm, by the same luck as in
   2.10.4. Third occurrence across five builds; the candidate stands: Testing-type tasks are never
   S for review purposes, or the task-completion gate runs the bound playbook when a Testing task
   skips review.
7. **The listen-port constraint went 2 for 3.** The control pinned its port in `app.Run(...)`
   because its own generated task list said so, and the T-001 reviewer accepted it as an advisory;
   both brief builds call `app.Run()` with no address. Four of six Sonnet builds have now honoured
   it; the two that did not were both specified wrong at task generation, not at implementation.
   The rubric probe for stakeholder constraints at *task review* is the right place for it.
8. **Variance is large and now measured.** Same brief, same arm, same day: the control's reviewers
   returned six revises where 2.10.3's returned three; the task generator produced 12 or 13 tasks
   with different S/M splits; the 2.10.3 and 2.10.5 controls differ by 8 points of adjusted kill
   rate with no change between them. Any future single-run comparison on this brief should be
   read against that band, which is what the 2.10.4 record could not do.
9. **Infrastructure held.** The sweep found nothing to stop in any of the three runs (no worker
   left a server behind this time), no run was interrupted, and no session was denied a shell.
   The runner's wall-clock accounting is therefore clean for all three.

## Reading

Three builds, one afternoon. The arm with the brief, the in-scope rule and the fold delivered the
stronger test suites (118 and 131 tests killing every meaningful mutant, against 70 tests and
three gaps), with no exam regression, no human triage, no guard firing, and for less money. The
mechanism is not the page as memory, which 2.10.4 already had; it is the sentence that turns a
remembered gap inside a task's scope into that task's required change, with the fold step catching
what still slips. On this brief, the orchestration brief is adopted: `policies/shortlist-brief-fold.json`
is the default arm from here, and the 2.10.3-style control stays as the reference arm for the next
release that needs one.

Raw per build: `shortlist-control/`, `shortlist-brief-a/`, `shortlist-brief-b/` (each: `record.md`,
`exam-v2.json`, `events.ndjson`, `report.md`, `review-kill-matrix-*.json`). Baseline matrices are
archived with the measuring tool as `examples/shortlist-2.10.5-{control,brief-a,brief-b}.json`.
