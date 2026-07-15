# .ai-framework — Bundled Framework Reference

This folder contains a local copy of the **AI Task Generation Documentation Framework** so that everything you need — templates, prompts, and guides — lives inside your project.

> **Don't edit this folder locally.** Its `templates/`, `prompts/`, `guides/`, and `tools/` are regenerated from the framework repo (via `scripts/sync-scaffold.sh`) — local edits will be lost on the next upgrade. Edit your project docs instead (`CLAUDE.md`, `docs/`). Only this README and `VERSION` are maintained by hand, in the framework repo.

## What's Inside

```
.ai-framework/
├── VERSION                    # Framework version, semver (for upgrade tracking)
├── README.md                  # This file
├── templates/                 # Full reference templates (detailed guidance)
│   ├── persona.md
│   ├── stakeholder.md
│   ├── architecture.md
│   ├── claude-md.md
│   ├── data-model.md
│   ├── api-spec.md
│   ├── ui-specification.md
│   ├── feature-brief.md
│   ├── bug-report.md
│   ├── improvement-proposal.md
│   └── examples/              # Filled work-item examples (reference only — copy the blanks, not these)
├── prompts/                   # Prompt templates for AI task generation
│   ├── base-template.md
│   ├── feature-tasks.md
│   ├── bugfix-tasks.md
│   ├── refactor-tasks.md
│   ├── review-tasks.md            # Fresh-session task-list review before implementation
│   ├── spec-generation.md
│   ├── ui-spec-generation.md
│   ├── mockup-generation.md
│   ├── plan-generation.md
│   ├── compile-adrs.md
│   └── compile-ddrs.md
├── tools/                     # Shipped tools
│   ├── validate-specs.py      # Cross-shard spec consistency + freshness linter — run after generating or editing specs
│   └── validate-tasks.py      # Task-list validator — run it after generating any task list and fix every error
└── guides/                    # Workflow guides
    ├── getting-started.md
    ├── context-compilation.md
    ├── maintenance.md
    └── release-lifecycle.md
```

## Getting Started with the Scaffold

The scaffold this folder ships in gives your project a fill-in-ready documentation structure.

### Option A: New Project

1. Copy the entire scaffold contents into your project root (see the framework repo README for the copy command)
2. Follow [`guides/getting-started.md`](guides/getting-started.md) — start with the **New Project** path
3. Fill system templates in order: Persona → Stakeholder → CLAUDE.md → Architecture → Data Model → API Spec → UI Spec
4. Write work items in `docs/work-items/` as needed — copy a `TEMPLATE-*` starter to `FEAT-XXX-short-title.md` (next free ID) before filling

### Option B: Existing Codebase

1. Copy the entire scaffold contents into your project root
2. Follow [`guides/getting-started.md`](guides/getting-started.md) — start with the **Existing Codebase** path
3. Fill system templates in order: CLAUDE.md → Stakeholder → Architecture → Data Model → API Spec → UI Spec → Persona
4. Write work items in `docs/work-items/` as needed

### What You Get

```
your-project/
├── CLAUDE.md                          # Code conventions & project context (with AI framework routing)
├── .claude/
│   └── commands/                      # Claude Code slash commands (/feature-tasks, /bugfix-tasks,
│                                      #   /mockup-generation, /plan-generation, ...)
├── .ai-framework/                     # This folder — bundled framework reference (don't edit)
│   ├── VERSION                        # Framework version for upgrade tracking
│   ├── README.md                      # What this folder is and how to use it
│   ├── templates/                     # Full reference templates
│   ├── prompts/                       # Prompt templates for AI task generation
│   ├── tools/
│   │   ├── validate-specs.py          # Cross-shard spec consistency + freshness linter
│   │   └── validate-tasks.py          # Task-list validator — run after generating any task list
│   └── guides/                        # Workflow guides
├── docs/
│   ├── personas/
│   │   └── primary-user.md            # Target user definition
│   ├── stakeholder-definition.md      # Product vision, scope & success criteria
│   ├── ARCHITECTURE.md                # System structure & technical decisions
│   ├── data-model/                    # Domain entities & relationships (sharded)
│   │   ├── index.md                   #   Cross-cutting: decisions, conventions, relationships, shared enums
│   │   └── entities/                  #   ONE entity per file (starter: TEMPLATE-entity.md)
│   ├── api-spec/                      # REST API contracts (sharded)
│   │   ├── index.md                   #   Cross-cutting: envelope, error catalog, auth, pagination
│   │   └── endpoints/                 #   ONE resource group per file (starter: TEMPLATE-resource.md)
│   ├── ui-specification/              # Screens & design system (sharded)
│   │   ├── index.md                   #   Cross-cutting: UI decisions, Design System, screen inventory, layouts
│   │   ├── screens/                   #   ONE screen per file (starter: TEMPLATE-screen.md)
│   │   └── components.md              #   Shared components inventory
│   ├── rationale/                     # Narrative & decision rationale — linked from contract docs, never loaded as AI context
│   └── work-items/                    # Work item documents
│       ├── TEMPLATE-feature-brief.md          # Blank Feature Brief starter
│       ├── TEMPLATE-bug-report.md             # Blank Bug Report starter
│       └── TEMPLATE-improvement-proposal.md   # Blank Improvement Proposal starter
├── tasks/                             # Generated task lists (tasks/FEAT-XXX-tasks.md, ...)
├── plans/                             # Implementation plans (plans/plan-T-XXX-short-title.md)
└── mockups/                           # HTML mockups (mockups/T-XXX-screen-name.html)
```

