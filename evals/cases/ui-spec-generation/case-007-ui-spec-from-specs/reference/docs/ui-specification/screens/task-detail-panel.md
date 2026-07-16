---
kind: screen
screen: task-detail-panel
route: /projects/:projectId/tasks/:taskId
endpoints: [tasks, comments, project-members]
---

# Screen: Task Detail Panel

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects/:projectId/tasks/:taskId
**Auth**: Required
**Layout**: App shell — overlay panel over the Project Board, see `index.md` Section 4.1
**Code**: `src/ui/task-detail-panel.tsx` (planned)

## Layout Sketch

```
                        ┌───────────────────────────────────┐
   (board dimmed        │ Title (inline edit)           ✕   │
    behind panel)       ├───────────────────────────────────┤
                        │ Status ▾   Due date 📅   Assignee ▾│
                        ├───────────────────────────────────┤
                        │ Description (textarea, autosave)  │
                        ├───────────────────────────────────┤
                        │ Comments (oldest first)           │
                        │ ⬤ badge · body · timestamp [edit] │
                        │ ⬤ badge · body · timestamp        │
                        │ ┌───────────────────────────────┐ │
                        │ │ CommentComposer      [Post]   │ │
                        │ └───────────────────────────────┘ │
                        └───────────────────────────────────┘
```

## Component Hierarchy

```
TaskDetailPanel
├── PanelHeader
│   ├── InlineTitleEdit
│   └── CloseButton
├── TaskFieldsRow
│   ├── StatusSelect (todo / in_progress / done)
│   ├── DueDatePicker (calendar date only — emits YYYY-MM-DD, clearable)
│   └── AssigneeSelect (options as UserBadge — shared; "Unassigned" option)
├── DescriptionEditor
├── CommentThread
│   ├── CommentItem (×N — UserBadge author, body, timestamp; edit affordance on own comments)
│   └── EmptyState (inline variant, when no comments — shared)
├── CommentComposer
└── ErrorBanner (shared)
```

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/{tasks,comments,project-members}.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| TaskDetailPanel | Task detail | GET /api/v1/tasks/{id} | On open |
| InlineTitleEdit / StatusSelect / DueDatePicker / AssigneeSelect / DescriptionEditor | Field update | PATCH /api/v1/tasks/{id} | On field commit (blur or selection) |
| AssigneeSelect | Current member list for options | GET /api/v1/projects/{projectId}/members | On dropdown open |
| CommentThread | Task's comments | GET /api/v1/tasks/{taskId}/comments | On open; on page change |
| CommentComposer | New comment | POST /api/v1/tasks/{taskId}/comments | On submit |
| CommentItem (own) | Edited comment | PATCH /api/v1/comments/{id} | On inline-edit save |

## States

<!-- Use the standard patterns from index.md Section 2.5 -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Task and comments loaded | Fields editable; thread oldest-first with composer at the bottom |
| **Loading** | Task or comments query in flight | Skeleton panel matching field/thread layout; composer disabled |
| **Empty** | Task has no comments | Inline `EmptyState` in the thread: "No comments yet — start the discussion"; fields unaffected |
| **Error** | Task query failed (e.g., `not-found` after deletion) | Panel-wide `ErrorBanner` with retry + close affordance; comments-only failure shows the banner inside the thread |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Edit the title | InlineTitleEdit (commit on blur/Enter) | Title updates on card and panel | PATCH /api/v1/tasks/{id} (`title`) |
| Change status | StatusSelect | Card moves column behind the panel | PATCH /api/v1/tasks/{id} (`status`) |
| Pick or clear a due date | DueDatePicker | Chip updates; clearing sends null | PATCH /api/v1/tasks/{id} (`dueDate`: `YYYY-MM-DD` or null) |
| Assign / unassign | AssigneeSelect | `UserBadge` updates; "Unassigned" sends null | PATCH /api/v1/tasks/{id} (`assigneeId`) |
| Edit the description | DescriptionEditor (commit on blur) | Text persists | PATCH /api/v1/tasks/{id} (`description`) |
| Post a comment | CommentComposer submit | Comment appends to the thread; composer clears | POST /api/v1/tasks/{taskId}/comments |
| Edit own comment | CommentItem edit affordance (author only) | Body updates in place with "edited" timestamp | PATCH /api/v1/comments/{id} |
| Close the panel | CloseButton / Escape / backdrop click | Route returns to /projects/:projectId/board | None |
