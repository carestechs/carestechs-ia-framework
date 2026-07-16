# Case 005 — Generate the Data Model from Strategy Docs (Spec Generation, Step 1)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/spec-generation/case-005-data-model-from-strategy/`).

## Setup

- Treat `input/` as the project root: `input/CLAUDE.md` is the project's CLAUDE.md, `input/docs/` its documentation set.
- Do not modify anything under `input/`.
- This fixture is at the **strategy stage**: `input/docs/` holds only the stakeholder definition and the architecture doc. There are **no spec docs and no source tree yet** — producing the data model spec set is this case's job.

## Context to Read

1. `input/CLAUDE.md` — conventions are ground truth (plural snake_case tables, UUID v4 `id` PKs, timestamptz audit columns, hard deletes, opaque auth-service user UUIDs / no local User entity)
2. `input/docs/stakeholder-definition.md` — Scope Lock, Complete User Flow, Backend Responsibilities
3. `input/docs/ARCHITECTURE.md` — module list (single `Core` module) and the API contract callout

## Procedure

1. Follow `../../../../prompts/spec-generation.md` — **Step 1 (Data Model) ONLY**. Do not generate an API spec or UI spec.
2. Use the sharded output format from `../../../../templates/data-model.md`:
   - `docs/data-model/index.md` — **cross-cutting content only**: Overview with Key Modeling Decisions, Module Ownership, Database Conventions, Relationships Overview (with ER diagram), Shared Enums and Value Types (used by 2+ entities), Usage Notes for AI Task Generation, Changelog. The index gets **no frontmatter**.
   - one `docs/data-model/entities/<entity>.md` **per entity** — kebab-case **singular** filename derived mechanically from the entity name. Each shard begins with a flat-key frontmatter block **before the H1**: `kind: entity`, `name` (PascalCase; its kebab-case MUST equal the filename), `module`, `endpoints`, `screens`. Because no `api-spec/` or `ui-specification/` shards exist yet, `endpoints` and `screens` must be the empty array `[]`.
3. **Freshness stamp** — every generated file (the index and every shard) carries, directly under its H1:

   ```
   > **Last verified against code:** 2026-07-16 (commit `fixture5`)
   ```

   Use exactly this date and commit (fixed so the checks are deterministic) — not today's real date.
4. **Entities come from the Scope Lock.** Every included scope item maps to at least one entity; derive fields from the user flow and backend responsibilities. Do **not** invent entities beyond the scope — explicitly NOT labels/tags, notifications, or file attachments (the Scope Lock excludes them), and no event/log entity (the activity feed is derived on read).

## Output

Write the tree under `output/docs/data-model/` (relative to this directory): `output/docs/data-model/index.md` plus one `output/docs/data-model/entities/<entity>.md` per entity. The files **are** the deliverable — not chat output. The framework's usual project-root `docs/data-model/` location does not apply inside the eval harness; `output/docs/data-model/` replaces it.

## Self-Check Before Finishing

Run, from this directory:

```
python ../../../../tools/validate-specs.py --root output --strict --max-age 0
```

and fix **every error and every warning** it reports (`--strict` promotes warnings to failures).
