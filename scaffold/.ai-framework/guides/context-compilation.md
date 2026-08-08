# Context Compilation Guide

> **Purpose**: This guide explains how to assemble the right documentation context for AI task generation using the 10 core templates: 7 system templates (Persona, Stakeholder Definition, Architecture, CLAUDE.md, Data Model, API Specification, UI Specification) and 3 work item templates (Feature Brief, Bug Report, Improvement Proposal).
>
> **Canonical source**: The per-task-type tables in this guide are the canonical context-selection matrix for humans. AI agents use the routing table in the project's CLAUDE.md, which mirrors these recipes. Other documents (README, getting-started) carry only teasers that link here.

---

## The "Cone of Context" Principle

Context should be provided in layers, from broad (strategic) to narrow (tactical). The AI needs just enough context to understand the "why" and "how" without being overwhelmed.

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGIC CONTEXT                            │
│  Stakeholder Definition, Persona                                │
│  "Why? For whom? What's in scope?"                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ARCHITECTURAL CONTEXT                          │
│  ARCHITECTURE.md                                                │
│  "What is the system? How is it structured?"                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SPECIFICATION CONTEXT                         │
│  Data Model, API Specification                                  │
│  "What are the entities? What are the API contracts?"           │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UI CONTEXT                                 │
│  UI Specification                                               │
│  "What do screens look like? What are the components?"          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WORK ITEMS CONTEXT                            │
│  Feature Brief, Bug Report, Improvement Proposal                │
│  "What specific work to do? What features/bugs/improvements?"   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 IMPLEMENTATION CONTEXT                          │
│  CLAUDE.md                                                      │
│  "How do we build things? What are the conventions?"            │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: Start narrow and add breadth only when needed. Too much context dilutes focus; too little causes misalignment.

---

## Context Selection by Task Type

### Retrieval Keys: How Spec Context Gets Selected

The three spec documents are sharded directories, not single files: `docs/data-model/` (`index.md` + `entities/`), `docs/api-spec/` (`index.md` + `endpoints/`), and `docs/ui-specification/` (`index.md` + `screens/` + `components.md`). Each `index.md` holds only cross-cutting content (conventions, decisions, shared definitions); every entity, resource, and screen lives in its own shard.

The work item's impact tables (Entities / API / UI) are **retrieval keys**: the names they list map mechanically (kebab-case) to shard paths —

- Entity `TaskLabel` → `docs/data-model/entities/task-label.md` (singular)
- Resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md` (matches the route segment, plural)
- Screen "Project Board" → `docs/ui-specification/screens/project-board.md`

**The rule:** wherever a table below (or the CLAUDE.md routing table) lists Data Model, API Specification, or UI Specification, read that spec's `index.md` plus ONLY the shards named by the work item's impact tables — never whole spec directories.

**Never include `docs/rationale/`:** narrative, history, and decision background live in `docs/rationale/<topic>.md`, linked from contract docs as `Why: see docs/rationale/<topic>.md`. Rationale files are never loaded as context — no recipe or routing-table row lists them.

---

### 1. New Feature Implementation

**Goal**: Generate tasks that implement a feature aligned with product vision.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Feature Brief | Always (preferred) | Full `docs/work-items/FEAT-*.md` — scope, ACs, impact |
| Required | Stakeholder Definition | Always | Philosophy, principles, scope lock |
| Required | CLAUDE.md | Always | Full document |
| Recommended | Data Model | Features involving entities | `docs/data-model/index.md` + entity shards named by the impact table (`entities/<entity>.md`) |
| Recommended | API Specification | Features with API endpoints | `docs/api-spec/index.md` + endpoint shards for the resources named by the impact table (`endpoints/<resource>.md`) |
| Recommended | UI Specification | User-facing features | `docs/ui-specification/index.md` + screen shards named by the impact table (`screens/<screen>.md`); add `components.md` when shared components are affected |
| Optional | Persona | User-facing features | Relevant persona |
| Optional | Architecture | Multi-component features | Affected components |

**Example Assembly**:
```xml
<context>
  <feature-brief>
    [Full Feature Brief document from docs/work-items/FEAT-XXX-name.md]
  </feature-brief>

  <stakeholder-definition>
    [Sections: Philosophy, Principles, Scope Lock, Success Metrics]
  </stakeholder-definition>

  <code-conventions>
    [Full CLAUDE.md]
  </code-conventions>

  <data-model>
    [docs/data-model/index.md + the entity shards named by the impact table]
  </data-model>

  <api-spec>
    [docs/api-spec/index.md + the endpoint shards named by the impact table]
  </api-spec>

  <ui-specification>
    [If user-facing: docs/ui-specification/index.md (Design System) + the screen shards named by the impact table]
  </ui-specification>

  <persona>
    [If user-facing: relevant persona details]
  </persona>

  <architecture>
    [If multi-component: affected components and data flow]
  </architecture>
