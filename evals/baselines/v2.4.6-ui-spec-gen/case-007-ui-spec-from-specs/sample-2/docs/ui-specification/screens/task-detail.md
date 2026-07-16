---
kind: screen
screen: task-detail
route: /projects/:projectId/tasks/:taskId
endpoints: [tasks, comments, project-members]
---

# Screen: Task Detail

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects/:projectId/tasks/:taskId
**Auth**: Required
**Layout**: App shell — overlay panel over the Project Board (right-side panel on desktop, full-screen below the Tablet breakpoint; see `index.md` Sections 2.6 and 4.1)

One task's fields plus its comment thread. Field edits commit individually (click-to-edit), each as its own PATCH. Covers user flow phases 4, 5, and 6.

## Layout Sketch

```
                    (Project Board remains visible behind)  ┌──────────────────────────┐
                                                            │ Task title (h3, editable)│✕
                                                            ├──────────────────────────┤
                                                            │ Status    [In progress ▾]│
                                                            │ Due date  [2026-07-20][×]│
                                                            │ Assignee  [‹UserIdChip› ▾]│
                                                            ├──────────────────────────┤
                                                            │ Description (editable)   │
                                                            ├──────────────────────────┤
                                                            │ Comments (7)             │
                                                            │ ‹UserIdChip› · caption ts│
                                                            │   Comment body    [Edit] │
                                                            │ …oldest → newest…        │
                                                            ├──────────────────────────┤
                                                            │ [Write a comment…] [Post]│
                                                            └──────────────────────────┘
```

## Component Hierarchy

```
TaskDetailPanel                     — src/ui/task-detail.tsx (one React file per screen)
├── PanelHeader                     — editable title, close (✕ / Esc)
├── TaskFields
│   ├── StatusSelect                — the three TaskStatus values
│   ├── DueDateField                — native <input type="date"> + Clear, renders DueDateBadge
│   └── AssigneeSelect              — "Unassigned" + current members as UserIdChips
├── TaskDescription                 — click-to-edit textarea
├── CommentThread
│   └── CommentItem                 — UserIdChip (authorId), body, createdAt/edited caption, Edit (author only)
├── CommentComposer                 — textarea + Post button
├── EmptyState / ErrorBanner / Skeleton — shared (components.md)
```

## Component → API Mapping

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| TaskDetailPanel | The task (`TaskDto`) | GET /api/v1/tasks/{id} | On panel open |
| AssigneeSelect | Member ids (`ProjectMemberDto[]`) for the options | GET /api/v1/projects/{projectId}/members | On panel open |
| TaskFields / TaskDescription / PanelHeader | Updated task (`TaskDto`) | PATCH /api/v1/tasks/{id} | On individual field commit |
| CommentThread | Comments (`CommentDto[]`, oldest first) | GET /api/v1/tasks/{taskId}/comments | On panel open; "Show older" pages backward when `meta.totalCount` > loaded |
| CommentComposer | Created comment (`CommentDto`) | POST /api/v1/tasks/{taskId}/comments | On Post |
| CommentItem (edit) | Updated comment (`CommentDto`) | PATCH /api/v1/comments/{id} | On save of inline edit (author only) |

> Responses use the envelope from `docs/api-spec/index.md` Section 2.1. `authorId`/`assigneeId` are opaque auth-service UUIDs rendered by `UserIdChip` — never resolved to names.

## States

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Task and comments loaded | All fields populated; comment thread oldest → newest with composer pinned below |
| **Loading** | GET task / comments in flight | Panel-shaped Skeleton: title bar, three field rows, three comment blocks (Section 2.5 pattern) |
| **Empty** | Task loaded, `meta.totalCount` = 0 comments | Fields render normally; thread area shows EmptyState (compact): "No comments yet" / "Start the discussion." — focus CTA moves to the composer |
| **Error** | GET task failed (incl. `404 not-found` / `403 forbidden`) | Panel body replaced by ErrorBanner with Retry; 404/403 variant offers "Back to board" closing the panel. Comment fetch failure shows ErrorBanner in the thread area only |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Edit title | Title text → inline input (Enter/blur commits, Esc cancels) | Optimistic update; invalidate `['task', taskId]` + `['tasks', projectId]` | PATCH /api/v1/tasks/{id} with `{ "title": "…" }` |
| Change status | StatusSelect | Board card moves column on invalidation | PATCH /api/v1/tasks/{id} with `{ "status": "…" }` |
| Set due date | DueDateField date input | Badge updates; value sent as literal `YYYY-MM-DD` (day precision — no timezone conversion) | PATCH /api/v1/tasks/{id} with `{ "dueDate": "YYYY-MM-DD" }` |
| Clear due date | [×] next to date | Badge shows "No due date" | PATCH /api/v1/tasks/{id} with `{ "dueDate": null }` |
| Change assignee | AssigneeSelect | Card chip updates; "Unassigned" sends null | PATCH /api/v1/tasks/{id} with `{ "assigneeId": "…" \| null }` |
| Edit description | Description → textarea, Save/Cancel | Updated text renders | PATCH /api/v1/tasks/{id} with `{ "description": "…" }` |
| Post comment | CommentComposer "Post" (pending state while in flight) | On 201: append to thread, clear composer, invalidate `['comments', taskId]` + `['feed', projectId]` | POST /api/v1/tasks/{taskId}/comments |
| Edit own comment | CommentItem "Edit" (visible only when `authorId` = caller id) → inline textarea → Save | Body updates, caption shows edited time; `403 forbidden` surfaces ErrorBanner (defense in depth) | PATCH /api/v1/comments/{id} |
| Failed field edit | Any field control | 400 `validation-error`: revert optimistic value, render `error.fields` message at the field (e.g., assignee not a current member) | (same PATCH as attempted) |
| Close panel | ✕ button, Esc, or backdrop click | Return to `/projects/:projectId/board`; board state preserved | None |

> Comments have no delete endpoint (hard deletes exist only at the data layer via cascades) — CommentItem intentionally has no delete action.
