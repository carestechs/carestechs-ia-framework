# Prompt Evals

Golden-set regression tests for the framework's prompts. Every prompt edit — and every
model update underneath you — can silently shift generation behavior across the whole
input distribution. These evals turn "the prompts still work" into a checkable claim.

This directory is framework-repo-only. It is **not** shipped into the scaffold.

## How it works

Each case is a frozen fixture project plus declarative assertions:

```
evals/cases/<prompt>/<case>/
├── GENERATE.md        # instructions an agent follows to produce the output
├── input/             # self-contained fixture project (CLAUDE.md, sharded docs/, src/)
├── assertions.json    # declarative checks against the generated output
└── output/            # generated artifacts land here (disposable, not reviewed content)
```

The loop has two steps, deliberately separated:

1. **Generate** (needs an agent + model — non-deterministic):
   have any agent follow the case's `GENERATE.md`. For example, with Claude Code:

   ```bash
   claude -p "Read evals/cases/feature-tasks/case-001-task-labels/GENERATE.md and follow it exactly."
   ```

2. **Check** (deterministic, no model, CI-safe):

   ```bash
   python evals/run-evals.py                 # check all cases with outputs present
   python evals/run-evals.py --case task-labels
   python evals/run-evals.py --require-all   # CI mode: missing outputs fail too
   ```

Assertion types (see `run-evals.py` docstring for the JSON schema):

| Type | What it verifies |
|------|------------------|
| `validator` | `tools/validate-tasks.py` passes — schema, enums, dependency DAG, AC coverage |
| `task_count` | task count within an expected range (catches over/under-decomposition) |
| `must_match` / `must_not_match` | required sections present; stack leaks and forbidden content absent |
| `paths_exist` | every file a task touches exists in the fixture or is marked `(new)` |
| `shard_refs_resolve` | every spec-shard reference resolves against the fixture (hallucination check) |

## Reading the results

- A `FAIL` on `shard_refs_resolve` or `paths_exist` = the prompt let the model invent
  entities/endpoints/files — the highest-severity regression class.
- A `FAIL` on `task_count` after a prompt edit usually means the edit changed
  decomposition granularity — decide deliberately whether that's intended.
- Because generation is stochastic, a single run is a smoke test, not a proof.
  For prompt A/B comparisons, generate 3-5 outputs per variant and compare pass rates.

## Adding a case

1. Copy an existing case directory; keep `input/` small but **internally consistent**
   (it should pass `python tools/validate-specs.py --root <case>/input` with 0 errors).
2. Write `GENERATE.md` with exact relative paths (fixture root, prompt file, output file).
3. Encode what "good" means in `assertions.json` — prefer checks that catch
   *hallucination* and *schema drift*; avoid asserting exact wording.
4. Run generate + check once to confirm the assertions are satisfiable.

## CI wiring (optional)

The check step is a plain exit-code command. A minimal gate for prompt-change PRs:
run the generation step with your agent of choice, then
`python evals/run-evals.py --require-all`. Budget note: one generation per case per
run; keep the case count small and high-signal rather than exhaustive.
