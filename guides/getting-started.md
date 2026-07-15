# Getting Started

This guide walks you from "I have a project idea" to "I'm generating AI tasks." Budget about 2-3 hours for the full workflow, or about an hour for a rough first pass.

---

## Phase 0: Prerequisites

**What you need:**
- A project idea (even a vague one works)
- A folder for your project

**That's it.** You don't need a tech stack chosen, wireframes, or a business plan. The templates will help you figure those out.

### Choose Your Path

| Path | You have... | Start with... |
|------|-------------|---------------|
| **New Project** | An idea but no code yet | Persona → Stakeholder → CLAUDE.md → Architecture → Data Model → API Spec → UI Spec |
| **Existing Codebase** | Code that needs documentation | CLAUDE.md → Stakeholder → Architecture → Data Model → API Spec → UI Spec → Persona |

---

## Phase 1: Set Up Structure

Copy the scaffold into your project:

```bash
# From your project root
cp -r path/to/carestechs-ia-framework/scaffold/. .
```

Note the `/.` at the end — it ensures dotfile directories (`.ai-framework/`, `.claude/`) are copied too.

> **Caution:** If your project already has a `CLAUDE.md`, merge the scaffold's version into it manually instead of overwriting.

You should now have:

```
your-project/
├── CLAUDE.md
├── .ai-framework/                # Bundled framework reference
│   ├── VERSION
│   ├── README.md
│   ├── templates/
│   ├── prompts/
│   ├── guides/
│   └── tools/                    # validate-tasks.py, validate-specs.py (validators)
├── .claude/
│   └── commands/                 # Claude Code slash commands (/feature-tasks, /plan-generation, ...)
├── docs/
│   ├── personas/
│   │   └── primary-user.md
│   ├── stakeholder-definition.md
│   ├── ARCHITECTURE.md
│   ├── data-model/
│   │   ├── index.md              # Conventions, module ownership, relationships overview, shared enums
│   │   └── entities/             # One shard per entity (TEMPLATE-entity.md starter)
│   ├── api-spec/
│   │   ├── index.md              # API decisions, response envelope, error catalog, auth, pagination
│   │   └── endpoints/            # One shard per resource group (TEMPLATE-resource.md starter)
│   ├── ui-specification/
│   │   ├── index.md              # UI decisions + Design System
│   │   ├── screens/              # One shard per screen (TEMPLATE-screen.md starter)
│   │   └── components.md         # Shared components inventory
│   ├── rationale/                # Narrative & history — never loaded as AI context
│   └── work-items/               # Feature briefs, bug reports, improvements
│       ├── TEMPLATE-feature-brief.md
│       ├── TEMPLATE-bug-report.md
│       └── TEMPLATE-improvement-proposal.md
├── tasks/                        # Generated task lists (FEAT-XXX-tasks.md, ...)
├── plans/                        # Implementation plans (plan-T-XXX-short-title.md)
└── mockups/                      # HTML mockups (T-XXX-screen-name.html)
```

Each file has section headers with `<!-- TODO -->` prompts telling you exactly what to fill in.

> **Spec docs are sharded.** `docs/data-model/`, `docs/api-spec/`, and `docs/ui-specification/` are directories, not single files: cross-cutting content lives in each `index.md`, and every entity, resource, and screen gets its own shard. Naming is mechanical (kebab-case): entity `TaskLabel` → `entities/task-label.md` (singular), resource `/api/task-labels` → `endpoints/task-labels.md` (matches the route segment, plural), screen "Project Board" → `screens/project-board.md`.
>
> **Keep spec docs contract-style.** Narrative, history, and decision background go to `docs/rationale/<topic>.md`, linked from the spec as `Why: see docs/rationale/<topic>.md`. Rationale files are never loaded as AI context.

### Step 1.1: Apply Architecture Decisions (Optional)

If you have a set of Architecture Decision Records (ADRs) from a shared repo (e.g., `your-architecture-decisions`):

1. Select the ADRs relevant to your project's tech stack (e.g., the `profiles/dotnet-angular-modular-monolith.md` manifest lists which ADRs to use together)
2. Use the [`.ai-framework/prompts/compile-adrs.md`](../prompts/compile-adrs.md) prompt to compile them into pre-filled template sections
3. Paste the compiled sections into your project docs before filling in project-specific details

