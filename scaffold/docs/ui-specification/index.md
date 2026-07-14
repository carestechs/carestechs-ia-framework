# UI Specification — [Product Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

> *Sharded document set: cross-cutting content lives in this index; every screen has its own shard at `screens/<screen>.md` (kebab-case — e.g., screen "Project Board" → `screens/project-board.md`); shared components live in `components.md`. Copy `screens/TEMPLATE-screen.md` to add a screen. Work items name screens as retrieval keys — task generation loads this index plus only the named shards.*

## 1. Overview

### 1.1 UI Summary

<!-- TODO: Describe the UI at a high level — what type of app, how many screens, primary interaction paradigm -->

### 1.2 Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Component library --> | <!-- e.g., Angular Material --> | <!-- e.g., Consistency, accessibility --> |
| <!-- e.g., Layout pattern --> | <!-- e.g., Sidebar + main content --> | <!-- e.g., Navigation density --> |
| <!-- e.g., Responsive strategy --> | <!-- e.g., Desktop-first --> | <!-- e.g., Primary device is desktop --> |
| <!-- e.g., Accessibility standard --> | <!-- e.g., WCAG 2.1 AA --> | <!-- e.g., Compliance, inclusive design --> |
| <!-- e.g., State management --> | <!-- e.g., Signals + services --> | <!-- e.g., Simplicity, reactivity --> |
| <!-- e.g., Styling approach --> | <!-- e.g., Tailwind CSS --> | <!-- e.g., Consistency, rapid iteration --> |
| <!-- e.g., Icon set --> | <!-- e.g., Material Icons --> | <!-- e.g., Matches component library --> |

## 2. Design System

<!-- Keep the 2.1–2.6 numbering — DDR compilation (compile-ddrs.md) writes into these numbered sections. -->

### 2.1 Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | <!-- #XXXXXX --> | <!-- Primary actions, active states --> |
| `secondary` | <!-- #XXXXXX --> | <!-- Secondary actions, accents --> |
| `neutral-50` | <!-- #XXXXXX --> | <!-- Backgrounds --> |
| `neutral-900` | <!-- #XXXXXX --> | <!-- Primary text --> |
| `success` | <!-- #XXXXXX --> | <!-- Success states --> |
| `warning` | <!-- #XXXXXX --> | <!-- Warning states --> |
| `error` | <!-- #XXXXXX --> | <!-- Error states --> |

### 2.2 Typography Scale

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| `h1` | <!-- 2rem --> | <!-- 700 --> | <!-- Page titles --> |
| `h2` | <!-- 1.5rem --> | <!-- 600 --> | <!-- Section headings --> |
| `body` | <!-- 1rem --> | <!-- 400 --> | <!-- Body text --> |
| `caption` | <!-- 0.75rem --> | <!-- 400 --> | <!-- Timestamps, metadata --> |

### 2.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-2` | <!-- 0.5rem --> | <!-- Standard internal padding --> |
| `space-4` | <!-- 1rem --> | <!-- Section padding --> |
| `space-8` | <!-- 2rem --> | <!-- Page-level padding --> |

### 2.4 Component Library

<!-- TODO: List the UI components you'll use -->

| UI Need | Component | Notes |
|---------|-----------|-------|
| <!-- Buttons --> | <!-- e.g., mat-button --> | <!-- Color overrides --> |
| <!-- Forms --> | <!-- e.g., mat-form-field --> | <!-- Outline appearance --> |
| <!-- Tables --> | <!-- e.g., mat-table --> | <!-- Sticky header --> |

### 2.5 State Patterns

<!-- TODO: Define standard UI patterns for loading, empty, error, and disabled states.
     If DDRs were compiled, this section is pre-filled from states-category DDRs. -->

