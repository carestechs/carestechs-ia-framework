# Changelog

Framework versions follow [semantic versioning](https://semver.org/). Projects can check which version they bundle via `.ai-framework/VERSION`.

## [2.8.5] — 2026-08-08

### Fixed
- **Per-task artifacts are work-item-scoped too** (`next-step.py`, prompts, routing table).
  v2.8.4 closed the task-ID collision on the commit rung; its own fresh review found the same
  collision untouched on the rungs *above* it, where it is worse. `tasks/T-XXX-implementation-review.md`,
  `plans/plan-T-XXX-*.md` and `mockups/T-XXX-*.html` are named by task ID alone, and the review
  rung outranks commit evidence — so a review file written for FEAT-002's `T-001` marked
  **BUG-001's** `T-001` `done`, skipping implementation *and* review, with no warning at all.
  - Artifacts now carry the owning work item: `tasks/<WI>-T-XXX-implementation-review.md`,
    `plans/plan-<WI>-T-XXX-*.md`, `mockups/<WI>-T-XXX-*.html`. `pick_artifact()` prefers the
    qualified name, accepts an unqualified one only while no other task list declares that ID,
    and otherwise refuses it with a warning — the same fail-safe as commit evidence.
  - Every path the tool prints (review, re-review, fix, plan, mockup prompts and gates) is now
    qualified, so sessions write the disambiguated name by default.
  - Prompt contracts (`review-implementation.md`, `plan-generation.md`) and the routing table in
    `templates/claude-md.md` + scaffold `CLAUDE.md` state the qualified form and why.
  - Legacy repos are unaffected: with one task list, unqualified names resolve exactly as before.
  - Fixture-verified: the unqualified-review collision marks *neither* work item done and warns;
    a qualified review credits only its owner; a single-work-item repo still resolves a plain
    `tasks/T-001-implementation-review.md`.

## [2.8.4] — 2026-08-08

### Fixed
- **Commit evidence no longer credits one work item's task to another** (`next-step.py`).
  Task IDs restart at `T-001` in every task list, and `has_impl_commit` matched `\bT-XXX\b`
  against every commit subject in the repo with no work-item scoping — so `feat(T-001):
  extract Chapas design tokens` (FEAT-002) was credited to BUG-001's `T-001`. Reported from
  live use, where it briefly marked **all five** BUG-001 tasks implemented; the operator
  corrected it through the progress overlay, and it would have recurred on every future work
  item. This is a false *positive*, which skips implementation entirely rather than looping —
  the more dangerous direction.
  - `task_id_owners()` maps each task ID to the work items whose task lists declare it; when an
    ID has more than one owner, a commit is credited only if its subject also names the owning
    work item (`feat(FEAT-002/T-001): ...`). Every `tasks/*-tasks.md` counts, including completed
    work items' — their commits stay in the log forever, which is what made the collision
    possible. IDs with a single owner are unchanged, so a repo with one task list behaves exactly
    as before.
  - When an otherwise-valid commit is skipped for this reason, the work item carries a warning
    naming the task, the colliding work items, and what to do — the ambiguity is never silent.
  - `impl_commit_match()` returns `(credited, skipped_subjects)`; `has_impl_commit()` is kept as
    the boolean wrapper. Both state derivation and re-review detection pass the work item.
  - Fixture-verified in all four directions: the reported false positive is gone, the rightful
    owner is credited once its subject is qualified, the other work item still is not, and an
    unambiguous single-work-item repo still credits a plain `feat(T-001): ...`.
- Warning is owner-aware: when the skipped commit names one of the other work items that
  declares the ID, it says so and offers no `--mark` remedy. The generic advice would have
  talked an operator (or an orchestrator session) into hand-recreating the exact false positive
  this check prevents. Re-review detection carries the same warning — a skipped fix commit there
  would otherwise silently keep printing `implementation-fix` forever. Both from the v2.8.4
  fresh review.
- Convention documented where it is used: `guides/orchestrator-integration.md` step 6 commit row
  and the evidence-ladder section now state the qualified-subject rule and why refusing to credit
  is the safe direction.

## [2.8.3] — 2026-08-07

### Added
- **Closure requires a repo-level CHANGELOG entry.** Evidence: two consecutive
  autonomously-shipped repos were born without a changelog (granary — org-review
  S-2026-08-05-12; business-framework — org-review S-2026-08-07-1). The rule existed only
  as prose in an external patterns doc, and prose rules do not survive closure; it is now
  stated at the step where the gap was created, in every place that carries the closure
  checklist or the work-item doc-maintenance triggers: `next-step.py`'s two closure action strings
  (the authority an autonomous orchestrator actually reads — the fresh review of this
  change caught that a docs-only edit would not have prevented the failure it cites),
  `guides/orchestrator-integration.md` Step 10, and the maintenance-trigger table in both
  `templates/claude-md.md` and scaffold `CLAUDE.md`. `guides/maintenance.md` now
  distinguishes spec-index changelogs from the repo-root one. BACKLOG gap #5
  (brief-closure checklist) is resolved by the same change. Promoted from the 2026-08-07
  org-review drift analysis.

## [2.8.2] — 2026-08-05

### Fixed
- **Documentation-type tasks now gain evidence from `docs:` commits** (`next-step.py`, org-review S-2026-08-05-11; evidence: pipeline-runner `runs/SUMMARY.md` item 7). `docs:` is rightly excluded from implementation evidence for every other task type — but for a Documentation task it is the *natural* prefix, and excluding it made doc tasks whose sessions self-commit invisible to the evidence ladder (measured live: a Documentation task looped through a redundant implementation pass because its own `docs: ... (T-XXX)` commit did not count). `has_impl_commit` is now type-aware: the `docs` exclusion is lifted only when the task block's Type is `Documentation`, in both state derivation and re-review detection; `chore` and the other bookkeeping prefixes remain excluded for all types.

## [2.8.1] — 2026-08-05

Both fixes adopt org-review suggestions (S-2026-08-05-7/-8) whose evidence is the pipeline-runner's committed hardening record (`runs/SUMMARY.md` items 8 and 9, from the granary build run).

### Fixed
- **`chore:` commits are no longer implementation evidence** (`next-step.py`). Bookkeeping commits that name a task ID — parks, overlay edits, event-log flushes — counted as implementation evidence, the same blind spot the `docs:` exclusion already covered for another prefix. Measured live: a `chore(...): drop stale overlay ... T-001` commit re-triggered a fresh re-review. `chore` joins the excluded prefixes.
- **A trusted overlay that contradicts review evidence now warns loudly** (`next-step.py`). Measured live: an overlay `implemented` written before a revise verdict silently masked the fix loop, costing a redundant review session. The overlay still wins — it is the orchestrator-owned state by design — but a `done`/`implemented` overlay entry over a `revise` verdict now emits a warning naming both, so stale entries get cleared instead of silently steering.

### Added
- **LICENSE: MIT** — the standing owner decision from BACKLOG, resolved (org-review S-2026-08-05-9).

## [2.8.0] — 2026-08-03

### Changed
- **Review verdicts are outcome-anchored: the approve-with-advisories tier.** Both review prompts' Step 4 previously blocked on "any CONFIRMED medium+" — and since reviewers rate nearly every real observation medium while fresh reviews are non-exhaustive, revise loops ratcheted instead of converging (measured three times: three disjoint-finding revise rounds in each worker-model arm, two in the /orchestrate fixture; the Opus arm's final round blocked on one medium with everything else explicitly advisory — the BACKLOG trigger). New rule: `revise` only when a CONFIRMED finding means the artifact as written yields **wrong**, **unbuildable**, or **unverified-against-AC** software (implementation reviews add failing tests, unmet ACs, and spec desync — unchanged); severity alone no longer blocks, and PLAUSIBLE findings never block alone. Non-blocking findings — whatever their severity — go in a structured `## Advisories` section with a disposition contract: never silently dropped; recorded in the committed review, cherry-picked at acceptance, or parked as new work items. The §2 verdict regex and every consumer (next-step, runners, /orchestrate) are unchanged: `approve` with advisories parses as `approve`. Expected effect (honest): trims the ratchet's tail, not its head — genuinely blocking rounds still revise; the terminal advisory-grade round now terminates. Evaluation guide notes that first-pass accept rates rise by definition from this version.