This pre-fills conventions, patterns, and decision tables so you only need to add project-specific content (entities, endpoints, screens, etc.).

### Step 1.2: Apply Design Decisions (Optional)

If you have a set of Design Decision Records (DDRs) from a shared repo (e.g., `your-ui-design-decisions`):

1. **Select a profile** that matches your project type (e.g., `profiles/corporate-clean.md` for B2B/enterprise, `profiles/modern-minimal.md` for content apps, `profiles/bold-startup.md` for consumer products) — or select individual DDRs
2. Use the [`.ai-framework/prompts/compile-ddrs.md`](../prompts/compile-ddrs.md) prompt to compile them into pre-filled template sections
3. Paste the compiled sections into your project docs:
   - **Design System** (colors, typography, spacing, component library, state patterns, responsive breakpoints) → `docs/ui-specification/index.md`
   - **Design Patterns to Follow / Avoid** → `CLAUDE.md`
   - **Component Examples Appendix** → save as reference for mockup generation

This pre-fills the Design System, state handling patterns, and responsive breakpoints so you only need to add project-specific content (screens, components, interactions). Run this step **before** filling the UI Specification (Step 7).

---

## Phase 2: Fill Templates (New Project Path)

Work through the templates in this order. Each step builds on the previous one.

### Step 1: Persona (`docs/personas/primary-user.md`)

**Goal:** Define who you're building for.

**Key questions to answer:**
- Who is your primary user? What's their role?
- What is their single biggest pain point?
- How do they solve this problem today (without your product)?
- Why target this user segment first?

**"Good enough" checklist:**
- [ ] You can describe the user in one sentence
- [ ] You've named their core pain point
- [ ] You know why their current workaround fails
- [ ] You've noted why you picked this segment over others

**Time:** ~15 minutes

> **Tip:** If you're stuck, think about the last time you personally felt this pain. That's often your best persona.

---

### Step 2: Stakeholder Definition (`docs/stakeholder-definition.md`)

**Goal:** Define what you're building, why, and where the boundaries are.

**Key questions to answer:**
- What type of product is this? (web app, CLI, API, mobile app...)
- What is the one-sentence value proposition?
- What are 3-5 guiding principles for every decision?
- What is explicitly in scope? What is explicitly out?
- How will you measure success?

**"Good enough" checklist:**
- [ ] Executive summary is filled (what, value prop, success criteria)
- [ ] You have at least 3 guiding principles
- [ ] Scope Lock has at least 3 items in scope and 2 items explicitly excluded
- [ ] You have at least 2 success metrics with measurable targets

**Time:** ~20 minutes

> **Tip:** The Scope Lock section is the most important. Be ruthless about what's out of scope — this prevents AI from suggesting features you don't want.

---

### Step 3: CLAUDE.md (`CLAUDE.md`)

**Goal:** Give AI assistants the context they need to write code correctly.

**Key questions to answer:**
- What's the tech stack?
- What are the essential commands (dev, build, test, lint)?
- What naming conventions do you use?
- What patterns should always be followed? What should never be done?

**"Good enough" checklist:**
- [ ] Project overview and tech stack are filled
- [ ] At least 2-3 common commands are documented
- [ ] Naming conventions table has entries for files, functions, and types
- [ ] At least 2 patterns and 2 anti-patterns are listed

**Time:** ~15 minutes

> **Tip:** For a new project, this can be aspirational — describe the conventions you *want* to follow. You'll refine it after writing your first code.

---

### Step 4: Architecture (`docs/ARCHITECTURE.md`)

**Goal:** Document how the system is structured.

**Key questions to answer:**
- What are the major components?
- What technologies are you using for each layer?
- How does data flow through the system?
- What external services do you integrate with?
- How do you handle authentication and security?

**"Good enough" checklist:**
- [ ] Technology stack table is filled
- [ ] At least 2-3 components are described with their responsibilities
- [ ] Primary data flow is described (even as a numbered list)
- [ ] Security approach is outlined (even if just "TBD — will use [X]")

