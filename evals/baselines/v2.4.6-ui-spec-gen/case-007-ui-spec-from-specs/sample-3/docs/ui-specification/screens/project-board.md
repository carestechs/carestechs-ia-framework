---
kind: screen
screen: project-board
route: /projects/:projectId/board
endpoints: [projects, tasks, project-members]
---

# Screen: Project Board

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: `/projects/:projectId/board`
**Auth**: Required (any member of the project; owner-only actions noted below)
**Layout**: App shell + project tab bar — see `index.md` Section 4.1
**Planned file**: `src/ui/project-board.tsx` (component `ProjectBoardPage`)

The board loads all task statuses in one request and groups them into three columns client-side (tasks have no ordering field — column order is API order, `createdAt` descending). The project activity feed — derived on read by the backend, flow phase 6 — renders in a collapsible panel on this screen.

## Layout Sketch

```
┌───────────────────────────────────────────────────────────────────┐
│ Filter: [Assignee ▾ Anyone]                [Activity] [+ New task] │
├───────────────────┬───────────────────┬───────────────┬───────────┤
│ To do (3)         │ In progress (2)   │ Done (5)      │ Activity  │
│ ┌───────────────┐ │ ┌───────────────┐ │ ┌───────────┐ │ feed      │
│ │ Task title    │ │ │ Task title    │ │ │ Task title│ │ panel     │
│ │ [due] [status]│ │ └───────────────┘ │ └───────────┘ │ (docked   │
│ │ [assignee]    │ │                   │               │ when open;│
│ └───────────────┘ │                   │               │ overlay   │
│ ┌───────────────┐ │                   │               │ < 1024px) │
│ │ …             │ │                   │               │           │
│ └───────────────┘ │                   │               │           │
└───────────────────┴───────────────────┴───────────────┴───────────┘
```

## Component Hierarchy

```
ProjectBoardPage
├── BoardToolbar
│   ├── AssigneeSelect* (filter variant, default "Anyone")
│   ├── ActivityToggleButton
│   └── NewTaskButton
├── BoardColumn ×3 (todo / in_progress / done — grouped client-side by status)
│   └── TaskCard (title, StatusBadge*, DueDateBadge*, assignee UserIdBadge*; draggable)
├── ActivityFeedPanel (collapsible)
│   ├── ActivityEventItem (event type, task title, actor UserIdBadge*, relative time)
│   └── PaginationControls* (compact variant)
├── CreateTaskModal (Modal*: title, description, status, due date, AssigneeSelect*)
├── RenameProjectModal (Modal*: name + description — owner only, opened from the ⋯ menu)
└── DeleteProjectConfirm (ConfirmDialog* — owner only, opened from the ⋯ menu)
```

`*` = shared component — see `components.md`. `TaskCard` is the Task entity's compact display component; `ActivityEventItem` renders `ActivityEventDto` rows (task events carry no actor — the actor badge renders only for `comment_added`).

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/projects.md, tasks.md, project-members.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| App shell header / ⋯ menu gating | `ProjectDto` (name, `ownerId` — owner gating is `ownerId === currentUserId`) | GET /api/v1/projects/{id} | On route load |
| BoardColumn ×3 | Project tasks, `TaskDto[]`, all statuses | GET /api/v1/projects/{projectId}/tasks | On route load (`pageSize=100`); refetch on filter change and after mutations |
| AssigneeSelect (filter) | Member options, `ProjectMemberDto[]` | GET /api/v1/projects/{projectId}/members | On first open of the filter (cached, shared with CreateTaskModal) |
| TaskCard (drag) | Updated `TaskDto` (status change) | PATCH /api/v1/tasks/{id} | On drop into another column |
| CreateTaskModal | Created `TaskDto`; member options for its AssigneeSelect | POST /api/v1/projects/{projectId}/tasks | On form submit |
| ActivityFeedPanel | `ActivityEventDto[]`, newest first | GET /api/v1/projects/{projectId}/feed | On panel open; on page change (`page`, `pageSize=50`) |
| RenameProjectModal | Updated `ProjectDto` | PATCH /api/v1/projects/{id} | On form submit (owner only) |
| DeleteProjectConfirm | — (204, no body) | DELETE /api/v1/projects/{id} | On confirm (owner only) |

