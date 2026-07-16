---
kind: screen
screen: project-board
route: /projects/:projectId
endpoints: [projects, tasks, project-members]
---

# Screen: Project Board

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: `/projects/:projectId`
**Auth**: Required
**Layout**: App shell — see `index.md` Section 4.1
**Screen file (planned)**: `src/ui/project-board.tsx` → `ProjectBoardPage`

The project's home: three fixed status columns (`todo`, `in_progress`, `done`) of task cards, task creation, an assignee filter, and a toggleable activity feed panel. Covers user-flow steps 4 (create/update tasks), 5 (assign), and the feed half of step 6. The Task Detail Panel (`screens/task-detail-panel.md`) opens over this screen via its own route.

Tasks have **no ordering/position field** — columns group by `status`, and within a column cards render in the API's `createdAt` descending order. Dragging between columns changes status only; there is no within-column reordering.

## Layout Sketch

```
┌──────────────────────────────────────────────────────────────────┐
│ App bar (shell)                                                  │
├──────────────────────────────────────────────────────────────────┤
│ ProjectHeader: ‹ Projects  Apollo            [Board] [Members]   │
├──────────────────────────────────────────────────────────────────┤
│ Assignee: [All ▾]                    [Activity]  [+ New task]    │
├────────────────────┬────────────────────┬────────────┬──────────┤
│ To do (4)          │ In progress (2)    │ Done (7)   │ Activity │
│ ┌────────────────┐ │ ┌────────────────┐ │ ┌────────┐ │ (panel,  │
│ │ Fix onboarding │ │ │ Ship API docs  │ │ │ ...    │ │  toggled)│
│ │ [todo] Jul 20  │ │ │ [in_progress]  │ │ └────────┘ │ ─────────│
│ │ [9f31c2a8…]  ⋮ │ │ │ overdue Jul 10 │ │            │ Comment  │
│ └────────────────┘ │ │ [3f2a91c4…]  ⋮ │ │            │ added on │
│ ┌────────────────┐ │ └────────────────┘ │            │ "Ship…"  │
│ │ + drag target  │ │                    │            │ by       │
│ └────────────────┘ │                    │            │ [9f31c2…]│
├────────────────────┴────────────────────┴────────────┴──────────┤
│                    [Load more tasks (42 of 120)]                 │
└──────────────────────────────────────────────────────────────────┘
```

Mobile (< 640px): columns stack vertically; the activity panel becomes a full-screen overlay.

## Component Hierarchy

```
ProjectBoardPage
├── ProjectHeader                       (shared — project name + Board/Members tabs)
├── BoardToolbar
│   ├── AssigneeFilter                  (select: All / Unassigned / one entry per member, as UserIdBadge)
│   ├── ActivityToggleButton
│   └── NewTaskButton
├── BoardColumns
│   ├── BoardColumn (status: todo)
│   │   └── TaskCard (×N)
│   │       ├── TaskStatusBadge         (shared)
│   │       ├── DueDateBadge            (shared — hidden when dueDate is null)
│   │       ├── UserIdBadge             (shared — assignee; "Unassigned" text when null)
│   │       └── CardActionsMenu         (keyboard fallback: "Move to…" status items)
│   ├── BoardColumn (status: in_progress)
│   └── BoardColumn (status: done)
├── LoadMoreBar → PaginationControls    (shared — load-more variant)
├── CreateTaskDialog → ModalDialog      (shared)
└── ActivityFeedPanel
    └── ActivityFeedItem (×N)           (event text + task title + occurredAt; UserIdBadge for comment actors)
```

`SkeletonBlock`, `EmptyState`, and `ErrorBanner` (shared) render per the States table. The feed panel manages its own loading/empty/error states independently of the board.

## Component → API Mapping

