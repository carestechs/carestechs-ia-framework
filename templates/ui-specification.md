# UI Specification Template

> **Purpose**: Document the screen layouts, component hierarchy, design tokens, interaction patterns, and state management for every user-facing screen. This sits between the API Specification (what data is available) and Feature Tasks (what to implement), giving AI the structural understanding needed to generate frontend tasks with consistent detail — including loading states, empty states, responsive behavior, and accessibility.

> **Context budget note:** This document is loaded into AI context. Keep it contract-style —
> tables, schemas, rules, one example each. Move narrative and history to `docs/rationale/`
> and link it; rationale files are never loaded by default.

---

## Directory Layout

The UI specification is a **sharded document set**, not a single file. Cross-cutting content (decisions, Design System, inventory, layouts) lives in `index.md`; every screen lives in its own shard; shared components live in a single `components.md`. Work items name screens in their impact tables, and task generation loads `index.md` plus only the named screen shards — shard boundaries are retrieval boundaries.

```
docs/ui-specification/
  index.md                  # Key UI Decisions, Design System (2.1 Brand Colors … 2.5 State
                            # Patterns, 2.6 Responsive Breakpoints), Usage Notes, Changelog
  screens/<screen>.md       # ONE screen per file: layout sketch, component hierarchy,
                            # states (default/loading/empty/error), interactions, API calls
  components.md             # shared components inventory (single file)
```

Rules:

- **One screen per shard.** Never fold two screens into one file, and never put screen specifications in `index.md`.
- **Shards are self-sufficient with the index.** Loading `index.md` + one screen shard must give everything needed to build that screen — the shard references the Design System and Shared Layouts by section number rather than restating them.
- **Shared components live in `components.md`** — a single inventory file, loaded whenever a task touches a shared component. Screen-specific components stay in the screen's shard (component hierarchy).

---

## Index File (`docs/ui-specification/index.md`)

Everything from here down to "Screen Shard" defines the contents of `index.md`. Start the file with its own H1 and the freshness stamp directly beneath it:

```
# UI Specification — [Product Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->
```

## 1. Overview

### 1.1 UI Summary