## [2.7.1] — 2026-08-03

### Fixed
- **`next-step.py` detects applied fixes and emits the fresh re-review step itself** — at both loop levels. A revise verdict goes stale the moment its fixes are committed, but the tool kept emitting revision/fix steps because it only read the verdict file. Measured live in the Opus-as-orchestrator test: a one-step-per-invocation driver ran the revision correctly, then had to escalate to the human purely to ask "re-review now?". Mechanical signal, no new state: commits touching `tasks/<WI>-tasks.md` (or, for implementation loops, fix-type commits referencing `T-XXX`) after the newest commit touching the corresponding review file ⇒ emit the fresh re-review step instead. Verified against three historical fixtures (the exact trapped states from the live runs) plus regressions. Commits are the step boundary (guide rule 2) — uncommitted edits deliberately do not count.

## [2.7.0] — 2026-08-03

All four changes come from the first full autonomous pipeline run (an 11-task feature driven end to end by an external runner over the v2.6.0 contracts — shipped working, tested software; findings below are what it surfaced).

### Fixed
- **`validate-specs.py` no longer scans inside HTML comments.** Reference checks in indexes and work items now strip `<!-- -->` blocks (line-numbers preserved) before matching shard paths. This is the root fix for two measured false-failure modes: the scaffold's spec-index stubs carry commented example rows (`screens/login.md`, `endpoints/resources.md`) that failed a fresh scaffold under `--strict`, and template guidance with example paths failed filled work items.
- **Work-item templates' "Retrieval key" guidance moved into HTML comments** (feature-brief ×3, bug-report, improvement-proposal — root templates + scaffold TEMPLATE copies). The guidance text is unchanged and still visible to authors editing raw markdown, but its example shard paths (`task-label.md`, `project-board.md`) can no longer leak into filled briefs as phantom references — measured cost of the old form: a $1.46 spec session gated out by pre-existing template text.
- **Closure can no longer be short-circuited by an early Status flip.** Measured failure: the closing docs task set the work item's Status to Completed itself, `next-step.py` derived the work item as closed, and the formal step-10 closure (strict gate, close commit) never ran. Now: a closed Status is trusted only when every task has completion evidence AND a `close(<WI>)` commit exists; otherwise the frontier continues with a warning, and an evidence-complete work item without a close commit still gets the closure step. The step-9 session prompt in orchestrator-integration.md now says explicitly: leave Status unchanged — closure owns the flip.
- **Task-list revision prompt now requires consistency, not just minimal diffs.** "Change nothing else" caused a measured extra review round: the revision applied the required changes and left the Summary contradicting the fixed Dependencies fields. The prompt (next-step.py + guide §4) now requires updating the Summary and AC-coverage table to stay consistent with the applied changes. The guide also documents the deeper measured behavior: fresh-review revise loops RATCHET (three consecutive reviews, disjoint finding sets) — the cap is structural. An approve-with-advisories verdict tier is recorded in BACKLOG.

