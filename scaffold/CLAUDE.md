# CLAUDE.md

> This file provides guidance to Claude Code (or any AI assistant) when working with this codebase.

> **Context budget note:** This document is loaded into AI context. Keep it contract-style —
> tables, schemas, rules, one example each. Move narrative and history to `docs/rationale/`
> and link it; rationale files are never loaded by default.

## Pre-Work Checklist

Before generating specs, tasks, mockups, or implementation plans, you MUST follow these steps:

1. **Identify the task type** using the routing table in the "AI-Assisted Development Framework" section below. **If working on a specific task (T-XXX), check its Workflow field** and follow the Workflow Enforcement rules before starting implementation.
2. **Read the required files** listed in the routing table for your task type — read them directly, do not ask the user to paste them.
3. **Read the prompt template** from `.ai-framework/prompts/` — this defines the required sections, structure, and quality criteria for the deliverable.
4. **Derive structure from the prompt template, NOT from existing output files.** Specs, tasks, and plans are *outputs* — they may reflect an older version of the framework. The prompt templates in `.ai-framework/prompts/` are the authoritative source for format and structure.
5. **Trust code over docs.** Before relying on a spec shard whose "Last verified against code" stamp is missing or older than 30 days, verify its claims against the source (grep/read the relevant code). If it drifted, fix the shard, add a changelog entry, and update the stamp.

---

## Project Overview

<!-- TODO: What does this project do in 1-2 sentences? -->

**Tech Stack:** <!-- e.g., Next.js, TypeScript, PostgreSQL, Tailwind CSS -->
**Repo Type:** <!-- e.g., Monorepo / Single app / Library / CLI tool -->

---

## Quick Reference

### Common Commands

```bash
# Development
# npm run dev          # Start dev server

# Build
# npm run build        # Production build

# Test
# npm test             # Run test suite

# Lint
# npm run lint         # Check code style

# Database (if applicable)
# npm run db:migrate   # Run migrations
```

### Key Directories

<!-- TODO: Map out the important parts of your project -->

```
src/
├── # <!-- e.g., components/  — UI components -->
├── # <!-- e.g., pages/       — Route handlers -->
├── # <!-- e.g., lib/         — Shared utilities -->
├── # <!-- e.g., services/    — Business logic -->
└── # <!-- e.g., types/       — TypeScript types -->
```

---

## Code Style & Conventions

<!-- TODO: List 3-5 conventions that matter most in your codebase -->

- <!-- e.g., Use TypeScript strict mode — no `any` types -->
- <!-- e.g., Prefer named exports over default exports -->
- <!-- e.g., All async functions must have error handling -->
- <!-- e.g., Components are functional with hooks, no class components -->

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files (components) | <!-- e.g., PascalCase --> | <!-- e.g., UserProfile.tsx --> |
| Files (utilities) | <!-- e.g., kebab-case --> | <!-- e.g., format-date.ts --> |
| Functions | <!-- e.g., camelCase --> | <!-- e.g., getUserById --> |
| Types/Interfaces | <!-- e.g., PascalCase --> | <!-- e.g., UserProfile --> |
| Constants | <!-- e.g., UPPER_SNAKE --> | <!-- e.g., MAX_RETRY_COUNT --> |
| Database tables | <!-- e.g., snake_case --> | <!-- e.g., user_profiles --> |

---

## Patterns & Anti-Patterns

### Patterns to Follow

<!-- TODO: What patterns should the AI always use in this codebase? -->

- <!-- e.g., Use the repository pattern for database access -->
- <!-- e.g., All API responses use the standard { data, error } format -->
- <!-- e.g., Use Zod for runtime validation of external inputs -->

### Anti-Patterns to Avoid

<!-- TODO: What should the AI never do in this codebase? -->

- <!-- e.g., Don't use raw SQL — always use the query builder -->
- <!-- e.g., Don't put business logic in route handlers -->
- <!-- e.g., Don't use `console.log` — use the logger service -->

### Design Patterns

#### Design Patterns to Follow

<!-- TODO: Populated by DDR compilation (.ai-framework/prompts/compile-ddrs.md) — or fill in design patterns manually. -->

#### Design Anti-Patterns to Avoid

<!-- TODO: Populated by DDR compilation (.ai-framework/prompts/compile-ddrs.md) — or fill in design anti-patterns manually. -->

---

## Error Handling

<!-- TODO: How should errors be handled? -->

- <!-- e.g., Use custom AppError class for application errors -->
- <!-- e.g., All API errors return { error: { code, message } } format -->
- <!-- e.g., Log errors with structured logging, never swallow silently -->

