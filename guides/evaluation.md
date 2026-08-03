# Evaluation Guide

How to measure whether the framework is actually working — for a single project or for
the framework itself. Four levels, from cheap compliance checks to counterfactual
experiments. Most metrics are computed mechanically from the repo because every pipeline
step ends in a committed artifact.

**The two numbers to start with** (before building anything else): first-pass acceptance
rate and human correction burden, tracked on every work item you run. Their absolute
values tell you whether the framework helps; their trend tells you whether changes to it
help.

---

## Level 1 — Compliance (the floor)

`tools/validate-tasks.py` and `tools/validate-specs.py` verify that artifacts are
well-formed and grounded. This is necessary but not sufficient — a schema-perfect task
list can still decompose work badly.

**Metric:** validator failures per generated artifact, over time. Should approach zero
and stay there. Anything else means the prompts and the schema have drifted apart.

---

## Level 2 — Step quality, offline (prompt evals)

The framework repo's `evals/` harness runs golden fixture cases against declarative
assertions (see `evals/README.md`). Two practices raise its signal:

- **Multi-sample runs.** Generation is stochastic; a single run is a smoke test. For
  prompt A/B comparisons, generate 3–5 outputs per variant and compare *pass rates*.
- **Anchored judge checks.** Assertions can't score decomposition quality. The runner's
  `judge` check type grades the output against a fixed rubric with a known-good
  reference output as anchor, in a fresh context. Judges are only reliable when
  anchored and rubric-bound — never ask for a free-floating score.

**Metrics:** eval pass rate per prompt; hallucination rate (`shard_refs_resolve` /
`paths_exist` violations per output — the highest-signal number); decomposition
stability (task-count variance across samples); judge score distribution.

---

## Level 3 — Pipeline effectiveness, online (real work items)

Measured on actual briefs flowing through the pipeline. Enabled by two conventions:
**every step ends in a commit**, and the orchestrator (or you, manually) appends events
to a log.

### The scorecard

| Metric | What it tells you | Computed from |
|--------|-------------------|---------------|
| First-pass acceptance rate (per step) | Does the framework produce usable artifacts? | Review-file verdicts + `revised` events |
| Human correction burden | How much did you fix before accepting? | Git diff: first committed version of an artifact vs its accepted version |
| AC leakage | Did generation miss scope? | Amendment commits to a task list after first acceptance |
| Post-merge defect attribution | Do framework-built features break less? | BUG-* work items whose Traceability links back to a FEAT-* |
| Doc drift trend | Is maintenance discipline holding? | `validate-specs.py` counts + freshness-stamp age distribution |
| Cycle time (per step / per brief) | Where does time go? | Step-boundary commit timestamps + event log |
| Token cost per accepted task | The efficiency denominator | `session_tokens` in the event log |

Run `python .ai-framework/tools/metrics-report.py` from the project root to print the
scorecard. It degrades gracefully: sections whose inputs are missing (no git, no event
log) are skipped with a note.

### Event log schema

Location: `metrics/events.ndjson` in the project root — one JSON object per line,
appended at step boundaries by the orchestrator (or by hand: `echo '{...}' >>
metrics/events.ndjson`).

| Field | Required | Values / format |
|-------|----------|-----------------|
| `ts` | yes | ISO-8601 UTC, e.g. `2026-07-14T15:04:05Z` |
| `work_item` | yes | `FEAT-001`, `BUG-003`, `IMP-002`, or `adhoc-<slug>` |
| `task` | no | `T-003` — omit for brief-level steps |
| `step` | yes | `brief` \| `task-generation` \| `task-review` \| `planning` \| `assignment` \| `implementation` \| `implementation-review` \| `docs-update` \| `closure` |
| `event` | yes | `started` \| `artifact_committed` \| `accepted` \| `revised` \| `completed` |
| `session_tokens` | no* | integer — approximate tokens consumed by the session that ran the step. *Every step should record it (approximate is the contract — best available figure beats nothing); drivers without a JSON writer use `next-step.py --log-event` |
| `model` | no | model the step's session ran on, e.g. `sonnet`, `opus` — enables per-model cost/quality comparisons across runs |
| `cost_usd` | no | session cost in USD as reported by the runner — NOTIONAL under subscription auth (no dollars charged); real only for API-key runs |
| `detail` | no | free text: verdict, commit sha, reviewer note |

> **Cross-version note:** v2.8.0 outcome-anchored the review verdict bar
> (approve-with-advisories) — first-pass `accepted` rates rise by definition from
> that version. Annotate cross-run comparisons with the framework version each
> run executed under.

Example:

```
{"ts": "2026-07-14T14:02:11Z", "work_item": "FEAT-001", "step": "task-generation", "event": "started"}
{"ts": "2026-07-14T14:09:40Z", "work_item": "FEAT-001", "step": "task-generation", "event": "artifact_committed", "detail": "tasks/FEAT-001-tasks.md @ 3fa9c21", "session_tokens": 38400}
{"ts": "2026-07-14T14:31:02Z", "work_item": "FEAT-001", "step": "task-review", "event": "revised", "detail": "verdict: revise (2 findings)"}
{"ts": "2026-07-14T15:00:19Z", "work_item": "FEAT-001", "step": "task-review", "event": "accepted"}
{"ts": "2026-07-15T10:12:00Z", "work_item": "FEAT-001", "task": "T-003", "step": "implementation", "event": "completed", "session_tokens": 91200}
```

Rules of thumb: emit `started` when a session begins a step, `artifact_committed` when
its output lands in git, `accepted`/`revised` when a human or reviewer rules on it, and
`completed` for terminal steps. Duration metrics pair `started` with the first
`accepted`/`completed` for the same (work_item, task, step).

---

## Level 4 — Counterfactuals (is it worth it?)

- **Context A/B.** Same real work item, tasks generated twice: full framework context
  vs minimal (brief + CLAUDE.md only). Grade both with Level 2 checks plus a blind
  judge. Settles "do the docs earn their tokens" with your own data.
- **Layer ablation** (quarterly, or whenever docs feel heavy). Drop one doc layer at a
  time from a golden case's context and measure degradation. Any layer whose removal
  doesn't hurt output quality is not paying its maintenance cost — trim or merge it.
  Every document in the framework should have an empirical justification.
- **Token cost per accepted task** from the event log — the denominator for everything
  above.

---

## Cadence

| When | What |
|------|------|
| Every prompt change | `evals/run-evals.py` (multi-sample if the change is behavioral) |
| Every work item | Append events; commit at step boundaries (no extra effort beyond that) |
| Monthly | `metrics-report.py` scorecard review — watch acceptance rate and correction burden trends |
| Quarterly | Layer ablation + judge-score drift check |