</context>
```

---

### 2. Bug Fix

**Goal**: Generate investigation and fix tasks that address root cause.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Bug Report | Always (preferred) | Full `docs/work-items/BUG-*.md` — reproduction, evidence, impact |
| Required | CLAUDE.md | Always | Full document |
| Optional | Architecture | Multi-component bug | Affected components |
| Optional | Data Model | Data-related bugs | `docs/data-model/index.md` + affected entity shards (`entities/<entity>.md`) |
| Optional | API Specification | API-related bugs | `docs/api-spec/index.md` + affected endpoint shards (`endpoints/<resource>.md`) |
| Optional | UI Specification | UI-related bugs | `docs/ui-specification/index.md` + affected screen shards (`screens/<screen>.md`) |
| Optional | Stakeholder Definition | Scope clarification needed | Scope lock, principles |

**Example Assembly**:
```xml
<context>
  <bug-report-doc>
    [Full Bug Report document from docs/work-items/BUG-XXX-name.md]
  </bug-report-doc>

  <code-conventions>
    [Full CLAUDE.md]
  </code-conventions>

  <architecture>
    [Components involved in the bug]
    [Data flow through affected area]
  </architecture>

  <data-model>
    [If data-related: docs/data-model/index.md + affected entity shards]
  </data-model>
</context>
```

---

### 3. Refactoring

**Goal**: Generate safe, incremental refactoring tasks that maintain functionality.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Improvement Proposal | Always (preferred) | Full `docs/work-items/IMP-*.md` — current/desired state, risks, criteria |
| Required | CLAUDE.md | Always | Full document |
| Required | Architecture | Always | Current + target state |
| Optional | Data Model | Data layer refactoring | `docs/data-model/index.md` + entity shards in the affected area |
| Optional | Stakeholder Definition | Large-scale refactoring | Principles, scope |

**Example Assembly**:
```xml
<context>
  <improvement-proposal>
    [Full Improvement Proposal document from docs/work-items/IMP-XXX-name.md]
  </improvement-proposal>

  <code-conventions>
    [Full CLAUDE.md]
  </code-conventions>

  <architecture>
    [Current architecture of affected area]
    [Target architecture after refactoring]
    [Component dependencies]
  </architecture>
</context>
```

---

### 4. Testing

**Goal**: Generate comprehensive test tasks covering requirements and edge cases.

> **Note:** No dedicated prompt exists for this task type — use `prompts/base-template.md` with this context recipe.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | CLAUDE.md | Always | Testing conventions section |
| Optional | Architecture | Testing component interactions | Component structure |
| Optional | Stakeholder Definition | Testing acceptance criteria | Success metrics |

**Example Assembly**:
```xml
<context>
  <code-conventions>
    [CLAUDE.md testing section]
  </code-conventions>

  <architecture>
    [Components under test]
    [Integration points to verify]
  </architecture>
