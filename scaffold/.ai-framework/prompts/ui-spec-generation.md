# UI Spec Generation Prompt

## Purpose

Generate a UI Specification document from existing strategic, architectural, and specification documentation. Use this prompt when you have the stakeholder definition, architecture, API spec, and code conventions, and need to derive the screen layouts, component hierarchy, design tokens, and interaction patterns before generating frontend feature tasks.

**When to use**: After completing the API Specification and before generating feature tasks. This fills the gap between "what data is available" and "what the UI looks like." (If applicable — skip for CLI tools, libraries, or headless services with no UI.)

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the context files listed in the project CLAUDE.md routing table for "UI spec generation", follow the **Guidance**, **Output Format**, and **Constraints** sections below, and **write the output files** (sharded): `docs/ui-specification/index.md`, one `docs/ui-specification/screens/<screen>.md` per screen, and `docs/ui-specification/components.md`.
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the **Chat Workflow Template (XML)** appendix — paste your documentation into the `<context>` sections and include the Guidance, Output Format, and Constraints sections of this prompt alongside it.

---

## Required Context

Context selection follows the canonical matrix — see `guides/context-compilation.md` (for manual assembly) or the project CLAUDE.md routing table (for agents).

Prompt-specific notes:

- **All four required documents (Stakeholder Definition, Architecture, API Specification, CLAUDE.md) should be included in full.** The UI spec needs the complete picture to derive a comprehensive screen inventory and component hierarchy.
- **Data Model** is recommended — entity definitions inform display fields, relationships inform navigation, enums inform dropdown/filter options.
- **Persona** is optional — include it for interaction complexity, information density, and onboarding decisions.
- **Compiled DDR output** (Design System tables, State Patterns, Responsive Breakpoints) is recommended if DDRs were compiled — use compiled values directly instead of deriving them.
- Read the output format template from `.ai-framework/templates/ui-specification.md` for section structure.

---

## Guidance

### Prerequisites

Before generating a UI spec, you should have:
1. **Stakeholder Definition** — for user flows and scope
2. **Architecture** — for module structure
3. **Data Model** — for entity definitions (generate first if missing)
4. **API Specification** — for endpoint definitions (generate first if missing)
5. **CLAUDE.md** — for frontend conventions

### Deriving Screens from User Flows

1. Read the Scope Lock — every in-scope feature implies at least one screen
2. Read the User Flow — each phase maps to one or more screens
3. For each screen, identify:
   - What data it displays (from API Spec response DTOs)
   - What actions the user can take (from API Spec request endpoints)
   - What navigation leads to/from it (from user flow transitions)

### Deriving Components from Entities

1. Each entity typically has:
   - A **list component** (table or card grid) — maps to list endpoint
   - A **detail component** (view/edit form) — maps to get/update endpoints
   - A **create component** (dialog or form) — maps to create endpoint
   - A **card component** (compact display) — used in lists, boards, and references

2. Cross-entity relationships create:
   - **Nested lists** (e.g., project → task list within project detail)
   - **Selection components** (e.g., assignee selector referencing users)
   - **Navigation patterns** (e.g., click task card → task detail)

### Deriving Interactions from Endpoints

Map each API endpoint to a user interaction:

| Endpoint Pattern | Typical Interaction |
|-----------------|-------------------|
| GET /api/resources | Page load, filter change, search |
| GET /api/resources/:id | Click item to view detail |
| POST /api/resources | Submit create form/dialog |
| PUT/PATCH /api/resources/:id | Submit edit form, inline edit, drag-drop |
| DELETE /api/resources/:id | Click delete with confirmation dialog |
| POST /api/resources/:id/action | Click action button (assign, move, etc.) |

### Deriving Design Tokens

1. **If DDRs were compiled**: Use the compiled Design System values directly for colors, typography, spacing, state patterns, and responsive breakpoints. Do not re-derive or invent new values — the DDR compilation is the authoritative source.
2. If the project has brand guidelines (but no DDR compilation), extract colors, fonts, and spacing
3. If using a component library [e.g., Angular Material], document the theme configuration
4. Map semantic colors (primary, error, success) to specific hex values
5. Define typography scale based on the heading hierarchy needed

### States for Every Screen

Every screen specification MUST include:

| State | What to Define |
|-------|---------------|
| **Default** | What the screen looks like with data loaded |
| **Loading** | What shows while data is being fetched (skeleton, spinner, shimmer) |
| **Empty** | What shows when there's no data yet (illustration, message, CTA) |
| **Error** | What shows when data fetch fails (error message, retry button) |

