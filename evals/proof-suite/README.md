# Proof Suite

Whole-pipeline validation of framework releases on fixed inputs. `evals/` grades single
prompts against golden fixtures and `tests/` guards the tooling; the proof suite answers
the question neither can: **does a given framework version turn the same human inputs
into a more correct product, with fewer corrections, for less?** It does so by building
the same small products end to end, autonomously, on each release, and grading the result
with an exam the builders never see.

This directory is framework-repo-only, like the rest of `evals/`. Runs happen in
throwaway project checkouts (by convention under `Repos/proof/`); only the frozen inputs,
the exams and the recorded outcomes live here.

---

## 1. Why this exists

The framework has been proven on real builds (ChatLens, Vision Lab, Inspetor IA, Flowmarket,
the autonomous granary and business-framework builds) and on one purpose-built test system:
**Shortlist**, a URL shortener built three ways on 2026-08-03 under framework 2.6.0/2.7.0 by
the pipeline-runner (`Repos/proof/testsys-shortlist` with Sonnet workers,
`testsys-shortlist-opus` as the all-Opus control, `testsys-orch` through the in-repo
`/orchestrate` fixture). Those runs produced v2.7.1 and v2.8.0 and the runner's standing
model policy.

Three gaps remained, and this suite closes them:

| Gap | Consequence | Here |
|---|---|---|
| Nothing re-ran the same brief on a later version | "Did v2.10 make the pipeline more precise than v2.7?" has no answer on identical inputs | frozen briefs, one run per minor release, results recorded per version |
| Quality was self-graded | the only success metric was the agents' own tests going green | an external **exam** per brief, held out of the build, run after closure |
| One brief covered one shape | API-only; never exercised spec generation from strategy, UI specs, mockup-first tasks, bugfix investigation or refactoring on existing code | three briefs of different shapes (section 3) |

Real-project field reports (e.g. `../../../ia-framework-field-report-chatlens.md`) stay the
richer source of *what to change*. The suite is the controlled measurement of *whether a
change helped*.

---

## 2. Design rules

1. **Frozen human inputs.** A brief is the set of files a human would author before the
   pipeline starts: `CLAUDE.md`, `docs/stakeholder-definition.md`, `docs/ARCHITECTURE.md`,
   `docs/personas/*.md`, the work items under `docs/work-items/`, and for brownfield briefs
   the seed codebase. They are committed under `briefs/<name>/inputs/` and never edited
   between runs. A change to a brief is a new brief version (`briefs/<name>/README.md`
   records it) and resets its history.
2. **An external exam.** `briefs/<name>/exam/` grades the delivered product against the
   brief's own acceptance criteria and edge cases, as a black box (HTTP calls, CLI runs,
   file checks). Agents never see it; it is not copied into the project. The exam is the
   correctness number. The agents' own tests remain a pipeline gate, not evidence.
3. **Two arms per brief.** The runner's default policy (Sonnet workers, Opus reviewers,
   Haiku closure) and the all-Opus control (`pipeline-runner/policies/*-opus.json`). The
   runner's attribution rule applies: a weakness present in both arms is the framework's;
   one present only in the default arm is the worker model's.
4. **One fresh scaffold per run.** Each run starts from `scaffold/` of the framework version
   under test, into an empty git repo, with the brief's inputs copied over the scaffold
   (the brief's `CLAUDE.md` replaces the scaffold's). The first commit is `seed: <brief>@<brief-version> on framework <version>`.
5. **Nothing from a previous run is reused.** No specs, no task lists, no plans. Bootstrapped
   specs are part of what is being measured.
6. **Recorded, not remembered.** Every run leaves a record under `results/<framework-version>/`
   (section 7) with the raw event log and the exam verdict copied in. A framework release
   may cite its record in `CHANGELOG.md` the way it already cites live failures.
7. **Read-only toward the framework.** The suite consumes only published contracts
   (`next-step.py --json`, the validators, the verdict regex, the event-log schema) through
   the pipeline-runner. It never patches the framework or the runner mid-run; a run that
   needs a patch is a finding, and the run is repeated after the release that carries it.

---

## 3. The briefs

