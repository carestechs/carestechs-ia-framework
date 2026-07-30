# AI Task Generation Documentation Framework

A comprehensive documentation framework that captures the essential context to enable AI-assisted task generation for software projects.

Current version: see [`CHANGELOG.md`](CHANGELOG.md) and `scaffold/.ai-framework/VERSION`.

## Overview

The framework provides **10 core templates** that cover a project from strategic planning through work item definition, **10 prompt templates** for different task types, and **4 workflow guides**.

**Applicability:** the framework assumes a web application with a REST API as its default shape (that's what the Data Model, API Spec, and UI Spec layers describe). For CLI tools, libraries, or headless services, skip or substitute the API/UI layers — the strategic, architectural, and implementation layers apply to any project.

### Why 10 Templates?

The framework defines 10 templates across 6 layers. Together they answer every question an AI needs to generate useful, actionable tasks:

**System Templates (7)** — describe the product and how it's built:
- **Persona** - WHO are we building for? (Strategic)
- **Stakeholder Definition** - WHAT/WHY are we building? (Strategic)
- **Architecture** - HOW is the system structured? (Architectural)
- **Data Model** - WHAT are the entities and relationships? (Specification)
- **API Specification** - WHAT are the API contracts? (Specification)
- **UI Specification** - WHAT do screens look like? (UI)
- **CLAUDE.md** - HOW should code be written? (Implementation)

**Work Item Templates (3)** — describe what specific work to do:
- **Feature Brief** - WHAT feature to build? (Work Items)
- **Bug Report** - WHAT bug to fix? (Work Items)
- **Improvement Proposal** - WHAT to improve? (Work Items)

### The "Cone of Context"

```
Layer 1: Strategic (WHO/WHY)
    |-- personas/               Who are we building for?
    |-- stakeholder-definition.md  Why are we building this? What's in scope?
    v
Layer 2: Architectural (WHAT)
    |-- ARCHITECTURE.md         How is the system structured?
    v
Layer 3: Specification (ENTITIES/CONTRACTS)
    |-- data-model.md           What are the entities, fields, relationships?
    |-- api-spec.md             What are the API endpoints and DTOs?
    v
Layer 4: UI (SCREENS)
    |-- ui-specification.md     What do screens look like? Components? States?
    v
Layer 5: Work Items (WHAT TO DO)
    |-- work-items/FEAT-*.md    What features to build?
    |-- work-items/BUG-*.md     What bugs to fix?
    |-- work-items/IMP-*.md     What improvements to make?
    v
Layer 6: Implementation (HOW)
    |-- CLAUDE.md               How should code be written? What conventions?
```

### Dependency Graph

```
Persona ──────→ Stakeholder
                    ↓
              Architecture
                    ↓
         Data Model + API Spec
                    ↓
            UI Specification
                    ↓
    Feature Brief / Bug Report / Improvement Proposal
                    ↓
         Task Generation (via prompts/)

CLAUDE.md (independent — cross-cuts all layers)
```

Recommended order: Persona → Stakeholder → CLAUDE.md → Architecture → Data Model → API Spec → UI Spec → Work Items.

---

## Quick Start

**Fastest path:** Copy the scaffold, fill in the templates, start generating tasks. The scaffold includes a bundled `.ai-framework/` folder with all templates, prompts, and guides, plus ready-made Claude Code slash commands — everything is self-contained.

```bash
# From your project root (the /. suffix also copies dotfolders like .ai-framework/ and .claude/)
cp -r path/to/carestechs-ia-framework/scaffold/. .
```

> **Caution:** if your project already has a `CLAUDE.md`, the copy will overwrite it — merge the scaffold's CLAUDE.md into yours manually instead.

Then follow the **[Getting Started Guide](guides/getting-started.md)** for a step-by-step walkthrough.

### The Short Version

1. **Copy scaffold** — Get the fill-in-ready template structure (`scaffold/`)
2. **Fill system templates** — Answer the guided questions in each file
3. **Generate specs** — Use spec-generation prompts to derive Data Model, API Spec, and UI Spec
4. **Write work items** — Copy a `TEMPLATE-*` starter in `docs/work-items/` to `FEAT-XXX-short-title.md` and fill it
5. **Generate tasks** — Use prompt templates from `prompts/` (or the `/feature-tasks` etc. slash commands in Claude Code); task lists are saved to `tasks/`
6. **Plan & implement** — Generate per-task implementation plans into `plans/`, then implement
7. **Maintain** — Keep docs updated as your project evolves

**Two paths depending on where you are:**

| Path | Start with | Guide section |
|------|-----------|---------------|
| **New project** (idea, no code) | Persona → Stakeholder → CLAUDE.md → Architecture → Data Model → API Spec → UI Spec | [Phase 2](guides/getting-started.md#phase-2-fill-templates-new-project-path) |
| **Existing codebase** | CLAUDE.md → Stakeholder → Architecture → Data Model → API Spec → UI Spec → Persona | [Phase 2-alt](guides/getting-started.md#phase-2-alt-fill-templates-existing-codebase-path) |

---

## Directory Contents

```
carestechs-ia-framework/
├── README.md                    # This file
├── CHANGELOG.md                 # Framework version history
├── scripts/
│   └── sync-scaffold.sh         # Regenerates scaffold/.ai-framework/ from root sources
├── scaffold/                    # Ready-to-copy project structure
│   ├── CLAUDE.md                # Fill-in-ready code conventions (with AI framework routing)
│   ├── .claude/
│   │   └── commands/            # Claude Code slash commands (/feature-tasks, /plan-generation, ...)
│   ├── .ai-framework/           # Bundled framework reference (GENERATED — edit root copies instead)
│   │   ├── VERSION              # Framework version for upgrade tracking
│   │   ├── README.md            # Scaffold usage guide + template↔doc mapping
│   │   ├── templates/           # Full reference templates (synced copy)
│   │   ├── prompts/             # Prompt templates (synced copy)
│   │   └── guides/              # Workflow guides (synced copy)
│   ├── docs/
│   │   ├── personas/
│   │   │   └── primary-user.md  # Fill-in-ready persona
│   │   ├── stakeholder-definition.md
│   │   ├── ARCHITECTURE.md
│   │   ├── data-model/          # index.md (conventions) + entities/<entity>.md shards
│   │   ├── api-spec/            # index.md (envelope, errors) + endpoints/<resource>.md shards
│   │   ├── ui-specification/    # index.md (design system) + screens/<screen>.md + components.md
│   │   ├── rationale/           # Narrative & history — never loaded as AI context
│   │   └── work-items/          # Copy a TEMPLATE-* file to FEAT-XXX-title.md and fill it
│   │       ├── TEMPLATE-feature-brief.md
│   │       ├── TEMPLATE-bug-report.md
│   │       └── TEMPLATE-improvement-proposal.md
│   ├── tasks/                   # Generated task lists (tasks/FEAT-XXX-tasks.md)
│   ├── plans/                   # Implementation plans (plans/plan-T-XXX-short-title.md)
│   └── mockups/                 # HTML mockups (mockups/T-XXX-screen-name.html)
├── templates/                   # SOURCE OF TRUTH — 10 core templates
│   ├── persona.md               # → docs/personas/primary-user.md
│   ├── stakeholder-definition.md # → docs/stakeholder-definition.md (1:1)
│   ├── architecture.md          # → docs/ARCHITECTURE.md
│   ├── claude-md.md             # → CLAUDE.md (project root)
│   ├── data-model.md            # → docs/data-model/ (index + entities/*.md)
│   ├── api-spec.md              # → docs/api-spec/ (index + endpoints/*.md)
│   ├── ui-specification.md      # → docs/ui-specification/ (index + screens/*.md + components.md)
│   ├── feature-brief.md         # → docs/work-items/FEAT-XXX-*.md
│   ├── bug-report.md            # → docs/work-items/BUG-XXX-*.md
│   ├── improvement-proposal.md  # → docs/work-items/IMP-XXX-*.md
│   └── examples/                # Genuinely filled work-item examples ("TaskFlow" sample product)
├── tools/                       # Shipped tooling (synced into scaffold/.ai-framework/tools/)
│   ├── validate-tasks.py        # Task-list schema/DAG/coverage validator (machine gate)
│   ├── validate-specs.py        # Cross-shard consistency + freshness linter
│   └── metrics-report.py        # Framework-effectiveness scorecard (see guides/evaluation.md)
├── evals/                       # Prompt regression evals (framework-repo only, not shipped)
│   ├── run-evals.py             # Deterministic assertion runner
│   └── cases/                   # Golden fixture projects + assertions per prompt
├── prompts/                     # Claude-optimized prompt templates (agent-first, chat appendix)
│   ├── base-template.md         # Canonical task schema + common prompt structure
│   ├── feature-tasks.md         # Generate feature tasks   → tasks/FEAT-XXX-tasks.md
│   ├── bugfix-tasks.md          # Generate bugfix tasks    → tasks/BUG-XXX-tasks.md
│   ├── refactor-tasks.md        # Generate refactor tasks  → tasks/IMP-XXX-tasks.md
│   ├── spec-generation.md       # Generate Data Model or API Spec
│   ├── ui-spec-generation.md    # Generate UI Specification
│   ├── mockup-generation.md     # Generate HTML mockup prototypes
│   ├── plan-generation.md       # Generate implementation plans → plans/plan-T-XXX-*.md
│   ├── compile-adrs.md          # Compile ADRs into template sections
│   └── compile-ddrs.md          # Compile DDRs into design system sections
└── guides/
    ├── getting-started.md       # Full workflow: idea → AI tasks
    ├── context-compilation.md   # CANONICAL context-selection matrix + assembly instructions
    ├── maintenance.md           # Keeping docs in sync with code
    ├── release-lifecycle.md     # Versioned vs continuous development
    ├── evaluation.md            # Measuring framework effectiveness (4 levels, event schema)
    └── orchestrator-integration.md  # Per-step contract for driving the pipeline externally
```

### Editing the framework

Root `templates/`, `prompts/`, and `guides/` are the single source of truth. `scaffold/.ai-framework/` is a generated copy — after editing root files, run:

```bash
scripts/sync-scaffold.sh          # regenerate the scaffold copy
scripts/sync-scaffold.sh --check  # verify no drift (use in CI / pre-commit)
```

`scaffold/.ai-framework/README.md` and `VERSION` are maintained by hand and are not overwritten by the sync.

**Scaffold parity rule** (when editing a template or its scaffold counterpart): scaffold docs match their template **heading-for-heading at every `##` level**, numbered identically. Subsections (`###`+) may be *condensed* — merged into a list or table — only when their content is fully preserved in condensed form; a template subsection whose content has no scaffold counterpart is drift and must be added. When in doubt, run the heading diff: template headings absent from the scaffold need either a heading or a documented condensation.

---

## Context Compilation by Task Type

The **canonical context-selection matrix** lives in [`guides/context-compilation.md`](guides/context-compilation.md) (for agents: the routing table in the project's `CLAUDE.md`). Quick teaser for the three work-item flows:

| Task Type | Required Context | Typical Additions |
|-----------|-----------------|-------------------|
| New Feature | Feature Brief + Stakeholder + CLAUDE.md | Data Model, API Spec, UI Spec (when the feature touches data/API/UI), Architecture, Persona |
| Bug Fix | Bug Report + CLAUDE.md | Architecture, Data Model, API Spec, UI Spec (per bug type) |
| Refactoring | Improvement Proposal + CLAUDE.md + Architecture | Data Model, Stakeholder |

Testing, Integration, and Prioritization have context recipes in the guide but no dedicated prompt — use `prompts/base-template.md` with the recipe.

**Key insight:** Work Item documents (Feature Brief, Bug Report, Improvement Proposal) are the primary input for task generation — they describe *what* to do. System templates describe *the system* and *how* to build. CLAUDE.md appears in every task-generation flow.

---

## Best Practices

### Document Quality

- **Be specific**: Vague documentation produces vague tasks
- **Include examples**: Real examples anchor abstract concepts (see `templates/examples/` for filled work items)
- **Stay current**: Outdated docs mislead AI and waste effort
- **Link related docs**: Cross-reference helps AI understand connections

### Context Selection

- **Start narrow**: Only include what's directly relevant
- **Use retrieval keys**: A work item's impact tables name the exact entity/endpoint/screen shards to load — read each spec's `index.md` plus only those shards, never whole spec directories
- **Add breadth for ambiguity**: When requirements are unclear, add context layers
- **Prioritize recent changes**: Recent code/docs may not be in AI training data
- **Keep contract and rationale separate**: Spec docs stay contract-style (tables, schemas, rules); narrative lives in `docs/rationale/` and is never loaded as AI context
- **Trust code over stale docs**: Every spec shard carries a "Last verified against code" stamp — verify shards older than 30 days against the source before relying on them

### Prompt Engineering

- **Use XML tags**: Structure context with clear sections (for chat workflows)
- **Specify output format**: Tell the AI exactly what format you want
- **Include constraints**: State what should NOT be done
- **Provide success criteria**: Define what "done" looks like

### Spec Generation Workflow

- **Generate in order**: Data Model → API Spec → UI Spec (each builds on the previous)
- **Review before next step**: Validate each spec before using it as context for the next
- **Keep specs in sync**: Update specs when code changes (see maintenance guide)

---

## Version History

See [`CHANGELOG.md`](CHANGELOG.md). Highlights of the v2 line: 10 core templates across 6 layers (v1 had 4), work-item templates and prompts with dual agent/chat usage, ADR/DDR compilation, release lifecycle guide. v2.1 adds defined output locations (`tasks/`, `plans/`, `mockups/`), a canonical task schema, Claude Code slash commands in the scaffold, stack-neutral prompts, and the scaffold sync script. v2.2 shards the spec docs for retrieval-key context loading, splits contract from rationale, adds freshness stamps, and ships the `validate-tasks.py` output gate. v2.3 adds the verification harnesses: shard frontmatter, the `validate-specs.py` cross-shard linter, the fresh-context task-list review prompt, and the `evals/` golden-set regression harness.