</context>
```

---

### 5. Integration

**Goal**: Generate tasks for connecting to external services correctly.

> **Note:** No dedicated prompt exists for this task type — use `prompts/base-template.md` with this context recipe.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Architecture | Always | Integration points, data flow |
| Required | CLAUDE.md | Always | Error handling patterns |
| Required | Data Model | Always | `docs/data-model/index.md` + entity shards involved in the integration |
| Required | API Specification | Always | `docs/api-spec/index.md` + endpoint shards that connect to or expose the integration |
| Optional | Stakeholder Definition | Scope check | What integrations are in scope |

**Example Assembly**:
```xml
<context>
  <architecture>
    [Where integration fits in system]
    [Data flow through integration]
    [External service details from integration points section]
  </architecture>

  <code-conventions>
    [Full CLAUDE.md]
    [Emphasis on error handling section]
  </code-conventions>

  <data-model>
    [docs/data-model/index.md + entity shards involved in the integration]
  </data-model>

  <api-spec>
    [docs/api-spec/index.md + endpoint shards that expose or connect to the integration]
  </api-spec>
</context>
```

---

### 6. Prioritization & Roadmap Planning

**Goal**: Evaluate and prioritize work items based on product strategy.

> **Note:** No dedicated prompt exists for this task type — use `prompts/base-template.md` with this context recipe.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Work Items | Always | All `docs/work-items/FEAT-*.md`, `BUG-*.md`, `IMP-*.md` to compare |
| Required | Stakeholder Definition | Always | Success metrics, scope, philosophy |
| Required | Persona | Always | User priorities and pain points |
| Optional | Architecture | Technical feasibility | Complexity factors |

**Example Assembly**:
```xml
<context>
  <work-items>
    [All Feature Briefs, Bug Reports, and Improvement Proposals to prioritize]
  </work-items>

  <stakeholder-definition>
    ## Success Metrics
    [What we're optimizing for]

    ## Scope Lock
    [What's in/out of scope]

    ## Product Philosophy
    [Guiding principles]
  </stakeholder-definition>

  <persona>
    [User pain points and priorities]
    [What the user values most]
  </persona>
</context>

<request>
Evaluate these work items and recommend prioritization:
1. FEAT-001: [Feature name]
2. BUG-003: [Bug summary]
3. IMP-002: [Improvement name]

Consider: user impact, severity, development cost, strategic alignment, dependencies.
</request>
```

---

### 7. UI Mockup Generation

**Goal**: Generate a self-contained HTML mockup for stakeholder visual approval before implementation in the stack declared in CLAUDE.md [e.g., Angular].

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | UI Specification | Always | Target screen's shard (`docs/ui-specification/screens/<screen>.md`: layout, hierarchy, states) + Design System from `docs/ui-specification/index.md`; `components.md` for shared components used |
| Required | CLAUDE.md | Always | Design tokens, CSS conventions [e.g., Tailwind], frontend patterns |
| Recommended | API Specification | When screen displays data | Endpoint shards the screen calls (`docs/api-spec/endpoints/<resource>.md`) — response DTO shapes for realistic placeholder content |
| Optional | Persona | User-facing screens | Content tone for placeholder text |
| Optional | Stakeholder Definition | Branding needed | Product name, philosophy |

**Example Assembly**:
```xml
<context>
  <ui-specification>
    [Target screen shard docs/ui-specification/screens/<screen>.md: layout sketch, component hierarchy, states]
    [Design System from docs/ui-specification/index.md: colors, typography, spacing tokens]
  </ui-specification>

  <code-conventions>
    [CLAUDE.md: CSS conventions (e.g., Tailwind), design tokens, frontend patterns]
  </code-conventions>

  <api-spec>
    [If data-driven screen: endpoint shards the screen calls — response DTO shapes for placeholder content]
  </api-spec>
</context>
```

---

### 8. Release Lifecycle Transition

**Goal**: Transition from versioned to continuous development, or mark a version as complete.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Stakeholder Definition | Always | Full document — current scope structure, all sections |
| Required | CLAUDE.md | Always | Full document |
| Recommended | Architecture | Structural changes during transition | Current component structure |
| Recommended | Release Lifecycle Guide | Always | `guides/release-lifecycle.md` — transition checklist and target structure |

**Example Assembly**:
```xml
<context>
  <stakeholder-definition>
    [Full stakeholder definition document]
  </stakeholder-definition>

  <code-conventions>
    [Full CLAUDE.md]
  </code-conventions>

  <release-lifecycle-guide>
    [Full guides/release-lifecycle.md]
  </release-lifecycle-guide>
</context>
```

---

### 9. ADR Compilation

**Goal**: Compile Architecture Decision Records from a shared ADR repo into pre-filled template sections.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | ADR files | Always | All selected ADR files from the shared ADR repo |
| Recommended | `.ai-framework/templates/` | Always | Target templates for correct heading structure (agents read directly) |

**Note:** This task type is different from the others — it produces pre-filled *template sections*, not a final deliverable. Run it when bootstrapping a new project, before filling in Phase 2 templates.

---

### 10. DDR Compilation

**Goal**: Compile Design Decision Records from a shared DDR repo into pre-filled Design System sections, component patterns, state handling, and responsive breakpoints.

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | DDR files | Always | All selected DDR files from the shared DDR repo (or specified via a profile) |
| Optional | Profile file | When using a curated visual identity | Profile from DDR repo with override values for tokens |
| Recommended | `.ai-framework/templates/` | Always | Target templates for correct heading structure (agents read directly) |

**Note:** This task type produces pre-filled *Design System sections*, not a final deliverable. Run it when bootstrapping a new project, after applying ADRs (Step 1.1) and before filling in UI-related templates (Phase 2, Step 7).

**Example Assembly**:
```xml
<context>
  <ddrs>
    [All DDR files selected for the project, or referenced by a profile]
  </ddrs>

  <profile>
    [If using a profile: the profile file with override values]
  </profile>
</context>
```

---

### 11. Task List Review

**Goal**: Adversarially review a generated task list before planning and implementation — verify AC coverage, scope fidelity, reference reality, dependency logic, sizing, and workflow correctness.

**Prompt:** `.ai-framework/prompts/review-tasks.md` — writes the review to `tasks/<WORK-ITEM-ID>-review.md` (verdict + findings table).

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Task List | Always | The full task list under review (`tasks/<WORK-ITEM-ID>-tasks.md`) |
| Required | Work Item | Always | The full `docs/work-items/` document the task list was generated from |
| Required | Data Model | Always | `docs/data-model/index.md` + entity shards named by the work item's impact tables |
| Required | API Specification | Always | `docs/api-spec/index.md` + endpoint shards named by the work item's impact tables |
| Required | UI Specification | Always | `docs/ui-specification/index.md` + screen shards named by the work item's impact tables |
| Required | CLAUDE.md | Always | Full document |

That list is exhaustive — nothing else goes into the reviewer's context. Two rules are absolute for this task type:

1. **Run in a FRESH context.** Never include the generating agent's conversation transcript or reasoning. Same-session self-review is unreliable; the reviewer must see only the artifacts and specs listed above.
2. **Never include `docs/rationale/`.** As with every recipe in this guide, rationale files stay out of context.

Before judging semantics, the reviewer runs the external validators — `python .ai-framework/tools/validate-tasks.py` and `python .ai-framework/tools/validate-specs.py` — and treats their output as ground truth (see the prompt's Guidance).

**Example Assembly**:
```xml
<context>
  <task-list>
    [Full task list under review from tasks/<WORK-ITEM-ID>-tasks.md]
  </task-list>

  <work-item>
    [Full work item from docs/work-items/ — the one the task list was generated from]
  </work-item>

  <data-model>
    [docs/data-model/index.md + the entity shards named by the impact table]
  </data-model>

  <api-spec>
    [docs/api-spec/index.md + the endpoint shards named by the impact table]
  </api-spec>

  <ui-specification>
    [docs/ui-specification/index.md + the screen shards named by the impact table]
  </ui-specification>

  <code-conventions>
    [Full CLAUDE.md]
  </code-conventions>

  <!-- NOTHING ELSE: no generator transcript, no reasoning, no docs/rationale/ -->
</context>
```

---

### 12. Implementation Review

**Goal**: Adversarially review an implemented task's code changes — after implementation, before the task is marked complete — verify AC satisfaction, plan adherence, scope fidelity, convention compliance, spec sync, and test adequacy.

**Prompt:** `.ai-framework/prompts/review-implementation.md` — writes the review to `tasks/<WORK-ITEM-ID>-<TASK-ID>-implementation-review.md` (verdict + findings table).

| Priority | Document | Include When | What to Include |
|----------|----------|--------------|-----------------|
| Required | Task Block | Always | The single `T-XXX` block under review from `tasks/<WORK-ITEM-ID>-tasks.md` — not the whole task list |
| Required | Implementation Plan | Always | The full `plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md` the implementation was supposed to follow |
| Required | Implementation Diff | Always | The diff or changed-file set, as provided by the requester (e.g., `git diff <base>..<head>` output, or a branch to inspect) |
| Required | CLAUDE.md | Always | Full document |
| Required | Spec Shards | Task references entities/endpoints/screens | Each spec's `index.md` + only the shards the task names, mapped via the retrieval-key naming rule |

That list is exhaustive — nothing else goes into the reviewer's context. Two rules are absolute for this task type:

1. **Run in a FRESH context.** Never include the implementing agent's conversation transcript or reasoning — the reviewer must not be the session that implemented the task. Same-session self-review is unreliable; the reviewer must see only the artifacts listed above.
2. **Never include `docs/rationale/`.** As with every recipe in this guide, rationale files stay out of context.

Before judging the diff, the reviewer gathers **external evidence** and treats it as ground truth: the project's test suite and linters, plus `python .ai-framework/tools/validate-specs.py` when the task touched spec shards (see the prompt's Guidance).

**Example Assembly**:
```xml
<context>
  <task-block>
    [The single T-XXX task block from tasks/<WORK-ITEM-ID>-tasks.md]
  </task-block>

  <implementation-plan>
    [Full plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md]
  </implementation-plan>

  <implementation-diff>
    [git diff <base>..<head> output, or the full content of each changed file]
  </implementation-diff>

  <code-conventions>
    [Full CLAUDE.md]
  </code-conventions>

  <spec-shards>
    [Each spec's index.md + only the shards the task references]
  </spec-shards>

  <evidence>
    [Raw test / linter / validate-specs.py output — pasted by the orchestrator/human]
  </evidence>

  <!-- NOTHING ELSE: no implementer transcript, no reasoning, no docs/rationale/ -->
</context>
```

---

## Context Size Management

### Guideline: Quality Over Quantity

With 10 templates, be mindful of total context size. For the sharded spec documents (data-model, api-spec, ui-specification), size control is built in: read each spec's `index.md` plus only the shards named by the work item's impact tables (see **Retrieval Keys** above) — never whole spec directories. Work item documents (Feature Brief, Bug Report, Improvement Proposal) should generally be included in full since they are scoped to a single work item. `docs/rationale/` files are never loaded — the contract docs stay lean and link out to them.

### Strategies for Large Single-File Documents

For the documents that remain single files (ARCHITECTURE.md, stakeholder definition, CLAUDE.md):

#### 1. Section Extraction
Instead of full document, extract only relevant sections:

```xml
<!-- Instead of full architecture doc -->
<architecture-excerpt>
## Order Service
[Order service section only]

## Integration Points
[Only relevant integration section]
</architecture-excerpt>
```

#### 2. Summary + Detail
Provide summary for context, detail only where needed:

```xml
<architecture-summary>
The system uses a microservices architecture with 5 services.
For this task, only the Order Service is relevant.
</architecture-summary>

<architecture-detail>
## Order Service
[Full Order Service definition]
</architecture-detail>
```

---

## Context Assembly Workflow

### Path A: AI Agents (Claude Code, etc.)

Agents have direct file access and don't need XML assembly. Follow these steps:

1. **Identify the task type** from the user's request — one of the 12 task types above (New Feature, Bug Fix, Refactoring, Testing, Integration, Prioritization, UI Mockup, Release Transition, ADR Compilation, DDR Compilation, Task List Review, Implementation Review)
2. **Read the files** listed in the CLAUDE.md routing table for that task type
3. **For the sharded spec docs**, read each spec's `index.md` plus only the shards named by the work item's impact tables — e.g., for a task about the `TaskLabel` entity and the `/api/task-labels` resource, read `docs/data-model/index.md` + `docs/data-model/entities/task-label.md` and `docs/api-spec/index.md` + `docs/api-spec/endpoints/task-labels.md`. Never read whole spec directories, and never read `docs/rationale/`
4. **Read the prompt template** from `.ai-framework/prompts/` — use the **Output Format** section as your deliverable structure, and apply the **Guidance**, **Constraints**, and **Post-Generation Checklist**
5. **Generate the deliverable** directly — no XML wrapping needed — and write it to its canonical location (task lists to `tasks/FEAT-XXX-tasks.md` etc., plans to `plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md`, mockups to `mockups/<WORK-ITEM-ID>-T-XXX-screen-name.html`)

### Path B: Manual Context Assembly (Chat Workflows)

For copy-paste workflows where you assemble an XML prompt to submit to Claude:

> **Ordering (chat assembly only):** in a single stuffed prompt, models attend best to
> the start and end of the context — place the request and constraints first, the
> acceptance criteria last, and bulk reference material in the middle. This applies
> only to single-prompt assembly: for agentic sessions that read files themselves,
> read order showed no measurable effect (EXP-003 in the framework's `evals/experiments.md`).

#### Step 1: Identify Task Type
What kind of task are you generating? One of the 12 task types above (New Feature, Bug Fix, Refactoring, Testing, Integration, Prioritization, UI Mockup, Release Transition, ADR Compilation, DDR Compilation, Task List Review, Implementation Review)

#### Step 2: Check Required Documents
Consult the task-type tables above for your task type. Gather required documents.

#### Step 3: Assess Complexity
- **Simple task**: CLAUDE.md only (or + 1 other document)
- **Standard task**: 2-3 documents
- **Complex task**: 4+ documents (extract only the relevant sections of each)

#### Step 4: Extract Relevant Sections
Don't include entire documents if only portions are relevant. For the sharded spec docs, paste each spec's `index.md` plus only the shards named by the work item's impact tables.

#### Step 5: Structure with XML Tags
Use clear XML tags to separate context sections. This helps Claude parse and reference specific sections.

#### Step 6: Add Task-Specific Details
Include the specific request, constraints, and output format requirements.

---

## Common Mistakes to Avoid

### 1. Missing Critical Context
**Wrong**: Generating feature tasks without scope lock
**Right**: Always include stakeholder definition for features

### 2. Outdated Context
**Wrong**: Using cached/old versions of documents
**Right**: Always pull latest versions before compilation

### 3. Unstructured Context
**Wrong**: Pasting documents without XML tags
**Right**: Use clear tags so Claude can reference sections

### 4. Missing Constraints
**Wrong**: Assuming Claude knows project constraints
**Right**: Explicitly state technology, timeline, and compatibility constraints

### 5. Loading Whole Spec Directories
**Wrong**: Reading every file under `docs/data-model/`, `docs/api-spec/`, or `docs/ui-specification/` — or pulling in `docs/rationale/` files
**Right**: Read each spec's `index.md` plus only the shards named by the work item's impact tables (see Retrieval Keys); never load rationale files

---

## Quick Reference Card

| Task Type | Must Include | Recommended / Optional |
|-----------|--------------|------------------------|
| New Feature | Feature Brief + Stakeholder + CLAUDE.md | Data Model†, API Spec†, UI Spec†, Persona, Architecture |
| Bug Fix | Bug Report + CLAUDE.md | Architecture, Data Model†, API Spec†, UI Spec†, Stakeholder |
| Refactoring | Improvement Proposal + CLAUDE.md + Architecture | Data Model†, Stakeholder |
| Testing* | CLAUDE.md | Architecture, Stakeholder |
| Integration* | Architecture + CLAUDE.md + Data Model† + API Spec† | Stakeholder |
| Prioritization* | Work Items + Stakeholder + Persona | Architecture |
| UI Mockup | UI Spec† (screen shard + Design System) + CLAUDE.md | API Spec†, Persona, Stakeholder |
| Release Transition | Stakeholder + CLAUDE.md | Architecture, `guides/release-lifecycle.md` |
| ADR Compilation | ADR files | `.ai-framework/templates/` |
| DDR Compilation | DDR files (+ optional profile) | `.ai-framework/templates/` |
| Task List Review‡ | Task list + Work Item + Data Model† + API Spec† + UI Spec† + CLAUDE.md | — (nothing else) |
| Implementation Review‡ | Task block + Plan + Implementation diff + CLAUDE.md + referenced spec shards† | — (nothing else) |

\* No dedicated prompt — use `prompts/base-template.md` with this context recipe.

† Sharded spec — include the spec's `index.md` plus ONLY the shards named by the work item's impact tables (see Retrieval Keys) — for Implementation Review, the shards the task itself references. Never load the whole directory; never load `docs/rationale/`.

‡ Runs in a FRESH context — never include the generating/implementing session's transcript or reasoning, never `docs/rationale/`. Task List Review: `.ai-framework/prompts/review-tasks.md` → `tasks/<WORK-ITEM-ID>-review.md`. Implementation Review: `.ai-framework/prompts/review-implementation.md` → `tasks/<WORK-ITEM-ID>-<TASK-ID>-implementation-review.md`.

---

## Example: Complete Context Compilation (Chat Workflow)

Here's a full example for a new feature task using the chat workflow (XML assembly). Agents skip this — they read files directly.

```xml
<task-generation-request>

<context>

<!-- Layer 1: Strategic -->
<stakeholder-definition>
## Product Philosophy
- Conversation-first: Feels like chat, not a form
- Keyboard-last: Typing only when unavoidable
- Trust before tech: Never surprise the user

## Scope Lock (V1)
Included: Pizza ordering, Multi-pizza cart, Visual guidance
Excluded: Discounts, User accounts, Loyalty programs, In-chat payments
</stakeholder-definition>

<persona>
## Primary User: The Busy Restaurant Owner
- Not tech-savvy, needs simple interactions
- Peak pain during Friday evening rush
- Success = fewer order errors, faster checkout
</persona>

<!-- Layer 2: Architectural -->
<architecture>
## Order Service
- Handles order lifecycle
- Connects to payment and notification services
- REST API with JSON payloads
</architecture>

<!-- Layer 3: Specification -->
<!-- Pasted from docs/data-model/entities/order.md and order-item.md
     (shards named by the work item's entity impact table) -->
<data-model>
## Order Entity (Orders Module)
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| phone_number | string(20) | Required, Indexed |
| status | enum: OrderStatus | Required |
| total_amount | decimal(10,2) | Required |
| created_at | timestamptz | Required, Auto |

## OrderItem Entity (Orders Module)
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK |
| order_id | UUID | FK → Order |
| pizza_name | string(100) | Required |
| quantity | int | Required, Min: 1 |
</data-model>

<!-- Pasted from docs/api-spec/endpoints/orders.md -->
<api-spec>
## GET /api/orders?phone={phone}&limit=10
Auth: Public (phone-based)
Response: { data: Order[], meta: { totalCount } }

## POST /api/orders
Auth: Public
Request: { phone_number, items: [{ pizza_id, quantity }] }
Response: { data: Order }
</api-spec>

<!-- Layer 4: UI -->
<!-- Pasted from docs/ui-specification/screens/order-history.md -->
<ui-specification>
## Order History Screen
Route: /orders/history
Components: OrderListComponent → OrderCardComponent
API: GET /api/orders?phone={phone}&limit=10
States: Loading (spinner), Empty ("No orders yet"), Error (retry banner)
Interactions: Click order → expand detail, Pull to refresh → re-fetch
</ui-specification>

<!-- Layer 5: Implementation -->
<code-conventions>
## Project Structure
- Flows: /flows/*.json
- Backend: /src/handlers/
- Types: /src/types/

## Patterns
- WhatsApp Flows for all UI
- Zod for validation
- Custom errors with APP- prefix
</code-conventions>

</context>

<task-type>New Feature</task-type>

<request>
Generate implementation tasks for the Order History feature.
</request>

<constraints>
- Must work within WhatsApp Flows (no web views)
- Phone number is the only user identifier
- History limited to last 30 days
</constraints>

<output-format>
[Specify desired task format]
</output-format>

</task-generation-request>
```
