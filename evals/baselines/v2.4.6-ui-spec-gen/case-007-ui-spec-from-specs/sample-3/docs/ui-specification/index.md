# UI Specification — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

## 1. Overview

### 1.1 UI Summary

TaskFlow is a React 18 single-page application (Vite, TanStack Query) with four screens: a project list, a per-project board that groups tasks into three status columns, a task detail overlay carrying the comment thread, and a member-management screen. The primary interaction paradigm is board-centric — drag a card between columns to change its `status` — with small forms (modals and inline fields) for everything else. There is no component library and no CSS framework: plain in-project function components styled with plain CSS against the Section 2 tokens. User identity is opaque throughout: the app renders auth-service UUIDs (truncated, monospace) and never shows names, emails, or avatars — there is no local User entity and no profile endpoint.

### 1.2 Key UI Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component approach | Plain React 18 function components + hooks — no third-party UI library | CLAUDE.md declares none; smallest dependency surface for a 4-screen app |
| Server state | TanStack Query — queries per shard-listed key, mutations invalidate on write | Architecture decision: server state stays server-owned; no client cache of record |
| Client state | Screen-local `useState` / `useReducer` only — no global store | Everything non-server (open dialogs, drafts, filters) is local to one screen |
| Layout pattern | Top header + per-project tab bar (Board / Members); no sidebar | Four screens do not warrant persistent side navigation |
| Responsive strategy | Desktop-first; board columns stack on mobile | Team task tracking is a desktop-primary workflow |
| Accessibility standard | WCAG 2.1 AA | Keyboard path for every pointer interaction (drag-and-drop included — see Section 2.4), visible focus rings, AA contrast for every Section 2.1 pairing |
| Styling approach | Plain CSS: Section 2 tokens as CSS custom properties in `src/ui/theme.css` (planned), kebab-case class names | CLAUDE.md declares no styling system; shared tokens keep the four screens consistent |
| User display | `UserIdBadge` renders truncated opaque UUIDs in monospace — never names or avatars | Opaque auth-service ids; no local User entity to resolve against |
| Drag & drop | Native HTML5 drag events on board cards | Single-card, column-to-column moves need no library |
| Icon set | Minimal in-project inline SVG icons | Only a handful of glyphs needed; no icon dependency |

---

## 2. Design System

### 2.1 Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #2563EB | Primary actions, active tab, links, focus rings |
| `primary-light` | #DBEAFE | Hover backgrounds, owner role pill background, selected card |
| `primary-dark` | #1D4ED8 | Active/pressed button states, owner pill text |
| `secondary` | #0D9488 | Secondary accents (activity feed markers) |
| `neutral-50` | #F8FAFC | App background |
| `neutral-100` | #F1F5F9 | Card and column backgrounds, `UserIdBadge` chip |
| `neutral-200` | #E2E8F0 | Dividers, borders, `todo` status pill background |
| `neutral-700` | #334155 | Secondary text, status pill text |
| `neutral-900` | #0F172A | Primary text |
| `success` | #16A34A | `done` status, success confirmations |
| `warning` | #D97706 | Due-today badge |
| `error` | #DC2626 | Error states, destructive buttons, overdue badge |
| `info` | #0284C7 | `in_progress` status, informational notices |

Semantic mappings: `TaskStatus` pills — `todo` → `neutral-200` background / `neutral-700` text, `in_progress` → `info` tint, `done` → `success` tint. `MemberRole` pills — `owner` → `primary-light` background / `primary-dark` text, `member` → `neutral-200` / `neutral-700`. Due dates — overdue → `error`, due today → `warning`, otherwise `neutral-700`.

### 2.2 Typography Scale

| Level | Size | Weight | Font Family | Usage |
|-------|------|--------|-------------|-------|
| `h1` | 2rem / 32px | 700 | system-ui stack | Page titles ("Projects", project name) |
| `h2` | 1.5rem / 24px | 600 | system-ui stack | Section headings, modal titles |
| `h3` | 1.25rem / 20px | 600 | system-ui stack | Column headers, card titles in detail panel |
| `body` | 1rem / 16px | 400 | system-ui stack | Body text, descriptions, form inputs |
| `body-sm` | 0.875rem / 14px | 400 | system-ui stack | Card metadata, table cells, labels |
| `caption` | 0.75rem / 12px | 400 | system-ui stack | Timestamps, pagination counts, badge text |