| State | Pattern | Key Constraints | Example Reference |
|-------|---------|----------------|-------------------|
| Loading (skeleton) | <!-- e.g., Skeleton placeholders with animate-pulse --> | <!-- e.g., Match real content dimensions --> | <!-- See Component Examples Appendix --> |
| Loading (action) | <!-- e.g., Inline spinner for buttons --> | <!-- e.g., Use for actions only, not page loads --> | <!-- See Component Examples Appendix --> |
| Empty | <!-- e.g., Centered heading + description + CTA --> | <!-- e.g., Always include heading and CTA --> | <!-- See Component Examples Appendix --> |
| Error | <!-- e.g., Inline banner with retry button --> | <!-- e.g., Human-readable message, never raw errors --> | <!-- See Component Examples Appendix --> |
| Disabled | <!-- e.g., opacity-50 + cursor-not-allowed --> | <!-- e.g., Use opacity, not gray colors --> | <!-- Describe inline --> |

### 2.6 Responsive Breakpoints

<!-- TODO: Define the breakpoint system and responsive strategy.
     If DDRs were compiled, this section is pre-filled from responsive-category DDRs. -->

| Breakpoint | Width | Utility Prefix [e.g., Tailwind] | Primary Use |
|------------|-------|--------------------------------|-------------|
| Mobile | <!-- < 640px --> | (base) | <!-- Single column, stacked --> |
| Tablet | <!-- 640px - 1023px --> | <!-- sm:, md: --> | <!-- Collapsed sidebar, 2-column --> |
| Desktop | <!-- 1024px+ --> | <!-- lg:, xl: --> | <!-- Full sidebar, multi-column --> |

**Responsive Strategy**: <!-- Mobile-first / Desktop-first -->

## 3. Screen Inventory

<!-- TODO: List all screens in the application. This table doubles as the shard directory — every screen listed here must have a shard at screens/<screen>.md -->

| Screen Name | Route | Auth Required | Parent Layout | Shard | Primary User Action |
|-------------|-------|---------------|---------------|-------|-------------------|
| <!-- Login --> | <!-- /login --> | <!-- No --> | <!-- Public --> | <!-- `screens/login.md` --> | <!-- Authenticate --> |
| <!-- Dashboard --> | <!-- /dashboard --> | <!-- Yes --> | <!-- App shell --> | <!-- `screens/dashboard.md` --> | <!-- Navigate to content --> |

## 4. Shared Layouts

### 4.1 App Shell (Authenticated)

<!-- TODO: Describe the main layout for authenticated users -->

```
┌──────────────────────────────────────────────────────────┐
│  Header: [logo, search, user menu]                       │
├──────────┬───────────────────────────────────────────────┤
│ Sidebar  │  Main Content Area                            │
│ [nav]    │  [Page content via router]                    │
├──────────┴───────────────────────────────────────────────┤
│  Footer (optional)                                       │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Public Layout (Unauthenticated)

```
┌──────────────────────────────────────────────────────────┐
│              [Centered content card]                     │
│              [Logo + login form]                         │
└──────────────────────────────────────────────────────────┘
```

## Usage Notes for AI Task Generation

- **Load only what's referenced**: Read this `index.md` plus ONLY the screen shards named by the work item's impact tables, plus `components.md` when a shared component is involved — do not read the whole `screens/` directory
- **Derive component structure** from each screen shard's Component Hierarchy
- **Map data requirements** from each screen shard's Component → API Mapping
- **Specify all states** — every component must handle loading, empty, and error per the shard's States table
- **Define interactions precisely** — each maps to a UI element, result, and API call
- **Reuse shared components** (`components.md`) before creating new ones
- **Follow the design system** (Section 2) for colors, typography, and spacing
- **Reference State Patterns** (Section 2.5) for consistent loading, empty, error, and disabled handling across all screens
- **Follow Responsive Breakpoints** (Section 2.6) for consistent breakpoint usage
- **Use Component Examples Appendix** (if DDRs were compiled) as the authoritative reference for component markup patterns in mockups and implementations
- **New screens**: Create a new shard at `screens/<screen>.md` (copy `screens/TEMPLATE-screen.md`), add a Screen Inventory row (Section 3), and record the change in the Changelog

## Changelog

<!-- Records changes across the whole docs/ui-specification/ set — screen shard and components.md edits included. Update the freshness stamp on every file touched. -->

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |
