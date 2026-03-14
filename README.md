# AI Task Generation Documentation Framework (v2)

A comprehensive documentation framework that captures the essential context to enable AI-assisted task generation for software projects.

## Overview

This is the **v2** version of the framework, expanding on v1's 4 foundational templates to include **7 core templates** that provide complete coverage from strategic planning through UI implementation. The framework also includes 9 prompt templates for different task types and 4 workflow guides.

### Why 7 Templates?

The framework defines 7 templates across 5 layers. Together they answer every question an AI needs to generate useful, actionable tasks:

- **Persona** - WHO are we building for? (Strategic)
- **Stakeholder Definition** - WHAT/WHY are we building? (Strategic)
- **Architecture** - HOW is the system structured? (Architectural)
- **Data Model** - WHAT are the entities and relationships? (Specification)
- **API Specification** - WHAT are the API contracts? (Specification)
- **UI Specification** - WHAT do screens look like? (UI)
- **CLAUDE.md** - HOW should code be written? (Implementation)

### The "Cone of Context"

```
Layer 1: Strategic (WHO/WHY)
    |-- personas/               Who are we building for?
    |-- stakeholder.md          Why are we building this? What's in scope?
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
Layer 5: Implementation (HOW)
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

CLAUDE.md (independent — cross-cuts all layers)
```

Recommended order: Persona → Stakeholder → Architecture → CLAUDE.md → Data Model → API Spec → UI Spec.

---

## Quick Start

**Fastest path:** Copy the scaffold, fill in the templates, start generating tasks. The scaffold includes a bundled `.ai-framework/` folder with all templates, prompts, and guides — everything is self-contained.

```bash
# Copy the scaffold into your project (includes .ai-framework/ reference)
cp -r path/to/ai-task-framework-v2/scaffold/* path/to/ai-task-framework-v2/scaffold/.ai-framework your-project/
```

Then follow the **[Getting Started Guide](guides/getting-started.md)** for a step-by-step walkthrough.

### The Short Version

1. **Copy scaffold** — Get the fill-in-ready template structure (`scaffold/`)
2. **Fill templates** — Answer the guided questions in each file (~1-2 hours)
3. **Generate specs** — Use spec-generation prompts to derive Data Model, API Spec, and UI Spec
4. **Generate tasks** — Use prompt templates from `prompts/` with your documentation as context
5. **Maintain** — Keep docs updated as your project evolves

**Two paths depending on where you are:**

