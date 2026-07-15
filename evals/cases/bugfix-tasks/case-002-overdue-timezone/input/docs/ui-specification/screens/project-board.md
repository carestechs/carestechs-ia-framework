---
kind: screen
screen: project-board
route: /projects/:projectId/board
endpoints: [tasks]
---

# Screen: Project Board

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

**Route**: /projects/:projectId/board
**Auth**: Required
**Layout**: App shell — see `index.md` Section 4.1
**Code**: `src/ui/project-board.tsx`

## Layout Sketch

```
┌──────────────────────────────────────────────────────────┐
│ BoardToolbar: project name · filter dropdown · refresh   │
├──────────────────┬──────────────────┬────────────────────┤
│  To Do           │  In Progress     │  Done              │
│ ┌──────────────┐ │ ┌──────────────┐ │ ┌──────────────┐   │
│ │ TaskCard     │ │ │ TaskCard     │ │ │ TaskCard     │   │
│ └──────────────┘ │ └──────────────┘ │ └──────────────┘   │
│ ┌──────────────┐ │                  │                    │
│ │ TaskCard     │ │                  │                    │
│ └──────────────┘ │                  │                    │
└──────────────────┴──────────────────┴────────────────────┘
```

## Component Hierarchy

```
ProjectBoardPage
├── BoardToolbar
├── BoardColumn (×3 — one per TaskStatus)
│   └── TaskCard (shared — see components.md)
│       (EmptyState shown when a column has no tasks — shared)
└── Dialog (shared — confirmation surface, currently unused on this screen)
```

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/tasks.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectBoardPage | All board tasks | GET /api/v1/projects/{projectId}/tasks | On load; refetch after any mutation |
| BoardToolbar (filter dropdown) | Filtered board tasks | GET /api/v1/projects/{projectId}/tasks (`filter=overdue`, `tz=<browser zone>`) | On selecting "Overdue" in the dropdown |
| TaskCard (drag) | Status/position update | PATCH /api/v1/tasks/{id} | On drop into a column slot |

## States

<!-- Use the standard patterns from index.md Section 2.5 -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Tasks loaded | Three columns with draggable TaskCards ordered by `position` |
| **Loading** | Board query in flight | Skeleton columns with card-shaped placeholders |
| **Empty** | Project has no tasks | `EmptyState` spanning the board: "No tasks yet" + create CTA |
| **Error** | Board query failed | Inline error banner with retry button above the columns |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Select "Overdue" in the filter dropdown | BoardToolbar dropdown | Board refetches showing only overdue tasks; selecting "All tasks" clears the filter | GET /api/v1/projects/{projectId}/tasks (`filter=overdue`, `tz=<browser zone>`) |
| Drag a card to another column/slot | TaskCard | Card moves optimistically; column renumbers | PATCH /api/v1/tasks/{id} (`status`, `position`) |
| Click a card | TaskCard | Task Detail Panel opens over the board (route change) | GET /api/v1/tasks/{id} (issued by the panel) |
| Click refresh | BoardToolbar button | Board refetches | GET /api/v1/projects/{projectId}/tasks |