## Template ↔ Project Doc Mapping

| Template (`.ai-framework/templates/`) | Your project doc |
|---------------------------------------|------------------|
| `persona.md` | `docs/personas/primary-user.md` |
| `stakeholder.md` | `docs/stakeholder-definition.md` |
| `claude-md.md` | `CLAUDE.md` (project root) |
| `architecture.md` | `docs/ARCHITECTURE.md` |
| `data-model.md` | `docs/data-model/` (`index.md` + `entities/*.md`, starter shard: `TEMPLATE-entity.md`) |
| `api-spec.md` | `docs/api-spec/` (`index.md` + `endpoints/*.md`, starter shard: `TEMPLATE-resource.md`) |
| `ui-specification.md` | `docs/ui-specification/` (`index.md` + `screens/*.md` + `components.md`, starter shard: `TEMPLATE-screen.md`) |
| `feature-brief.md` | `docs/work-items/FEAT-XXX-short-title.md` (starter: `TEMPLATE-feature-brief.md`) |
| `bug-report.md` | `docs/work-items/BUG-XXX-short-title.md` (starter: `TEMPLATE-bug-report.md`) |
| `improvement-proposal.md` | `docs/work-items/IMP-XXX-short-title.md` (starter: `TEMPLATE-improvement-proposal.md`) |

## Scaffold vs Full Templates

| | Scaffold docs (`CLAUDE.md`, `docs/`) | Full Templates (`.ai-framework/templates/`) |
|---|---|---|
| **Purpose** | Quick start — fill in the essentials | Reference — comprehensive coverage |
| **Time to fill** | 15-30 min per file | 1-2 hours per file |
| **Detail level** | Section headers + fill prompts | Full guidance, examples, edge cases |
| **When to use** | Starting a project | Deepening documentation later |

## How to Use This Folder

- **Use templates as reference** when filling in your project docs — they contain detailed guidance and examples for every section.
- **Use prompts** to generate AI tasks from your documentation:
  - **AI agents (Claude Code, etc.):** Read the routing table in CLAUDE.md — it lists which files to read, which prompt template to use, and which output file to write for each task type. The scaffold also ships slash-command wrappers in `.claude/commands/` (e.g., `/feature-tasks FEAT-001`).
  - **Chat workflows:** Copy the prompt structure from `prompts/`, paste in your project docs as context.
- **Use ADR compilation** to pre-fill templates from a shared Architecture Decision Records repo — select ADRs for your tech stack, run `prompts/compile-adrs.md`, and paste the output into your project docs.
- **Use DDR compilation** to pre-fill the Design System from a shared Design Decision Records repo — select a profile or individual DDRs, run `prompts/compile-ddrs.md`, and paste the output into your UI spec and CLAUDE.md.
- **Use guides** for workflow help — getting started, assembling context, and maintaining docs.

## Tips

- **Don't overthink it.** A rough first pass beats a perfect blank page. You can always refine later.
- **Use the full templates as reference.** If a scaffold section feels unclear, check the corresponding file in `.ai-framework/templates/` (see the mapping table above) for detailed guidance.
- **CLAUDE.md is the most frequently used.** Even a minimal version helps AI generate better code immediately.
- **Generate specs from docs.** After filling Stakeholder + Architecture + CLAUDE.md, use `.ai-framework/prompts/spec-generation.md` (or `/spec-generation`) to generate `docs/data-model/` and `docs/api-spec/` (index + shards), then `.ai-framework/prompts/ui-spec-generation.md` (or `/ui-spec-generation`) for `docs/ui-specification/` (index + screens + components).
- **Keep freshness stamps current.** Every spec `index.md` and shard (and `docs/ARCHITECTURE.md`) carries a `> **Last verified against code:** YYYY-MM-DD (commit ...)` line directly under its H1 — update it whenever you edit a file or verify it against the code. AI agents trust code over any shard whose stamp is missing or older than 30 days.
- **Validate task lists.** After any task generation, run `python .ai-framework/tools/validate-tasks.py tasks/<file>.md` (add `--work-item docs/work-items/<file>.md` for features) and fix every error.
- **Review task lists in a fresh session.** Before implementation (recommended for L/XL work), run `prompts/review-tasks.md` (or `/review-tasks FEAT-001`) in a NEW session with no generation history — it writes `tasks/<WORK-ITEM-ID>-review.md`.
- **Update as you go.** These are living documents. Revisit them as your project evolves (see [`guides/maintenance.md`](guides/maintenance.md)).
- **Upgrading the framework.** `VERSION` holds the installed semver (e.g., `2.1.0`). To upgrade, replace the `.ai-framework/` folder with the latest `scaffold/.ai-framework/` from the framework repo — your project docs are unaffected.

## Upgrading

The `VERSION` file tracks which framework version is installed (semver, e.g., `2.1.0`). To upgrade:

1. Check the framework repo's `CHANGELOG.md` for the latest version and what changed
2. Replace this `.ai-framework/` folder with the updated `scaffold/.ai-framework/` (regenerated there by `scripts/sync-scaffold.sh`)
3. Your project docs (`CLAUDE.md`, `docs/`) are unaffected — only the reference material updates
