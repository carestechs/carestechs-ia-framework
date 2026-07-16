---
kind: screen
screen: task-detail
route: /projects/:projectId/tasks/:taskId
endpoints: [tasks, comments, project-members]
---

# Screen: Task Detail

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: `/projects/:projectId/tasks/:taskId`
**Auth**: Required (any member of the owning project)
**Layout**: App shell (overlay panel above the Project Board) — see `index.md` Section 4.1
**Planned file**: `src/ui/task-detail.tsx` (component `TaskDetailPanel`)

Route-addressable overlay: deep links render the board behind it; closing returns to `/projects/:projectId/board`. Below 640px the panel is full-screen (Section 2.6). Every field edits independently via PATCH — there is no monolithic "save the task" form.

## Layout Sketch

```
(Project Board dimmed behind)   ┌─────────────────────────────────────┐
                                │ [✕]  Task title (inline editable)   │
                                ├─────────────────────────────────────┤
                                │ Status   [To do ▾]                  │
                                │ Due date [2026-07-20] [clear]       │
                                │ Assignee [3f2a91c4… ▾]              │
                                ├─────────────────────────────────────┤
                                │ Description                         │
                                │ ┌─────────────────────────────────┐ │
                                │ │ textarea                        │ │
                                │ └─────────────────────────────────┘ │
                                │ [Save] [Cancel]  (only when edited) │
                                ├─────────────────────────────────────┤
                                │ Comments (oldest → newest)          │
                                │  7b4402ee… · 2026-07-15 14:02       │
                                │  Comment body text          [Edit]  │
                                │  …                                  │
                                │  [Show more comments]               │
                                │ ┌─────────────────────────────────┐ │
                                │ │ Write a comment…        [Post]  │ │
                                │ └─────────────────────────────────┘ │
                                └─────────────────────────────────────┘
```

## Component Hierarchy

```
TaskDetailPanel
├── PanelHeader (close button, inline-editable title)
├── TaskFieldsForm
│   ├── StatusSelect (renders current value as StatusBadge*)
│   ├── DueDateField (date input + [clear]; display via DueDateBadge*)
│   └── AssigneeSelect* (form variant, options from the members list)
├── DescriptionEditor (textarea; Save/Cancel appear when dirty)
└── CommentThread
    ├── CommentItem (author UserIdBadge*, created/edited times, body; [Edit] on own comments)
    ├── ShowMoreCommentsButton (only when more pages exist)
    └── CommentComposer (textarea + [Post])
```

`*` = shared component — see `components.md`. `CommentItem` is the Comment entity's display component; the fields form is the Task entity's detail/edit component.

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/tasks.md, comments.md, project-members.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| TaskDetailPanel | `TaskDto` | GET /api/v1/tasks/{id} | On panel open (route load) |
| AssigneeSelect | Member options, `ProjectMemberDto[]` | GET /api/v1/projects/{projectId}/members | On panel open (cached — shared with the board) |
| PanelHeader title / StatusSelect / DueDateField / AssigneeSelect / DescriptionEditor | Updated `TaskDto` | PATCH /api/v1/tasks/{id} | On each field commit (see User Interactions) |
| CommentThread | `CommentDto[]`, oldest first (thread order) | GET /api/v1/tasks/{taskId}/comments | On panel open; on [Show more comments] (`page`, `pageSize=50`) |
| CommentComposer | Created `CommentDto` | POST /api/v1/tasks/{taskId}/comments | On [Post] |
| CommentItem (inline edit) | Updated `CommentDto` | PATCH /api/v1/comments/{id} | On save of an inline edit (author only) |

Query keys: `['task', taskId]`, `['comments', taskId, { page }]`, `['members', projectId]`. Task field mutations invalidate `['task', taskId]`, `['tasks', projectId]`, and `['feed', projectId]`; comment mutations invalidate `['comments', taskId]` and `['feed', projectId]`.

## States

<!-- Use the standard patterns from index.md Section 2.5 — do not invent new loading/error UIs -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Task loaded | Fields populated from `TaskDto`; thread below in chronological order; composer enabled |
| **Loading** | GET /api/v1/tasks/{id} in flight | Skeleton panel: title bar, 3 field rows, 2 comment rows (Section 2.5) |
| **Empty** | Task loaded, `meta.totalCount === 0` comments | Fields render normally; the thread shows `EmptyState`: "No comments yet" / "Start the discussion." (no CTA — the composer is right below) |
| **Error** | Task GET failed | 404 `not-found`: panel shows "Task not found" + [Close]; 403 `forbidden`: full-page error (Section 2.5) with a link to `/projects`; network failure: `ErrorBanner` + Retry inside the panel. Comment GET failure: `ErrorBanner` + Retry in the thread region only |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Close panel | [✕] button, Esc, or backdrop click | Return to `/projects/:projectId/board`; focus returns to the originating TaskCard | None |
| Edit title | Title text (click or Enter) → input; commit on Enter or blur, Esc cancels | Title updates; 400 `validation-error` → inline error and the previous value is restored | PATCH /api/v1/tasks/{id} with `{ title }` |
| Change status | Status select | Value updates; the board card moves columns via invalidation | PATCH /api/v1/tasks/{id} with `{ status }` |
| Set due date | Date input (`<input type="date">`, day precision — the `YYYY-MM-DD` value is sent as-is, no timezone math) | DueDateBadge updates | PATCH /api/v1/tasks/{id} with `{ dueDate: "YYYY-MM-DD" }` |
| Clear due date | [clear] button beside the date input | Badge and input cleared | PATCH /api/v1/tasks/{id} with `{ dueDate: null }` |
| Assign task | AssigneeSelect option (a current member) | Assignee updates; 400 `validation-error` (id no longer a member) → field error and the members list refetches | PATCH /api/v1/tasks/{id} with `{ assigneeId }` |
| Unassign task | AssigneeSelect "Unassigned" option | Assignee cleared | PATCH /api/v1/tasks/{id} with `{ assigneeId: null }` |
| Save description | [Save] under the textarea (action spinner; [Cancel] restores) | Description updates | PATCH /api/v1/tasks/{id} with `{ description }` |
| Post comment | [Post] button (disabled while empty; action spinner) | Composer clears; comment appears at the thread's end; 400 `validation-error` (1–5000 chars) → field error | POST /api/v1/tasks/{taskId}/comments |
| Edit own comment | [Edit] on a CommentItem where `authorId === currentUserId` → inline textarea → [Save] | Body updates and the edited time refreshes; 403 `forbidden` never occurs from the UI (the button is hidden on others' comments) | PATCH /api/v1/comments/{id} |
| Show more comments | [Show more comments] button (only when more pages exist) | Next page appended in chronological order | GET /api/v1/tasks/{taskId}/comments (`page={n}`, `pageSize=50`) |