Endpoints live in `docs/api-spec/endpoints/projects.md`, `docs/api-spec/endpoints/tasks.md`, and `docs/api-spec/endpoints/project-members.md`; all responses use the envelope.

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectHeader | `{ data: ProjectDto }` — name for the header | GET /api/v1/projects/{id} | On page load |
| BoardColumns / TaskCard | `{ data: TaskDto[], meta }` — all statuses, grouped client-side; `pageSize=100` | GET /api/v1/projects/{projectId}/tasks | On page load; on assignee-filter change; on load-more (next `page`) |
| AssigneeFilter | `{ data: ProjectMemberDto[], meta }` — member user ids for filter options | GET /api/v1/projects/{projectId}/members | On page load |
| CreateTaskDialog | `{ data: TaskDto }` — the created task | POST /api/v1/projects/{projectId}/tasks | On dialog submit |
| TaskCard (drag / "Move to…") | `{ data: TaskDto }` — task with updated `status` | PATCH /api/v1/tasks/{id} | On drop in another column; on menu status change |
| ActivityFeedPanel | `{ data: ActivityEventDto[], meta }` — newest first | GET /api/v1/projects/{projectId}/feed | On panel open; on load-more (next `page`) |

## States

Patterns from `index.md` Section 2.5.

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Tasks loaded | Three columns with cards grouped by `status`; column headers show per-status counts; LoadMoreBar appears while fewer than `meta.totalCount` tasks are loaded |
| **Loading** | Task fetch in flight | Each column shows 3 skeleton cards (`SkeletonBlock` card variant), `aria-busy`; header shows a skeleton line while the project fetch is in flight |
| **Empty** | `meta.totalCount === 0` (no filter) | Columns replaced by `EmptyState`: "No tasks yet" / "Create the first task to get the board moving." / CTA "New task". With an active assignee filter and zero matches: "No tasks match this filter" + "Clear filter" CTA instead |
| **Error** | Task or project fetch failed (non-401) | `ErrorBanner` above the board with Retry; feed panel failures show the banner inside the panel only; 401 triggers the auth redirect |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Drag a card to another column | TaskCard (HTML5 drag; column highlights with `primary-light` on drag-over) | Optimistic move to the target column (TanStack Query mutation with rollback); on failure the card returns and an `ErrorBanner` explains | PATCH /api/v1/tasks/{id} (body `{ "status": … }`) |
| Change status without dragging | CardActionsMenu → "Move to To do / In progress / Done" (keyboard-accessible fallback) | Same optimistic move as drag | PATCH /api/v1/tasks/{id} (body `{ "status": … }`) |
| Click a card | TaskCard body | Navigate to `/projects/:projectId/tasks/:taskId` — opens the Task Detail Panel over the board (`screens/task-detail-panel.md`) | None (the panel fetches) |
| Click "New task" | Toolbar primary button (also the Empty-state CTA) | Opens CreateTaskDialog: title (required, 1–200 chars), description, status (default `todo`), due date (native date input), assignee (select from members / Unassigned) | None until submit |
| Submit create task | Dialog "Create" button | On 201: close dialog, card appears in its status column; 400 `validation-error` renders field-level messages from `error.fields` | POST /api/v1/projects/{projectId}/tasks |
| Filter by assignee | AssigneeFilter select | Refetches the list with the `assigneeId` query parameter and rebuilds the columns; "All" clears the filter | GET /api/v1/projects/{projectId}/tasks |
| Load more tasks | LoadMoreBar button (visible while loaded < `meta.totalCount`) | Fetches the next `page` (`pageSize=100`) and appends to the columns | GET /api/v1/projects/{projectId}/tasks |
| Toggle activity panel | ActivityToggleButton | Opens/closes the right-docked feed panel; first open fetches page 1 | GET /api/v1/projects/{projectId}/feed |
| Load more activity | PaginationControls (load-more) at panel bottom | Appends the next feed page (events ordered `occurredAt` descending) | GET /api/v1/projects/{projectId}/feed |
| Click a feed item | ActivityFeedItem | Navigate to the event's task: `/projects/:projectId/tasks/:taskId` | None (the panel fetches) |
| Switch to Members tab | ProjectHeader tab | Navigate to `/projects/:projectId/members` | None |
