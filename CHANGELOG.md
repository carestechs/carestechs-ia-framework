# Changelog

Framework versions follow [semantic versioning](https://semver.org/). Projects can check which version they bundle via `.ai-framework/VERSION`.

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