Query keys: `['project', projectId]`, `['tasks', projectId, { assigneeId, page }]`, `['members', projectId]`, `['feed', projectId, { page }]`. Task mutations invalidate `['tasks', projectId]` and `['feed', projectId]`; project mutations invalidate `['project', projectId]` and `['projects']`.

## States

<!-- Use the standard patterns from index.md Section 2.5 — do not invent new loading/error UIs -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Tasks exist for the current filter | Three columns with cards grouped by status; column headers show counts; when `meta.totalCount` exceeds the loaded count, a [Load more] button renders under the columns |
| **Loading** | Initial tasks GET in flight | Three skeleton columns with 3 skeleton cards each (Section 2.5) |
| **Empty** | `meta.totalCount === 0` with no filter — or 0 results with an assignee filter | No filter: `EmptyState` across the board, "No tasks yet" / "Create the project's first task." / [New task] CTA. Filtered: "No tasks for this assignee" + [Clear filter] |
| **Error** | Tasks GET failed | `ErrorBanner` + Retry above the columns. Project GET 403/404 → full-page error (Section 2.5) with a link back to `/projects` |

ActivityFeedPanel has its own region states: loading = 3 skeleton rows; empty = `EmptyState` ("No activity yet" / "Task and comment changes will appear here."); error = inline `ErrorBanner` + Retry inside the panel.

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Move task between columns | TaskCard (HTML5 drag, drop on another column) | Card moves optimistically; on error the move reverts and an `ErrorBanner` shows | PATCH /api/v1/tasks/{id} with `{ status }` |
| Move task without a pointer | Keyboard: focus card, Enter opens Task Detail, change the status select there | Same status change via the detail panel (WCAG keyboard path) | PATCH /api/v1/tasks/{id} — see `screens/task-detail.md` |
| Open task | TaskCard (click or Enter) | Navigate to `/projects/:projectId/tasks/:taskId` — detail opens as an overlay panel | GET /api/v1/tasks/{id} (fired by the detail screen) |
| Filter by assignee | AssigneeSelect (filter variant; options: Anyone, Unassigned, each member) | Tasks refetched with the `assigneeId` query parameter; columns re-render | GET /api/v1/projects/{projectId}/tasks (`assigneeId={userId}`) |
| Open create dialog | [+ New task] button | CreateTaskModal opens, title focused; status defaults to `todo` | None until submit |
| Create task | [Create] button in modal (action spinner) | On 201: modal closes, card appears in its status column; 400 `validation-error` (incl. assignee not a member) → field errors | POST /api/v1/projects/{projectId}/tasks |
| Toggle activity panel | [Activity] button in toolbar | Panel docks right (overlays below 1024px); feed fetched on first open | GET /api/v1/projects/{projectId}/feed (`page=1`, `pageSize=50`) |
| Open task from feed | ActivityEventItem (click) | Navigate to the event's task detail overlay (`event.taskId`) | GET /api/v1/tasks/{id} (fired by the detail screen) |
| Page through feed | PaginationControls (compact) in panel footer | Fetch and render the requested feed page | GET /api/v1/projects/{projectId}/feed (`page={n}`, `pageSize=50`) |
| Rename project | ⋯ menu → "Rename project…" (owner only) | RenameProjectModal; on 200 the header name updates; 409 `conflict` → field error "This name is already taken" | PATCH /api/v1/projects/{id} |
| Delete project | ⋯ menu → "Delete project…" (owner only) | ConfirmDialog (danger): "This permanently deletes the project, its tasks, comments, and memberships."; on 204 navigate to `/projects` | DELETE /api/v1/projects/{id} |
| Load more tasks | [Load more] under the columns (only when `meta.totalCount` > loaded count) | Next page appended and regrouped into columns | GET /api/v1/projects/{projectId}/tasks (`page={n}`, `pageSize=100`) |