**Time:** ~20 minutes

> **Tip:** For a brand-new project, keep this high-level. You can flesh out the component diagram and data flows after you've written some code.

---

### Step 5: Data Model (`docs/data-model/`)

**Goal:** Define every entity, its fields, relationships, and module ownership — as `index.md` (key modeling decisions, module ownership, database conventions, relationships overview, shared enums) plus one shard per entity in `entities/`.

**Key questions to answer:**
- What entities does each module own?
- What fields does each entity have (name, type, constraints)?
- How do entities relate to each other (1:N, M:N)?
- Which references cross module boundaries (ID-only)?
- What enums and value types exist?

**"Good enough" checklist:**
- [ ] Every in-scope feature maps to at least one entity
- [ ] Each entity has its own shard `entities/<entity>.md` (kebab-case, singular — `TaskLabel` → `task-label.md`) with a field table (types, constraints)
- [ ] Relationships are defined with cascade behaviors; the relationships overview (ER diagram) in `index.md` covers them
- [ ] Cross-module references are ID-only
- [ ] Standard audit fields (id, created_at, updated_at) are on every entity

**Time:** ~20 minutes

> **Tip:** Use the `spec-generation.md` prompt to generate this from your existing stakeholder + architecture + CLAUDE.md docs — it writes `index.md` plus one shard per entity. Review and refine the output rather than writing from scratch.

---

### Step 6: API Specification (`docs/api-spec/`)

**Goal:** Define every REST endpoint with routes, request/response shapes, and status codes — as `index.md` (key API decisions, response envelope, error catalog, authentication endpoints, pagination) plus one shard per resource group in `endpoints/`.

**Key questions to answer:**
- What CRUD endpoints does each entity need?
- What non-CRUD actions exist (assign, move, upload)?
- What are the request and response DTO shapes?
- Which endpoints require authentication? What roles?
- How are lists paginated?

**"Good enough" checklist:**
- [ ] Every entity has appropriate CRUD endpoints
- [ ] Each resource group has its own shard `endpoints/<resource>.md`, named after the route segment (plural — `/api/task-labels` → `task-labels.md`), holding all endpoint blocks for that resource
- [ ] Request/response DTOs are fully defined
- [ ] Auth requirements are specified per endpoint
- [ ] List endpoints support pagination (convention defined once in `index.md`)
- [ ] Error status codes are listed for each endpoint and map to the Error Catalog in `index.md`

**Time:** ~20 minutes

> **Tip:** Generate the data model first, then use it as additional context when generating the API spec — endpoints map naturally from entities. The `spec-generation.md` prompt writes `index.md` plus the endpoint shards.

---

### Step 7: UI Specification (`docs/ui-specification/`)

**Goal:** Define every screen's layout, component hierarchy, design tokens, interaction patterns, and state handling (loading, empty, error) — as `index.md` (key UI decisions + Design System), one shard per screen in `screens/`, and a shared `components.md` inventory.

**Key questions to answer:**
- What screens does each user flow step require?
- What is the component hierarchy for each screen?
- Which component calls which API endpoint?
- What does each screen look like in loading, empty, and error states?
- What shared/reusable components exist across screens?
- What are the design tokens (colors, typography, spacing)?

**"Good enough" checklist:**
- [ ] Every user flow step has a corresponding screen shard `screens/<screen>.md` (kebab-case — "Project Board" → `project-board.md`)
- [ ] Every screen maps to at least one API endpoint
- [ ] Every screen has all 4 states defined (default, loading, empty, error)
- [ ] Component hierarchy is defined in each screen shard
- [ ] Shared components (used in 2+ screens) are inventoried in `components.md`
- [ ] Design tokens (colors, typography, spacing) are defined in the `index.md` Design System
- [ ] Interactions are specific — each maps to a UI element, result, and API call

**Time:** ~20 minutes

> **Tip:** Generate the API spec first, then use it as additional context when generating the UI spec — endpoints map directly to component data needs. Use the `ui-spec-generation.md` prompt to auto-generate from your existing docs — it writes `index.md`, the screen shards, and `components.md`.

---

### Step 7.5: HTML Mockups (Optional)

