---
kind: screen
screen: project-list
route: /projects
endpoints: [projects]
---

# Screen: Project List

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects
**Auth**: Required
**Layout**: App shell (see `index.md` Section 4.1) — no ProjectSubnav (not project-scoped)

The landing screen after sign-in: the caller's projects (user flow phase 2 — "create or open a project").

## Layout Sketch

```
┌──────────────────────────────────────────────────────────────┐
│ Projects                                    [+ New project]  │
├──────────────────────────────────────────────────────────────┤
│ Name ▲          │ Description        │ Owner      │ Updated  │
│ Apollo          │ Q3 launch work     │ ‹UserIdChip›│ 2026-07-15│
│ Billing rewrite │ —                  │ ‹UserIdChip›│ 2026-07-14│
│ …               │                    │            │          │
├──────────────────────────────────────────────────────────────┤
│                    ‹Pagination — meta.totalCount›            │
└──────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
ProjectListPage                     — src/ui/project-list.tsx (one React file per screen)
├── PageHeader                      — "Projects" h1 + NewProjectButton
├── ProjectTable
│   └── ProjectRow                  — name (link to board), description, UserIdChip (ownerId), updatedAt
├── Pagination                      — shared (components.md)
├── EmptyState                      — shared (components.md)
├── ErrorBanner                     — shared (components.md)
├── Skeleton                        — shared (components.md), row variant
└── CreateProjectDialog             — shared Dialog wrapper (components.md)
    └── ProjectForm                 — name (required, 1–120 chars), description (optional)
```

## Component → API Mapping

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectTable | Caller's projects (`ProjectDto[]`, sorted by name ascending) | GET /api/v1/projects?page&pageSize | On page load, on page change |
| CreateProjectDialog | Created project (`ProjectDto`) | POST /api/v1/projects | On form submit |

> Responses use the envelope from `docs/api-spec/index.md` Section 2.1: the table consumes `data` and passes `meta` to `Pagination`.

## States

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Projects loaded, `meta.totalCount` > 0 | Table of ProjectRows, name ascending (API default sort); Pagination below when `totalCount` > `pageSize` |
| **Loading** | GET /api/v1/projects in flight | 5 Skeleton table rows matching column layout (Section 2.5 pattern) |
| **Empty** | `meta.totalCount` = 0 | EmptyState: "No projects yet" / "Create your first project to start tracking tasks." / CTA "New project" opens CreateProjectDialog |
| **Error** | GET /api/v1/projects failed | ErrorBanner with message mapped from `error.code` + Retry (refetches) |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Click "New project" | Header button | Open CreateProjectDialog (focus in name field) | None until submit |
| Submit new project | Dialog "Create" button | On 201: close dialog, invalidate `['projects']`, navigate to `/projects/:projectId/board` (caller became owner) | POST /api/v1/projects |
| Submit with invalid name | Dialog "Create" button | 400 `validation-error`: render `error.fields.name` messages under the name field; dialog stays open | POST /api/v1/projects |
| Submit duplicate name | Dialog "Create" button | 409 `conflict`: inline message "A project with this name already exists" under the name field | POST /api/v1/projects |
| Click a project row | ProjectRow (name link) | Navigate to `/projects/:projectId/board` | None (the board screen fetches) |
| Change page | Pagination controls | Fetch and render the requested page | GET /api/v1/projects?page={n} |
