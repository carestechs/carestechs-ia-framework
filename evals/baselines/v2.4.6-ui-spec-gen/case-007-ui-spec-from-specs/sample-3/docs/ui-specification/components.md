---
kind: component-inventory
---

# Shared Components

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Reusable components used across multiple screens. Screen-specific components (ProjectCard, TaskCard, MemberRow, CommentItem, ActivityEventItem, …) live in their screen's shard, not here. Planned location: `src/ui/components/<component>.tsx` — kebab-case filename, PascalCase component export (e.g. `UserIdBadge` → `src/ui/components/user-id-badge.tsx`). All components are React 18 function components; "Input" rows are props, "Output" rows are callback props. Data props carry DTOs exactly as the API returns them (camelCase, unwrapped from the `{ "data": ... }` envelope).*

## UserIdBadge

**Used in**: Project List, Project Board, Task Detail, Project Members
**Description**: Renders an opaque auth-service user UUID as a truncated monospace chip (first 8 characters + ellipsis) — the app's only representation of a person; it never shows names, emails, or avatars because none exist.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| userId | Input | `string \| null` | The opaque UUID to display; `null` renders the Unassigned variant |
| isCurrentUser | Input | `boolean` | Appends "(you)" when the id equals the caller's token subject |

No callback props. The full UUID is exposed via the `title` attribute, and clicking the badge copies it to the clipboard (with a brief "Copied" confirmation for screen readers via a live region).

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Any user reference (owner, assignee, author, member) | `neutral-100` chip, monospace truncated UUID |
| You | `isCurrentUser` is true | Adds "(you)" suffix in `neutral-700` |
| Unassigned | `userId` is `null` (task assignee display) | Italic "Unassigned" in `neutral-700`, no chip background |

## StatusBadge

**Used in**: Project Board, Task Detail
**Description**: Pill displaying a `TaskStatus` value with the Section 2.1 semantic color mapping and a human label.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| status | Input | `'todo' \| 'in_progress' \| 'done'` | The task's workflow state |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| To do | `status === 'todo'` | `neutral-200` background, `neutral-700` text |
| In progress | `status === 'in_progress'` | `info` tint background, `info` text |
| Done | `status === 'done'` | `success` tint background, `success` text |

## DueDateBadge

**Used in**: Project Board, Task Detail
**Description**: Renders a task's day-precision due date (`YYYY-MM-DD`) with urgency coloring. Comparisons use the calendar date only — the value is never parsed through a timezone.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| dueDate | Input | `string \| null` | `YYYY-MM-DD` calendar date; `null` renders nothing |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Upcoming | Due date after today | `neutral-700` text, calendar glyph |
| Due today | Due date equals today | `warning` text and glyph |
| Overdue | Due date before today | `error` text and glyph, bold |

## AssigneeSelect

**Used in**: Project Board (create-task dialog, toolbar filter), Task Detail
**Description**: Native `<select>` of the project's current members (rendered as truncated UUIDs), for choosing a task assignee or filtering the board. Options come from `GET /api/v1/projects/{projectId}/members` via the shared `['members', projectId]` query.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| members | Input | `ProjectMemberDto[]` | Current members to offer as options |
| value | Input | `string \| null` | Selected user id; `null` selects the empty option |
| variant | Input | `'form' \| 'filter'` | Which empty option set to show (see variants) |
| disabled | Input | `boolean` | Disabled while a related mutation is pending |
| onChange | Output | `(userId: string \| null) => void` | Fires with the chosen member's id, or `null` for the empty option |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Form | Create-task dialog, Task Detail assignee field | First option "Unassigned" (`null`) |
| Filter | Board toolbar | First options "Anyone" (no filter) and "Unassigned"; selected filter tinted `primary-light` |

## Modal

**Used in**: Project List (create project), Project Board (create task, rename project)
**Description**: Dialog wrapper built on the native `<dialog>` element: title bar, body slot, footer slot; focus is trapped while open and returned to the trigger on close.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | `string` | Title bar text (`h2` level) |
| open | Input | `boolean` | Controls the native `<dialog>` open state |
| children | Input | `ReactNode` | Body content (form fields) |
| footer | Input | `ReactNode` | Action row (primary/secondary buttons) |
| onClose | Output | `() => void` | Fires on Esc, backdrop click, or the ✕ button |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Create/rename forms | 480px width (full-width below 640px), neutral title bar |
| Danger | Wrapped by ConfirmDialog for destructive actions | `error` accent on the title bar |

## ConfirmDialog

**Used in**: Project Board (delete project), Project Members (remove member)
**Description**: A Modal preconfigured for confirm/cancel decisions on destructive actions, stating the consequence before the user commits.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | `string` | e.g. "Delete project?" |
| message | Input | `string` | Consequence statement, e.g. "Their assigned tasks in this project become unassigned." |
| confirmLabel | Input | `string` | Confirm button text, e.g. "Delete project" |
| busy | Input | `boolean` | Shows the action spinner in the confirm button and disables both buttons |
| onConfirm | Output | `() => void` | Fires the mutation |
| onCancel | Output | `() => void` | Closes without acting |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Danger | Deletes and removals (both current uses) | `.btn--danger` confirm button, Danger Modal title bar |
| Neutral | Reserved for non-destructive confirmations | `.btn--primary` confirm button |

## EmptyState

**Used in**: Project List, Project Board, Task Detail (comment thread), Project Members
**Description**: Standard empty-region block per Section 2.5 — heading, one-line description, and an optional CTA; never a blank region.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| heading | Input | `string` | e.g. "No tasks yet" |
| description | Input | `string` | One-line explanation or next step |
| ctaLabel | Input | `string \| undefined` | CTA button text; omitted → no button |
| onCta | Output | `() => void` | Fires the create path (open modal, focus form) |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| With CTA | Caller can act (create project/task, add member) | Primary button below the description |
| Hint only | No action applies (no comments yet; non-owner member list) | Heading + description only |

## ErrorBanner

**Used in**: Project List, Project Board, Task Detail, Project Members
**Description**: Inline error block per Section 2.5 showing the response envelope's `error.message` with an optional Retry; announced via `role="alert"`.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| message | Input | `string` | Human-readable message from `error.message` |
| onRetry | Output | `(() => void) \| undefined` | Refetches the failed query; omitted → no Retry button |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| With retry | Recoverable fetch failures (network, 5xx) | `error`-tinted banner + [Retry] button |
| Without retry | Non-recoverable responses surfaced inline (e.g. 409 on a form) | Banner only |

## PaginationControls

**Used in**: Project List, Project Members, Project Board (activity feed panel)
**Description**: Offset pagination controls driven by the list envelope's `meta` (`totalCount`, `page`, `pageSize`); hidden entirely when `totalCount <= pageSize`.

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| page | Input | `number` | Current page (1-based, from `meta.page`) |
| pageSize | Input | `number` | From `meta.pageSize` |
| totalCount | Input | `number` | From `meta.totalCount` |
| onPageChange | Output | `(page: number) => void` | Fires with the requested page; the screen refetches its query |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Full-width lists (Project List, Project Members) | [← Prev] "Page X of Y (N total)" [Next →] |
| Compact | Activity feed panel footer | [← Prev] / [Next →] only, `caption` size |
