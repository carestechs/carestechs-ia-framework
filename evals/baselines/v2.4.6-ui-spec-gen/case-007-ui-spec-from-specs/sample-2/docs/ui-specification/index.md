# UI Specification — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

## 1. Overview

### 1.1 UI Summary

TaskFlow's UI is a React 18 SPA (Vite, TanStack Query) served alongside the Express API. Five screens cover the entire V1 flow: a project list, a per-project Kanban board (three `TaskStatus` columns), a task detail overlay panel with the comment thread, a member management screen, and a derived activity feed. The interaction paradigm is click-to-edit with lightweight dialogs; the board adds drag-and-drop between status columns (with a keyboard alternative). All server state lives in the TanStack Query cache; every response arrives in the `{ "data": ... }` envelope (lists add `"meta"`). Users are only ever opaque auth-service UUIDs — the UI renders them with the shared `UserIdChip` and never shows names, emails, or avatars, because no local User entity exists.

### 1.2 Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component approach | In-project React 18 function components + hooks — no UI component library | CLAUDE.md declares no component library; zero added dependencies, full control of markup |
| Server state | TanStack Query — one query/mutation hook per endpoint | Declared in CLAUDE.md; server state stays server-owned (ARCHITECTURE.md) |
| Local state | React `useState`/`useReducer` per component — no global store | Everything shared between screens is server state, already in the Query cache |
| Layout pattern | Top header app shell; project screens add a `ProjectSubnav` tab row (Board / Members / Activity) | Small screen count; tabs match the three per-project views in the user flow |
| Routing | SPA client-side routes as listed in Section 3 (router library is an implementation choice; routes are the contract) | CLAUDE.md declares no router; the spec pins routes, not the dependency |
| Responsive strategy | Desktop-first; layouts simplify downward at the Section 2.6 breakpoints | Team work tool used primarily on desktop; board is the center of gravity |
| Accessibility standard | WCAG 2.1 AA — keyboard path for every pointer interaction (incl. a menu-based alternative to board drag-and-drop), visible focus, 4.5:1 text contrast, dialogs trap focus and close on Esc | Inclusive by default; drag-and-drop and overlay panels are the two known risk areas, so they get explicit contracts |
| Styling approach | Plain CSS with design-token custom properties (`--color-*`, `--space-*`) in a small global stylesheet | CLAUDE.md declares no styling system; tokens keep values consistent without a framework |
| Icon set | None in V1 — text-first UI (a handful of inline SVGs for close/drag affordances only) | No icon dependency; labels beat icons at this screen count |
| User display | Opaque UUIDs via the shared `UserIdChip` (truncated id, full value on hover, "(you)" suffix for the caller) | No local User entity — the API never returns names or profiles; do not invent them |
| Due date display | Render `dueDate` as the literal `YYYY-MM-DD` calendar date — never timezone-converted | The API defines day-precision dates with no time component |

---

## 2. Design System

### 2.1 Brand Colors

> *No brand guidelines exist for TaskFlow; these are the V1 defaults, exposed as CSS custom properties (`--color-primary`, …).*

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #2563EB | Primary actions, active tab, links, focus rings |
| `primary-light` | #DBEAFE | Hover backgrounds, selected rows, drag-over column highlight |
| `primary-dark` | #1D4ED8 | Active/pressed states |
| `secondary` | #0D9488 | Secondary accents (e.g., "(you)" chip highlight) |
| `neutral-50` | #F8FAFC | App background |
| `neutral-100` | #F1F5F9 | Card and column backgrounds |
| `neutral-200` | #E2E8F0 | Dividers, subtle borders, skeleton base |
| `neutral-700` | #334155 | Secondary text, timestamps |
| `neutral-900` | #0F172A | Primary text |
| `success` | #16A34A | Success feedback (e.g., saved confirmation), `done` accents |
| `warning` | #D97706 | Overdue due-date badge |
| `error` | #DC2626 | Error banners, destructive buttons, validation messages |
| `info` | #0284C7 | Informational notices |

