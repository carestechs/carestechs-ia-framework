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
