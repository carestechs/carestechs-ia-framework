---
kind: screen
screen: project-activity
route: /projects/:projectId/activity
endpoints: [projects]
---

# Screen: Project Activity

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects/:projectId/activity
**Auth**: Required
**Layout**: App shell + ProjectSubnav (see `index.md` Section 4.1)

The project's activity feed — recent task and comment changes, newest first. The feed is **derived on read** from task and comment records (there is no event store and no feed-write UI); the endpoint lives in the projects resource shard. Covers user flow phase 6 ("show what changed in a project without asking anyone").

## Layout Sketch

```
┌ ProjectSubnav: ‹Project name›   [Board] [Members] [Activity]* ┐
│ Activity                                                      │
├───────────────────────────────────────────────────────────────┤
│ ● Comment added on “Ship the login flow”      ‹UserIdChip›    │
│   caption: 2026-07-16 09:12                     → opens task  │
│ ● Task updated — “Fix pagination meta”                        │
│   caption: 2026-07-16 08:40          (no actor: task events   │
│ ● Task created — “Draft Q3 roadmap”     carry none)           │
│   caption: 2026-07-15 17:02                                   │
├───────────────────────────────────────────────────────────────┤
│                     ‹Pagination — meta.totalCount›            │
└───────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
ProjectActivityPage                 — src/ui/project-activity.tsx (one React file per screen)
├── ProjectSubnav                   — shared (components.md); fetches the project
├── ActivityList
│   └── ActivityItem                — event sentence from `type` (task_created | task_updated |
│                                     comment_added), taskTitle as link to the task,
│                                     UserIdChip (actorId — comment_added only), occurredAt caption
├── Pagination                      — shared (components.md)
├── EmptyState / ErrorBanner / Skeleton — shared (components.md)
```

## Component → API Mapping

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectSubnav | Project header (`ProjectDto`) | GET /api/v1/projects/{id} | On page load |
| ActivityList | Feed events (`ActivityEventDto[]`, `occurredAt` descending) | GET /api/v1/projects/{projectId}/feed?page&pageSize | On page load, on page change, refetch on window focus |

> Responses use the envelope from `docs/api-spec/index.md` Section 2.1. `actorId` is set only for `comment_added` (task events carry no actor — tasks do not record who changed them); render an actor chip only when present. Refetch-on-focus keeps the success metric honest: a new comment is visible on the next page load.

## States

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Events loaded, `meta.totalCount` > 0 | Chronological list, newest first; each item's task title links to the Task Detail overlay |
| **Loading** | GET feed in flight | 6 Skeleton line-item blocks (Section 2.5 pattern) |
| **Empty** | `meta.totalCount` = 0 | EmptyState: "No activity yet" / "Activity appears here as tasks are created, updated, and discussed." / CTA "Go to board" navigating to `/projects/:projectId/board` |
| **Error** | GET feed (or project) failed | ErrorBanner with message mapped from `error.code` + Retry; `403 forbidden` / `404 not-found` render the full-page error pattern with "Back to projects" (Section 2.5) |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Click an event's task title | ActivityItem link | Open the Task Detail overlay at `/projects/:projectId/tasks/:taskId` (see `screens/task-detail.md`) | None (the panel fetches) |
| Change page | Pagination controls | Fetch and render the requested page | GET /api/v1/projects/{projectId}/feed?page={n} |
| Return to the tab / refocus window | — (TanStack Query refetch-on-focus) | Feed silently refetches; new events appear | GET /api/v1/projects/{projectId}/feed |

> Read-only screen: the feed is derived on read from tasks and comments — there is no "post to feed" action and none may be invented.
