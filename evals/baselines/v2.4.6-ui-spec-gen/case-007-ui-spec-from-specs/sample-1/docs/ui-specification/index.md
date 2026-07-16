# UI Specification — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

## 1. Overview

### 1.1 UI Summary

TaskFlow's UI is a React 18 single-page application (Vite, TanStack Query) with **four screens** under one authenticated app shell: a Project List, a per-project Project Board (three status columns plus an on-demand activity feed panel), a Task Detail Panel that overlays the board, and a Member Management screen. The interaction paradigm is board-centric direct manipulation — drag a card to change its status, click a card to edit it in place — with creation and destructive actions confined to small dialogs. There is no in-app sign-in screen: authentication is a full-page redirect to the external auth service (see Section 4.2), and the only user identity the UI ever renders is the opaque auth-service UUID (via the shared `UserIdBadge`) — the API returns no names, emails, or avatars, and no user search or profile endpoint exists.

### 1.2 Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component approach | Hand-rolled React 18 function components + hooks; no UI component library | CLAUDE.md declares no component library; the V1 surface (4 screens, ~10 shared components) is small enough to own |
| Routing | React Router (client-side routes listed in Section 3) | An SPA needs a router; React Router is the minimal standard choice and contradicts no convention |
| Layout pattern | Top app bar + per-project tab navigation (Board / Members); no sidebar | Only two navigation levels exist (project list → project screens); a persistent sidebar would be nearly empty |
| Task detail presentation | Routed overlay panel above the Project Board | Preserves board context while editing; matches the flow's "task detail panel" |
| Responsive strategy | Desktop-first; board columns stack vertically below the Tablet breakpoint (Section 2.6) | Team task tracking is a desktop-primary workflow |
| Accessibility standard | **WCAG 2.1 AA** — semantic HTML, a full keyboard path for every pointer interaction (drag-and-drop has a menu-based status-change fallback), visible focus rings, `aria-live` announcements for async state changes | Drag-only board UIs exclude keyboard and screen-reader users; AA is the baseline for an inclusive team tool |
| State management | TanStack Query for all server state (queries + mutations, envelope-aware); local `useState`/`useReducer` for UI-only state (open dialogs, drag, filters) | CLAUDE.md convention — server state stays server-owned; no global client-state library |
| Styling approach | Plain CSS: design tokens as CSS custom properties in a shared `tokens.css`; one kebab-case `.css` file co-located per screen or component | No styling framework is declared in CLAUDE.md; tokens keep hand-rolled CSS consistent |
| User display | `UserIdBadge` — monospace truncated UUID (first 8 characters, full id on hover/focus), with a "you" marker when it matches the caller's JWT subject | User ids are opaque auth-service UUIDs; the API never resolves them to names or avatars |
| Icon set | Inline SVG icons (in-project, sized via tokens) | No icon-font or library dependency for a handful of icons |
| Drag & drop | Native HTML5 drag-and-drop on task cards | The board is the only DnD surface; avoids a dependency and keeps the keyboard fallback first-class |

---

## 2. Design System

> *Keep the 2.1–2.6 numbering exactly as below — DDR compilation writes into these numbered sections. No DDRs are compiled for TaskFlow V1; the values below are derived defaults.*

### 2.1 Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #2563EB | Primary actions, active tab, links, focus rings |
| `primary-light` | #DBEAFE | Hover backgrounds, selected-row background, drag-over column highlight |
| `primary-dark` | #1D4ED8 | Active/pressed states |
| `secondary` | #0D9488 | Secondary accents ("you" marker, owner role badge) |
| `neutral-50` | #F9FAFB | App background |
| `neutral-100` | #F3F4F6 | Card and column backgrounds |
| `neutral-200` | #E5E7EB | Dividers, subtle borders, skeleton base |
| `neutral-700` | #374151 | Secondary text, captions |
| `neutral-900` | #111827 | Primary text |
| `success` | #16A34A | `done` status accents, success feedback |
| `warning` | #D97706 | Due-soon due-date badge, `in_progress` status accents |
| `error` | #DC2626 | Error states, destructive actions, overdue due-date badge |
| `info` | #0284C7 | Informational banners, `todo` status accents |

### 2.2 Typography Scale

| Level | Size | Weight | Font Family | Usage |
|-------|------|--------|-------------|-------|
| `h1` | 2rem / 32px | 700 | System UI stack¹ | Page titles ("Projects", project name) |
| `h2` | 1.5rem / 24px | 600 | System UI stack¹ | Section headings, dialog titles |
| `h3` | 1.25rem / 20px | 600 | System UI stack¹ | Column headers, panel headers |
| `body` | 1rem / 16px | 400 | System UI stack¹ | Body text, form fields, comments |
| `body-sm` | 0.875rem / 14px | 400 | System UI stack¹ | Card text, table cells, labels |
| `caption` | 0.75rem / 12px | 400 | System UI stack¹ | Timestamps, metadata, feed entries |
| `mono` | 0.8125rem / 13px | 400 | Monospace stack² | Opaque user UUIDs (`UserIdBadge`) |