---

## Testing Conventions

<!-- TODO: How should tests be written? -->

- **Test location:** <!-- e.g., Co-located `__tests__/` folders OR top-level `tests/` -->
- **Naming:** <!-- e.g., `*.test.ts` or `*.spec.ts` -->
- **Framework:** <!-- e.g., Jest, Vitest, Playwright -->
- **Priority:** <!-- e.g., Unit tests for business logic, integration tests for API routes -->

---

## Git Conventions

- **Branch naming:** <!-- e.g., feature/description, fix/description, chore/description -->
- **Commit style:** <!-- e.g., Conventional commits: feat:, fix:, chore:, docs: -->
- **PR requirements:** <!-- e.g., Must pass CI, needs 1 review -->

---

## AI-Assisted Development Framework

This project includes a bundled AI framework (`.ai-framework/`) with prompt templates, context assembly guides, and documentation maintenance rules.

**If you are an AI agent (e.g., Claude Code):** Read the files listed in the routing table below directly — do not ask the user to paste them. Read the prompt template for your task type to determine the output format. For manual/chat workflows, see `.ai-framework/guides/context-compilation.md` for XML assembly instructions.

### Task Generation Routing

When asked to generate tasks, identify the task type, read the required files, read the prompt template for output format, then **write the output file** listed in the Output column — do not leave results only in chat.

| Task Type | Prompt Template | Files to Read (required) | Output |
|-----------|----------------|--------------------------|--------|
| New feature | `.ai-framework/prompts/feature-tasks.md` | `docs/work-items/FEAT-*.md` (target feature), `docs/stakeholder-definition.md`, `CLAUDE.md` | `tasks/FEAT-XXX-tasks.md` |
| Bug fix | `.ai-framework/prompts/bugfix-tasks.md` | `docs/work-items/BUG-*.md` (target bug), `CLAUDE.md` | `tasks/BUG-XXX-tasks.md` |
| Refactoring | `.ai-framework/prompts/refactor-tasks.md` | `docs/work-items/IMP-*.md` (target improvement), `CLAUDE.md`, `docs/ARCHITECTURE.md` | `tasks/IMP-XXX-tasks.md` |
| Task list review | `.ai-framework/prompts/review-tasks.md` | The task list under review (`tasks/<WORK-ITEM-ID>-tasks.md`), the work item, each spec's `index.md` + the shards named by the work item's impact tables, `CLAUDE.md`. **MUST run in a fresh agent session** — no generation history in context | `tasks/<WORK-ITEM-ID>-review.md` |
| Spec generation | `.ai-framework/prompts/spec-generation.md` | `docs/stakeholder-definition.md`, `CLAUDE.md`, `docs/ARCHITECTURE.md` | `docs/data-model/index.md` + `docs/data-model/entities/*.md`, `docs/api-spec/index.md` + `docs/api-spec/endpoints/*.md` |
| UI spec generation | `.ai-framework/prompts/ui-spec-generation.md` | `docs/stakeholder-definition.md`, `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/api-spec/index.md` + `docs/api-spec/endpoints/*.md` | `docs/ui-specification/` (`index.md` + `screens/*.md` + `components.md`) |
| UI mockup | `.ai-framework/prompts/mockup-generation.md` | `docs/ui-specification/screens/<screen>.md` (target screen) + Design System from `docs/ui-specification/index.md`, `CLAUDE.md` | `mockups/T-XXX-screen-name.html` |
| ADR compilation | `.ai-framework/prompts/compile-adrs.md` | ADR files (from shared ADR repo), `.ai-framework/templates/` | Updated `CLAUDE.md` sections |
| DDR compilation | `.ai-framework/prompts/compile-ddrs.md` | DDR files (from shared DDR repo), `.ai-framework/templates/` | `docs/component-examples.md`, updated `docs/ui-specification/index.md` + `CLAUDE.md` design sections |
| Release transition | `.ai-framework/guides/release-lifecycle.md` | `docs/stakeholder-definition.md`, `CLAUDE.md` | Updated `docs/stakeholder-definition.md` |
| Task implementation plan | `.ai-framework/prompts/plan-generation.md` | `CLAUDE.md`, task definition, files listed in task's "Files to Modify/Create" | `plans/plan-T-XXX-short-title.md` |
| Testing / Integration / Prioritization | No dedicated prompt — use `.ai-framework/prompts/base-template.md` with the context recipe from `.ai-framework/guides/context-compilation.md` | Per the context recipe for that task type | `tasks/adhoc-short-title-tasks.md` |