| Path | Start with | Guide section |
|------|-----------|---------------|
| **New project** (idea, no code) | Persona → Stakeholder → CLAUDE.md → Architecture → Data Model → API Spec → UI Spec | [Phase 2](guides/getting-started.md#phase-2-fill-templates-new-project-path) |
| **Existing codebase** | CLAUDE.md → Stakeholder → Architecture → Data Model → API Spec → UI Spec → Persona | [Phase 2-alt](guides/getting-started.md#phase-2-alt-fill-templates-existing-codebase-path) |

---

## Directory Contents

```
ai-task-framework-v2/
├── README.md                    # This file
├── scaffold/                    # Ready-to-copy project structure
│   ├── README.md               # Scaffold usage instructions
│   ├── CLAUDE.md               # Fill-in-ready code conventions (with AI framework section)
│   ├── .ai-framework/          # Bundled framework reference
│   │   ├── VERSION             # Framework version (v2)
│   │   ├── README.md           # What this folder is
│   │   ├── templates/          # Full reference templates (copied)
│   │   ├── prompts/            # Prompt templates (copied)
│   │   └── guides/             # Workflow guides (copied)
│   └── docs/
│       ├── personas/
│       │   └── primary-user.md # Fill-in-ready persona
│       ├── stakeholder-definition.md  # Fill-in-ready stakeholder def
│       ├── ARCHITECTURE.md     # Fill-in-ready architecture doc
│       ├── data-model.md       # Fill-in-ready data model
│       ├── api-spec.md         # Fill-in-ready API specification
│       └── ui-specification.md # Fill-in-ready UI specification
├── templates/                   # Full reference templates (7 core)
│   ├── persona.md              # Target user definition
│   ├── stakeholder.md          # Product philosophy & scope
│   ├── architecture.md         # System architecture
│   ├── claude-md.md            # Code conventions (CLAUDE.md)
│   ├── data-model.md           # Domain entity definitions
│   ├── api-spec.md             # REST API endpoint contracts
│   └── ui-specification.md     # Screen layouts & component specs
├── prompts/                     # Claude-optimized prompt templates
│   ├── base-template.md        # Common prompt structure
│   ├── feature-tasks.md        # Generate feature tasks
│   ├── bugfix-tasks.md         # Generate bugfix tasks
│   ├── refactor-tasks.md       # Generate refactoring tasks
│   ├── spec-generation.md      # Generate Data Model or API Spec
│   ├── ui-spec-generation.md   # Generate UI Specification
│   ├── mockup-generation.md    # Generate HTML mockup prototypes
│   ├── plan-generation.md      # Generate implementation plans for tasks
│   ├── compile-adrs.md         # Compile ADRs into template sections
│   └── compile-ddrs.md         # Compile DDRs into design system sections
└── guides/
    ├── getting-started.md      # Full workflow: idea → AI tasks
    ├── context-compilation.md  # How to assemble context for AI
    ├── maintenance.md          # Keeping docs in sync with code
    └── release-lifecycle.md    # Versioned vs continuous development
```

## Context Compilation by Task Type

With 7 templates, context selection is based on task type:

| Task Type | Required Context | Optional Context |
|-----------|-----------------|------------------|
| New Feature | Stakeholder + CLAUDE.md | Data Model, API Spec, UI Spec, Persona, Architecture |
| Bug Fix | CLAUDE.md | Architecture, Data Model, API Spec, UI Spec |
| Refactoring | CLAUDE.md + Architecture | Data Model, Stakeholder |
| Testing | CLAUDE.md | Architecture, API Spec, UI Spec |
| Integration | Architecture + CLAUDE.md + Data Model + API Spec | Stakeholder |
| Prioritization | Stakeholder + Persona | Architecture |
| UI Mockup | UI Spec + CLAUDE.md | API Spec, Persona, Component Examples |
| DDR Compilation | DDR files (+ optional profile) | `.ai-framework/templates/` |

**Key insight:** CLAUDE.md appears in every task type except prioritization. For features, Data Model + API Spec + UI Spec provide the specification-level context that v1 lacked.

See `guides/context-compilation.md` for detailed instructions.

---

## What's New in v2

### New Templates (3)

| Template | Purpose |
|----------|---------|
| **Data Model** (`data-model.md`) | Entity definitions, fields, relationships, module ownership, database conventions |
| **API Specification** (`api-spec.md`) | REST endpoint contracts, DTOs, auth requirements, pagination, error handling |
| **UI Specification** (`ui-specification.md`) | Screen layouts, component hierarchy, design tokens, interaction patterns, states |

### New Prompts (5)

| Prompt | Purpose |
|--------|---------|
| **Spec Generation** (`spec-generation.md`) | Generate Data Model or API Spec from strategic docs |
| **UI Spec Generation** (`ui-spec-generation.md`) | Generate UI Specification from strategic + spec docs |
| **Mockup Generation** (`mockup-generation.md`) | Generate HTML mockup prototypes for stakeholder approval |
| **Plan Generation** (`plan-generation.md`) | Generate implementation plans for individual tasks |
| **ADR Compilation** (`compile-adrs.md`) | Compile Architecture Decision Records into pre-filled template sections |
| **DDR Compilation** (`compile-ddrs.md`) | Compile Design Decision Records into pre-filled design system sections |

### New Guide (1)

| Guide | Purpose |
|-------|---------|
| **Release Lifecycle** (`release-lifecycle.md`) | Versioned vs continuous development models, feature lifecycle, transition process |

### Updated Files

- All existing templates, prompts, and guides updated to reference 7 templates, 5-layer cone of context
- CLAUDE.md template now includes AI-Assisted Development Framework section with routing table
- Stakeholder template includes continuous development model note
- All prompts include dual "AI agents" vs "Chat workflows" usage instructions

---

## Best Practices

### Document Quality

- **Be specific**: Vague documentation produces vague tasks
- **Include examples**: Real examples anchor abstract concepts
- **Stay current**: Outdated docs mislead AI and waste effort
- **Link related docs**: Cross-reference helps AI understand connections

### Context Selection

- **Start narrow**: Only include what's directly relevant
- **Add breadth for ambiguity**: When requirements are unclear, add context layers
- **Prioritize recent changes**: Recent code/docs may not be in AI training data
- **Use spec documents for implementation**: Data Model + API Spec + UI Spec give AI the detail it needs

### Prompt Engineering

- **Use XML tags**: Structure context with clear sections (for chat workflows)
- **Specify output format**: Tell the AI exactly what format you want
- **Include constraints**: State what should NOT be done
- **Provide success criteria**: Define what "done" looks like

### Spec Generation Workflow

- **Generate in order**: Data Model → API Spec → UI Spec (each builds on the previous)
- **Review before next step**: Validate each spec before using it as context for the next
- **Keep specs in sync**: Update specs when code changes (see maintenance guide)