### Review and Validate

After generating, validate against the source docs:
- Does every user flow step have a screen?
- Does every screen map to at least one API endpoint?
- Does every entity have a display component?
- Are all states (loading, empty, error) specified for every screen?
- Are the component library and styling constraints from CLAUDE.md respected?

---

## Output Format

Write the generated spec as a **sharded document set** at the canonical location **`docs/ui-specification/`**, following the template structure from `.ai-framework/templates/ui-specification.md`:

**`docs/ui-specification/index.md`** (cross-cutting content only):
1. **Overview** — UI summary + Key UI Decisions table
2. **Design System** — 2.1 Brand Colors, 2.2 Typography Scale, 2.3 Spacing Scale, 2.4 Component Library, 2.5 State Patterns, 2.6 Responsive Breakpoints
3. **Screen Inventory** — table of all screens with routes, auth, layouts
4. **Shared Layouts** — app shell structure, public layout
5. **Usage Notes for AI Task Generation**
6. **Changelog**

**`docs/ui-specification/screens/<screen>.md`** — **one screen per file**, each with:
- Layout sketch (ASCII)
- Component hierarchy (tree)
- Component → API mapping (table)
- States: default, loading, empty, error
- User interactions: action → result → API call

**`docs/ui-specification/components.md`** — the shared components inventory (single file): reusable components with inputs/outputs/variants.

**Shard naming (mechanical, kebab-case):** screen "Project Board" → `screens/project-board.md`.

**Freshness stamp:** every generated file (index, every screen shard, and components.md) starts with this line directly under its H1 — fill in today's date and the current commit hash:

```
> **Last verified against code:** YYYY-MM-DD (commit `abc1234`)
```

Derive all content from the context documents provided:
- Screens from stakeholder user flows and scope lock
- Component hierarchy from architecture modules and API endpoint groupings
- Design tokens from project branding and conventions (or compiled DDR output)
- Interaction patterns from user flow steps and API endpoints
- States (loading, empty, error) for every screen and component

---

## Constraints

- Follow all conventions from CLAUDE.md exactly — use the component framework, component library, and styling system declared there [e.g., Angular standalone components + Angular Material + Tailwind]
- Use the component library declared in CLAUDE.md — do not define custom UI primitives when the library provides an equivalent
- Use the styling system declared in CLAUDE.md for all layout and spacing — do not create ad-hoc component-scoped styles outside its conventions
- Respect module boundaries from the architecture document — components belong to the module whose data they primarily display
- Only include screens for features within the scope lock — do not invent screens or features beyond it
- Every screen must map to at least one API endpoint
- Every entity with a list endpoint must have a corresponding list screen or embedded list component
- Use the response envelope format from CLAUDE.md when describing what data components receive

---

## Post-Generation Checklist

After the AI generates a UI spec document set, verify:

- [ ] Every generated file (index.md, every screen shard, components.md) starts with the freshness stamp directly under its H1, filled with today's date and the current commit
- [ ] Every user flow phase from the stakeholder definition has at least one screen
- [ ] Every screen in the Screen Inventory (index.md) has its own shard in `screens/` (kebab-case filename)
- [ ] Every screen specification includes all 4 states (default, loading, empty, error)
- [ ] Every screen has a component hierarchy tree
- [ ] Every screen and component maps to at least one API endpoint from the API spec
- [ ] Every entity from the data model has a display component (list, detail, or card)
- [ ] Every interaction is specific (not vague) — each maps to a UI element, result, and API call
- [ ] Component hierarchy uses the conventions declared in CLAUDE.md [e.g., Angular standalone components, no NgModules]
- [ ] All UI uses the component library and styling system declared in CLAUDE.md (no custom primitives or ad-hoc styles)
- [ ] Shared components used in 2+ screens are documented in `components.md`
- [ ] Design tokens (colors, typography, spacing) are fully defined
- [ ] All component-library components used are listed with customization notes
- [ ] Routes follow a consistent pattern and match the screen inventory
- [ ] No screens exist for features outside the scope lock
- [ ] Layout sketches match the shared layout definitions in index.md's Shared Layouts section (Section 4)

---

## Chat Workflow Template (XML)

Copy this skeleton, paste your documentation into the `<context>` sections, and submit together with the Guidance, Output Format, and Constraints sections above.