Font family for every level: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`; `UserIdBadge` uses the monospace stack `ui-monospace, "Cascadia Mono", Consolas, monospace`.

### 2.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 0.25rem / 4px | Tight internal padding (badges, pills) |
| `space-2` | 0.5rem / 8px | Standard internal padding (buttons, inputs) |
| `space-3` | 0.75rem / 12px | Gaps between cards in a column |
| `space-4` | 1rem / 16px | Card padding, gaps between columns |
| `space-6` | 1.5rem / 24px | Section margins, modal padding |
| `space-8` | 2rem / 32px | Page-level padding |

> **Base unit**: 0.25rem. All spacing is a multiple of the base unit, applied through the CSS custom properties above (e.g. `padding: var(--space-4)`) — no ad-hoc pixel values.

### 2.4 Component Library

**Library**: None — in-project components only (plain React 18 function components; CLAUDE.md declares no component library, so no external primitives are used)
**Version**: n/a (React 18)

| UI Need | Component | Customization Notes |
|---------|-----------|-------------------|
| Buttons | Native `<button>` with `.btn`, `.btn--primary`, `.btn--danger` classes | Action-pending state shows an inline spinner (Section 2.5) |
| Form fields | Native `<input>`, `<textarea>`, `<select>`, `<input type="date">` in a `.field` wrapper with `<label>` | Field-level validation errors render below the control in `error` red |
| Dialogs | `Modal`, `ConfirmDialog` (see `components.md`) built on native `<dialog>` | Focus trapped; Esc and backdrop click close |
| Status pills | `StatusBadge` (`components.md`) | Color mapping in Section 2.1 |
| Due dates | `DueDateBadge` (`components.md`) | Calendar-date display only — never converts through a timezone |
| User identity | `UserIdBadge` (`components.md`) | Truncated UUID, monospace; full id on hover + click-to-copy |
| Assignee picking | `AssigneeSelect` (`components.md`) | Native `<select>` populated from the members list |
| Empty / error / pagination | `EmptyState`, `ErrorBanner`, `PaginationControls` (`components.md`) | Standard patterns in Section 2.5 |
| Drag & drop | Native HTML5 drag events on board cards | Keyboard alternative: change status via the Task Detail status select — every drag outcome is reachable without a pointer |

### 2.5 State Patterns

| State | Pattern | Key Constraints | Example Reference |
|-------|---------|----------------|-------------------|
| Loading (skeleton) | `.skeleton` blocks matching real content dimensions, CSS pulse animation | Match final layout (cards, table rows); show for at least 200ms to avoid flicker | Board renders 3 skeleton cards per column |
| Loading (action) | Inline spinner inside the triggering `<button>`, button disabled, label kept | Action feedback only, never page loads; set `aria-busy="true"` | "Create" button while POST is in flight |
| Empty | `EmptyState`: heading + one-line description + CTA button | Never a blank region; the CTA triggers the relevant create path | "No projects yet" → [New project] |
| Error (inline) | `ErrorBanner`: message + Retry button | Show the envelope's `error.message`; Retry refetches the failed query | Board task fetch fails |
| Error (full-page) | Centered error block: heading + message + link back to `/projects` | Used for 403/404 on route load; never show raw error payloads | Non-member opens a board URL (403 `forbidden`) |
| Disabled | `.is-disabled`: opacity 0.5 + `cursor: not-allowed` | Pair with the `disabled` attribute or `aria-disabled` — never signal by color alone | Remove button while a delete is pending |

Cross-cutting error handling: `401 unauthorized` is intercepted at the TanStack Query client level and triggers the auth redirect (Section 4.2); `400 validation-error` maps `error.fields` onto field-level messages; `409 conflict` renders as an inline field or banner error naming the conflict.

### 2.6 Responsive Breakpoints

| Breakpoint | Width | Media Query (plain CSS) | Primary Use |
|------------|-------|-------------------------|-------------|
| Mobile | < 640px | `@media (max-width: 639px)` | Board columns stack vertically; task detail overlay becomes full-screen; tables scroll horizontally |
| Tablet | 640px – 1023px | `@media (max-width: 1023px)` | Three compressed board columns; activity feed panel overlays instead of docking |
| Desktop | 1024px – 1279px | Base styles (no media query) | Full layout: three comfortable columns, docked activity panel |
| Large Desktop | ≥ 1280px | `@media (min-width: 1280px)` | Content capped at `max-width: 1280px`, centered, extra whitespace |

**Responsive Strategy**: Desktop-first — base styles describe the desktop layout and `max-width` media queries progressively simplify it for tablet and mobile, matching the desktop-primary team workflow.

---

## 3. Screen Inventory

> *This table doubles as the shard directory: every screen listed here has a shard at `screens/<screen>.md` (kebab-case, derived mechanically from the screen name).*

| Screen Name | Route | Auth Required | Parent Layout | Shard | Primary User Action |
|-------------|-------|---------------|---------------|-------|-------------------|
| Project List | `/projects` | Yes | App shell | `screens/project-list.md` | Open or create a project |
| Project Board | `/projects/:projectId/board` | Yes | App shell | `screens/project-board.md` | Move tasks between status columns |
| Task Detail | `/projects/:projectId/tasks/:taskId` | Yes | App shell (overlay panel) | `screens/task-detail.md` | Edit task fields and discuss in comments |
| Project Members | `/projects/:projectId/members` | Yes | App shell | `screens/project-members.md` | Add or remove members |

### 3.1 User Flow Coverage

| Stakeholder Flow Phase | Covered By |
|------------------------|-----------|
| 1. Sign in | No in-app screen — authentication is fully external; the SPA redirects to the auth service (Section 4.2) |
| 2. Create or open a project | Project List (`screens/project-list.md`) |
| 3. Manage membership | Project Members (`screens/project-members.md`) |
| 4. Create and update tasks | Project Board (`screens/project-board.md`) + Task Detail (`screens/task-detail.md`) |
| 5. Assign tasks | Task Detail assignee select; Project Board create-task dialog |
| 6. Discuss and review | Task Detail comment thread; Project Board activity feed panel |

---

## 4. Shared Layouts

### 4.1 App Shell (Authenticated)

Every screen renders inside the app shell: a fixed top header, a project tab bar on project-scoped routes, and the main content area. There is no sidebar. The SPA decodes the JWT subject into `currentUserId` (an opaque UUID) and uses it for role gating and "(you)" badges — it is never resolved to a name.

```
┌────────────────────────────────────────────────────────────────┐
│ Header:  [TaskFlow → /projects]   [Project name]               │
│                          [UserIdBadge (you)]  [Sign out]       │
├────────────────────────────────────────────────────────────────┤
│ Project tab bar (project routes only):                         │
│   [Board]  [Members]                        [⋯ owner menu]     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   Main content area (router outlet)                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Header contents**:
- Left: TaskFlow wordmark (links to `/projects`); on project-scoped routes, the current project name from `GET /api/v1/projects/{id}`
- Right: the caller's `UserIdBadge` with "(you)" suffix, and a Sign out button (clears the in-memory JWT and redirects to the external auth service)

