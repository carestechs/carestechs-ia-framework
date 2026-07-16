---
kind: component-inventory
---

# Shared Components

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Reusable React function components used across multiple screens. Screen-specific components live in the screen's shard (component hierarchy), not here. All are hand-rolled (no component library — see `index.md` Section 2.4), presentational, and styled with the Section 2 design tokens: screens own the data fetching (TanStack Query, envelope `{ data, meta }`) and pass `data` down as props; "Output" rows are React callback props. The endpoint each component's data comes from is listed in the consuming screen's Component → API Mapping.*

## ProjectHeader

**Used in**: Project Board, Member Management
**Description**: Per-project navigation strip — back link to `/projects`, the project name, and the Board / Members tab pair.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| project | Input | ProjectDto | Supplies the name; `ownerId` is not rendered here |
| activeTab | Input | 'board' \| 'members' | Which tab is highlighted |

Navigation is via router links — no callback props.

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Project loaded | Name as `h1`, active tab underlined in `primary` |
| Loading | Project fetch in flight | Skeleton line in place of the name; tabs disabled |

## UserIdBadge

**Used in**: Project List, Project Board, Task Detail Panel, Member Management (and the app-shell app bar)
**Description**: The only user-identity rendering in the app — a monospace pill showing the first 8 characters of an opaque auth-service UUID, with the full id available on hover/focus (`title`) and a "you" marker when the id equals the caller's JWT subject. Never a name, email, or avatar: the API does not have them.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| userId | Input | string (UUID) | The opaque auth-service user id to display |
| isCaller | Input | boolean | Appends the "you" marker (`secondary` accent) |
| compact | Input | boolean | Drops the "you" marker text, id only |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Tables, comments, feed items | `neutral-100` pill, `mono` type, first 8 chars + "…" |
| You | `isCaller` true | Adds a `secondary`-colored "you" tag |
| Compact | Card assignee slot, select options | Pill only, tighter padding (`space-1`) |

## TaskStatusBadge

**Used in**: Project Board, Task Detail Panel
**Description**: Color-coded pill for the `TaskStatus` enum — the visual anchor of board columns and the status field.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| status | Input | 'todo' \| 'in_progress' \| 'done' | Which status to render |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| To do | `status === 'todo'` | `info` accent, label "To do" |
| In progress | `status === 'in_progress'` | `warning` accent, label "In progress" |
| Done | `status === 'done'` | `success` accent, label "Done" |

## DueDateBadge

**Used in**: Project Board, Task Detail Panel
**Description**: Renders a task's day-precision due date. The `dueDate` string (`YYYY-MM-DD`, no time, no timezone) is formatted **as literal calendar-date parts — never passed through `Date`/timezone conversion**, so the shown day can't drift across timezones. Hidden when `dueDate` is null.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| dueDate | Input | string (`YYYY-MM-DD`) | The calendar date to display |
| doneTask | Input | boolean | Suppresses overdue/due-soon emphasis on `done` tasks |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Due more than 2 days out | `neutral-200` outline, caption type |
| Due soon | Due today or within 2 days (and not done) | `warning` accent |
| Overdue | Date before today (and not done) | `error` accent, bold |

## ModalDialog

**Used in**: Project List, Project Board, Member Management
**Description**: Accessible modal primitive hosting every create/edit form — focus trap, focus restore on close, Esc and backdrop close, `role="dialog"` + `aria-modal`, labelled by its title.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | string | Dialog heading (`h2`), also the `aria-label` source |
| open | Input | boolean | Controls mount/visibility |
| children | Input | ReactNode | Form content supplied by the consuming screen |
| onClose | Output | () => void | Fired on ✕, Esc, or backdrop click |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Desktop/tablet | Centered card, max-width 480px, `space-6` padding |
| Full-screen | Mobile (< 640px, Section 2.6) | Fills the viewport |

## ConfirmDialog

**Used in**: Project List (delete project), Member Management (remove member)
**Description**: Destructive-action confirmation built on `ModalDialog` — states the consequence (cascade delete, task unassignment) and requires an explicit button press; confirm button carries the action spinner while pending.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | string | e.g. "Delete project?" |
| message | Input | string | Consequence sentence shown in the body |
| confirmLabel | Input | string | e.g. "Delete", "Remove" |
| pending | Input | boolean | Disables buttons, shows the inline spinner |
| onConfirm | Output | () => void | Fires the mutation |
| onCancel | Output | () => void | Closes without acting |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Danger | All V1 uses (delete/remove) | Confirm button in `error` red (`.btn-danger`) |

## EmptyState

**Used in**: Project List, Project Board, Task Detail Panel, Member Management
**Description**: The standard empty pattern (Section 2.5): centered heading + one-line description + actionable CTA — a region is never left blank.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| heading | Input | string | e.g. "No tasks yet" |
| description | Input | string | One supporting sentence |
| ctaLabel | Input | string \| undefined | CTA text; omit to render without a button |
| compact | Input | boolean | Smaller type/padding for in-panel use |
| onCtaClick | Output | () => void | Fired when the CTA is pressed |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Full content regions (list, board) | Centered, `h2` heading, `space-8` padding |
| Compact | Inside panels (comment thread, member list) | `h3` heading, `space-4` padding, no illustration space |

## ErrorBanner

**Used in**: Project List, Project Board, Task Detail Panel, Member Management
**Description**: The inline error pattern (Section 2.5): maps the stable Error Catalog `error.code` to a human-readable message and offers Retry. Announced via `role="alert"`. 401 `unauthorized` is never rendered — it triggers the auth redirect (index Section 4.2).

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| error | Input | { code: string, message: string } | The envelope `error` object from the failed call |
| onRetry | Output | (() => void) \| undefined | Refetches; omit to hide the Retry button |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Recoverable fetch failures | `error`-tinted banner, message + Retry button |
| Blocking | Region cannot render (task 404, membership 403) | Fills the region, adds a navigation escape link instead of Retry |

## SkeletonBlock

**Used in**: Project List, Project Board, Task Detail Panel, Member Management
**Description**: The loading-skeleton pattern (Section 2.5): pulse-animated placeholder sized to match the real content; parent container sets `aria-busy="true"`.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| variant | Input | 'row' \| 'card' \| 'line' | Table row, board card, or single text line shape |
| count | Input | number | How many placeholders to render (default 3) |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Row | Project/member tables | Full-width bar at table-row height |
| Card | Board columns | Card-sized block with inner line hints |
| Line | Header names, panel fields | Single text-height bar |

## PaginationControls

**Used in**: Project List, Project Board, Task Detail Panel, Member Management
**Description**: Envelope-driven paging for the offset pagination convention (`page`/`pageSize`, `meta.totalCount`). Two modes: a Prev/Next pager for tables, and a load-more button for append/prepend flows (board tasks, activity feed, older comments).

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| meta | Input | { totalCount, page, pageSize } | The list response `meta` object |
| variant | Input | 'pager' \| 'load-more' | Presentation mode |
| loadedCount | Input | number \| undefined | Items shown so far (load-more label: "Load more (42 of 120)") |
| pending | Input | boolean | Disables controls, shows the inline spinner |
| onPageChange | Output | (page: number) => void | Requests the given page |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Pager | Project List, Member Management tables | "‹ Page X of Y ›" buttons, right-aligned |
| Load more | Board tasks, activity feed, older comments | Single full-width button with progress count |