[One paragraph describing the application's user interface at a high level — what type of app it is (SPA, PWA, etc.), how many major screens exist, what the primary interaction paradigm is (form-heavy, drag-and-drop, conversational, etc.), and any key UI decisions.]

### 1.2 Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Design system / component library] | [e.g., Angular Material] | [Why — consistency, accessibility, speed] |
| [Layout pattern] | [e.g., Sidebar + main content] | [Why — navigation density, user workflows] |
| [Responsive strategy] | [e.g., Desktop-first, collapse sidebar on tablet] | [Why — primary device is desktop] |
| [Accessibility standard] | [e.g., WCAG 2.1 AA] | [Why — compliance, inclusive design] |
| [State management] | [e.g., Angular signals + services] | [Why — simplicity, reactivity] |
| [Styling approach] | [e.g., Tailwind CSS utility classes, no component CSS] | [Why — consistency, rapid iteration] |
| [Icon set] | [e.g., Material Icons] | [Why — matches component library] |

---

## 2. Design System

> *Keep the 2.1–2.6 numbering exactly as below — DDR compilation (`compile-ddrs.md`) writes into these numbered sections.*

### 2.1 Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | [#XXXXXX] | [Primary actions, active states, links] |
| `primary-light` | [#XXXXXX] | [Hover states, backgrounds] |
| `primary-dark` | [#XXXXXX] | [Active/pressed states] |
| `secondary` | [#XXXXXX] | [Secondary actions, accents] |
| `neutral-50` | [#XXXXXX] | [Backgrounds] |
| `neutral-100` | [#XXXXXX] | [Card backgrounds, borders] |
| `neutral-200` | [#XXXXXX] | [Dividers, subtle borders] |
| `neutral-700` | [#XXXXXX] | [Secondary text] |
| `neutral-900` | [#XXXXXX] | [Primary text] |
| `success` | [#XXXXXX] | [Success states, confirmations] |
| `warning` | [#XXXXXX] | [Warning states, alerts] |
| `error` | [#XXXXXX] | [Error states, destructive actions] |
| `info` | [#XXXXXX] | [Informational messages] |

### 2.2 Typography Scale

| Level | Size | Weight | Font Family | Usage |
|-------|------|--------|-------------|-------|
| `h1` | [2rem / 32px] | [700] | [Font name] | [Page titles] |
| `h2` | [1.5rem / 24px] | [600] | [Font name] | [Section headings] |
| `h3` | [1.25rem / 20px] | [600] | [Font name] | [Card titles, subsections] |
| `body` | [1rem / 16px] | [400] | [Font name] | [Body text, descriptions] |
| `body-sm` | [0.875rem / 14px] | [400] | [Font name] | [Secondary text, labels] |
| `caption` | [0.75rem / 12px] | [400] | [Font name] | [Timestamps, metadata] |

### 2.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | [0.25rem / 4px] | [Tight internal padding] |
| `space-2` | [0.5rem / 8px] | [Standard internal padding] |
| `space-3` | [0.75rem / 12px] | [Component gaps] |
| `space-4` | [1rem / 16px] | [Section padding, card padding] |
| `space-6` | [1.5rem / 24px] | [Section margins] |
| `space-8` | [2rem / 32px] | [Page-level padding] |

> **Base unit**: [X]rem. All spacing is a multiple of the base unit. Use the spacing utilities of the styling system declared in CLAUDE.md [e.g., Tailwind classes `p-2`, `gap-4`, `mt-6`] mapped to these values.

### 2.4 Component Library

> **Note**: If DDRs were compiled using `compile-ddrs.md`, the rows below are pre-filled from component-category DDRs. Only add project-specific customizations.

**Library**: [e.g., Angular Material]
**Version**: [e.g., 20.x]

| UI Need | Component | Customization Notes |
|---------|-----------|-------------------|
| [Buttons] | [mat-button, mat-raised-button, mat-icon-button] | [Color overrides with brand tokens] |
| [Forms] | [mat-form-field, mat-input, mat-select] | [Outline appearance by default] |
| [Tables] | [mat-table with mat-sort and mat-paginator] | [Sticky header, row hover states] |
| [Dialogs] | [mat-dialog] | [Standard width, custom close button] |
| [Menus] | [mat-menu] | [Context menus for right-click actions] |
| [Snackbar] | [mat-snackbar] | [Success/error variants] |
| [Drag & Drop] | [CDK drag-drop] | [For Kanban board columns] |
| [Tabs] | [mat-tab-group] | [For view switching] |

### 2.5 State Patterns

> *Defines the standard UI patterns for loading, empty, error, and disabled states across the application. If DDRs were compiled, these are pre-filled from states-category DDRs.*

| State | Pattern | Key Constraints | Example Reference |
|-------|---------|----------------|-------------------|
| Loading (skeleton) | [e.g., Skeleton placeholders matching content layout, animate-pulse] | [e.g., Match real content dimensions; show for at least 200ms to avoid flicker] | [See Component Examples Appendix or describe inline] |
| Loading (action) | [e.g., Inline spinner for button/form actions] | [e.g., Use for action feedback only, not page loads; include sr-only text] | [See Component Examples Appendix or describe inline] |
| Empty | [e.g., Centered heading + description + CTA button] | [e.g., Always include heading, description, and actionable CTA; never blank] | [See Component Examples Appendix or describe inline] |
| Error (inline) | [e.g., Error banner with retry button] | [e.g., Human-readable message; include retry for network errors] | [See Component Examples Appendix or describe inline] |
| Error (full-page) | [e.g., Full-page error with illustration + message + home link] | [e.g., Never show raw stack traces; provide navigation escape] | [See Component Examples Appendix or describe inline] |
| Disabled | [e.g., opacity-50 + cursor-not-allowed] | [e.g., Use opacity for disabled states, not gray colors] | [Describe inline] |

### 2.6 Responsive Breakpoints

> *Defines the breakpoint system and responsive strategy. If DDRs were compiled, these are pre-filled from responsive-category DDRs.*

| Breakpoint | Width | Utility Prefix [e.g., Tailwind] | Primary Use |
|------------|-------|--------------------------------|-------------|
| Mobile | [< 640px] | (base) | [Single column, stacked layout, full-width cards] |
| Tablet | [640px - 1023px] | [sm:, md:] | [Collapsed sidebar, 2-column grid where appropriate] |
| Desktop | [1024px - 1279px] | [lg:] | [Full sidebar, multi-column layouts] |
| Large Desktop | [1280px+] | [xl:, 2xl:] | [Max-width content, additional whitespace] |

**Responsive Strategy**: [Mobile-first / Desktop-first] — [One sentence explaining the choice and its implications for how responsive utility classes are authored]

---

## 3. Screen Inventory

> *Every screen in the application listed with its route, auth requirement, parent layout, and primary user action. This table doubles as the shard directory: every screen listed here must have a shard at `screens/<screen>.md` (see Naming Rule at the bottom of this template).*

| Screen Name | Route | Auth Required | Parent Layout | Shard | Primary User Action |
|-------------|-------|---------------|---------------|-------|-------------------|
| [Login] | [/login] | [No] | [Public layout] | [`screens/login.md`] | [Authenticate via OAuth] |
| [Dashboard] | [/dashboard] | [Yes] | [App shell] | [`screens/dashboard.md`] | [Select a project] |
| [Project Board] | [/projects/:id/board] | [Yes] | [App shell] | [`screens/project-board.md`] | [Move tasks between columns] |
| [Task Detail] | [/projects/:id/tasks/:taskId] | [Yes] | [App shell (overlay/panel)] | [`screens/task-detail.md`] | [Edit task fields] |
| [...] | [...] | [...] | [...] | [...] | [...] |

---

## 4. Shared Layouts

### 4.1 App Shell (Authenticated)

[Describe the overall layout structure for authenticated users — header, sidebar, main content area, footer (if any).]

```
┌──────────────────────────────────────────────────────────┐
│  Header: [logo, search, user avatar/menu]                │
├──────────┬───────────────────────────────────────────────┤
│ Sidebar  │  Main Content Area                            │
│          │                                               │
│ [nav]    │  [Page content rendered here via router]      │
│ [items]  │                                               │
│          │                                               │
│          │                                               │
├──────────┴───────────────────────────────────────────────┤
│  Footer (optional): [status, version]                    │
└──────────────────────────────────────────────────────────┘
```

**Sidebar behavior**:
- [Desktop: always visible, fixed width (e.g., 260px)]
- [Tablet: collapsible, toggle via hamburger icon]
- [Mobile: overlay drawer]

**Header contents**:
- [Left: app logo + project name]
- [Center: global search]
- [Right: notifications icon, user avatar with dropdown menu]

### 4.2 Public Layout (Unauthenticated)

[Describe the layout for public/login pages — typically simpler, centered content.]

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│              [Centered content card]                     │
│              [Logo + login form]                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Usage Notes for AI Task Generation

### When generating frontend tasks, use this document set to:

1. **Load only what's referenced** — Read `index.md` plus ONLY the screen shards named by the work item's impact tables (mapped via the Naming Rule), plus `components.md` when a shared component is involved. Do not read the whole `screens/` directory.
2. **Derive component structure** — Use the screen shard's Component Hierarchy to know exactly which components to create or modify for each screen.
3. **Map data requirements** — Use the screen shard's Component → API Mapping to know which service calls each component needs.
4. **Specify all states** — Every component task should include handling for loading, empty, and error states as defined in the screen shard's States table.
5. **Define interactions precisely** — Use the screen shard's User Interactions table to specify exact behavior, not vague descriptions.
6. **Reuse shared components** — Check `components.md` before creating new components. If a shared component exists, use it.
7. **Follow the design system** — Reference Section 2 for colors, typography, spacing, and component library usage.
8. **Respect layouts** — Reference Section 4 for app shell structure. New screens must fit within the defined layouts.
9. **Use state patterns consistently** — Reference Section 2.5 for the standard loading, empty, error, and disabled patterns. Every screen must use these patterns — do not invent new loading or error UIs.
10. **Use defined breakpoints** — Reference Section 2.6 for the responsive breakpoints and strategy. Follow the mobile-first or desktop-first approach consistently across all screens.
11. **Reference component examples** — If DDRs were compiled with a Component Examples Appendix, use those HTML markup patterns as the starting point for mockups and implementations. DDR examples take precedence over AI invention.

### Rules:

- Every frontend task must reference a specific screen shard (`screens/<screen>.md`)
- Every component must handle all 4 states (default, loading, empty, error) unless explicitly noted otherwise
- Use the component library from Section 2.4 — do not build custom primitives
- Use utility classes from the styling system declared in CLAUDE.md [e.g., Tailwind] for layout and spacing — do not create per-component CSS
- Shared components (`components.md`) must be used instead of duplicating UI across screens
- New screens: create a new shard at `screens/<screen>.md`, add a Screen Inventory row (Section 3), and record the change in the Changelog

---

## Changelog

> *Lives at the very bottom of `index.md` and records changes across the whole `docs/ui-specification/` set — screen shard and `components.md` edits included. Every edited or verified file also gets its freshness stamp updated.*

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |

---

## Screen Shard (`docs/ui-specification/screens/<screen>.md`)

One file per screen. Every shard follows this skeleton — reuse it verbatim when adding a new screen:

````markdown
# Screen: [Screen Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

**Route**: [/path]
**Auth**: [Required / Public]
**Layout**: [App shell / Public — see `index.md` Section 4]

## Layout Sketch

```
[ASCII diagram or description of the screen layout]
```

## Component Hierarchy

```
[ScreenName]Page
├── [ComponentA]
│   ├── [SubComponentA1]
│   └── [SubComponentA2]
├── [ComponentB]
│   └── [SubComponentB1]
└── [ComponentC]
```

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/<resource>.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| [ComponentA] | [List of items] | [GET /api/items?filter=X] | [On page load] |
| [ComponentB] | [Item details] | [GET /api/items/:id] | [On item select] |
| [ComponentC] | [Create item] | [POST /api/items] | [On form submit] |

## States

<!-- Use the standard patterns from index.md Section 2.5 — do not invent new loading/error UIs -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | [Data loaded, items exist] | [Show list/grid/board with data] |
| **Loading** | [API request in flight] | [Show skeleton loaders / spinner] |
| **Empty** | [No items match filters or none exist] | [Show illustration + "No items yet" message + CTA to create first item] |
| **Error** | [API request failed] | [Show error banner with retry button] |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| [Click create button] | [FAB / toolbar button] | [Open create dialog] | [None until submit] |
| [Submit form] | [Save button in dialog] | [Close dialog, add item to list] | [POST /api/items] |
| [Click item] | [List row / card] | [Navigate to detail or open side panel] | [GET /api/items/:id] |
| [Drag item] | [Kanban card] | [Move to new column, update status] | [PATCH /api/items/:id] |
````

---

## Shared Components File (`docs/ui-specification/components.md`)

A single file inventorying every reusable component used across multiple screens, with inputs, outputs, and visual variants. Skeleton:

````markdown
# Shared Components

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> *Reusable components used across multiple screens. Screen-specific components live in the screen's shard (component hierarchy), not here.*

## [Component Name]

**Used in**: [Screen A, Screen B, Screen C]
**Description**: [One sentence — what this component renders and its purpose]

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| [item] | Input | [ItemDto] | [The data to display] |
| [compact] | Input | [boolean] | [Whether to use compact layout] |
| [clicked] | Output | [event\<string\> — e.g., Angular `EventEmitter<string>`, React callback prop] | [Emitted when user clicks, payload is item ID] |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| [Default] | [Standard display in lists] | [Full size, all fields visible] |
| [Compact] | [Sidebar, dropdowns] | [Smaller, only name + avatar shown] |
| [Selected] | [Currently active item] | [Highlighted border, accent background] |

<!-- Repeat one ## block per shared component -->
````

---

## Naming Rule

Screen shard names derive **mechanically** from screen names — kebab-case:

| Screen Name | Shard Path |
|-------------|-----------|
| "Project Board" | `docs/ui-specification/screens/project-board.md` |
| "Task Detail" | `docs/ui-specification/screens/task-detail.md` |
| "Label Management Dialog" | `docs/ui-specification/screens/label-management-dialog.md` |

Shared components do not get shards — they all live in `docs/ui-specification/components.md`.

Never deviate from this mapping: work-item impact tables use screen names as retrieval keys, and task generation resolves `screen name → shard path` without guessing.