**Goal:** Create browser-viewable HTML prototypes of key screens for stakeholder visual approval before writing frontend code in the stack declared in CLAUDE.md [e.g., Angular].

**When to use:**
- User-facing screens with novel or complex layouts
- Multi-state screens where stakeholders need to see all states (default, loading, empty, error)
- Screens where the ASCII layout sketch needs visual validation

**When to skip:**
- Standard CRUD layouts (list/detail/form)
- Screens that follow a pattern already approved in a previous mockup
- Backend-only features with no UI

**Process:**
1. Pick a screen from `docs/ui-specification/screens/`
2. Use the [`mockup-generation.md`](../prompts/mockup-generation.md) prompt template
3. Assemble context: the screen's shard (`docs/ui-specification/screens/<screen>.md`) + Design System from `docs/ui-specification/index.md` + CLAUDE.md
4. Generate the HTML mockup file and save it as `mockups/T-XXX-screen-name.html`
5. Open in a browser and review visually
6. Share with stakeholders for approval

**"Good enough" checklist:**
- [ ] Layout matches the ASCII sketch from the UI Specification
- [ ] Design tokens (colors, fonts, spacing) match the Design System
- [ ] All requested states are shown side-by-side
- [ ] Stakeholder has reviewed and approved

**Time:** ~10 minutes per screen

> **Tip:** Focus on novel layouts — don't mock up every screen. Standard CRUD screens rarely need a visual prototype.

---

## Phase 2-alt: Fill Templates (Existing Codebase Path)

If you already have code, document what exists first, then layer in the strategic context.

### Step A1: CLAUDE.md (Document What Exists)

Start here because this is the most immediately useful — it makes every AI interaction with your code better right away.

- Look at your `package.json` (or equivalent) for commands
- Look at your file structure for naming conventions
- Think about what patterns you've already established
- Note any "gotchas" a new developer (or AI) would hit

### Step A2: Stakeholder Definition (What You're Building Toward)

Even for an existing codebase, clarifying your vision and scope helps the AI make better prioritization decisions.

- Focus on the **Scope Lock** — what's in and out for the current version
- Fill the **Product Philosophy** — this shapes how AI approaches tasks
- Set **Success Metrics** — what are you optimizing for right now?

### Step A3: Architecture (Document Current System)

Describe the system as it is today, not as you wish it were.

- Map out the components that actually exist
- Document the real data flow
- Note integration points and their current state
- Be honest about security — document gaps as "TODO" items

### Step A4: Data Model (Reverse-Engineer from Code)

Document the entities as they exist in your persistence layer today.

- Use the [`spec-generation.md`](../prompts/spec-generation.md) prompt with your entity classes/schema files, CLAUDE.md, and architecture doc as context
- Write one shard per entity under `docs/data-model/entities/`; conventions, module ownership, and the relationships overview go in `docs/data-model/index.md`
- Capture fields, types, constraints, relationships, and module ownership as implemented — not as planned
- Note any known modeling debt (missing indexes, cross-module navigation) as TODO items

### Step A5: API Specification (Reverse-Engineer from Code)

Document the endpoints your backend actually exposes.

- Use the [`spec-generation.md`](../prompts/spec-generation.md) prompt with your controllers/route handlers and the fresh data model as context
- Write one shard per resource group under `docs/api-spec/endpoints/`; the response envelope, error catalog, auth, and pagination conventions go in `docs/api-spec/index.md`
- Record routes, methods, request/response DTO shapes, auth requirements, and status codes as implemented
- Flag inconsistencies (e.g., unpaginated list endpoints) rather than papering over them

### Step A6: UI Specification (Reverse-Engineer from Screens)

Document the screens and components your frontend already has.

- Use the [`ui-spec-generation.md`](../prompts/ui-spec-generation.md) prompt with your existing routes/components, the API spec, and CLAUDE.md as context
- Write one shard per screen under `docs/ui-specification/screens/`, shared components in `docs/ui-specification/components.md`, and design tokens in `docs/ui-specification/index.md`
- Capture component hierarchies, component → API mappings, and existing design tokens
- Note screens missing loading/empty/error states as gaps to close

### Step A7: Persona (If Not Already Clear)

