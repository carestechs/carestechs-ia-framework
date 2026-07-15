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
