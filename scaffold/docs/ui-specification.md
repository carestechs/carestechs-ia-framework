# UI Specification

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

<!-- TODO: List all screens in the application -->

| Screen Name | Route | Auth Required | Parent Layout | Primary User Action |
|-------------|-------|---------------|---------------|-------------------|
| <!-- Login --> | <!-- /login --> | <!-- No --> | <!-- Public --> | <!-- Authenticate --> |
| <!-- Dashboard --> | <!-- /dashboard --> | <!-- Yes --> | <!-- App shell --> | <!-- Navigate to content --> |

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

## 5. Screen Specifications

<!-- TODO: Define each screen. See .ai-framework/templates/ui-specification.md for the full template. -->

### 5.1 [Screen Name]

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

<!-- TODO: Repeat screen specification blocks (5.2, 5.3, ...) for each screen -->

## 6. Shared Components

<!-- TODO: Document reusable components used across 2+ screens -->

### 6.1 [Component Name]

**Used in**: [Screen A, Screen B]
**Description**: [One sentence]

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| <!-- item --> | <!-- Input --> | <!-- ItemDto --> | <!-- Data to display --> |
| <!-- clicked --> | <!-- Output --> | <!-- e.g., event<string> — EventEmitter / callback prop --> | <!-- Emitted on click --> |

## 7. Usage Notes for AI Task Generation

- **Derive component structure** from the Component Hierarchy for each screen
- **Map data requirements** from Component → API Mapping
- **Specify all states** — every component must handle loading, empty, and error
- **Define interactions precisely** — each maps to a UI element, result, and API call
- **Reuse shared components** (Section 6) before creating new ones
- **Follow the design system** (Section 2) for colors, typography, and spacing
- **Reference State Patterns** (Section 2.5) for consistent loading, empty, error, and disabled handling across all screens
- **Follow Responsive Breakpoints** (Section 2.6) for consistent breakpoint usage
- **Use Component Examples Appendix** (if DDRs were compiled) as the authoritative reference for component markup patterns in mockups and implementations

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |
