# Case 009 — Compile the Python + React Stack Profile ADRs into Template Sections

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/compile-adrs/case-009-python-react-profile/`).

## Setup

- Treat `input/adr-repo/` as the organization's shared ADR repository: `input/adr-repo/profiles/python-react-modular-monolith-docker-compose.md` is the stack profile to compile, `input/adr-repo/adrs/<category>/*.md` are the ADRs it lists (18 files), and `input/adr-repo/ADR-FORMAT.md` documents the ADR format.
- Do not modify anything under `input/`.
- This fixture has no project docs and no `.ai-framework/` directory — the **Output Format** blocks of the prompt define exactly which sections to fill; the target templates live at `../../../../templates/` (`claude-md.md`, `architecture.md`, `data-model.md`, `api-spec.md`) if you need the surrounding heading structure.

## Context to Read

1. `input/adr-repo/profiles/python-react-modular-monolith-docker-compose.md` — the stack profile: its Required/Recommended/Optional lists select the ADR set to compile (all 18 listed ADRs are selected).
2. Every ADR file under `input/adr-repo/adrs/` — the Category/Status/Requires/Conflicts header fields plus the Decision, Rationale, and Constraints sections are the sole derivation source.
3. `input/adr-repo/ADR-FORMAT.md` — format reference only.

## Procedure

1. Follow `../../../../prompts/compile-adrs.md` end-to-end.
2. **Step 0 (Validate Dependencies) FIRST**: check every selected ADR's `Requires` and `Conflicts with` fields against the selected set, and check that every profile-Required ADR is selected. Report any findings using the prompt's exact string formats (`⚠ [adr-file] requires [missing-adr] which is not in the selected set. Include it or remove the dependent ADR.` / `❌ [adr-a] conflicts with [adr-b]. Remove one before compiling.`). This fixture is expected to validate clean — record the clean result as a short HTML comment at the top of each output file (e.g., `<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->`). If you find warnings or errors, list them there verbatim instead.
3. Apply the **Derivation Rules** (Rules 1-6) to all 18 ADRs and produce the four **Output Format** blocks, one file per block (see Output below).
4. **Traceability**: every derived bullet and table row carries an HTML comment with the ADR's repo-relative path — `<!-- from: adrs/<category>/<file>.md -->` — as the only traceability marker (never inline `(from: ...)` text). When de-duplicating a rule contributed by several ADRs, keep one entry and append one `from:` comment per contributing ADR.
5. **Scaffold discipline**: sections the rules do not fill get `<!-- TODO: ... -->` scaffolds under their template headings. Do not invent any project-specific content (no product overview, entities, endpoints, screens, commands, or naming rules the ADRs do not state).
6. The CLAUDE.md block's derived headings must be exactly `### Patterns to Follow` and `### Anti-Patterns to Avoid`.

## Output

Write FOUR files under `output/` (relative to this directory), one per Output Format block of the prompt:

| File | Output Format block |
|------|---------------------|
| `output/claude-md.md` | CLAUDE.md sections (Patterns to Follow, Anti-Patterns to Avoid, Naming Conventions + TODO scaffolds) |
| `output/architecture.md` | ARCHITECTURE.md sections (Key Architectural Decisions table, one row per ADR + TODO scaffolds) |
| `output/data-model-index.md` | `docs/data-model/index.md` sections (Key Modeling Decisions, Database Conventions + TODO scaffolds) |
| `output/api-spec-index.md` | `docs/api-spec/index.md` sections (Key API Decisions, Common Conventions + TODO scaffolds) |

The files **are** the deliverable — not chat output. The framework's usual paste-into-project-docs flow does not apply inside the eval harness; these four files replace it.

## Self-Check Before Finishing

Grep your own output and fix every failure:

1. Every `<!-- from: ... -->` path resolves to an existing file under `input/adr-repo/` (e.g., `from: adrs/database/snake-case-naming.md` → `input/adr-repo/adrs/database/snake-case-naming.md`).
2. Every one of the 18 frozen ADR filenames appears in at least one `from:` comment across the four files (Rule 1 completeness — every ADR must be represented).
3. The headings `### Patterns to Follow` and `### Anti-Patterns to Avoid` appear exactly in that form in `output/claude-md.md`.
