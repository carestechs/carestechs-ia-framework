# UI Specification

## Overview

<!-- TODO: Describe the UI at a high level — what type of app, how many screens, primary interaction paradigm -->

### Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Component library --> | <!-- e.g., Angular Material --> | <!-- e.g., Consistency, accessibility --> |
| <!-- e.g., Layout pattern --> | <!-- e.g., Sidebar + main content --> | <!-- e.g., Navigation density --> |
| <!-- e.g., Styling approach --> | <!-- e.g., Tailwind CSS --> | <!-- e.g., Consistency, rapid iteration --> |
| <!-- e.g., Responsive strategy --> | <!-- e.g., Desktop-first --> | <!-- e.g., Primary device is desktop --> |

## Design System

### Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | <!-- #XXXXXX --> | <!-- Primary actions, active states --> |
| `secondary` | <!-- #XXXXXX --> | <!-- Secondary actions, accents --> |
| `neutral-50` | <!-- #XXXXXX --> | <!-- Backgrounds --> |
| `neutral-900` | <!-- #XXXXXX --> | <!-- Primary text --> |
| `success` | <!-- #XXXXXX --> | <!-- Success states --> |
| `warning` | <!-- #XXXXXX --> | <!-- Warning states --> |
| `error` | <!-- #XXXXXX --> | <!-- Error states --> |

### Typography Scale

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| `h1` | <!-- 2rem --> | <!-- 700 --> | <!-- Page titles --> |
| `h2` | <!-- 1.5rem --> | <!-- 600 --> | <!-- Section headings --> |
| `body` | <!-- 1rem --> | <!-- 400 --> | <!-- Body text --> |
| `caption` | <!-- 0.75rem --> | <!-- 400 --> | <!-- Timestamps, metadata --> |

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-2` | <!-- 0.5rem --> | <!-- Standard internal padding --> |
| `space-4` | <!-- 1rem --> | <!-- Section padding --> |
| `space-8` | <!-- 2rem --> | <!-- Page-level padding --> |

### Component Library

<!-- TODO: List the UI components you'll use -->

| UI Need | Component | Notes |
|---------|-----------|-------|
| <!-- Buttons --> | <!-- e.g., mat-button --> | <!-- Color overrides --> |
| <!-- Forms --> | <!-- e.g., mat-form-field --> | <!-- Outline appearance --> |
| <!-- Tables --> | <!-- e.g., mat-table --> | <!-- Sticky header --> |

### State Patterns

<!-- TODO: Define standard UI patterns for loading, empty, error, and disabled states.
     If DDRs were compiled, this section is pre-filled from states-category DDRs. -->

| State | Pattern | Key Constraints | Example Reference |
|-------|---------|----------------|-------------------|
| Loading (skeleton) | <!-- e.g., Skeleton placeholders with animate-pulse --> | <!-- e.g., Match real content dimensions --> | <!-- See Component Examples Appendix --> |
| Loading (action) | <!-- e.g., Inline spinner for buttons --> | <!-- e.g., Use for actions only, not page loads --> | <!-- See Component Examples Appendix --> |
| Empty | <!-- e.g., Centered heading + description + CTA --> | <!-- e.g., Always include heading and CTA --> | <!-- See Component Examples Appendix --> |
| Error | <!-- e.g., Inline banner with retry button --> | <!-- e.g., Human-readable message, never raw errors --> | <!-- See Component Examples Appendix --> |

### Responsive Breakpoints

<!-- TODO: Define the breakpoint system and responsive strategy.
     If DDRs were compiled, this section is pre-filled from responsive-category DDRs. -->

| Breakpoint | Width | Tailwind Prefix | Primary Use |
|------------|-------|-----------------|-------------|
| Mobile | <!-- < 640px --> | (base) | <!-- Single column, stacked --> |
| Tablet | <!-- 640px - 1023px --> | <!-- sm:, md: --> | <!-- Collapsed sidebar, 2-column --> |
| Desktop | <!-- 1024px+ --> | <!-- lg:, xl: --> | <!-- Full sidebar, multi-column --> |

**Responsive Strategy**: <!-- Mobile-first / Desktop-first -->

## Screen Inventory

<!-- TODO: List all screens in the application -->

| Screen Name | Route | Auth Required | Parent Layout | Primary User Action |
|-------------|-------|---------------|---------------|-------------------|
| <!-- Login --> | <!-- /login --> | <!-- No --> | <!-- Public --> | <!-- Authenticate --> |
| <!-- Dashboard --> | <!-- /dashboard --> | <!-- Yes --> | <!-- App shell --> | <!-- Navigate to content --> |

## Shared Layouts

### App Shell (Authenticated)

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

### Public Layout (Unauthenticated)

```
┌──────────────────────────────────────────────────────────┐
│              [Centered content card]                     │
│              [Logo + login form]                         │
└──────────────────────────────────────────────────────────┘
```

## Screen Specifications

<!-- TODO: Define each screen. See .ai-framework/templates/ui-specification.md for the full template. -->

### [Screen Name]

**Route**: [/path]
**Auth**: [Required / Public]
**Layout**: [App shell / Public]

#### Layout Sketch

```
[ASCII diagram of the screen layout]
```

#### Component Hierarchy

```
[ScreenName]Page
├── [ComponentA]
│   └── [SubComponent]
└── [ComponentB]
```

#### Component → API Mapping

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| <!-- Component --> | <!-- Data --> | <!-- GET /api/... --> | <!-- On page load --> |

#### States

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Data loaded | Show content |
| **Loading** | API in flight | Show spinner/skeleton |
| **Empty** | No items | Show message + CTA |
| **Error** | API failed | Show error + retry |

#### User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| <!-- Click create --> | <!-- Button --> | <!-- Open dialog --> | <!-- None until submit --> |

---

<!-- TODO: Repeat screen specification blocks for each screen -->

## Shared Components

<!-- TODO: Document reusable components used across 2+ screens -->

### [Component Name]

**Used in**: [Screen A, Screen B]
**Description**: [One sentence]

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| <!-- item --> | <!-- Input --> | <!-- ItemDto --> | <!-- Data to display --> |
| <!-- clicked --> | <!-- Output --> | <!-- EventEmitter --> | <!-- Emitted on click --> |

## AI Task Generation Notes

- **Derive component structure** from the Component Hierarchy for each screen
- **Map data requirements** from Component → API Mapping
- **Specify all states** — every component must handle loading, empty, and error
- **Define interactions precisely** — each maps to a UI element, result, and API call
- **Reuse shared components** before creating new ones
- **Follow the design system** for colors, typography, and spacing
- **Reference State Patterns** (Section 2.5) for consistent loading, empty, and error handling across all screens
- **Follow Responsive Breakpoints** (Section 2.6) for consistent breakpoint usage
- **Use Component Examples Appendix** (if DDRs were compiled) as the authoritative reference for component HTML/Tailwind patterns in mockups and implementations
