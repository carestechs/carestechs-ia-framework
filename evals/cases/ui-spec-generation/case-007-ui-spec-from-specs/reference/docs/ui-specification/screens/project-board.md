---
kind: screen
screen: project-board
route: /projects/:projectId/board
endpoints: [tasks, projects, project-members]
---

# Screen: Project Board

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects/:projectId/board
**Auth**: Required
**Layout**: App shell — see `index.md` Section 4.1
**Code**: `src/ui/project-board.tsx` (planned)

## Layout Sketch

```
┌──────────────────────────────────────────────────────────────────┐
│ BoardToolbar: project name · assignee filter · [+ New task]      │
│               · Members link · Activity toggle                   │
├──────────────────┬──────────────────┬──────────────┬─────────────┤
│  To Do           │  In Progress     │  Done        │ Activity    │
│ ┌──────────────┐ │ ┌──────────────┐ │ ┌──────────┐ │ (drawer,    │
│ │ TaskCard     │ │ │ TaskCard     │ │ │ TaskCard │ │  collapsed  │
│ └──────────────┘ │ └──────────────┘ │ └──────────┘ │  by default)│
│ ┌──────────────┐ │                  │              │ · event     │
│ │ TaskCard     │ │                  │              │ · event     │
│ └──────────────┘ │                  │              │ · event     │
└──────────────────┴──────────────────┴──────────────┴─────────────┘
```

## Component Hierarchy

```
ProjectBoardPage
├── BoardToolbar
│   ├── AssigneeFilter (options rendered as UserBadge — shared)
│   ├── NewTaskButton
│   ├── MembersLink (→ /projects/:projectId/members)
│   └── ActivityToggle
├── BoardColumn (×3 — one per TaskStatus: todo, in_progress, done)
│   ├── TaskCard (screen-specific — see below)
│   │   └── UserBadge (assignee — shared)
│   └── EmptyState (inline variant, when a column has no tasks — shared)
├── ActivityFeedDrawer
│   └── ActivityRow (×N — event text, task title, UserBadge for comment authors)
├── Dialog (shared — new-task form)
└── ErrorBanner (shared)
```

`TaskCard` (screen-specific): title, assignee `UserBadge` (or an "unassigned" placeholder), and a due-date chip — `warning`-colored when the calendar date is past. Draggable between columns. Tasks have **no position field**: within a column, cards render in the list's `createdAt` descending order; dragging changes `status` only, never intra-column order.

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/{tasks,projects,project-members}.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectBoardPage | Project name for the toolbar | GET /api/v1/projects/{id} | On load |
| ProjectBoardPage | All board tasks | GET /api/v1/projects/{projectId}/tasks | On load; refetch after any mutation |
| AssigneeFilter | Member list for filter options | GET /api/v1/projects/{projectId}/members | On first open of the filter |
| BoardColumn (filtered view) | Tasks for one assignee | GET /api/v1/projects/{projectId}/tasks?assigneeId={userId} | On filter change |
| TaskCard (drag) | Status update | PATCH /api/v1/tasks/{id} | On drop into another column |
| Dialog (new task) | Task creation | POST /api/v1/projects/{projectId}/tasks | On form submit |
| ActivityFeedDrawer | Recent task/comment changes | GET /api/v1/projects/{projectId}/feed | On drawer open; on page change |

## States

<!-- Use the standard patterns from index.md Section 2.5 -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Tasks loaded | Three columns of TaskCards grouped by `status`; drawer collapsed |
| **Loading** | Board queries in flight | Skeleton columns with card-shaped placeholders; drawer shows row skeletons while the feed loads |
| **Empty** | Project has no tasks (or none match the filter) | Board-wide `EmptyState`: "No tasks yet" + "New task" CTA; per-column inline variant when only one column is empty; drawer shows "No activity yet" |
| **Error** | Board or feed query failed | `ErrorBanner` with retry above the columns (board) or inside the drawer (feed) |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Drag a card to another column | TaskCard | Card moves optimistically; rolls back with an `ErrorBanner` on failure | PATCH /api/v1/tasks/{id} (`status` only) |
| Move a card via keyboard | TaskCard context menu ("Move to…") | Same status change without drag (WCAG 2.1 AA equivalent) | PATCH /api/v1/tasks/{id} (`status` only) |
| Click a card | TaskCard | Task Detail Panel opens over the board (route change to /projects/:projectId/tasks/:taskId) | None here (the panel issues GET /api/v1/tasks/{id}) |
| Click "New task" | BoardToolbar button | Dialog opens: title (required), description, status, due date (calendar date), assignee | None until submit |
| Submit new-task form | Dialog primary action | Dialog closes; card appears in its status column | POST /api/v1/projects/{projectId}/tasks |
| Pick an assignee filter | AssigneeFilter | Columns show only that member's tasks; "All" clears | GET /api/v1/projects/{projectId}/tasks?assigneeId={userId} |
| Toggle the activity drawer | ActivityToggle | Drawer slides in from the right, newest events first | GET /api/v1/projects/{projectId}/feed |
| Click "Members" | MembersLink | Navigate to /projects/:projectId/members | None (that screen issues its own queries) |