### 2.2 Typography Scale

| Level | Size | Weight | Font Family | Usage |
|-------|------|--------|-------------|-------|
| `h1` | 2rem / 32px | 700 | System UI stack¹ | Page titles ("Projects", project name) |
| `h2` | 1.5rem / 24px | 600 | System UI stack | Section headings, dialog titles |
| `h3` | 1.25rem / 20px | 600 | System UI stack | Column headers, task title in detail panel |
| `body` | 1rem / 16px | 400 | System UI stack | Body text, descriptions, comments |
| `body-sm` | 0.875rem / 14px | 400 | System UI stack | Card metadata, table cells, form labels |
| `caption` | 0.75rem / 12px | 400 | System UI stack | Timestamps, `UserIdChip` text, counts |

¹ `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` — no webfont dependency.

### 2.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 0.25rem / 4px | Tight internal padding (chips, badges) |
| `space-2` | 0.5rem / 8px | Standard internal padding (buttons, table cells) |
| `space-3` | 0.75rem / 12px | Gaps between cards in a column, form field gaps |
| `space-4` | 1rem / 16px | Card padding, gaps between board columns |
| `space-6` | 1.5rem / 24px | Section margins, dialog padding |
| `space-8` | 2rem / 32px | Page-level padding |

> **Base unit**: 0.25rem. All spacing is a multiple of the base unit, exposed as CSS custom properties (`--space-1` … `--space-8`) and applied with plain CSS (`padding: var(--space-2)`), per the styling decision in Section 1.2.

### 2.4 Component Library

**Library**: None — in-project React 18 function components (CLAUDE.md declares no component library; shared ones are inventoried in `components.md`)
**Version**: — (React 18)

| UI Need | Component | Customization Notes |
|---------|-----------|-------------------|
| Buttons | Native `<button>` with `.btn`, `.btn-primary`, `.btn-danger` classes | Pending state: disabled + inline spinner (Section 2.5) |
| Form fields | Native `<input>`, `<textarea>`, `<select>` in a `.field` wrapper (label + control + message slot) | Server `validation-error` `fields` messages render in the message slot |
| Date input | Native `<input type="date">` | Emits `YYYY-MM-DD` — matches the `dueDate` wire format exactly, no conversion |
| Tables | Semantic `<table>` with `.table` styles | Header row, row hover; stacks to cards below the Tablet breakpoint |
| Dialogs | Shared `Dialog` wrapper over the native `<dialog>` element | Focus trap, Esc to close, backdrop click closes — see `components.md` |
| Confirmation | Shared `ConfirmDialog` | Danger variant for destructive actions — see `components.md` |
| Drag & drop | Native HTML5 drag events on the board's `TaskCard` | Keyboard alternative required: card menu "Move to …" (Section 1.2 accessibility decision) |
| Feedback states | Shared `Skeleton`, `EmptyState`, `ErrorBanner` | Implement the Section 2.5 patterns — see `components.md` |
| Pagination | Shared `Pagination` driven by the list envelope `meta` | See `components.md` |

### 2.5 State Patterns

| State | Pattern | Key Constraints | Example Reference |
|-------|---------|----------------|-------------------|
| Loading (skeleton) | `Skeleton` placeholder blocks matching the final content layout, CSS pulse animation | Match real content dimensions; keep visible ≥200ms to avoid flicker | `components.md` — Skeleton |
| Loading (action) | Button enters pending state: disabled + inline spinner + `sr-only` "Saving…" | For mutations only, never page loads; the triggering control shows the state | Described inline |
| Empty | `EmptyState`: heading + one-line description + CTA button | Never a blank region; the CTA performs (or navigates to) the creating action | `components.md` — EmptyState |
| Error (inline) | `ErrorBanner`: human-readable message mapped from the Error Catalog `error.code` + Retry button | Retry calls the TanStack Query `refetch`; never show raw error payloads | `components.md` — ErrorBanner |
| Error (full-page) | Route-level error boundary: message + "Back to projects" link | Never raw stack traces; always provide a navigation escape | Described inline |
| Disabled | `.is-disabled`: `opacity: 0.5` + `cursor: not-allowed` | Use opacity, not color swaps — keeps token contrast intact | Described inline |