**Optional context** (read only when relevant to the specific task):

| Task Type | Optional Files | When to Include |
|-----------|---------------|-----------------|
| New feature | `docs/data-model/index.md` + entity shards referenced by the work item, `docs/api-spec/index.md` + endpoint shards referenced by the work item, `docs/ui-specification/index.md` + screen shards referenced by the work item | When the feature touches data, API, or UI respectively — typical for most features |
| New feature | `docs/ARCHITECTURE.md`, `docs/personas/primary-user.md` | Multi-component features, user-facing features |
| Bug fix | `docs/ARCHITECTURE.md`; `docs/data-model/index.md` + entity shards, `docs/api-spec/index.md` + endpoint shards, `docs/ui-specification/index.md` + screen shards referenced by the bug report | Multi-component bugs; data/API/UI bugs respectively |
| Refactoring | `docs/data-model/index.md` + entity shards referenced by the work item, `docs/stakeholder-definition.md` | Data refactors, scope questions |
| Spec generation | `docs/personas/primary-user.md` | User-facing entity/endpoint decisions |
| UI mockup | `docs/api-spec/index.md` + endpoint shards for the screen's API calls, `docs/personas/primary-user.md` | Data-driven screens, content tone |
| Prioritization | `docs/work-items/FEAT-*.md`, `docs/work-items/BUG-*.md`, `docs/work-items/IMP-*.md`, `docs/stakeholder-definition.md`, `docs/personas/` | Comparing and prioritizing work items |

