# UI Specification — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

## 1. Overview

### 1.1 UI Summary

TaskFlow is a React 18 SPA with four screens: a Project List, a drag-and-drop kanban Project Board with a collapsible Activity Feed drawer, a Task Detail Panel that overlays the board, and a Member Management screen. Desktop-first, keyboard-accessible, no external UI kit. Sign-in is not a screen: unauthenticated visitors are redirected to the external auth service, and the SPA renders only once a JWT is present.

### 1.2 Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component library | In-house components in `src/ui/components/` — no external UI kit | Tiny surface; full control over accessibility |
| Layout pattern | App shell: slim header + full-bleed content, no sidebar | The board is the product; maximize its space |
| Responsive strategy | Desktop-first; board columns stack on mobile | Primary device is desktop |
| Accessibility standard | WCAG 2.1 AA — full keyboard operability incl. drag-and-drop alternative | Inclusive by default; drag actions get a keyboard menu equivalent |
| State management | TanStack Query for server state; local `useState`/`useReducer` for UI state | Server state stays server-owned (per architecture); no global store |
| Styling approach | CSS Modules; design tokens as CSS custom properties | Scoped styles, kebab-case files, no utility-class dependency |
| Icon set | Inline SVG icons | No icon-font dependency |
| User display | `UserBadge`: deterministic color + shortened opaque UUID | The app stores no names or avatars — user ids are opaque auth-service UUIDs |
| Auth entry | Redirect to the external auth service; no login screen | Auth is fully external (JWT); the SPA has no credential UI |
| Due dates | Calendar-date picker only (`YYYY-MM-DD`) — no time-of-day control | Due dates are day-precision per the data model and API |

---

## 2. Design System

### 2.1 Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #2563EB | Primary actions, active states, links |
| `primary-dark` | #1D4ED8 | Hover/pressed states |
| `neutral-50` | #F8FAFC | App background |
| `neutral-100` | #F1F5F9 | Card, column, and drawer backgrounds |
| `neutral-300` | #CBD5E1 | Dividers, borders |
| `neutral-700` | #334155 | Secondary text |
| `neutral-900` | #0F172A | Primary text |
| `success` | #16A34A | Success toasts |
| `warning` | #D97706 | Overdue due-date chips |
| `error` | #DC2626 | Error states, destructive actions |

### 2.2 Typography Scale

| Level | Size | Weight | Font Family | Usage |
|-------|------|--------|-------------|-------|
| `h1` | 1.5rem / 24px | 600 | System font stack | Screen titles |
| `h2` | 1.125rem / 18px | 600 | System font stack | Column headers, panel sections |
| `body` | 0.875rem / 14px | 400 | System font stack | Card titles, form fields, comments |
| `caption` | 0.75rem / 12px | 400 | System font stack | Timestamps, metadata, badges |

### 2.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight internal padding (badges, chips) |
| `space-2` | 8px | Standard internal padding |
| `space-3` | 12px | Gaps between cards and rows |
| `space-4` | 16px | Column, panel, and form padding |
| `space-6` | 24px | Page-level padding |

> **Base unit**: 4px. All spacing is a multiple of the base unit, exposed as CSS custom properties.

### 2.4 Component Library

**Library**: in-house — `src/ui/components/` (inventory: `components.md`)

| UI Need | Component | Customization Notes |
|---------|-----------|-------------------|
| Modals / confirmations / create forms | `Dialog` (`src/ui/components/dialog.tsx`) | Focus trap, Escape closes, one primary action; destructive variant |
| Empty states | `EmptyState` (`src/ui/components/empty-state.tsx`) | Heading + description + CTA, never blank |
| Inline errors | `ErrorBanner` (`src/ui/components/error-banner.tsx`) | Human-readable message + retry for network errors |
| User identity | `UserBadge` (`src/ui/components/user-badge.tsx`) | Deterministic color + shortened opaque UUID — no names exist |
| Board cards | `TaskCard` — screen-specific, documented in `screens/project-board.md` | Lives with the board; not shared in V1 |

### 2.5 State Patterns

