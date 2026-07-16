---
kind: component-inventory
---

# Shared Components

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

> *Reusable components used across multiple screens. Screen-specific components (e.g., the board's `TaskCard`) live in their screen's shard, not here. All are React function components with typed props, kebab-case filenames under `src/ui/components/` (planned).*

## UserBadge

**Used in**: Project List, Project Board, Task Detail Panel, Member Management, app-shell header
**Description**: The only way a user is ever rendered. The app stores no names, emails, or avatars — user ids are opaque auth-service UUIDs — so the badge derives a deterministic background color from the UUID hash and shows the id's first 8 characters, making the same user visually recognizable everywhere.
**Code**: `src/ui/components/user-badge.tsx`

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| userId | Input | string (UUID) | The opaque auth-service user id to render |
| size | Input | 'sm' \| 'md' | `sm` in dense rows and cards, `md` in headers and selects |
| onClick | Output | (userId: string) => void | Optional — e.g., apply the board's assignee filter |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default (`md`) | Selects, headers, member rows | Color swatch + 8-char id in `caption` type |
| Compact (`sm`) | TaskCards, comment bylines | Swatch only, id in a tooltip/`title` attribute |
| Unassigned | Null assignee slots | Dashed outline, neutral color, "Unassigned" label |

## Dialog

**Used in**: Project List, Project Board, Member Management
**Description**: Modal wrapper with focus trap, Escape-to-close, and a single primary action; hosts create/rename forms and destructive confirmations.
**Code**: `src/ui/components/dialog.tsx`

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | string | Dialog heading |
| confirmLabel | Input | string | Primary action label |
| destructive | Input | boolean | Renders the primary action in `error` color |
| busy | Input | boolean | Action-loading state: primary button disabled with inline spinner (Section 2.5) |
| onConfirm | Output | () => void | Fired on primary action |
| onClose | Output | () => void | Fired on Escape / ✕ / backdrop click |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Create/rename forms | Primary-colored confirm button |
| Destructive | Irreversible actions (project delete, member removal) | `error`-colored confirm button + warning line |

## EmptyState

**Used in**: Project List, Project Board, Task Detail Panel, Member Management
**Description**: Standard empty pattern — heading, one-line description, optional CTA button; never a blank region (index.md Section 2.5).
**Code**: `src/ui/components/empty-state.tsx`

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| heading | Input | string | Short headline ("No tasks yet") |
| description | Input | string | One-line explanation |
| ctaLabel | Input | string | CTA button label (optional) |
| onCta | Output | () => void | Fired when the CTA is clicked |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Region-sized empty areas (project grid, whole board) | Centered, `space-6` padding |
| Inline | Small slots (single board column, comment thread) | Left-aligned, `space-2` padding, no CTA |

## ErrorBanner

**Used in**: Project List, Project Board, Task Detail Panel, Member Management
**Description**: Standard inline error pattern — human-readable message mapped from the API's stable error codes, plus a retry button for network failures; never shows raw codes or stack traces.
**Code**: `src/ui/components/error-banner.tsx`

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| message | Input | string | Human-readable error text (mapped from the Error Catalog code) |
| retryLabel | Input | string | Retry button label (optional; omit to hide the button) |
| onRetry | Output | () => void | Fired on retry — typically the query's refetch |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Region | Failed screen/section queries | Full-width banner, `error` accent border, retry button |
| Field | Form-level failures (409 conflict, 400 validation) | Compact, attached under the offending input, no retry |
