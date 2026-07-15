# Changelog

Framework versions follow [semantic versioning](https://semver.org/). Projects can check which version they bundle via `.ai-framework/VERSION`.

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