```xml
<ui-spec-generation-request>

<context>

<stakeholder-definition>
<!-- REQUIRED: User flows drive screen inventory — every flow step maps to a screen.
     Scope lock determines which screens exist. Philosophy shapes interaction patterns. -->
[Paste full stakeholder-definition.md content]
</stakeholder-definition>

<architecture>
<!-- REQUIRED: Component structure, real-time capabilities, and module boundaries
     inform the component hierarchy and data flow patterns. -->
[Paste full ARCHITECTURE.md content]
</architecture>

<api-spec>
<!-- REQUIRED: Endpoints map directly to component data needs.
     DTOs inform what fields each component displays. -->
[Paste docs/api-spec/index.md + all endpoint shards (docs/api-spec/endpoints/)]
</api-spec>

<data-model>
<!-- RECOMMENDED: Entity definitions inform display fields, relationships inform
     navigation patterns, enums inform dropdown/filter options. -->
[Paste docs/data-model/index.md + relevant entity shards (docs/data-model/entities/)]
</data-model>

<code-conventions>
<!-- REQUIRED: Frontend stack conventions (component framework, component library,
     styling system), naming conventions, and frontend patterns directly
     constrain component implementation. -->
[Paste full CLAUDE.md content]
</code-conventions>

<persona>
<!-- OPTIONAL: User expertise level and pain points inform interaction complexity,
     information density, and onboarding patterns. -->
[Paste persona details if available]
</persona>

<design-decisions>
<!-- RECOMMENDED: If DDRs were compiled, include the compiled Design System output.
     This provides pre-defined colors, typography, spacing, component patterns,
     state patterns, and responsive breakpoints.
     Use compiled DDR values directly — do not re-derive or override them. -->
[Paste compiled DDR output (Design System tables, State Patterns, Responsive Breakpoints), if available]
</design-decisions>

</context>

<spec-type>UI Specification</spec-type>

<request>
Generate a complete UI Specification document for this project,
following the Guidance, Output Format, and Constraints from prompts/ui-spec-generation.md.
</request>

</ui-spec-generation-request>
```

---

## Example

Generating a UI Spec for a project management app (this example project declares an Angular stack in its CLAUDE.md — substitute your own):

```xml
<ui-spec-generation-request>

<context>

<stakeholder-definition>
## Executive Summary
Internal project management web application with Kanban, List, and Gantt views.

## User Flow
Phase 1: Login via Google OAuth
Phase 2: Select or create project, manage members
Phase 3: Create tasks, assign to members, set status/priority/dates
Phase 4: View tasks in Kanban (drag columns), List (sortable table), Gantt (timeline)
Phase 5: Collaborate via comments and file attachments on tasks

## Scope Lock (V1)
Included: Projects, Tasks (Kanban/List/Gantt), Team members, Labels, Comments
Excluded: Time tracking, Billing, External integrations, Mobile app
</stakeholder-definition>

<architecture>
## Frontend
- Angular 20+ SPA with standalone components
- Angular Material for UI components
- Tailwind CSS for styling
- Route-based lazy loading

## Modules
- Auth → Google OAuth, JWT
- Users → profiles, roles
- Projects → projects, membership
- Tasks → tasks, labels, comments, attachments
</architecture>

<api-spec>
## Projects Module
- GET /api/projects — List user's projects
- POST /api/projects — Create project
- GET /api/projects/:id — Get project detail
- PATCH /api/projects/:id — Update project

## Tasks Module
- GET /api/projects/:id/tasks — List tasks (with filters)
- POST /api/projects/:id/tasks — Create task
- GET /api/tasks/:id — Get task detail
- PATCH /api/tasks/:id — Update task (status, assignee, etc.)
- DELETE /api/tasks/:id — Soft-delete task
</api-spec>

<code-conventions>
## Frontend Conventions
- Angular standalone components (no NgModules)
- Angular Material for all UI components
- Tailwind CSS for all styling
- TypeScript strict mode — no `any`
- Signals where appropriate
</code-conventions>

</context>

<spec-type>UI Specification</spec-type>

<request>
Generate a complete UI Specification for this project management application.
Derive all screens from the user flow phases.
Map each screen to the appropriate API endpoints.
</request>

</ui-spec-generation-request>
```

**Output:** `docs/ui-specification/index.md` + one `screens/<screen>.md` per screen (e.g., `screens/login.md`, `screens/project-board.md`) + `components.md` — a complete sharded UI specification following the `ui-specification.md` template structure, every file stamped `> **Last verified against code:** ...` directly under its H1.
