---
kind: component-inventory
---

# Shared Components

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

> *Reusable components used across multiple screens. Screen-specific components live in the screen's shard (component hierarchy), not here.*

## TaskCard

**Used in**: Project Board
**Description**: Draggable card rendering a task's title, assignee avatar, and due date.
**Code**: `src/ui/components/task-card.tsx`

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| task | Input | TaskDto | The task to display |
| compact | Input | boolean | Denser layout for narrow columns |
| onOpen | Output | (taskId: string) => void | Fired on click — opens the Task Detail Panel |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Standard board display | Title, avatar, due date |
| Compact | Columns narrower than 240px | Title only, single line |
| Dragging | While being dragged | Elevated shadow, slight tilt |

## Dialog

**Used in**: Project Board, Task Detail Panel
**Description**: Modal wrapper with focus trap, Escape-to-close, and a single primary action; used for confirmations.
**Code**: `src/ui/components/dialog.tsx`

### Inputs / Outputs

| Name | Direction | Type | Description |
|------|-----------|------|-------------|
| title | Input | string | Dialog heading |
| confirmLabel | Input | string | Primary action label |
| destructive | Input | boolean | Renders the primary action in `error` color |
| onConfirm | Output | () => void | Fired on primary action |
| onClose | Output | () => void | Fired on Escape / ✕ / backdrop click |

### Visual Variants

| Variant | When Used | Visual Difference |
|---------|-----------|-------------------|
| Default | Informational confirmations | Primary-colored confirm button |
| Destructive | Irreversible actions (deletions) | `error`-colored confirm button |

## EmptyState

**Used in**: Project Board, Task Detail Panel
**Description**: Standard empty pattern — heading, one-line description, and a CTA button; never a blank region.
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
| Default | Region-sized empty areas | Centered, `space-6` padding |
| Inline | Small slots (single column) | Left-aligned, `space-2` padding, no CTA |