| Brief | Shape | Stack | Exercises | Exam shape | Status |
|---|---|---|---|---|---|
| `shortlist` | greenfield API, no UI, no persistence | .NET 10 Minimal API, zero NuGet deps | task generation, task-list review, planning, implementation, fresh implementation review, S-task skip rule, closure | HTTP contract: 16 checks over AC-1..AC-4 and section 9 edge cases (`exam/shortlist_exam.py`) | **frozen** (v1, from `testsys-shortlist @ 052f580`) |
| `taskflow-slice` | greenfield full stack | React + Express (the TaskFlow sample product) | spec generation from strategy (data model, API, UI spec), mockup-first tasks, work item with UI impact | HTTP contract for the labels API plus a DOM-level check of the board filter via a headless browser or the rendered HTML | planned; inputs to be lifted from `evals/cases/spec-generation/case-005-*/input` (strategy) and `evals/cases/feature-tasks/case-001-*/input/docs/work-items/` (brief) |
| `brownfield-pair` | one BUG and one IMP on an existing codebase | React + Express TaskFlow seed with its sharded specs | investigation-first tasks, refactor safety net (Phase 0), docs-update step, freshness stamps, two work items sharing task IDs (the v2.8.4/v2.8.5 collision rules) | the fixture's own regression scenario (overdue filter across time zones) run against the fixed API, plus "no behaviour change" differential tests for the refactor | planned; seed is `evals/cases/bugfix-tasks/case-002-*/input` (code, tests, specs) with the BUG-001 and IMP-001 briefs from case-002 and case-004 |

Shortlist is the canary: cheap, fast, and already measured once. The other two are added
when their first run is scheduled; a planned brief is listed so the shapes they cover are
not forgotten, not because a design exists yet.

**Lesson carried into the next freeze:** the Shortlist brief leaves the request and
response field names to spec generation. Both 2026-08-03 arms converged on `url` and
`customCode` because `CLAUDE.md` pins the error-handling and JSON conventions, but the
exam depends on that convergence. From the next brief onward, section 7 of a brief states
the wire contract the exam will probe (field names, status codes, error shape).

---

## 4. Arms and policy

| Arm | Policy file (pipeline-runner) | Models | Purpose |
|---|---|---|---|
| default | `policy.json` + `policies/<brief>.json` (test command, bootstrap flags) | Sonnet workers, Opus task/implementation reviewers, Haiku closure | the recommended production policy |
| control | `policies/<brief>-opus.json` | Opus everywhere | attribution: separates framework weakness from worker-model weakness |

An optional third arm, **attended**, drives the same brief through `/orchestrate` in a
Claude Code session (one step per invocation, human runs the gates). It measures the
in-repo mode rather than the runner and is the analogue of `testsys-orch`.

Record the exact model IDs the runner reports (`model` in the event log), not the aliases:
model updates underneath a fixed policy are a confound the record must expose.

---

## 5. Procedure per release

For each brief and each arm:

1. **Seed.** `mkdir Repos/proof/<brief>-<version>-<arm>` and `git init`. Copy
   `scaffold/.` from the framework checkout at the version under test, then copy
   `briefs/<brief>/inputs/.` over it (the brief's `CLAUDE.md` wins; when the scaffold's
   framework section has moved on, keep the brief's project sections and take the scaffold's
   framework section, and say so in the record). Set every freshness stamp in the brief's
   human inputs to the seed date: they describe intent, not verified code, and the runner's
   strict bootstrap gate rejects stamps that are unfilled or older than 30 days, so an
   un-restamped brief expires a month after it is frozen. For brownfield briefs also copy
   `inputs/seed/.`. Commit: `seed: <brief>@v<brief-version> on framework <version>`.
2. **Dry run.** `python runner.py --project <path> --policy <arm policy> --dry-run` and read
   the bootstrap decisions and the first step. Fix nothing in the project; if the dry run is
   wrong, the finding goes to the record and the run is skipped.
3. **Run.** `python runner.py --project <path> --policy <arm policy>` to closure or to the
   runner's stop. Do not intervene except to answer the runner's own parks (record each
   park: it is the human-triage count).
4. **Exam.** Start the product the way its `README`/`CLAUDE.md` says, then run
   `briefs/<brief>/exam/*` against it with `--json`. Stop the product.
5. **Scorecard.** `python <framework>/tools/metrics-report.py --root <path>` for the
   validator and acceptance lines; `python <framework>/tools/next-step.py --root <path>
   --json` to confirm every work item is closed (or record what is not).