### 2.6 Responsive Breakpoints

| Breakpoint | Width | Media Query (desktop-first) | Primary Use |
|------------|-------|------------------------------|-------------|
| Mobile | < 640px | `@media (max-width: 639px)` | Single column; board scrolls horizontally with snap; task detail goes full-screen |
| Tablet | 640px – 1023px | `@media (max-width: 1023px)` | Narrower board columns with horizontal scroll; tables keep tabular layout |
| Desktop | 1024px – 1279px | Base styles (no query) | Three board columns side by side; task detail as right-side panel |
| Large Desktop | 1280px+ | `@media (min-width: 1280px)` | Max content width 1280px, centered, extra whitespace |

**Responsive Strategy**: Desktop-first — TaskFlow is a team work tool used primarily on desktop, so base styles target desktop and `max-width` queries progressively simplify layout downward.

---

## 3. Screen Inventory

> *This table doubles as the shard directory: every screen listed here has a shard at `screens/<screen>.md` (kebab-case, per the template Naming Rule).*

| Screen Name | Route | Auth Required | Parent Layout | Shard | Primary User Action |
|-------------|-------|---------------|---------------|-------|-------------------|
| Project List | /projects | Yes | App shell | `screens/project-list.md` | Open or create a project |
| Project Board | /projects/:projectId/board | Yes | App shell + ProjectSubnav | `screens/project-board.md` | Move tasks between status columns |
| Task Detail | /projects/:projectId/tasks/:taskId | Yes | App shell (overlay panel over Project Board) | `screens/task-detail.md` | Edit task fields and discuss in comments |
| Project Members | /projects/:projectId/members | Yes | App shell + ProjectSubnav | `screens/project-members.md` | Add or remove members |
| Project Activity | /projects/:projectId/activity | Yes | App shell + ProjectSubnav | `screens/project-activity.md` | Review recent task and comment changes |

**User flow coverage** (stakeholder definition, Section 3 — every phase maps to a screen or shared layout):

| Flow Phase | Covered By |
|------------|-----------|
| 1. Sign in | Signed-out layout (Section 4.2) — redirect to the external auth service; no in-app screen and no API endpoint (none exists) |
| 2. Create or open a project | Project List (`screens/project-list.md`) |
| 3. Manage membership | Project Members (`screens/project-members.md`) |
| 4. Create and update tasks | Project Board (`screens/project-board.md`) + Task Detail (`screens/task-detail.md`) |
| 5. Assign tasks | Task Detail assignee select; Project Board assignee filter |
| 6. Discuss and review | Task Detail comment thread + Project Activity (`screens/project-activity.md`) |

Out of scope (Scope Lock): no label/tag, notification, or file-attachment screens or components anywhere in this set.

---

## 4. Shared Layouts

### 4.1 App Shell (Authenticated)