¹ `system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` — no webfont dependency.
² `ui-monospace, "Cascadia Mono", Consolas, monospace`.

### 2.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 0.25rem / 4px | Tight internal padding (badges) |
| `space-2` | 0.5rem / 8px | Standard internal padding (buttons, inputs) |
| `space-3` | 0.75rem / 12px | Component gaps (cards within a column) |
| `space-4` | 1rem / 16px | Card padding, gaps between columns |
| `space-6` | 1.5rem / 24px | Section margins, dialog padding |
| `space-8` | 2rem / 32px | Page-level padding |

> **Base unit**: 0.25rem. All spacing is a multiple of the base unit, exposed as CSS custom properties (`--space-1` … `--space-8`) in the shared `tokens.css`; components consume the variables — no hard-coded pixel values.

### 2.4 Component Library

**Library**: None — in-project React function components only (shared inventory in `components.md`)
**Version**: —

| UI Need | Component | Customization Notes |
|---------|-----------|-------------------|
| Dialogs & confirmations | `ModalDialog`, `ConfirmDialog` | Shared (components.md); focus trap, Esc to close, `aria-modal` |
| Status / identity / date badges | `TaskStatusBadge`, `UserIdBadge`, `DueDateBadge` | Shared (components.md); color-coded via Section 2.1 tokens |
| Async feedback | `SkeletonBlock`, `ErrorBanner`, `EmptyState` | Shared (components.md); implement the Section 2.5 patterns |
| Pagination / load more | `PaginationControls` | Shared (components.md); pager and load-more variants |
| Per-project navigation | `ProjectHeader` | Shared (components.md); project name + Board/Members tabs |
| Form controls | Native `input`, `textarea`, `select` (incl. `input type="date"`) styled with tokens | Day-precision due dates use the native date input — the `YYYY-MM-DD` string passes through untouched |
| Buttons | Native `button` with `.btn`, `.btn-primary`, `.btn-danger` token classes | No custom button component needed |
| Drag & drop | Native HTML5 DnD on `TaskCard` | Keyboard fallback: status change via card menu / Task Detail Panel |

### 2.5 State Patterns

> *Standard UI patterns for loading, empty, error, and disabled states across the application. Every screen uses these — do not invent new loading or error UIs.*

| State | Pattern | Key Constraints | Example Reference |
|-------|---------|----------------|-------------------|
| Loading (skeleton) | `SkeletonBlock` placeholders matching the real content layout, CSS pulse animation | Match real content dimensions; container gets `aria-busy="true"` | Board columns render 3 skeleton cards each while tasks load |
| Loading (action) | Inline spinner inside the triggering button; button disabled while pending | Action feedback only, never page loads; include visually-hidden "Saving…" text | Dialog Save buttons, comment Send button |
| Empty | `EmptyState`: heading + one-line description + CTA button, centered | Always heading + description + actionable CTA; never a blank region | "No projects yet" + "New project" CTA on Project List |
| Error (inline) | `ErrorBanner`: message mapped from the Error Catalog code + Retry button | Human-readable message from the stable `error.code`; Retry refetches; never show raw payloads | Board shows banner if task fetch fails |
| Error (full-page) | Route-level error boundary: message + "Back to projects" link | Never raw stack traces; always a navigation escape; 401 `unauthorized` instead triggers the auth redirect (Section 4.2) | Broken route / render failure |
| Disabled | `opacity: 0.5` + `cursor: not-allowed` + `aria-disabled="true"` | Opacity, not gray recoloring; tooltips explain owner-only actions | "Add member" for non-owners |

### 2.6 Responsive Breakpoints

| Breakpoint | Width | Media Query | Primary Use |
|------------|-------|-------------|-------------|
| Mobile | < 640px | `(max-width: 639px)` | Single column; board columns stack vertically; dialogs and Task Detail Panel go full-screen |
| Tablet | 640px – 1023px | `(min-width: 640px)` | Board columns side-by-side with horizontal scroll; activity feed panel overlays the board |
| Desktop | 1024px – 1279px | `(min-width: 1024px)` | Three board columns fully visible; Task Detail Panel and feed panel dock right |
| Large Desktop | 1280px+ | `(min-width: 1280px)` | Max-width content (1280px) centered, additional whitespace |

**Responsive Strategy**: Desktop-first — base styles target desktop and `max-width` queries adapt downward, because the primary team-tracking workflow is desktop and smaller viewports are the exception.

---

## 3. Screen Inventory

> *Every screen with its route, auth requirement, parent layout, and primary user action. This table doubles as the shard directory: every screen listed here has a shard at `screens/<screen>.md` (kebab-case, mechanical — see the template Naming Rule).*

