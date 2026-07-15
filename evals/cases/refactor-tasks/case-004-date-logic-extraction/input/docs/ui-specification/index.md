# UI Specification — TaskFlow

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

## 1. Overview

### 1.1 UI Summary

TaskFlow is a React SPA with two primary screens: a drag-and-drop kanban Project Board and a Task Detail Panel that slides over it. Desktop-first, keyboard-accessible, no external UI kit.

### 1.2 Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component library | In-house components in `src/ui/components/` — no external UI kit | Tiny surface; full control over accessibility |
| Layout pattern | App shell: slim header + full-bleed board | Board is the product; maximize its space |
| Responsive strategy | Desktop-first; board columns stack on mobile | Primary device is desktop |
| Accessibility standard | WCAG 2.1 AA | Pilot customers require it |
| State management | TanStack Query for server state; local `useState`/`useReducer` for UI state | No global store needed at this size |
| Styling approach | CSS Modules; design tokens as CSS custom properties | Scoped styles, no utility-class dependency |
| Icon set | Inline SVG icons | No icon-font dependency |

---

## 2. Design System

### 2.1 Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #2563EB | Primary actions, active states, links |
| `primary-dark` | #1D4ED8 | Hover/pressed states |
| `neutral-50` | #F8FAFC | App background |
| `neutral-100` | #F1F5F9 | Card and column backgrounds |
| `neutral-300` | #CBD5E1 | Dividers, borders |
| `neutral-700` | #334155 | Secondary text |
| `neutral-900` | #0F172A | Primary text |
| `success` | #16A34A | Success toasts |
| `error` | #DC2626 | Error states, destructive actions |

**Accent palette** (12 tokens — used for colored chips and highlights; chip text color is chosen per token to keep WCAG 2.1 AA contrast):

| Token | Hex | Token | Hex | Token | Hex | Token | Hex |
|-------|-----|-------|-----|-------|-----|-------|-----|
| `accent-01` | #DC2626 | `accent-04` | #CA8A04 | `accent-07` | #0D9488 | `accent-10` | #7C3AED |
| `accent-02` | #EA580C | `accent-05` | #65A30D | `accent-08` | #0891B2 | `accent-11` | #C026D3 |
| `accent-03` | #D97706 | `accent-06` | #16A34A | `accent-09` | #2563EB | `accent-12` | #DB2777 |

### 2.2 Typography Scale

| Level | Size | Weight | Font Family | Usage |
|-------|------|--------|-------------|-------|
| `h1` | 1.5rem / 24px | 600 | System font stack | Screen titles |
| `h2` | 1.125rem / 18px | 600 | System font stack | Column headers, panel sections |
| `body` | 0.875rem / 14px | 400 | System font stack | Card titles, form fields |
| `caption` | 0.75rem / 12px | 400 | System font stack | Timestamps, metadata, chips |

### 2.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight internal padding (chips) |
| `space-2` | 8px | Standard internal padding |
| `space-3` | 12px | Gaps between cards |
| `space-4` | 16px | Column and panel padding |
| `space-6` | 24px | Page-level padding |

> **Base unit**: 4px. All spacing is a multiple of the base unit, exposed as CSS custom properties.

### 2.4 Component Library

**Library**: in-house — `src/ui/components/` (inventory: `components.md`)

| UI Need | Component | Customization Notes |
|---------|-----------|-------------------|
| Board cards | `TaskCard` (`src/ui/components/task-card.tsx`) | Compact variant for dense boards |
| Modals / confirmations | `Dialog` (`src/ui/components/dialog.tsx`) | Focus trap, Escape closes, one primary action |
| Empty states | `EmptyState` (`src/ui/components/empty-state.tsx`) | Heading + description + CTA, never blank |

### 2.5 State Patterns

| State | Pattern | Key Constraints |
|-------|---------|----------------|
| Loading (screen) | Skeleton placeholders matching content layout | Match real content dimensions; show ≥200ms to avoid flicker |
| Loading (action) | Inline spinner inside the triggering button | Button disabled while pending; include sr-only text |
| Empty | `EmptyState` component: heading + description + CTA | Never render a blank region |
| Error (inline) | Error banner with retry button | Human-readable message; retry for network errors |
| Disabled | `opacity: 0.5` + `cursor: not-allowed` | Use opacity, not gray recoloring |

### 2.6 Responsive Breakpoints

| Breakpoint | Width | Primary Use |
|------------|-------|-------------|
| Mobile | < 640px | Board columns stack vertically; panel becomes full-screen |
| Tablet | 640px – 1023px | Two visible columns, horizontal scroll |
| Desktop | ≥ 1024px | All columns visible; panel overlays right side |

**Responsive Strategy**: Desktop-first — media queries narrow the layout downward; the board is designed at desktop width first.

---

## 3. Screen Inventory

> *This table doubles as the shard directory: every screen listed here has a shard at `screens/<screen>.md` (kebab-case).*

| Screen Name | Route | Auth Required | Parent Layout | Shard | Primary User Action |
|-------------|-------|---------------|---------------|-------|-------------------|
| Project Board | /projects/:projectId/board | Yes | App shell | `screens/project-board.md` | Move tasks between columns |
| Task Detail Panel | /projects/:projectId/tasks/:taskId | Yes | App shell (overlay panel on the board) | `screens/task-detail-panel.md` | Edit task fields |

---

## 4. Shared Layouts

### 4.1 App Shell (Authenticated)

```
┌──────────────────────────────────────────────────────────┐
│  Header: logo · project name · user avatar               │
├──────────────────────────────────────────────────────────┤
│  Main content area (screen rendered here via router)     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- Header is 48px tall, always visible; no sidebar.
- Overlay screens (Task Detail Panel) render above the board inside the main content area.

---

## Usage Notes for AI Task Generation

1. **Load only what's referenced** — Read this index plus ONLY the screen shards named by the work item's impact tables (kebab-case naming rule), plus `components.md` when a shared component is involved. Do not read the whole `screens/` directory.
2. **All four states** — Every component task must handle default, loading, empty, and error states per the shard's States table and Section 2.5.
3. **Reuse shared components** — Check `components.md` before creating new components; use the in-house set from Section 2.4 — do not add an external UI kit.
4. **Design tokens** — Use Section 2 tokens (colors, spacing, typography) via CSS custom properties; no hard-coded values.
5. **New screens** — Create a new shard at `screens/<screen>.md`, add a Screen Inventory row (Section 3), and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-01 | TaskFlow team | Initial version (Project Board, Task Detail Panel) | v1.0 baseline |
| 2026-07-06 | TaskFlow team | Project Board toolbar gains the filter dropdown (`screens/project-board.md`); TaskCard due-date chip overdue styling | v1.2 board filters (FEAT-003) |