> **Retrieval keys:** When generating tasks for a work item, read each spec's `index.md` plus ONLY the shards named by the work item's impact tables (mapped via the naming rule: entity `TaskLabel` → `docs/data-model/entities/task-label.md`; resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md`; screen "Project Board" → `docs/ui-specification/screens/project-board.md`). Do not read whole spec directories.

**Work Items** (`docs/work-items/`): Feature Briefs, Bug Reports, and Improvement Proposals are the preferred input for task generation. Blank starters ship in the scaffold as `docs/work-items/TEMPLATE-feature-brief.md`, `TEMPLATE-bug-report.md`, and `TEMPLATE-improvement-proposal.md` — copy one to `FEAT-XXX-short-title.md` (next free ID) before filling it in. If no work item document exists for a task, the prompts support inline fallbacks — but structured work items produce higher-quality task breakdowns.

**Claude Code shortcuts**: The scaffold ships slash-command wrappers in `.claude/commands/` (e.g., `/feature-tasks FEAT-001`, `/bugfix-tasks BUG-002`, `/mockup-generation T-012`). Each wrapper reads the matching prompt template and the routing table above, then writes the output file per this table — prefer them over re-explaining the workflow by hand.

### Workflow Enforcement

Each task definition (in the task-list file under `tasks/` — e.g., `tasks/FEAT-XXX-tasks.md`, `tasks/BUG-XXX-tasks.md`, `tasks/IMP-XXX-tasks.md`) includes a **Workflow** field. Before starting any task, check its Workflow value and follow the required steps:

| Workflow | Required Steps Before Implementation |
|----------|--------------------------------------|
| `standard` | 1. Generate an implementation plan using `.ai-framework/prompts/plan-generation.md`. Output: `plans/plan-T-XXX-short-title.md`. 2. Implement following the plan. |
| `mockup-first` | 1. Generate an HTML mockup using `.ai-framework/prompts/mockup-generation.md`. Get stakeholder approval. See `.ai-framework/guides/getting-started.md` Step 7.5. 2. Generate an implementation plan using `.ai-framework/prompts/plan-generation.md`. Output: `plans/plan-T-XXX-short-title.md`. 3. Implement following the plan. |
| `investigation-first` | 1. Complete all investigation steps in the task. Document findings (root cause, affected areas). 2. Generate an implementation plan using `.ai-framework/prompts/plan-generation.md`. Output: `plans/plan-T-XXX-short-title.md`. 3. Implement following the plan. |

**If a task has no Workflow field** (legacy tasks), classify it yourself:
- Type is Frontend + adds/changes a screen → treat as `mockup-first`
- Task requires root cause analysis → treat as `investigation-first`
- Otherwise → treat as `standard`

### Development Pipeline

When implementing tasks from a generated task list (saved in `tasks/` per the routing table above):

0. **Validate the task list** — immediately after task generation (once per task list), run `python .ai-framework/tools/validate-tasks.py tasks/<file>.md` and fix every error before implementation begins. Companion check: `python .ai-framework/tools/validate-specs.py` — the cross-shard spec-consistency linter — catches drift in the spec shards the task list relies on.

**Fresh-context review (recommended for L/XL work):** in a NEW session, run the Task list review row from the routing table above (`.ai-framework/prompts/review-tasks.md` → `tasks/<WORK-ITEM-ID>-review.md`) — the reviewer must have no generation history in context. Address every required change before implementation.

Then follow this sequence for **each task**:

1. **Pick a task** from the task-list file in `tasks/` (respect dependency order).
2. **Check its Workflow field** and complete any prerequisites (see Workflow Enforcement above).
3. **Generate an implementation plan** using `.ai-framework/prompts/plan-generation.md`. Output: `plans/plan-T-XXX-short-title.md`.
4. **Implement** following the steps in the plan.
5. **Verify** the acceptance criteria from the task definition are met.

This sequence applies to every task. The plan file is a developer-facing artifact — it bridges "what to do" (task definition) and "how to do it" (exact code changes).

### Context Assembly Rules

Read files in **Cone of Context** order — broad (strategic) to narrow (tactical):

| Layer | Files | Purpose |
|-------|-------|---------|
| Strategic | `docs/stakeholder-definition.md`, `docs/personas/primary-user.md` | Why? For whom? What's in scope? |
| Architectural | `docs/ARCHITECTURE.md` | What is the system? How is it structured? |
| Specification | `docs/data-model/index.md` + entity shards referenced by the work item; `docs/api-spec/index.md` + endpoint shards referenced by the work item | What are the entities and API contracts? |
| UI | `docs/ui-specification/index.md` + screen shards referenced by the work item (+ `components.md` when shared components are involved) | What do screens look like? What are the components? |
| Work Items | `docs/work-items/FEAT-*.md`, `docs/work-items/BUG-*.md`, `docs/work-items/IMP-*.md` | What specific work to do? Features, bugs, improvements |
| Implementation | `CLAUDE.md` | How do we build things? What are the conventions? |

**Load only what's referenced:** Specs are sharded — read each spec's `index.md` plus only the shards named by the work item's impact tables (e.g., for a task about labels: `docs/data-model/entities/label.md` and `docs/api-spec/endpoints/labels.md`). Do not read whole spec directories. Quality over quantity.

For the full context selection matrix and XML assembly examples, see `.ai-framework/guides/context-compilation.md`.

### Documentation Maintenance Discipline

When code changes happen, check which docs need updating per `.ai-framework/guides/maintenance.md`. Include doc updates in the same PR as the code change.

| Code Change | Document to Update |
|-------------|-------------------|
| New entity or field | `docs/data-model/entities/<entity>.md` (+ `docs/data-model/index.md` if conventions or the relationships overview change) |
| New/changed endpoint or DTO | `docs/api-spec/endpoints/<resource>.md` (+ `docs/api-spec/index.md` if envelope, error catalog, shared DTOs, or the endpoint summary change) |
| New/changed screen or component | `docs/ui-specification/screens/<screen>.md` or `docs/ui-specification/components.md` (+ `docs/ui-specification/index.md` if Design System or screen inventory change) |
| New component or service | `docs/ARCHITECTURE.md` |
| New pattern or convention | `CLAUDE.md` |
| Scope or strategy change | `docs/stakeholder-definition.md` |
| Design token or screen layout change | `mockups/` (affected screens) |
| DDR updated in shared repo | Re-run DDR compilation, update Component Examples + `docs/ui-specification/index.md` + CLAUDE.md Design Patterns |
| Feature tasks completed | `docs/work-items/FEAT-*.md` — update Status to "Completed" |
| Bug resolved | `docs/work-items/BUG-*.md` — update Status to "Resolved" |
| Improvement completed | `docs/work-items/IMP-*.md` — update Status to "Completed" |

**Changelog rule:** Every update under `docs/data-model/`, `docs/api-spec/`, or `docs/ui-specification/` (shard edits included), and every update to `docs/ARCHITECTURE.md`, must include a changelog entry at the bottom of that spec's `index.md` (or of `ARCHITECTURE.md`) — and an updated "Last verified against code" stamp on every file touched. See `.ai-framework/guides/maintenance.md` for format.

### Framework Reference

For deeper reading on the full workflow and rules:

- `.ai-framework/guides/getting-started.md` — full workflow from docs to task generation
- `.ai-framework/guides/context-compilation.md` — context assembly details and task-type matrix
- `.ai-framework/guides/maintenance.md` — doc update triggers and review checklists
