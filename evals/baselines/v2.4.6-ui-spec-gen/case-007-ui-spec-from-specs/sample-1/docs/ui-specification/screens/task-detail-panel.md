---
kind: screen
screen: task-detail-panel
route: /projects/:projectId/tasks/:taskId
endpoints: [tasks, comments, project-members]
---

# Screen: Task Detail Panel

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: `/projects/:projectId/tasks/:taskId`
**Auth**: Required
**Layout**: App shell — overlay panel docked right over the Project Board (full-screen on mobile); see `index.md` Sections 4.1 and 2.6
**Screen file (planned)**: `src/ui/task-detail-panel.tsx` → `TaskDetailPanel`

Routed overlay for editing one task's fields and discussing it in comments — user-flow steps 4 (update tasks), 5 (assign), and the discussion half of step 6. Closing the panel returns to `/projects/:projectId` with the board still in place underneath.

The V1 API defines **no task delete and no comment delete** — the panel deliberately offers neither. Comment editing is author-only (`authorId` equals the caller's JWT subject).

## Layout Sketch

```
                    (board remains visible, dimmed)
┌──────────────────────────────────────────┬───────────────────────┐
│                                          │ Task Detail        ✕  │
│                                          ├───────────────────────┤
│                                          │ Title (inline edit)   │
│                                          │ Status   [In progress▾]│
│                                          │ Due date [2026-07-20] ⌫│
│                                          │ Assignee [3f2a91c4… ▾]│
│                                          │ Description           │
│                                          │ ┌───────────────────┐ │
│                                          │ │ (textarea)        │ │
│                                          │ └───────────────────┘ │
│                                          │ Created Jul 12 · Updated Jul 15
│                                          ├───────────────────────┤
│                                          │ Comments (7)          │
│                                          │  [Load older]         │
│                                          │  [9f31c2a8…] Jul 14   │
│                                          │  Looks good to me.    │
│                                          │  [3f2a91c4… you] Jul 15 (edited) ✎
│                                          │  Shipping tomorrow.   │
│                                          ├───────────────────────┤
│                                          │ [Write a comment… ][Send]
└──────────────────────────────────────────┴───────────────────────┘
```

## Component Hierarchy

```
TaskDetailPanel
├── PanelHeader
│   ├── TitleInlineEditor               (text input styled as h2; saves on blur/Enter)
│   └── ClosePanelButton
├── TaskFields
│   ├── StatusSelect                    (todo / in_progress / done; shows TaskStatusBadge, shared)
│   ├── DueDateField                    (native input type="date" + Clear button; DueDateBadge, shared)
│   ├── AssigneeSelect                  (Unassigned / one entry per current member, as UserIdBadge, shared)
│   └── DescriptionEditor               (textarea; saves on blur)
├── TaskMeta                            (createdAt / updatedAt captions)
├── CommentThread
│   ├── PaginationControls              (shared — load-more variant, "Load older" at thread top)
│   └── CommentItem (×N)
│       ├── UserIdBadge                 (shared — author)
│       ├── CommentBody                 (plain text; "(edited)" caption when updatedAt > createdAt)
│       └── EditCommentButton           (author only → inline textarea + Save/Cancel)
└── CommentComposer                     (textarea + Send button, 1–5000 chars)
```

`SkeletonBlock`, `EmptyState`, and `ErrorBanner` (shared) render per the States table.

## Component → API Mapping

Endpoints live in `docs/api-spec/endpoints/tasks.md`, `docs/api-spec/endpoints/comments.md`, and `docs/api-spec/endpoints/project-members.md`; all responses use the envelope.

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| TaskDetailPanel (fields) | `{ data: TaskDto }` | GET /api/v1/tasks/{id} | On panel open (route match) |
| AssigneeSelect | `{ data: ProjectMemberDto[], meta }` — current members as options | GET /api/v1/projects/{projectId}/members | On panel open (shares the board's cached query) |
| TitleInlineEditor / StatusSelect / DueDateField / AssigneeSelect / DescriptionEditor | `{ data: TaskDto }` — the updated task | PATCH /api/v1/tasks/{id} | On field commit (blur/Enter/selection) |
| CommentThread | `{ data: CommentDto[], meta }` — `createdAt` ascending (thread order) | GET /api/v1/tasks/{taskId}/comments | On panel open; on "Load older" |
| CommentComposer | `{ data: CommentDto }` — the created comment | POST /api/v1/tasks/{taskId}/comments | On Send |
| CommentItem (edit) | `{ data: CommentDto }` — the updated comment | PATCH /api/v1/comments/{id} | On edit Save (author only) |

## States

Patterns from `index.md` Section 2.5.

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Task and comments loaded | All fields editable; comment thread oldest-first with the composer pinned at the bottom |
| **Loading** | Task fetch in flight | Skeleton lines for title and each field, 3 skeleton comment rows (`SkeletonBlock`), `aria-busy`; fields disabled until loaded |
| **Empty** | Task loaded, `meta.totalCount === 0` comments | Fields render normally; thread shows `EmptyState` (compact): "No comments yet" / "Start the discussion below." (the composer is the CTA) |
| **Error** | Task fetch failed (non-401) | Panel body replaced by `ErrorBanner` with Retry; on 404 `not-found` (task deleted elsewhere): "This task no longer exists" + Close action returning to the board; comment fetch/mutation failures show the banner inside the thread only; 401 triggers the auth redirect |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Edit the title | TitleInlineEditor (saves on blur or Enter) | Optimistic update; board card title updates via the shared query cache; 400 `validation-error` (1–200 chars) restores the old value and shows the field error | PATCH /api/v1/tasks/{id} (body `{ "title": … }`) |
| Change status | StatusSelect | Task moves columns on the board behind the panel (cache update) | PATCH /api/v1/tasks/{id} (body `{ "status": … }`) |
| Set a due date | DueDateField native date input | Saves the picked calendar date **as the literal `YYYY-MM-DD` string** — day precision, no timezone conversion | PATCH /api/v1/tasks/{id} (body `{ "dueDate": "YYYY-MM-DD" }`) |
| Clear the due date | Clear (⌫) button beside DueDateField | Removes the due date; DueDateBadge disappears from the board card | PATCH /api/v1/tasks/{id} (body `{ "dueDate": null }`) |
| Assign the task | AssigneeSelect — pick a member | Sets the assignee; 400 `validation-error` if the user is no longer a current member (options then refresh) | PATCH /api/v1/tasks/{id} (body `{ "assigneeId": … }`) |
| Unassign the task | AssigneeSelect — "Unassigned" option | Clears the assignee | PATCH /api/v1/tasks/{id} (body `{ "assigneeId": null }`) |
| Edit the description | DescriptionEditor (saves on blur) | Updates the description | PATCH /api/v1/tasks/{id} (body `{ "description": … }`) |
| Submit a comment | CommentComposer Send button (disabled while empty or over 5000 chars; inline spinner while pending) | Appends the comment to the thread bottom, clears the composer, scrolls to the new comment | POST /api/v1/tasks/{taskId}/comments |
| Edit own comment | EditCommentButton (✎, visible only on the caller's comments) → inline textarea → Save | Replaces the body; "(edited)" caption appears (updatedAt changes); 403 `forbidden` is impossible via UI (button hidden for non-authors) | PATCH /api/v1/comments/{id} |
| Load older comments | "Load older" (PaginationControls load-more) at thread top | Prepends the next older page, preserving scroll position | GET /api/v1/tasks/{taskId}/comments |
| Close the panel | ✕ button, Esc key, or backdrop click | Navigate back to `/projects/:projectId`; board state is untouched | None |
