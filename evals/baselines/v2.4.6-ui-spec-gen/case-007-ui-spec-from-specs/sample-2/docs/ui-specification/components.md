---
kind: component-inventory
---

# Shared Components

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Reusable React 18 function components used across multiple screens. Screen-specific components live in the screen's shard (component hierarchy), not here. Files: one component per file under `src/ui/components/` — kebab-case filename, PascalCase component (e.g., `UserIdChip` → `src/ui/components/user-id-chip.tsx`). "Inputs" are props; "Outputs" are callback props.*

## ProjectSubnav

**Used in**: Project Board, Project Members, Project Activity
**Description**: Project-scoped navigation row — project name plus the Board / Members / Activity tabs; owns the project header fetch (`GET /api/v1/projects/{id}`, TanStack Query key `['project', projectId]`) so every project screen shows the name without refetching.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| projectId | Input | string (UUID) | Project whose name and tabs to render |
| active | Input | 'board' \| 'members' \| 'activity' | Which tab is highlighted |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Project loaded | Name (h1) + three tab links, active tab underlined in `primary` |
| Loading | Project fetch in flight | Skeleton bar in place of the name; tabs render immediately |

## UserIdChip

**Used in**: Project List, Project Board, Task Detail, Project Members, Project Activity, App shell header
**Description**: The only way users appear in TaskFlow — renders an opaque auth-service UUID as a monospace chip: first 8 characters shown, full UUID in the `title` tooltip, "(you)" suffix when it equals the authenticated caller's id. Never shows names, emails, or avatars (no local User entity exists — do not extend this component to fetch profiles).

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| userId | Input | string (UUID) \| null | The opaque user id; null renders the empty variant |
| emptyLabel | Input | string | Text for the null case (default "Unassigned") |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Any user id | `neutral-100` chip, monospace truncated id |
| You | `userId` equals the caller's token subject | `secondary`-tinted chip with "(you)" suffix |
| Empty | `userId` is null | Muted `neutral-700` text ("Unassigned" / custom label), no chip background |

## DueDateBadge

**Used in**: Project Board, Task Detail
**Description**: Renders a task's `dueDate` as the literal `YYYY-MM-DD` calendar date — day precision, never timezone-converted (per the TaskDto contract).

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| dueDate | Input | string (`YYYY-MM-DD`) \| null | The task's due date |
| done | Input | boolean | Whether the task status is `done` (suppresses the overdue variant) |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Date set, not past | `neutral-100` badge with the date |
| Overdue | Date before today and `done` is false | `warning` background, bold date |
| None | `dueDate` is null | Muted "No due date" text (Task Detail) or omitted entirely (board cards) |

## Dialog

**Used in**: Project List, Project Board, Project Members
**Description**: Modal wrapper over the native `<dialog>` element used by all create/edit dialogs (CreateProjectDialog, CreateTaskDialog, RenameProjectDialog, AddMemberDialog). Focus trap, initial focus on the first field, Esc and backdrop click close, focus returns to the opener — the WCAG 2.1 AA dialog contract from `index.md` Section 1.2.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | string | Dialog heading (h2) |
| open | Input | boolean | Controls visibility |
| onClose | Output | () => void | Fired on Esc, backdrop click, or ✕ |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Forms | 480px max width, `space-6` padding |
| Wide | Forms with a textarea (task create) | 640px max width |

## ConfirmDialog

**Used in**: Project Board (delete project), Project Members (remove member)
**Description**: Confirmation step for destructive actions, built on `Dialog`. States the consequence in plain language (e.g., "removes all tasks, comments, and members") and shows a pending state on the confirm button while the mutation is in flight.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | string | e.g., "Delete project?" |
| message | Input | string | Consequence statement |
| confirmLabel | Input | string | e.g., "Delete project" |
| pending | Input | boolean | Confirm button pending state (Section 2.5 action-loading pattern) |
| onConfirm | Output | () => void | Fires the mutation |
| onCancel | Output | () => void | Closes without action |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Danger | Destructive actions (both current uses) | `error`-colored confirm button |
| Default | Reserved for non-destructive confirmations | `primary` confirm button |

## EmptyState

**Used in**: Project List, Project Board, Task Detail (comment thread), Project Activity
**Description**: The standard empty pattern from `index.md` Section 2.5 — centered heading, one-line description, and an actionable CTA. Never leave a data region blank.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| heading | Input | string | e.g., "No tasks yet" |
| description | Input | string | One line of guidance |
| ctaLabel | Input | string \| undefined | CTA text; omit to render without a button |
| onCta | Output | () => void | CTA click (opens a dialog or navigates) |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Full data region is empty | Centered block, `space-8` padding |
| Compact | Sub-regions (comment thread, filtered board) | Smaller heading (`h3`), `space-4` padding |

## ErrorBanner

**Used in**: Project List, Project Board, Task Detail, Project Members, Project Activity
**Description**: The standard inline error pattern from `index.md` Section 2.5 — human-readable message mapped from the API Error Catalog `error.code` (never raw payloads), plus a Retry button wired to the TanStack Query `refetch`.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| error | Input | ApiErrorEnvelope (`{ error: { code, message, fields? } }`) | The failed response body (or a synthesized network-failure code) |
| onRetry | Output | () => void \| undefined | Refetch; omit to hide the Retry button |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Query failures inside a region | `error`-tinted banner with Retry |
| Full-page | `403 forbidden` / `404 not-found` on route-level data | Centered block with "Back to projects" link (Section 2.5 full-page pattern) |

## Skeleton

**Used in**: Project List, Project Board, Task Detail, Project Members, Project Activity, ProjectSubnav
**Description**: Loading placeholder implementing the Section 2.5 skeleton pattern — `neutral-200` blocks with a CSS pulse, dimensioned to match the real content, kept visible ≥200ms to avoid flicker.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| variant | Input | 'row' \| 'card' \| 'panel' \| 'line' \| 'bar' | Shape preset (table row, board card, detail panel, feed line, subnav bar) |
| count | Input | number | How many blocks to render (default 1) |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| row | Project List, Project Members tables | Full-width row with column-shaped segments |
| card | Project Board columns | Card-sized block with title and meta lines |
| panel | Task Detail | Title bar + field rows + comment blocks |
| line | Project Activity feed | Single text-height line with leading dot |
| bar | ProjectSubnav project name | Short heading-height bar |

## Pagination

**Used in**: Project List, Project Members, Project Activity
**Description**: Page controls driven directly by the list envelope `meta` (`totalCount`, `page`, `pageSize` — API spec Section 2.4). Renders nothing when `totalCount` ≤ `pageSize`.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| meta | Input | `{ totalCount, page, pageSize }` | The list response `meta` object |
| onPageChange | Output | (page: number) => void | Requests the given page (refetch with `page` param) |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | `totalCount` > `pageSize` | Prev / next + "Page x of y" caption |
| Hidden | `totalCount` ≤ `pageSize` | Renders nothing |