**Project tab bar behavior**:
- Rendered only on `/projects/:projectId/*` routes: Board and Members tabs (active tab underlined in `primary`)
- The ⋯ menu (Rename project…, Delete project…) renders only when `project.ownerId === currentUserId`; its actions are specified in `screens/project-board.md`
- All breakpoints keep the horizontal tabs — two tabs fit even on mobile

### 4.2 Public Layout (Unauthenticated)

**There is no public layout in V1.** Every API endpoint requires a bearer token and the SPA has no unauthenticated screens. The route guard performs a full-page redirect to the external auth service whenever no JWT is held in memory, and the query client does the same on any `401 unauthorized` response. Returning from the auth service with a token, the user lands on `/projects`. This is user flow phase 1 — the auth service owns the entire sign-in UI; the app stores nothing about the user beyond the opaque UUID.

---

## Usage Notes for AI Task Generation

### When generating frontend tasks, use this document set to:

1. **Load only what's referenced** — Read this `index.md` plus ONLY the screen shards named by the work item's impact tables (screen name → `screens/<kebab-case>.md`, e.g. "Project Board" → `screens/project-board.md`), plus `components.md` when a shared component is involved. Do not read the whole `screens/` directory.
2. **Derive component structure** — Use the shard's Component Hierarchy for exactly which components to create or modify. One React file per screen under `src/ui/` (kebab-case file, PascalCase component); shared components under `src/ui/components/` (planned).
3. **Map data requirements** — Use the shard's Component → API Mapping. Components receive DTOs exactly as the API returns them: unwrap the `{ "data": ... }` envelope, read list totals from `meta.totalCount` / `meta.page` / `meta.pageSize`. Never invent fields the DTO does not carry.
4. **Use the shared query keys** — `['projects', {page}]`, `['project', projectId]`, `['tasks', projectId, {assigneeId, page}]`, `['members', projectId, {page}]`, `['comments', taskId, {page}]`, `['feed', projectId, {page}]`. Mutations invalidate the keys their shard names; the only optimistic update is the board drag.
5. **Specify all states** — Every screen task includes default, loading, empty, and error handling exactly as its shard's States table defines, using the Section 2.5 patterns — do not invent new loading or error UIs.
6. **Define interactions precisely** — Use the shard's User Interactions table: exact UI element, result, and API call.
7. **Reuse shared components** — Check `components.md` before creating anything; user ids always render through `UserIdBadge` (never raw UUID text, never a name).
8. **Follow the design system** — Section 2 tokens via CSS custom properties; plain CSS with kebab-case class names; no CSS-in-JS, no utility framework, no component library.
9. **Respect the scope lock** — No labels/tags, notifications, file attachments, or real-time UI anywhere: no such screens, components, fields, or affordances.
10. **Use defined breakpoints** — Section 2.6, desktop-first with `max-width` overrides.

### Rules:

- Every frontend task must reference a specific screen shard (`screens/<screen>.md`)
- Every component must handle all 4 states (default, loading, empty, error) unless its shard explicitly notes otherwise
- Server state lives in TanStack Query only — no copies of API data in component state
- New screens: create a shard at `screens/<screen>.md` (kebab-case from the screen name), add a Screen Inventory row (Section 3), and record the change in the Changelog

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | ui-spec-generation | Initial version: 4 screens (Project List, Project Board, Task Detail, Project Members) + shared components inventory | Derived from stakeholder flow, architecture, data model, and API spec |