6. **Record.** Create `results/<version>/<brief>-<arm>/` with `record.md` (section 7),
   `exam.json`, `events.ndjson` (copied from the project's `metrics/`), and the runner's
   `report.md` if one exists. Commit to the framework repo on the release branch.

The project checkout is kept (it is the evidence behind the record) but is not required to
reproduce the numbers: the record carries the raw logs.

---

## 6. Metrics recorded

| Metric | Source | Why it is the one that matters |
|---|---|---|
| Exam pass rate | `exam.json` | the independent correctness number |
| Work items closed / parked | `next-step.py --json` | did the pipeline finish |
| Tasks generated, S/M/L/XL mix | task list | decomposition shape |
| First-pass acceptance per review step | **event log** (`accepted` vs `revised`), never current verdict files, which re-reviews overwrite | precision of the artifacts |
| Revise rounds per artifact, max loop depth | event log | convergence |
| Human triage count | runner parks + manual interventions | the correction burden the pipeline pushes to a person |
| Validator errors at gates, repair sessions | runner report | schema/grounding drift |
| Tokens by step, notional cost, wall-clock | event log, runner report | the efficiency denominator |
| Model IDs per step | event log | confound control |
| Framework version, runner commit, brief version, exam version | record header | reproducibility |

Trend across versions is the signal; a single run per arm is a smoke test. When a number
has to carry a decision (adopt or revert a prompt change), run the arm three times and
compare pass rates, exactly as `evals/README.md` prescribes for prompt A/B.

---

## 7. Result record format

`results/<framework-version>/<brief>-<arm>/record.md`:

```markdown
# <brief> / <arm> on framework <version>

| Field | Value |
|---|---|
| Framework version | 2.10.1 (commit ...) |
| Brief | shortlist v1 |
| Arm / policy | default / policy.json + policies/testsys-shortlist.json |
| Runner | pipeline-runner @ <commit> |
| Models (as reported) | ... |
| Started / finished | ISO timestamps |
| Project checkout | Repos/proof/<name> @ <commit> |

## Outcome
| Exam | 16/16 | 
| Work items | 1 closed, 0 parked |
| Tasks | 11 (S 3, M 6, L 2) |
| First-pass acceptance | task-review 0/3, planning 11/11, implementation-review 8/12 |
| Revise rounds | task list 3 (cap hit), implementation max 1 |
| Human triage | 1 park (reason) |
| Tokens / notional cost / wall-clock | ... |

## Findings
What the run taught, in the CHANGELOG's style: measured, attributed (framework vs model vs
environment), with the artifact that shows it.
```

Alongside: `exam.json`, `events.ndjson`, and the runner's `report.md`.

---

## 8. Cadence and cost

- **Every minor release** (`2.N.0`): Shortlist, both arms. Add the other briefs as they are
  frozen. Patch releases rely on `tests/` and the baseline rescore gate instead.
- **Before adopting a behavioural prompt change** on evidence from a single real project:
  run the brief that exercises the changed step, three samples per arm.
- Cost reference from 2026-08-03: Shortlist cost ~$30 notional on the default policy and
  ~$57 on the all-Opus control, about three hours wall-clock each, under a subscription login
  (no dollars charged; the constraint is the plan's rate window shared with interactive use).

---

## 9. Caveats and failure modes

- **Stochastic.** One run per arm detects collapses, not small shifts. Compare trends.
- **Model drift.** The same alias may be a different model two months later. Record IDs,
  and when a comparison across versions matters, re-run the older framework version in the
  same week as the newer one.
- **Environment kills.** Background worker sessions were killed randomly on the original host
  (runner lesson 11); the runner is stateless and resumes, but wall-clock numbers include it.
- **The exam tests the wire contract, not the code.** Internal quality (tests, structure)
  is what the fresh reviews are for; the exam only says whether the product does what the
  brief asked.
- **Brief silence becomes exam fragility.** See the lesson in section 3.
- **Tokens are approximate** and self-reported per step; the orchestrator's own context is
  not logged.

---

## 10. What this is not

- Not shipped to projects. Nothing here enters `scaffold/`.
- Not a model benchmark. Models are a confound to control, not the subject.
- Not a replacement for real-project field reports, which remain where the framework's
  changes come from.
- Not part of the framework's doctrine. It is the framework's own evaluation apparatus,
  one level above `evals/cases/`, and it lives here for the same reason the prompt evals do.