Top header only — no sidebar (five screens don't warrant one). Project-scoped screens render the shared `ProjectSubnav` (project name + Board / Members / Activity tabs) directly under the header. There is no notifications icon (notifications are excluded scope) and no global search (no search endpoint exists).

```
┌──────────────────────────────────────────────────────────────┐
│ Header:  TaskFlow → /projects            [UserIdChip (you)]  │
│                                          [Sign out]          │
├──────────────────────────────────────────────────────────────┤
│ ProjectSubnav (project screens only):                        │
│   ‹Project name›      [Board] [Members] [Activity]           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Main content — routed screen renders here                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Header contents**:
- Left: "TaskFlow" wordmark, links to `/projects`
- Right: `UserIdChip` for the authenticated caller (the token's opaque user UUID) + "Sign out" button — sign-out clears the stored token client-side and returns to the signed-out layout; there is no sign-out API call (the external auth service owns sessions)

**Auth behavior**: every route in Section 3 requires a JWT bearer token. Any `401 unauthorized` response clears the token and redirects to the signed-out layout (per the API spec Error Catalog: "client redirects to the external auth service").

### 4.2 Signed-Out Layout (Public)

Sign-in itself happens at the external auth service — the app has no credential UI and no auth endpoints. This layout is a single centered card shown when no token is present.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                 ┌──────────────────────────┐                 │
│                 │        TaskFlow          │                 │
│                 │  [Continue to sign-in →] │  → external     │
│                 └──────────────────────────┘    auth service │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

On return from the auth service with a JWT, the app stores the token and navigates to `/projects`.

---

## Usage Notes for AI Task Generation

### When generating frontend tasks, use this document set to:

1. **Load only what's referenced** — Read this `index.md` plus ONLY the screen shards named by the work item's impact tables (Section 3 maps screen name → shard), plus `components.md` when a shared component is involved. Do not read the whole `screens/` directory.
2. **Derive component structure** — Each screen shard's Component Hierarchy is the component list for that screen. One React file per screen under `src/ui/` (kebab-case filename, PascalCase component, per CLAUDE.md); screen-local subcomponents live in that same file; shared components live one-per-file under `src/ui/components/`.
3. **Map data requirements** — Use the shard's Component → API Mapping. Every endpoint named there exists in `docs/api-spec/` (index Section 4 is the authoritative route list); components consume the envelope's `data` payload, and list components also receive `meta`.
4. **Wire TanStack Query consistently** — one hook per endpoint; suggested query keys: `['projects', page]`, `['project', projectId]`, `['tasks', projectId, filters]`, `['task', taskId]`, `['members', projectId]`, `['comments', taskId]`, `['feed', projectId, page]`. Mutations invalidate the keys named in the shard's interaction Result column.
5. **Specify all states** — Every screen task includes the shard's four states (default / loading / empty / error) using the Section 2.5 patterns — do not invent new loading or error UIs.
6. **Define interactions precisely** — Use the shard's User Interactions table verbatim: UI element, result, exact API method + route.
7. **Reuse shared components** — Check `components.md` before creating anything; `UserIdChip`, `DueDateBadge`, `Dialog`, `ConfirmDialog`, `EmptyState`, `ErrorBanner`, `Skeleton`, `Pagination`, and `ProjectSubnav` already exist as contracts.
8. **Respect the design system and layouts** — Section 2 tokens and patterns; Section 4 shells. New screens must fit these layouts.
9. **Render users as opaque ids only** — always via `UserIdChip`; never fetch, display, or invent names, emails, or avatars (no local User entity, no user endpoints).
10. **Map errors through the Error Catalog** — `validation-error` renders per-field messages from `error.fields`; `conflict` renders inline near the conflicting control; fetch failures render `ErrorBanner` with Retry.

### Rules:

- Every frontend task must reference a specific screen shard (`screens/<screen>.md`)
- Every component must handle all 4 states (default, loading, empty, error) unless the shard explicitly notes otherwise
- Build on the in-project primitives from Section 2.4 — no UI library, no ad-hoc per-component CSS outside the token system
- Shared components (`components.md`) must be used instead of duplicating UI across screens
- Do not add screens or components for excluded scope (labels/tags, notifications, file attachments, real-time collaboration)
- New screens: create a new shard at `screens/<screen>.md`, add a Screen Inventory row (Section 3), and record the change in the Changelog

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | ui-spec-generation | Initial version — 5 screens (project-list, project-board, task-detail, project-members, project-activity) + shared components inventory | Derived from stakeholder user flow, architecture, data model, and API spec |