If you've been building for a while, you likely already know your user. Document that knowledge so the AI can reference it.

---

## Phase 2.5: Write Work Items

Before generating tasks, describe **what specific work to do** using work item templates. Work items bridge the gap between your system documentation (what the product is) and task generation (how to build it).

The scaffold ships blank starters in `docs/work-items/`: `TEMPLATE-feature-brief.md`, `TEMPLATE-bug-report.md`, and `TEMPLATE-improvement-proposal.md`. Copy the relevant starter to a new file with the next free ID (e.g., `FEAT-001-short-title.md`) — don't fill the TEMPLATE files in place.

Every work item has a **Status** field. Set the initial value when you create the file — Feature Brief: `Not Started`, Bug Report: `Reported`, Improvement Proposal: `Proposed` — and keep it updated as work progresses (see [`maintenance.md`](maintenance.md) for the full status lifecycles).

### Feature Brief (`docs/work-items/FEAT-XXX-name.md`)

**When:** You want to build a new feature.
**What to fill:** User story, feature-level scope (in/out), acceptance criteria, entity/API/UI impact, edge cases, constraints, traceability.
**Template reference:** `.ai-framework/templates/feature-brief.md`

### Bug Report (`docs/work-items/BUG-XXX-name.md`)

**When:** You need to fix a bug.
**What to fill:** Reproduction steps, expected vs actual behavior, error evidence, environment, impact assessment, traceability.
**Template reference:** `.ai-framework/templates/bug-report.md`

### Improvement Proposal (`docs/work-items/IMP-XXX-name.md`)

**When:** You want to refactor, optimize, or improve code quality.
**What to fill:** Current state + problems, desired state + benefits, risk assessment, success criteria, test coverage baseline, traceability.
**Template reference:** `.ai-framework/templates/improvement-proposal.md`

### ID Convention

- Features: `FEAT-001`, `FEAT-002`, ...
- Bugs: `BUG-001`, `BUG-002`, ...
- Improvements: `IMP-001`, `IMP-002`, ...
- File naming: `docs/work-items/FEAT-001-short-title.md`

> **Tip:** You don't need work items for every small task. For quick, ad-hoc work, the task generation prompts still support inline descriptions as a fallback. But for anything non-trivial, a work item document produces significantly better task breakdowns.

---

## Phase 3: Generate Your First AI Tasks

You've got documentation and work items. Now put them to work.

### Pick a Task Type

| I want to... | Use this prompt template |
|--------------|------------------------|
| Build a new feature | [`.ai-framework/prompts/feature-tasks.md`](../prompts/feature-tasks.md) |
| Fix a bug | [`.ai-framework/prompts/bugfix-tasks.md`](../prompts/bugfix-tasks.md) |
| Refactor existing code | [`.ai-framework/prompts/refactor-tasks.md`](../prompts/refactor-tasks.md) |
| Generate a data model or API spec | [`.ai-framework/prompts/spec-generation.md`](../prompts/spec-generation.md) |
| Generate a UI specification | [`.ai-framework/prompts/ui-spec-generation.md`](../prompts/ui-spec-generation.md) |
| Generate an HTML mockup | [`.ai-framework/prompts/mockup-generation.md`](../prompts/mockup-generation.md) |
| Plan the implementation of a single task | [`.ai-framework/prompts/plan-generation.md`](../prompts/plan-generation.md) |
| Pre-fill templates from ADRs | [`.ai-framework/prompts/compile-adrs.md`](../prompts/compile-adrs.md) |
| Pre-fill design system from DDRs | [`.ai-framework/prompts/compile-ddrs.md`](../prompts/compile-ddrs.md) |

### The Task Pipeline

Task generation is not just chat output — it produces files that feed the next stage:

