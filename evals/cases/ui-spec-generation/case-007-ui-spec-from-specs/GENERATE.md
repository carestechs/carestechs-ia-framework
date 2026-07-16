# Case 007 — Generate the UI Specification from the Spec Set (UI Spec Generation)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/ui-spec-generation/case-007-ui-spec-from-specs/`).

## Setup

- Treat `input/` as the project root: `input/docs/` holds the project's generated spec sets.
- This case continues the TaskFlow pipeline from case 005: the **strategy docs live in that sibling case's fixture** and are referenced below by relative path — read them there, do not copy them.
- Do not modify anything under `input/` or under the sibling case directory.
- This fixture is at the **UI-spec stage**: the data model (`input/docs/data-model/`) and the API spec (`input/docs/api-spec/`) exist; producing the UI specification set is this case's job.

## Context to Read

1. `../../spec-generation/case-005-data-model-from-strategy/input/CLAUDE.md` — conventions are ground truth (React 18 function components + hooks, TanStack Query, kebab-case filenames / PascalCase components, one React file per screen under `src/ui/`, response envelope, opaque auth-service user UUIDs / **no local User entity**)
2. `../../spec-generation/case-005-data-model-from-strategy/input/docs/stakeholder-definition.md` — Scope Lock and **Complete User Flow** (the flow drives the screen inventory)
3. `../../spec-generation/case-005-data-model-from-strategy/input/docs/ARCHITECTURE.md` — single `Core` module, React SPA decision, API contract callout
4. `input/docs/data-model/` — `index.md` plus all four entity shards (`entities/project.md`, `entities/task.md`, `entities/project-member.md`, `entities/comment.md`)
5. `input/docs/api-spec/` — `index.md` (envelope, Error Catalog, pagination, Endpoint Summary) plus all endpoint shards (`endpoints/projects.md`, `endpoints/project-members.md`, `endpoints/tasks.md`, `endpoints/comments.md`)

## Procedure

1. Follow `../../../../prompts/ui-spec-generation.md` end-to-end (Guidance, Output Format, Constraints, Post-Generation Checklist).
2. Use the sharded output format from `../../../../templates/ui-specification.md`:
   - `docs/ui-specification/index.md` — **cross-cutting content only, no frontmatter**: Overview with Key UI Decisions (including an explicit accessibility decision), Design System with the **exact numbered sections 2.1 Brand Colors … 2.6 Responsive Breakpoints**, Screen Inventory (with the Shard column — it doubles as the shard directory), Shared Layouts, Usage Notes for AI Task Generation, Changelog.
   - one `docs/ui-specification/screens/<screen>.md` **per screen** — kebab-case filename derived mechanically from the screen name. Each shard begins with a flat-key frontmatter block **before the H1**: `kind: screen`, `screen` (MUST equal the filename), `route`, and `endpoints` — an inline array naming **ONLY endpoint shard names that exist** in `input/docs/api-spec/endpoints/` (e.g. `[tasks, projects]`). Every shard needs a layout sketch, component hierarchy, Component → API mapping, all four states (default/loading/empty/error), and user interactions.
   - `docs/ui-specification/components.md` — the shared-components inventory, opening with `kind: component-inventory` frontmatter.
3. **Screens come from the stakeholder User Flow** — every flow phase must be covered (roughly: a project list, a project board, a task detail panel or screen, member management). Do **not** invent screens for excluded scope: no labels/tags, notifications, or file-attachment screens or components (the Scope Lock excludes them).
4. **Every Component → API mapping row and every interaction's API call must name a method + route that exists in `input/docs/api-spec/`** — do not invent endpoints.
5. **Freshness stamp** — every generated file (the index, every screen shard, and components.md) carries, directly under its H1:

   ```
   > **Last verified against code:** 2026-07-16 (commit `fixture7`)
   ```

   Use exactly this date and commit (fixed so the checks are deterministic) — not today's real date.
6. **Conventions fidelity** — this fixture is React 18 + Express (see CLAUDE.md): React function components, TanStack Query for server state, plain in-project styling conventions. No other frontend framework's concepts or components.

## Output

Write the tree under `output/docs/ui-specification/` (relative to this directory): `output/docs/ui-specification/index.md`, one `output/docs/ui-specification/screens/<screen>.md` per screen, and `output/docs/ui-specification/components.md`. The files **are** the deliverable — not chat output. The framework's usual project-root `docs/ui-specification/` location does not apply inside the eval harness; `output/docs/ui-specification/` replaces it.

## Self-Check Before Finishing

`python ../../../../tools/validate-specs.py --root output --strict --max-age 0` will **FAIL** here: screen frontmatter `endpoints` entries cross-reference `docs/api-spec/endpoints/<name>.md`, which lives under `input/`, not `output/`. Verifying the cross-references "mentally" is **not** acceptable — build a merged root and lint that instead. From this directory:

```
mkdir -p _selfcheck/docs && cp -r input/docs/* _selfcheck/docs/ && cp -r output/docs/* _selfcheck/docs/ && python ../../../../tools/validate-specs.py --root _selfcheck --strict --max-age 0
rm -rf _selfcheck
```

Fix **every error and every warning** it reports (`--strict` promotes warnings to failures), re-running the merged check after each fix, and remove `_selfcheck/` when done.
