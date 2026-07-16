---
kind: screen
screen: project-board
route: /projects/:projectId/board
endpoints: [projects, tasks, project-members]
---

# Screen: Project Board

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects/:projectId/board
**Auth**: Required
**Layout**: App shell + ProjectSubnav (see `index.md` Section 4.1)

The Kanban view of a project's tasks: one column per `TaskStatus` value (`todo`, `in_progress`, `done`), grouped client-side from a single task list fetch (tasks have no ordering field — order within a column is presentation-side, `createdAt` descending). Covers user flow phases 4 and 5.

## Layout Sketch

```
┌ ProjectSubnav: ‹Project name›   [Board]* [Members] [Activity] ┐
│ Toolbar: [Assignee: All ▾]              [⋯ project] [+ New task]
├───────────────────┬───────────────────┬───────────────────────┤
│ To do (3)         │ In progress (2)   │ Done (5)              │
│ ┌───────────────┐ │ ┌───────────────┐ │ ┌───────────────┐     │
│ │ Task title    │ │ │ Task title    │ │ │ Task title    │     │
│ │ ‹DueDateBadge›│ │ │ ‹UserIdChip›  │ │ │ ‹UserIdChip›  │     │
│ │ ‹UserIdChip›  │ │ └───────────────┘ │ └───────────────┘     │
│ │           [⋮] │ │                   │                       │
│ └───────────────┘ │                   │                       │
└───────────────────┴───────────────────┴───────────────────────┘
  (Mobile/Tablet: columns scroll horizontally with snap — Section 2.6)
```

## Component Hierarchy

```
ProjectBoardPage                    — src/ui/project-board.tsx (one React file per screen)
├── ProjectSubnav                   — shared (components.md); fetches the project
├── BoardToolbar
│   ├── AssigneeFilter              — select: All / member UserIdChips (from members list)
│   ├── ProjectMenu                 — "⋯" menu, owner only: Rename…, Delete…
│   └── NewTaskButton
├── BoardColumn (×3, one per TaskStatus)
│   ├── ColumnHeader                — status label + count
│   └── TaskCard                    — title, DueDateBadge, UserIdChip (assigneeId), [⋮] card menu
├── CreateTaskDialog                — shared Dialog wrapper: title, description, status, due date, assignee
├── RenameProjectDialog             — shared Dialog wrapper: name, description
├── ConfirmDialog                   — shared (components.md), danger variant (delete project)
├── EmptyState / ErrorBanner / Skeleton — shared (components.md)
```

## Component → API Mapping

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectSubnav | Project header (`ProjectDto` — name, `ownerId` decides owner-only controls) | GET /api/v1/projects/{id} | On page load |
| BoardColumn / TaskCard | All tasks (`TaskDto[]`), grouped by `status` client-side | GET /api/v1/projects/{projectId}/tasks?pageSize=100 | On page load; refetch on filter change |
| AssigneeFilter | Member ids (`ProjectMemberDto[]`) for the dropdown | GET /api/v1/projects/{projectId}/members | On page load |
| TaskCard (drag / move menu) | Status change | PATCH /api/v1/tasks/{id} | On drop in another column, or card menu "Move to …" |
| CreateTaskDialog | Created task (`TaskDto`) | POST /api/v1/projects/{projectId}/tasks | On form submit |
| RenameProjectDialog | Updated project (`ProjectDto`) | PATCH /api/v1/projects/{id} | On form submit (owner only) |
| ConfirmDialog (delete) | — | DELETE /api/v1/projects/{id} | On confirm (owner only) |

> Responses use the envelope from `docs/api-spec/index.md` Section 2.1. The task list is paginated (`pageSize` max 100): when `meta.totalCount` > 100, each column footer shows "Load more" fetching the next page and appending.

## States

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Tasks loaded | Three columns with TaskCards grouped by `status`, `createdAt` descending within a column; per-column counts in headers; a column with no tasks shows a muted "No tasks" hint (not the full EmptyState) |
| **Loading** | Task/project fetches in flight | Column skeletons: 3 columns × 3 Skeleton card blocks (Section 2.5 pattern) |
| **Empty** | `meta.totalCount` = 0 and no filter active | EmptyState across the board area: "No tasks yet" / "Create the first task to get the board moving." / CTA "New task" opens CreateTaskDialog. With an assignee filter active: "No tasks for this assignee" + CTA "Clear filter" |
| **Error** | GET tasks (or project) failed | ErrorBanner with message mapped from `error.code` + Retry; `403 forbidden` / `404 not-found` render the full-page error pattern with a "Back to projects" link (Section 2.5) |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Drag card to another column | TaskCard (HTML5 drag; drop target column highlights `primary-light`) | Optimistic move to target column; invalidate `['tasks', projectId]`; on failure roll back + ErrorBanner | PATCH /api/v1/tasks/{id} with `{ "status": "…" }` |
| Move card via keyboard | TaskCard [⋮] menu → "Move to To do / In progress / Done" | Same as drag (accessibility path — Section 1.2 decision) | PATCH /api/v1/tasks/{id} with `{ "status": "…" }` |
| Click a card | TaskCard body | Open Task Detail overlay at `/projects/:projectId/tasks/:taskId` (see `screens/task-detail.md`) | None (the panel fetches) |
| Click "+ New task" | Toolbar button | Open CreateTaskDialog (assignee select lists current members + "Unassigned") | None until submit |
| Submit new task | Dialog "Create" button | On 201: close dialog, card appears in its status column, invalidate `['tasks', projectId]`; 400 `validation-error` renders `error.fields` messages under the fields (incl. assignee not a current member) | POST /api/v1/projects/{projectId}/tasks |
| Filter by assignee | AssigneeFilter select | Refetch task list filtered server-side | GET /api/v1/projects/{projectId}/tasks?assigneeId={userId} |
| Rename project | ProjectMenu → "Rename…" (owner only) | Dialog pre-filled; on 200 subnav name updates, invalidate `['project', projectId]`; 409 `conflict` shows inline name-taken message | PATCH /api/v1/projects/{id} |
| Delete project | ProjectMenu → "Delete…" (owner only) → ConfirmDialog (danger) warning "removes all tasks, comments, and members" | On 204: navigate to `/projects`, invalidate `['projects']` | DELETE /api/v1/projects/{id} |
| Load more in columns | Column footer button (only when `meta.totalCount` > loaded) | Fetch next page, append to columns | GET /api/v1/projects/{projectId}/tasks?page={n}&pageSize=100 |

> There is no delete-task endpoint in the API spec — TaskCards intentionally have no delete action.