| State | Pattern | Key Constraints |
|-------|---------|----------------|
| Loading (screen) | Skeleton placeholders matching content layout | Match real content dimensions; show ≥200ms to avoid flicker |
| Loading (action) | Inline spinner inside the triggering button | Button disabled while pending; include sr-only text |
| Empty | `EmptyState` component: heading + description + CTA | Never render a blank region |
| Error (inline) | `ErrorBanner` with retry button | Human-readable message; retry for network errors; never raw error codes |
| Disabled | `opacity: 0.5` + `cursor: not-allowed` | Use opacity, not gray recoloring |

### 2.6 Responsive Breakpoints

| Breakpoint | Width | Primary Use |
|------------|-------|-------------|
| Mobile | < 640px | Board columns stack vertically; panel and drawer become full-screen |
| Tablet | 640px – 1023px | Two visible columns, horizontal scroll; drawer overlays |
| Desktop | ≥ 1024px | All columns visible; panel and drawer overlay the right side |

**Responsive Strategy**: Desktop-first — media queries narrow the layout downward; the board is designed at desktop width first.

---

## 3. Screen Inventory

> *This table doubles as the shard directory: every screen listed here has a shard at `screens/<screen>.md` (kebab-case).*

| Screen Name | Route | Auth Required | Parent Layout | Shard | Primary User Action |
|-------------|-------|---------------|---------------|-------|-------------------|
| Project List | /projects | Yes | App shell | `screens/project-list.md` | Open or create a project |
| Project Board | /projects/:projectId/board | Yes | App shell | `screens/project-board.md` | Move tasks between status columns |
| Task Detail Panel | /projects/:projectId/tasks/:taskId | Yes | App shell (overlay panel over the board) | `screens/task-detail-panel.md` | Edit task fields and discuss in comments |
| Member Management | /projects/:projectId/members | Yes | App shell | `screens/member-management.md` | Add or remove project members |

---

## 4. Shared Layouts

### 4.1 App Shell (Authenticated)

```
┌──────────────────────────────────────────────────────────┐
│  Header: logo · project name (when in a project) · UserBadge (caller) │
├──────────────────────────────────────────────────────────┤
│  Main content area (screen rendered here via router)     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- Header is 48px tall, always visible; no sidebar.
- Overlay surfaces (Task Detail Panel, Activity Feed drawer) render above the board inside the main content area.
- The header's `UserBadge` shows the caller's own opaque user id (from the JWT subject) — there is no profile menu, because no profile exists.

### 4.2 Public Layout (Unauthenticated)

None in V1. A request without a valid JWT is redirected to the external auth service; the SPA ships no login or registration screen and renders nothing until a token is present.

---

## Usage Notes for AI Task Generation

1. **Load only what's referenced** — Read this index plus ONLY the screen shards named by the work item's impact tables (kebab-case naming rule), plus `components.md` when a shared component is involved. Do not read the whole `screens/` directory.
2. **All four states** — Every component task must handle default, loading, empty, and error states per the shard's States table and Section 2.5.
3. **Reuse shared components** — Check `components.md` before creating new components; use the in-house set from Section 2.4 — do not add an external UI kit.
4. **Design tokens** — Use Section 2 tokens (colors, spacing, typography) via CSS custom properties; no hard-coded values.
5. **Envelope discipline** — Components receive `data` (and `meta` on lists) from the response envelope defined in `docs/api-spec/index.md` Section 2.1; error handling keys off the stable codes in its Error Catalog.
6. **Opaque users** — Render user ids only through `UserBadge`. Never generate tasks that fetch names, emails, or avatars: no such data or endpoint exists.
7. **Day-precision dates** — Due-date UI is a calendar-date control emitting `YYYY-MM-DD`; never add time-of-day or timezone handling to due dates.
8. **New screens** — Create a new shard at `screens/<screen>.md`, add a Screen Inventory row (Section 3), and record the change in the Changelog.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | ui-spec-generation | Initial version (Project List, Project Board, Task Detail Panel, Member Management) | Derived from stakeholder user flow, data model, and API spec |
