# Experiment Log

## EXP-001 — Context A/B: spec docs vs work item only (2026-07-15)

**Question.** Do the sharded spec docs earn their context tokens at task-generation
time, or does a dense work item alone suffice? (The "extensive docs" debate.)

**Design.** Arm A = case-001 (full fixture: work item + spec indexes + impact-table
shards). Arm B = case-901, identical fixture with `docs/data-model/`, `docs/api-spec/`,
and `docs/ui-specification/` physically removed from the generation input; assertions
check against the full sibling fixture (ground truth the generator never saw). Same
prompt, model, judge rubric, and reference anchor. Arm A samples reused from the
v2.4.2 baseline.

**Run 1 (flawed, kept for its accidental finding).** Arm B's GENERATE.md omitted the
self-check step (`validate-tasks.py` before finishing) that arm A's includes — two
variables changed at once. Result: 0/3 deterministic (TASK-XXX headings, bulleted
fields — pure schema drift; up to 120 validator errors/sample) while judge scores held
at 8.7. Archived under `baselines/ab-minimal-context/`.

**Run 2 (corrected: only the docs differ).** Archived under
`baselines/ab-minimal-context-v2/` (stopped after 2 of 3 samples; n=2).

| | Arm A (with docs, n=3) | Arm B (no docs, n=2) |
|---|---|---|
| Deterministic pass | 3/3 | 2/2 |
| Judge score | 8.7 avg (8–9) | 8.5 avg (8–9) |
| Task count | 10–14 | 13 |
| Generation time | 583–690 s | 558–704 s |
| Error-code vocabulary | validation-error, conflict, duplicate-name | identical |
| Routes | `/api/v1/...` per spec | identical |

**Reading — three findings, in order of confidence:**

1. **The self-check loop, not the docs, is the compliance lever** (run 1 vs run 2:
   0/3 → 2/2 with the identical no-docs context). External tool feedback inside the
   generation step is the largest single effect measured in this harness so far.
   Never generate without it.
2. **Information density at the point of use beats document volume.** Arm B matched
   arm A because the work item's impact tables and ACs already carry the routes,
   business rules, and constraints — the docs reached arm B *compressed through the
   brief*. This validates the retrieval-key/impact-table design and argues against
   loading more documents at generation time; it does NOT show docs are useless
   (see caveat 1).
3. No hallucination increase without docs — for this fixture (shard refs sanctioned
   by the brief, paths visible in `src/`).

**Caveats.**
1. The brief was *authored from the specs* — the realistic no-docs scenario (brief
   written without spec knowledge) was not tested and should be expected to be worse.
   The experiment measures "docs at generation time" vs "docs distilled into the
   brief," not "docs vs nothing."
2. n=2/3, one work item, one fixture, one model. Directional, not conclusive.
3. The judge rubric has no spec-fidelity dimension and the deterministic checks can't
   see convention drift; convention alignment was probed manually (error codes,
   routes) and found identical — but only because the brief encodes them.
4. Specs likely matter more for steps not tested here: planning (reads code +
   shards), implementation (needs contracts), bugfix (needs current-state truth a
   brief cannot carry), and brief authoring itself.

**Actions.** (a) Treat the generation-time self-check as mandatory in the
orchestrator — it is the measured compliance guarantee. (b) Prioritize brief quality
(dense impact tables) over adding generation-time context — consistent with the
framework's existing design. (c) Candidate rubric improvement: add a spec-fidelity
dimension so future runs can see convention drift mechanically.

### Addendum (2026-07-15): re-judged with the spec-fidelity dimension

Action (c) was implemented — rubrics gained a sixth **spec fidelity** dimension and
the judge prompt now embeds ground-truth spec excerpts (`context` key in the judge
check). Re-judging the same archived samples:

| | Arm A (with docs) | Arm B (no docs) |
|---|---|---|
| Judge, 5 dimensions (no ground truth) | 8.7 (8–9) | 8.5 (8–9) |
| Judge, 6 dimensions (ground truth embedded) | **9.0 (9–9)** | **7.0 (6–8), 1 of 2 fails** |

**The verdict flips: a 2-point fidelity gap the earlier rubric could not see.**
Arm A samples are explicitly praised for spec fidelity (correct `/api/v1` base path,
409/conflict codes per the error catalog). Arm B's failing sample plans to *create*
spec files that already exist in the ground-truth project (data-model/api-spec
indexes, `endpoints/tasks.md`, `components.md` marked `(new)`) — in a real pipeline
that plan would duplicate or overwrite existing documentation.

Two readings, both fair: judged against its own (docless) input, arm B behaved
correctly; judged against the ground-truth project, its output contradicts reality.
For the practical question — *should generation load the spec docs when they exist?* —
the answer is now measured: **yes; skipping them costs ~2 judge points and produces
plans that contradict the existing project state.** Finding 2's density argument
stands for what the *brief* should carry; it no longer supports skipping the docs.

**Revised conclusion.** Lean, sharded, retrieval-keyed docs at generation time earn
their tokens (fidelity); dense briefs are necessary but not sufficient; the
self-check loop remains the compliance guarantee. The 30-page-documents position
remains unsupported: everything measured here was achieved with lean contract-style
shards.

