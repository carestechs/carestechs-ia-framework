# Changelog

Framework versions follow [semantic versioning](https://semver.org/). Projects can check which version they bundle via `.ai-framework/VERSION`.

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