| Screen Name | Route | Auth Required | Parent Layout | Shard | Primary User Action |
|-------------|-------|---------------|---------------|-------|-------------------|
| Project List | `/projects` | Yes | App shell | `screens/project-list.md` | Open or create a project |
| Project Board | `/projects/:projectId` | Yes | App shell | `screens/project-board.md` | Move tasks between status columns |
| Task Detail Panel | `/projects/:projectId/tasks/:taskId` | Yes | App shell (overlay panel over Project Board) | `screens/task-detail-panel.md` | Edit task fields and discuss in comments |
| Member Management | `/projects/:projectId/members` | Yes | App shell | `screens/member-management.md` | Add or remove project members |

Notes:

- `/` redirects to `/projects`. There is **no login route** — every route requires auth, and unauthenticated visits redirect to the external auth service (Section 4.2). This covers user-flow step 1 (Sign in).
- The project activity feed (user-flow step 6) is a panel inside the Project Board screen (`screens/project-board.md`), backed by `GET /api/v1/projects/{projectId}/feed` — it is not a separate screen.
- Scope Lock exclusions (labels/tags, notifications, file attachments, real-time collaboration) have **no screens and no components** anywhere in this set.

---

## 4. Shared Layouts

### 4.1 App Shell (Authenticated)

Fixed top app bar, full-width main content routed below it. Project screens (Board, Member Management) render the shared `ProjectHeader` (project name + tab navigation) as the first element of their content. There is no sidebar.

```
┌──────────────────────────────────────────────────────────────┐
│ App bar: TaskFlow logo/name          [you: 3f2a91c4…] [Sign out] │
├──────────────────────────────────────────────────────────────┤
│ ProjectHeader (project screens only):                        │
│   ‹ Projects   Project Name            [Board] [Members]    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Main content area (router outlet)                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**App bar contents**:
- Left: TaskFlow wordmark — links to `/projects`
- Right: the caller's own `UserIdBadge` (truncated JWT subject UUID — the only identity the app knows) and a "Sign out" action that clears the token and redirects to the external auth service

**App bar behavior**:
- Desktop/Tablet: fixed at top, content scrolls beneath
- Mobile: identical (no hamburger — there is no sidebar to collapse)

### 4.2 Public Layout (Unauthenticated)

**None in V1.** The API has zero unauthenticated endpoints and the app stores no credentials, so there is no in-app login screen or public layout. On first visit without a valid JWT — or on any `401 unauthorized` response — the SPA performs a full-page redirect to the external auth service; the service redirects back with a token whose subject is the caller's opaque user UUID. This redirect **is** the "Sign in" step of the stakeholder user flow.

---

## Usage Notes for AI Task Generation

### When generating frontend tasks, use this document set to:

1. **Load only what's referenced** — Read this `index.md` plus ONLY the screen shards named by the work item's impact tables (screen name → `screens/<kebab-case>.md`), plus `components.md` when a shared component is involved. Do not read the whole `screens/` directory.
2. **Derive component structure** — Use the screen shard's Component Hierarchy to know which components to create or modify; one React file per screen under `src/ui/` (kebab-case file, PascalCase component) per CLAUDE.md.
3. **Map data requirements** — Use the screen shard's Component → API Mapping; every call goes through TanStack Query and receives the response envelope (`{ data }`, lists add `meta`).
4. **Specify all states** — Every component task includes default, loading, empty, and error handling as defined in the screen shard's States table, using the Section 2.5 patterns.
5. **Define interactions precisely** — Use the screen shard's User Interactions table: exact UI element, result, and API call. Do not add interactions whose endpoint does not exist in `docs/api-spec/` (V1 has **no** task delete, comment delete, member role change, or user search).
6. **Reuse shared components** — Check `components.md` before creating a component. Shared components are presentational: screens own the fetching and pass envelope `data` down as props.
7. **Follow the design system** — Section 2 tokens (CSS custom properties), typography, and spacing; no component library — do not introduce one.
8. **Respect layouts** — Section 4 app shell; project screens start with `ProjectHeader`; there is no public layout.
9. **Use state patterns consistently** — Section 2.5 patterns only; never invent new loading/error UIs.
10. **Use defined breakpoints** — Section 2.6, desktop-first, `max-width` queries downward.
11. **Render user identity only as `UserIdBadge`** — user ids are opaque UUIDs; never render or invent names, emails, or avatars.

### Rules:

- Every frontend task must reference a specific screen shard (`screens/<screen>.md`)
- Every component must handle all 4 states (default, loading, empty, error) unless explicitly noted otherwise
- Use plain CSS with the Section 2 tokens — no styling framework, no CSS-in-JS, no per-component ad-hoc values
- Shared components (`components.md`) must be used instead of duplicating UI across screens
- Day-precision due dates (`YYYY-MM-DD`) are rendered and submitted as-is — never converted through `Date`/timezone APIs
- New screens: create a new shard at `screens/<screen>.md`, add a Screen Inventory row (Section 3), and record the change in the Changelog

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | ui-spec-generation | Initial version — 4 screens (project-list, project-board, task-detail-panel, member-management) + shared components inventory | Derived from stakeholder user flow, Scope Lock V1, data model, and API spec |