### Addendum 2 (2026-07-15): arm B completed at n=3; judge variance observed

The third arm B sample was generated (deterministic PASS, judged 8/10) and the full
n=3 archive re-judged in one pass: **arm B final = 3/3 deterministic, judge 7.7 avg
(7–8)** vs arm A 9.0 (9–9). The fidelity gap holds at ~1.3–2 points, direction
consistent across every judge pass.

**Variance note.** The borderline sample-1 scored **6** in one judge pass (failing,
with a specific spec-contradiction finding) and **8** in another (passing) — single
judge runs are noisy near the threshold, exactly as the self-consistency literature
predicts. Arm A's tight 9–9 range was stable across passes. Practical rule adopted:
treat single judge scores within ±1 of `min_score` as inconclusive; for gating
decisions, run the judge 3× and take the median. Candidate runner improvement:
a `judge_samples` key automating this.

### Addendum 3 (2026-07-15): median-of-3 judging validated

With `judge_samples` (median of N): arm B samples score **7 [7,7,7], 8 [7,8,8],
7 [8,7,7]** — the sample that flip-flopped 6↔8 across single passes now sits stably
at 7. Adopted: `--judge-samples 3` for any score that gates a decision.

## EXP-002 — Anti-example ablation (2026-07-15): RUN 1 ABORTED — access confound

**Question.** Do the contrastive Anti-Example blocks (v2.4.1) earn their tokens?
**Design.** case-902: identical fixture to case-001 via sibling refs; prompt variant
with only the Anti-Example section stripped (1,456 chars; budgets retained).

**Aborted** mid-run when project memory surfaced an infrastructure fact that
invalidates the comparison: headless generation agents (cwd = case dir) were
**permission-blocked from reading the framework prompts** all along. Verified
empirically: a Read of `prompts/base-template.md` from a case dir hangs on an
unanswerable permission request; with `--add-dir <repo root>` it succeeds. Agents had
been reverse-engineering the schema by probing `validate-tasks.py` (the stray
`probe.md` was evidence) and later reading files via a `Bash(python *)` sandbox
bypass, then sharing the recovered schema through project auto-memory across runs.

Consequences:
- **EXP-002 run 1 invalid**: the control arm (baseline) never reliably read the full
  prompt (anti-example included), while the variant arm's prompt sat readable inside
  its case dir — the arms differed in ACCESS, not just content. Partial samples
  discarded.
- **Baseline v2.4.2 caveat**: its samples measure the pipeline under degraded prompt
  access (GENERATE.md restatements + validator feedback carried the schema). Still
  valid as a regression floor for that configuration, but not comparable to runs made
  after the access fix.
- **EXP-001 remains internally valid**: both arms ran under the same access handicap,
  and its variable (spec docs in the fixture) was unaffected — fixture files live
  inside the case dirs.

**Fixes applied**: `run-baseline.py` default gen command now passes `--add-dir
"<repo root>"`; the schema-bearing memory was purged and replaced with the access
lesson; validator no longer parses `---` separators as file entries (a gotcha the
probing agents discovered).

**Status**: pending re-run — requires a fresh post-fix baseline for the control arm
plus 3 variant samples, so both arms read their prompts verbatim.

## EXP-002 — Anti-example ablation, RUN 2 (2026-07-15/16): completed under fixed access

**Setup.** Post-access-fix baseline `v2.4.6` (all agents read their prompts verbatim,
verified; `--add-dir` in the gen command; median-of-3 judging throughout). Control =
case-001 (full feature-tasks prompt); variant = case-902 (identical except the
Anti-Example section stripped, budgets retained).

| | Control (with anti-example) | Variant (without) |
|---|---|---|
| Deterministic | 3/3 | 3/3 |
| Judge (median-of-3 per sample) | **9.0** — 9 [9,9,8], 9 [9,9,9], 9 [9,9,9] | **8.7** — 9 [9,9,9], 9 [9,9,9], 8 [9,8,8] |

**Verdict: no measurable effect at n=3** — scores overlap, deterministic identical.
The contrastive anti-example neither helps nor harms this model on this case. By the
framework's own "every element earns its place" standard the anti-examples are on
probation: kept for now as cheap insurance (~350 tokens; the research evidence is
strongest for weaker models and noisier contexts), re-test on the next model change.

**Bonus: EXP-001 replicated under correct access.** The same baseline regenerated the
no-docs arm (case-901): judge **6.7 (6–7), one sample failing at median 6** vs
control 9.0. The docs gap *widened* from ~1.3–2 to ~2.3 points once all agents
actually read the prompts — the strongest confirmation yet that the sharded spec
docs earn their context.

**v2.4.6 is the canonical regression floor** (old baselines carry the access caveat):
deterministic 18/18 across all 6 cases; judged medians — feature 9.0, bugfix 8.0,
ablation-arm 8.7, no-docs-arm 6.7. Judge robustness: verdict-line omissions by the
judge model are now retried (3 attempts) instead of failing the check.