1. **Generate the task list.** The feature/bugfix/refactor prompts write a task list to `tasks/` — `tasks/FEAT-XXX-tasks.md`, `tasks/BUG-XXX-tasks.md`, or `tasks/IMP-XXX-tasks.md` (for ad-hoc work without a work item: `tasks/adhoc-short-title-tasks.md`).
2. **Validate the task list.** Run `python .ai-framework/tools/validate-tasks.py tasks/<file>.md` and fix every error before planning or implementation. Add `--work-item docs/work-items/<id>-short-title.md` to cross-check the Acceptance Criteria Coverage table (other optional flags: `--root`, `--strict`).
3. **Review the task list (recommended).** In a NEW agent session — one with no generation history in context — run [`review-tasks.md`](../prompts/review-tasks.md) per the CLAUDE.md routing row "Task list review". The reviewer re-runs `python .ai-framework/tools/validate-tasks.py` and `python .ai-framework/tools/validate-specs.py` as ground truth, then judges the tasks against the work item and spec shards, writing its verdict and findings to `tasks/<WORK-ITEM-ID>-review.md`. Recommended for L/XL work items, or when an orchestrator samples multiple candidate task lists — review each validator-clean candidate, then pick or synthesize the best.
4. **Plan each task before implementing.** For each task `T-XXX` in the list, run [`plan-generation.md`](../prompts/plan-generation.md) to produce `plans/plan-T-XXX-short-title.md` — a concrete implementation plan an agent can execute.
5. **Execute under Workflow Enforcement.** The **Workflow Enforcement** section in your project's CLAUDE.md defines how agents move through the pipeline (which workflow each task follows, when mockups or investigation come first, and how status gets updated).

### Assemble Context

Follow [`.ai-framework/guides/context-compilation.md`](context-compilation.md) — the **canonical context-selection reference** — to pick which documents to include based on your task type. A teaser of the most common recipes:

| Task Type | Always Include | Include If Relevant |
|-----------|---------------|---------------------|
| New Feature | Feature Brief + Stakeholder + CLAUDE.md | Data Model, API Spec, UI Spec, Persona, Architecture |
| Bug Fix | Bug Report + CLAUDE.md | Architecture, Data Model, API Spec, UI Spec |
| Refactoring | Improvement Proposal + CLAUDE.md + Architecture | Data Model, Stakeholder |

Spec documents are sharded — wherever a recipe lists Data Model, API Spec, or UI Spec, read that spec's `index.md` plus only the shards named by the work item's impact tables (see the **Retrieval Keys** section of [`context-compilation.md`](context-compilation.md)). `docs/rationale/` files are never included as context.

For the full matrix — including Testing, Integration, Prioritization, UI Mockup, Release Transition, and ADR/DDR Compilation — see [`context-compilation.md`](context-compilation.md).

### Generate Tasks

#### AI agents (Claude Code, etc.)

1. Read the required files listed in the CLAUDE.md routing table for your task type
2. Read the prompt template from `.ai-framework/prompts/` — follow its **Guidance**, use the **Output Format** section as the deliverable structure, and apply the **Constraints** and **Post-Generation Checklist**
3. Generate the deliverable directly, using the file contents as context — no XML assembly needed — and write it to its home per the artifact map below (e.g., task lists to `tasks/`, plans to `plans/`)

#### Chat workflows (manual copy-paste)

1. Open the relevant prompt template from `.ai-framework/prompts/`
2. Copy the XML template structure
3. Fill in the `<context>` sections by pasting from your documentation
4. Fill in the task-specific details (feature description, bug report, refactoring scope)
5. Paste into Claude and iterate

<details>
<summary>Example — generating feature tasks via chat workflow</summary>

```xml
<task-generation-request>
  <context>
    <feature-brief>
      [Paste the full work item from docs/work-items/FEAT-XXX-short-title.md]
    </feature-brief>
    <stakeholder-definition>
      [Paste relevant sections from docs/stakeholder-definition.md]
    </stakeholder-definition>
    <code-conventions>
      [Paste from CLAUDE.md]
    </code-conventions>
    <data-model>
      [Paste docs/data-model/index.md + the entity shards named by the work item's impact table]
    </data-model>
    <api-spec>
      [Paste docs/api-spec/index.md + the endpoint shards named by the impact table]
    </api-spec>
  </context>

  <task-type>New Feature</task-type>
  <request>
    Add user authentication with email/password login
  </request>
</task-generation-request>
```

</details>