### Added
- **Per-step token accounting as a first-class contract.** Every pipeline step should record its approximate `session_tokens` in `metrics/events.ndjson`; the schema (guides/evaluation.md) gains optional `model` and `cost_usd` fields (cost explicitly notional under subscription auth). New `next-step.py --log-event step=... wi=... event=... tokens=... model=...` appends a well-formed event from any driver — human, `/orchestrate` session, or external runner — and `/orchestrate` step 3 now records usage after every gate.

## [2.6.0] — 2026-08-02

### Added
- **`tools/next-step.py` — the pipeline's sequencing gate.** Derives pipeline position per work item from artifacts alone (orchestrator-integration.md rule 1) and prints the next legal step(s) with the session prompt and the exact gate command — sequencing stops being a model judgment call, the same mechanical-beats-prose lever that made the validators work. Evidence ladder per task (first hit wins): progress overlay > implementation-review verdict (approve ⇒ done, revise ⇒ needs-fix, via the guide's §2 verdict regex verbatim) > git commit evidence (a commit referencing `T-XXX` whose type prefix is not plan/review/tasks/docs/close) > plan file exists > pending. Understands workflow gates (`mockup-first` requires the mockup before planning surfaces), the step-7 S-complexity review skip rule, step-9 docs-only detection, step-10 closure, dependency-DAG readiness, and file-set conflict warnings for parallel candidates. Read-only except `--mark`; `--json` for machine use; ASCII-only output; stdlib-only; task parsing mirrors `validate-tasks.py` (the validator stays the schema gate).
- **Per-work-item progress overlay** (`tasks/<WI>-progress.json`) — §6's orchestrator-owned state in repo form, written only by `next-step.py --mark T-XXX=<status> [--note ...]` (plus `task-review=accepted`). Exists precisely for the states artifacts cannot express: S-task completions without a review, reviews accepted after their revise loop, external blockers. Everything artifacts CAN express is derived, never duplicated; accepted artifacts stay immutable.
- **`/orchestrate` scaffold command** — the slim in-repo driver loop: run next-step.py, execute exactly ONE step by spawning a subagent with the printed prompt (`[FRESH SESSION]` steps get clean context by construction), run the printed gate, commit, re-run, stop. The orchestrating session's context stays process-only, which is what keeps long pipelines from drifting.
- **orchestrator-integration.md §8** — documents the in-repo solo/attended mode (evidence ladder, overlay semantics, what the tooling deliberately does not do) and when to graduate to an external orchestrator. Validated against a real 15-task project: derived state matched known reality for all 15 tasks, and immediately surfaced a genuine drift (a task-list review whose file still said `revise` after its changes were applied and accepted only conversationally — exactly the overlay's job).

### Fixed
- **The 2.5.5 release never reached the scaffold** — it edited root `prompts/compile-adrs.md` but ran neither `scripts/sync-scaffold.sh` (the scaffold's copy was still the pre-2.5.5 text) nor the hand-maintained `scaffold/.ai-framework/VERSION` bump (still 2.5.4). Both fixed by this release's sync; VERSION is now 2.6.0. A `--check` in CI or pre-commit would have caught this — noted in BACKLOG's team-scale items.

## [2.5.5] — 2026-08-02

### Changed
- **`prompts/compile-adrs.md` synced to the ADR repo's current metadata format.** The prompt still documented the pre-migration bold-line metadata; ADRs have since moved to YAML frontmatter and grown `family`, `last_reviewed`, `superseded_by`, and `verify_against` keys. The Format Reference now shows the frontmatter (with selection semantics: one member per `family` matching the project stack; Superseded files are tombstones — follow `superseded_by` to the replacement; freshness keys are maintenance metadata, not derivation inputs). Step 0 gains the family-exclusivity error and a note to run the ADR repo's validator as a preflight when one ships. The Stack Profile Format now matches real profiles (tiered tables with ADR-path rows, ignorable generation markers, optional Golden Skeleton reference implementations). Compiled output now records the ADR repo version tag. Rule 2 gains explicit `typescript` and `deployment` rows; the appendix examples use frontmatter.

## [2.5.4] — 2026-07-30

### Fixed
- **Scaffold stakeholder §3 now mirrors the template's 3.1/3.2 split** — `### 3.2 What We Intentionally Avoid in [Version]` had no counterpart content in the scaffold (the philosophy-level anti-scope was simply absent; distinct from the Scope Lock's feature list). Missed by v2.5.2, which swept top-level headings only. The §4 stub also gains the "Why this works" line for content parity with template §4.2.

### Changed
- **Scaffold parity rule codified** (README, "Editing the framework"): scaffold docs match templates heading-for-heading at every `##` level; subsections may be condensed only when their content is fully preserved. A full heading audit found §3.2 to be the only content gap; the remaining differences are documented condensations: stakeholder §4.1/4.2, §5.1, §7 phases → bullets; ARCHITECTURE §2.1–2.4 → one stack table, component/flow subsections → lean lists, §7.1/7.2 → two bullets; persona alternative-segment subsections → one table.

## [2.5.3] — 2026-07-30

### Changed
- **`templates/stakeholder.md` renamed to `templates/stakeholder-definition.md`** so the template↔doc pair matches 1:1. The old asymmetry was inherited wording, not design; the doc side (68 references + every consuming project's existing file) was the expensive direction, the template side had zero path references. The remaining name differences in the mapping all have real justifications: `claude-md.md` → `CLAUDE.md` (naming the template `CLAUDE.md` would make Claude Code load it as live instructions inside the framework repo), `persona.md` → `personas/primary-user.md` (one template, many instances), `architecture.md` → `ARCHITECTURE.md` (repo-level docs convention, case only).

## [2.5.2] — 2026-07-29

### Fixed
- **Scaffold docs no longer ship silent section gaps.** The "strict subset" rule from the v2.1 convergence let scaffold docs omit template sections while keeping template numbering — producing visibly discontinuous numbering (stakeholder-definition jumped §3 → §7) with no in-file explanation, indistinguishable from an authoring error. The omissions bought nothing measurable: the scaffold's leanness lives in shorter guidance, not absent sections, and no cross-reference depended on the gaps. All omitted sections are restored as lean fill-in stubs, preserving the template's "(Optional — delete if not applicable)" markers: `stakeholder-definition.md` gains §4, §5 (UX Strategy — never marked optional in the template; its omission was an inherited oversight), §6, §11; `ARCHITECTURE.md` gains §5.2, §7, §8; `data-model/index.md` gains §5.2. Every scaffold doc now numbers contiguously and matches its template heading-for-heading.

## [2.5.1] — 2026-07-16

### Added
- **`guides/orchestrator-integration.md`** — the per-step contract for driving the pipeline from an external orchestrator: the session contract (spawn flags, --add-dir requirement, timeouts, retry policy), per-step specifications for all ten pipeline steps (preconditions, session prompts, outputs, gate commands, commit conventions, event emissions, revise loops), mechanical parsing contracts (verdicts, dependency DAG, file-set conflict scheduling), the orchestrator-owned state boundary, and auto-accept calibration from the measured baselines.

## [2.5.0] — 2026-07-16

The pipeline's last gate: implementation review, written and measured.

### Added
- **`prompts/review-implementation.md`** — the step-6 gate: fresh-session adversarial review of an implemented task's diff against its acceptance criteria, plan, conventions, spec sync, and test adequacy; external evidence first (tests/linters/validate-specs as ground truth); verdict to `tasks/<TASK-ID>-implementation-review.md`, ≤120-line budget. Wired: routing row + Development Pipeline step 6, context-compilation §12, getting-started pipeline step, `/review-implementation` command.
- **case-010-review-t002-impl**: a git-apply-clean implementation diff with five planted defects. Baseline: reviews caught **all four CONFIRMED defects in 3/3 samples** (unmet 409 AC, skipped index sync — corroborated via the validator warning, scope-creep export endpoint, undocumented PUT-for-PATCH deviation) **plus real unplanted findings** (export's envelope violation; the test file colliding with T-007's ownership — true in the fixture). The fifth plant (inline normalization as a convention violation) was explicitly examined and cleared by reviewers — it was sanctioned by the fixture's own conventions; its anchor was removed as a calibration false positive. Rescored: **3/3**.
- **Coverage: every prompt in use is measured** — 10 of 11, with compile-ddrs dormant (no DDR repo in the organization yet; BACKLOG documents the revival path).

## [2.4.11] — 2026-07-16

### Added
- **case-009-python-react-profile** — compile-adrs measured for the first time, against a fixture frozen from the organization's REAL ADR repo (18 ADRs, closed Requires chains, profile edited to match): **3/3 deterministic, judge 8.7 (8–9)** — every ADR represented exactly once, constraints faithfully derived, traceability comments resolving, no invented content, no cross-profile leakage. **Prompt coverage: 9/11** (remaining: compile-ddrs — needs a DDR repo; review-implementation — not yet written).

## [2.4.10] — 2026-07-16

### Added
- **case-008-project-board-mockup** — mockup-generation measured for the first time: **3/3 deterministic, judge 8.0 (8–8, fully stable)**. The v2.1 "fully self-contained HTML" guarantee is now mechanically asserted (no external URLs, no `<link>`/`<script src>`, embedded CSS, design-token hex fidelity, four states side-by-side) and held in every sample. **Prompt coverage: 8/11** — everything except the two compile prompts (which need ADR/DDR fixture repos) and the not-yet-written review-implementation prompt.

## [2.4.9] — 2026-07-16

### Added
- **case-007-ui-spec-from-specs** — ui-spec-generation measured for the first time, completing the spec-generation chain (strategy → data model → API spec → UI spec) in the shared TaskFlow fixture world. Results: **3/3 deterministic (merged-overlay strict lint clean), judge 9.0 (9–9)** — full user-flow coverage, zero excluded-scope screens, all component→API mappings use real endpoints (the deliberate no-task-delete hallucination trap caught nobody). **Prompt coverage: 7/11.**
- `spec_validator` **overlay** option: merges input-fixture docs with the generated tree into a temp root before linting, enabling downstream-spec cases whose outputs cross-reference fixture shards.

## [2.4.8] — 2026-07-16

### Added
- **case-006-plan-label-endpoints** — plan-generation measured for the first time: plans T-002 from case-001's golden task list. Results: **3/3 deterministic, judge 9.0 (9–9)**, all plans 74–78 lines (half the ≤150 budget), exact single-task scope, conventions fidelity confirmed. **Prompt coverage: 6/11.**
- `line_count` check type — the v2.4.1 plan/output budgets are now mechanically enforceable in evals.

### Fixed
- **Frozen-fixture staleness time-bomb**: `validate-specs --max-age 0` disables stamp-age checking (presence still verified); `spec_validator` eval checks default to it. Without this, every strict fixture lint would have started failing ~30 days after its fixed stamp date.

## [2.4.7] — 2026-07-16

### Added
- **Multi-output eval support**: `output` in assertions.json may be a directory (concatenated with `<!-- FILE: … -->` headers for text/judge checks, archived/restored as trees); new `spec_validator` and `files_exist` check types; judge reference anchors accept trees.
- **case-005-data-model-from-strategy** — spec-generation covered at last: strategy-stage fixture (stakeholder + architecture, no specs), hand-written 4-entity reference tree, six-dimension rubric. First results: **3/3 deterministic (validate-specs --strict clean on every generated tree), judge 8.3 (8–9)** — exact scope coverage, zero scope creep. **Prompt coverage: 5/5.**
- **EXP-003 (read-order sensitivity)**: inverted context read order scored identically to control (9.0 vs 9.0) — read order is not a lever for agentic sessions; a chat-assembly-only ordering note was added to context-compilation.md and the pending U-curve recommendation resolved.

### Fixed
- Whole-directory output cleanup no longer deletes the tracked `output/.gitkeep` anchor.

## [2.4.6] — 2026-07-16

Access-confound fix, judge robustness, and the post-fix canonical baseline.

### Fixed
- **Headless eval generation agents were permission-blocked from reading the framework prompts** (cwd = case dir); they had been reverse-engineering the schema via validator probing and a `Bash(python *)` sandbox bypass, sharing findings through project auto-memory. Gen command now passes `--add-dir <repo root>` (verified); the schema-bearing memory was purged. EXP-002 run 1 was aborted as invalid; the old baselines carry an access caveat.
- Judge verdict-line omissions are retried (3 attempts) instead of failing the check; subprocess captures forced to UTF-8; validator no longer parses `---` separators as file entries.

### Added
- **`judge_samples` / `--judge-samples`**: median-of-N judging, validated to stabilize near-threshold scores (a 6↔8 flip-flop sample settled at 7).
- **Baseline `v2.4.6`** — the canonical post-fix regression floor: 18/18 deterministic across all 6 cases; judged medians (median-of-3): feature 9.0, bugfix 8.0, ablation arm 8.7, no-docs arm 6.7.
- **EXP-002 run 2 (anti-example ablation) completed**: control 9.0 vs variant 8.7 — no measurable effect at n=3; anti-examples kept as cheap insurance, on probation per the "every element earns its place" standard.
- **EXP-001 replicated under correct access**: docs gap widened to ~2.3 points (9.0 vs 6.7, one no-docs sample failing) — strongest confirmation that the sharded spec docs earn their context.

## [2.4.5] — 2026-07-15

### Added
- **Spec-fidelity judge dimension**: rubrics gained a sixth dimension (technical details must match project ground truth — routes, envelope, error codes, field names; invented conventions penalized), and the judge check gained a `"context"` key embedding spec excerpts into the judge prompt so fidelity is checkable against ground truth the candidate may never have seen.
- **EXP-001 addendum**: re-judging the archived A/B samples with the new dimension flipped the verdict — with-docs 9.0 (up from 8.7, fidelity explicitly praised) vs no-docs **7.0 with one failing sample** (down from 8.5; it planned to create spec files that already exist in the ground-truth project). Skipping existing spec docs at generation time costs ~2 judge points and produces plans contradicting project state; the lean-docs position is affirmed, the no-docs and 30-page positions are both unsupported.
- **EXP-001 addendum 2** (arm B completed at n=3): final arm B = 3/3 deterministic, judge **7.7 (7–8)** vs arm A 9.0 (9–9) — gap direction consistent in every pass. Judge variance observed on the borderline sample (6 in one pass, 8 in another): single scores within ±1 of `min_score` are inconclusive; rule adopted — median of 3 judge runs for gating decisions (`judge_samples` runner key backlogged).

## [2.4.4] — 2026-07-15

### Added
- **EXP-001, the context A/B experiment** (`evals/experiments.md`): arm A (with sharded spec docs) vs arm B (`case-901`, spec docs physically removed from generation input, checked against the full fixture). Results: statistically indistinguishable on all metrics (A: 3/3 deterministic, judge 8.7; B: 2/2, judge 8.5; identical routes and error vocabulary) — because the work item's impact tables already carry the grounding. Three findings: the generation-time validator **self-check is the compliance lever** (its accidental omission in run 1 produced 0/3 schema compliance with unchanged judge scores); information density at the point of use beats document volume; briefs authored *from* specs compress them effectively (the realistic no-docs scenario remains untested). Both runs archived under `evals/baselines/ab-minimal-context*/`.
- `case-901-task-labels-minimal-context`: permanent experimental arm tracking the docs/no-docs gap in future baselines.

## [2.4.3] — 2026-07-15

First measured baseline, and the eval loop's first catch — a false-positive in its own assertion.

### Added
- **`evals/run-baseline.py`**: N samples per case via headless Claude Code CLI (parallel across cases), archives every sample under `evals/baselines/<label>/`, tabulates pass rates and failing checks; `--rescore <label>` re-checks archived samples after assertion/checker changes without regenerating.
- **Baseline `v2.4.2`** (4 cases × 3 samples, 12/12 generated, ~6–11 min/sample): initial scoring 75% overall; diagnosis showed all failures were the same false positive — prose mentions of legitimately-`(new)` shards failing the same-line marker requirement, a rule stricter than the prompts state. After the checker fix (below), rescored **12/12 pass** — the true v2.4.2 baseline.

### Changed
- `shard_refs_resolve` now sanctions a not-yet-existing shard reference when it is marked `(new)` on the same line, anywhere in the document, or in a `sanctioned_by` doc (typically the work item whose impact tables declare the new shards). Verified against a negative test: genuinely invented shards still fail.
- `run-baseline.py` now captures per-check detail text (including numeric judge scores) into the results JSON and shows a judge avg/range column in the summary table.

### Judged baseline (v2.4.2, anchored judge over archived samples)
- feature-tasks: **8.7 avg (8–9)** — judge findings substantive (e.g., one sample flagged a missing dependency between a (new) file and its creating task).
- bugfix-tasks: **8.3 avg (8–9)** — investigation-first structure and root-cause discipline confirmed across all samples.
- Deterministic checks: 12/12. These numbers are the quality floor for future prompt/model changes.

## [2.4.2] — 2026-07-15

### Added
- **Three new eval cases** (framework-repo only), bringing prompt coverage to 4 of the 5 generation prompts:
  - `bugfix-tasks/case-002-overdue-timezone` — internal timezone bug (Status: Reported, root cause deliberately unfilled); asserts investigation-first ordering and root-cause discipline; judge rubric explicitly rewards *not* inventing a producer-contract step for an internal bug.
  - `review-tasks/case-003-review-flawed-tasks` — a validator-clean task list with four planted semantic defects (dependency inversion, scope creep, Type mismatch, AC-5 coverage omission); asserts the fresh-context review reaches a revise verdict and cites each defect. Tests exactly what the validators cannot catch.
  - `refactor-tasks/case-004-date-logic-extraction` — duplicated date logic across API and UI; asserts the Phase-0 coverage baseline precedes the refactor and the Cleanup type is used.
  - All three inputs pass `validate-specs.py --strict` clean; every case ships a hand-written reference output verified to satisfy its own assertions.

## [2.4.1] — 2026-07-14

### Changed
- **Contrastive anti-examples** in the three task prompts: each `## Example` section now ends with an "Anti-Example (would fail review)" block — a compact bad task with every defect annotated against the rule it violates (grab-bag scope, dual Type, untestable ACs, free-text dependencies, skipped investigation/coverage phases, non-canonical field names). Models follow "not like this, because X" better than rules alone.
- **Output budgets**, canonical in `base-template.md`: Description ≤ 3 sentences, 2–5 testable ACs, Technical Notes ≤ 5 bullets, ~6 files per task, ~15 tasks per list before splitting; plans ≤ ~150 lines / 10 steps (`plan-generation.md`). Rationale: generated artifacts are the input to later pipeline steps, so verbose output degrades downstream precision the same way verbose docs do. Task prompts reference the canonical budgets; checklists gained matching items.

## [2.4.0] — 2026-07-14

Effectiveness measurement: turn "the framework works" into numbers computed from the repo.

### Added
- **`guides/evaluation.md`**: the four-level evaluation methodology (compliance → offline prompt evals → online pipeline scorecard → counterfactual ablations), the Level 3 metric definitions (first-pass acceptance, human correction burden, AC leakage, defect attribution, doc drift, cycle time, token cost), the `metrics/events.ndjson` event-log schema for orchestrators, and the measurement cadence.
- **`tools/metrics-report.py`** (shipped into `.ai-framework/tools/`): prints the effectiveness scorecard from artifacts + git history + the optional event log — per task list: correction burden (diff of first committed vs current version) and amendment count; review verdict acceptance rates; doc health (validate-specs + stamp-age distribution); BUG→FEAT defect attribution; per-step acceptance/duration/token metrics from events. Degrades gracefully without git or events.
- **`judge` check type** in `evals/run-evals.py`: anchored LLM-judge scoring (rubric + known-good reference + JSON verdict contract), skipped by default so deterministic runs stay CI-safe; `--judge` executes with a configurable command template (Claude Code CLI by default). Case-001 gains `rubric.md` (five-dimension scoring guide) and `reference/tasks.md` (verified anchor output).
- **`BACKLOG.md`**: documented deferred items — the five pipeline lifecycle gaps (per-task status, implementation record, implementation-review prompt, mandatory closing docs task, brief-closure checklist), team-scale items, and prompt refinements.
- `validate-tasks.py`: work-item acceptance criteria in `- **AC-n**:` bullet form are now recognized by the coverage cross-check.

## [2.3.0] — 2026-07-14

Verification harnesses: external-feedback checks at every step, per the self-correction research (models can't reliably self-review; tools and fresh contexts can).

### Added
- **`tools/validate-specs.py`** (shipped into `.ai-framework/tools/`): cross-shard consistency linter — frontmatter parsing/kind/name-vs-filename checks, cross-reference resolution (entity↔resource↔screen), index↔shard bidirectional consistency, freshness-stamp presence and staleness (`--max-age`, default 30 days), and work-item retrieval-key resolution. Wired into spec-generation/ui-spec-generation checklists (first item), task-prompt checklists (second item), the Development Pipeline, and the maintenance PR checklist.
- **Shard frontmatter**: every spec shard now begins with flat machine-readable frontmatter (`kind`, `name`/`resource`/`screen`, cross-reference arrays) enabling deterministic retrieval-key resolution by orchestrators and mechanical linting. Index files carry none; the freshness stamp stays as the blockquote under the H1.
- **`prompts/review-tasks.md`** + routing row "Task list review" + `/review-tasks` command: adversarial review of a generated task list in a FRESH agent session (no generation history) — runs both validators first as ground truth, then judges against a six-point rubric (AC completeness, scope fidelity, reference reality, dependency logic, sizing, workflow correctness) with CONFIRMED/PLAUSIBLE findings and an approve/revise verdict written to `tasks/<WORK-ITEM-ID>-review.md`. Includes orchestrator guidance for best-of-N candidate selection.
- **`evals/` harness** (framework-repo only): golden-set regression testing for the prompts — fixture TaskFlow project + declarative assertions (`validator`, `task_count`, `must_match`/`must_not_match`, `paths_exist`, `shard_refs_resolve`) executed by `evals/run-evals.py`; generation and checking deliberately separated so the check step is deterministic and CI-safe.

## [2.2.0] — 2026-07-14

Context-efficiency and precision release: load less, trust fresher, verify outputs.

### Changed
- **Spec documents are now sharded.** `docs/data-model.md`, `docs/api-spec.md`, and `docs/ui-specification.md` become directories: a lean `index.md` for cross-cutting content (conventions, envelope/error catalog, design system) plus one shard per entity (`entities/<entity>.md`), resource (`endpoints/<resource>.md`), and screen (`screens/<screen>.md`, plus `components.md`). Names map mechanically (kebab-case) so shard paths are derivable.
- **Work-item impact tables are retrieval keys.** Task generation reads each spec's `index.md` plus only the shards named by the work item's impact tables — never whole spec directories. Routing table, prompts, and the canonical context matrix updated accordingly.
- **Contract/rationale split.** Spec and architecture docs stay contract-style (tables, schemas, rules, one example each); narrative and history move to `docs/rationale/`, which is never loaded as AI context. All templates carry a context-budget callout.

### Added
- **Freshness stamps**: every spec shard, spec index, and ARCHITECTURE.md carries `> **Last verified against code:** YYYY-MM-DD (commit ...)`. New CLAUDE.md pre-work rule: verify shards with missing/stale (>30 days) stamps against the source before relying on them; maintenance guide defines the stamp lifecycle.
- **`tools/validate-tasks.py`** (shipped into `.ai-framework/tools/`): machine-checkable gate for generated task lists — required fields and enum values, unique/sequential task IDs, dependency DAG (dangling refs, cycles), file-path existence with a `(new)` marker convention, per-task acceptance-criteria checkboxes, and `--work-item` cross-checking of the new Acceptance Criteria Coverage table. `--strict` promotes warnings to failures for CI.
- **Acceptance Criteria Coverage table** required in feature task lists (recommended for bugfix/refactor): maps each work-item AC to the tasks covering it.
- Validation step added to the Development Pipeline and to every task prompt's Post-Generation Checklist; sync script now also syncs `tools/`.

## [2.1.0] — 2026-07-14

### Fixed
- Scaffold copy commands: `guides/getting-started.md` referenced the v1 path and used `scaffold/*`, which silently skipped the hidden `.ai-framework/` folder; the README variant clobbered the target project's README. Both now use `cp -r .../scaffold/. .`.
- Recommended fill order was contradictory between README sections (Architecture vs CLAUDE.md first); standardized on Persona → Stakeholder → CLAUDE.md → Architecture → specs.
- Dead references: `scaffold/docs/ui-specification.md` pointed at "Section 2.5/2.6" that only existed in the full template; `release-lifecycle.md` referenced nonexistent "Change Policy" sections; guides cited prompt section headings that didn't exist.
- `spec-generation.md` required a "Backend Responsibilities" section the scaffold stakeholder doc didn't have (section added to scaffold + fallback added to prompt).
- ADR/DDR compilation targeted CLAUDE.md headings that differed between the template ("Preferred Patterns") and scaffold ("Patterns to Follow"); standardized on "Patterns to Follow" / "Anti-Patterns to Avoid", and added the missing "Design Patterns to Follow" / "Design Anti-Patterns to Avoid" stubs to the scaffold CLAUDE.md.
- Existing-codebase path (Phase 2-alt) was missing the steps that produce the three spec docs.
- Numerous cross-file drift issues in the context-selection matrix (required vs optional context now aligned everywhere; `guides/context-compilation.md` is canonical).

### Added
- **Defined output locations**: task lists → `tasks/FEAT-XXX-tasks.md` (previously undefined), plans → `plans/plan-T-XXX-short-title.md`, mockups → `mockups/T-XXX-screen-name.html`, DDR component examples → `docs/component-examples.md`. Scaffold ships `tasks/`, `plans/`, `mockups/` directories.
- **Canonical task schema** in `prompts/base-template.md` (Task ID, Title, Type, Workflow, Description, Rationale, Acceptance Criteria, Dependencies, Complexity S/M/L/XL, Files to Modify/Create, Technical Notes); task prompts now declare only deltas.
- **Claude Code slash commands** in the scaffold (`.claude/commands/`): `/feature-tasks`, `/bugfix-tasks`, `/refactor-tasks`, `/spec-generation`, `/ui-spec-generation`, `/mockup-generation`, `/plan-generation`, `/compile-adrs`, `/compile-ddrs`.
- **Changelog stubs** at the bottom of the four living spec docs (data model, API spec, architecture, UI spec) in both templates and scaffold, satisfying the maintenance guide's changelog rule.
- **Filled work-item examples** (`templates/examples/`) for a fictional "TaskFlow" product — the scaffold blanks are now named `TEMPLATE-*` so `FEAT-*` globs never match empty shells.
- API spec template: Error Catalog and Authentication Endpoints sections. Architecture template: Observability section and Failure Strategy column. Bug report: Root Cause & Resolution section. Feature brief: Blocked status + NFR row. Improvement proposal: Estimated Effort field.
- `scripts/sync-scaffold.sh` (+ `--check` mode) to regenerate `scaffold/.ai-framework/` from the root sources.
- This CHANGELOG; `VERSION` now uses semver.

### Changed
- **All 10 prompts restructured agent-first**: Purpose / How to Use / Required Context / Guidance / Output Format / Constraints / Post-Generation Checklist as plain sections; the chat XML skeleton is now an appendix instead of wrapping the normative rules. Agents are instructed to write output files, not just return chat text.
- **Stack neutrality**: unconditional Angular / Angular Material / Tailwind / EF Core / DbContext mandates replaced with "the stack declared in CLAUDE.md" plus bracketed examples; mockups default to self-contained plain-CSS HTML (Tailwind v4 browser build referenced where a CDN is wanted); client-specific profile names removed.
- Scaffold docs converged with templates: numbered headings restored, closing sections renamed to "Usage Notes for AI Task Generation", dropped rows restored (accessibility, API versioning, disabled state), stakeholder section order matched.
- Removed stale prompt-engineering advice from `base-template.md` (sub-2000-token context loading patterns, manual reasoning priming) and per-file "(v1)"/"(v2)" labels.
- `scaffold/README.md` merged into `scaffold/.ai-framework/README.md` (so copying the scaffold no longer ships a stray README), which now also documents the template↔doc name mapping.

## [2.0.0]

- v2 baseline: 10 core templates (7 system + 3 work item) across 6 layers, 10 prompt templates with dual AI-agent/chat usage, 4 workflow guides, bundled `.ai-framework/` scaffold, ADR/DDR compilation prompts, release lifecycle guide.

## [1.0.0]

- Initial framework: 4 foundational templates (Persona, Stakeholder, Architecture, CLAUDE.md) and basic task-generation prompts.