The AI will return structured tasks with IDs, descriptions, acceptance criteria, complexity estimates, and file lists. Save the result to `tasks/` (e.g., `tasks/FEAT-XXX-tasks.md`) so it can feed the planning stage, then validate it — and preferably review it in a fresh session (Task Pipeline steps 2-3) — before generating plans.

---

## Where Things Live

Every generated artifact has a fixed home. Agents write to these locations; humans look here first.

| Artifact | Location | Naming |
|----------|----------|--------|
| Work items | `docs/work-items/` | `FEAT-XXX-short-title.md`, `BUG-XXX-short-title.md`, `IMP-XXX-short-title.md` |
| Work item starters | `docs/work-items/` | `TEMPLATE-feature-brief.md`, `TEMPLATE-bug-report.md`, `TEMPLATE-improvement-proposal.md` (copy, don't fill in place) |
| Task lists | `tasks/` | `FEAT-XXX-tasks.md`, `BUG-XXX-tasks.md`, `IMP-XXX-tasks.md`; ad-hoc work: `adhoc-short-title-tasks.md` |
| Implementation plans | `plans/` | `plan-T-XXX-short-title.md` |
| HTML mockups | `mockups/` | `T-XXX-screen-name.html` |
| Component Examples (DDR output) | `docs/` | `component-examples.md` |
| Data model | `docs/data-model/` | `index.md` + `entities/<entity>.md` (kebab-case, singular) |
| API spec | `docs/api-spec/` | `index.md` + `endpoints/<resource>.md` (matches route segment, plural) |
| UI spec | `docs/ui-specification/` | `index.md` + `screens/<screen>.md` + `components.md` |
| Rationale | `docs/rationale/` | `<topic>.md` — narrative/history linked from spec docs; **never loaded as AI context** |
| System docs | `docs/` | `stakeholder-definition.md`, `ARCHITECTURE.md`, `personas/primary-user.md` |
| Code conventions | project root | `CLAUDE.md` |

---

## Phase 4: Maintain

Documentation drifts. Keep it alive.

**Review cadence:**

| Document | Review When |
|----------|-------------|
| **CLAUDE.md** | After establishing new patterns or conventions |
| **Stakeholder Definition** | When a feature ships or strategy changes |
| **Architecture** | After adding/removing components or services |
| **Persona** | Quarterly, or after significant user feedback |
| **Data Model** | After adding/changing entities, fields, or relationships |
| **API Specification** | After adding/changing endpoints or DTO shapes |
| **UI Specification** | After adding/changing screens, components, or design tokens |
| **HTML Mockups** | After design token changes, screen layout changes, or stakeholder feedback |
| **Work Items** | Update status when tasks are generated, in progress, or completed |

**Key rule:** If a task touches a document's area of concern, update the document in the same PR.

**Freshness stamps:** every spec shard, every spec `index.md`, and `ARCHITECTURE.md` carries a "Last verified against code" stamp directly under its H1. Update it whenever you edit a file or verify it against the code — stale stamps (missing or older than 30 days) force agents to re-verify the shard before trusting it. See the maintenance guide for the stamp rules.

For full maintenance guidance, see [`.ai-framework/guides/maintenance.md`](maintenance.md).

---

## Quick Reference

```
1.   Copy scaffold into project                        →  Phase 1
1.1  (Optional) Compile ADRs → pre-fill conventions    →  Phase 1 (Step 1.1)
1.2  (Optional) Compile DDRs → pre-fill design system  →  Phase 1 (Step 1.2)
2.   Fill core templates (~70 min)                     →  Phase 2 (Steps 1-4)
3.   Generate data model + API spec (40 min)           →  Phase 2 (Steps 5-6)
4.   Generate UI specification (20 min)                →  Phase 2 (Step 7)
4.5  (Optional) Create HTML mockups for key screens    →  Phase 2 (Step 7.5)
5.   Write work items (Feature/Bug/Improvement)        →  Phase 2.5
6.   Pick prompt template + add context                →  Phase 3
7.   Generate tasks → tasks/, validate, review, plans/ →  Phase 3
8.   Keep docs updated                                 →  Phase 4
```

**Stuck?** Check the full templates in `.ai-framework/templates/` for detailed guidance on any section. Each scaffold file is a simplified version of its corresponding template.
