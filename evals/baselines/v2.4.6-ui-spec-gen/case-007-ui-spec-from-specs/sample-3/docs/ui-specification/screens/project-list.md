---
kind: screen
screen: project-list
route: /projects
endpoints: [projects]
---

# Screen: Project List

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: `/projects`
**Auth**: Required
**Layout**: App shell — see `index.md` Section 4.1 (no project tab bar; this route is not project-scoped)
**Planned file**: `src/ui/project-list.tsx` (component `ProjectListPage`)

## Layout Sketch

```
┌────────────────────────────────────────────────────────┐
│  Projects                              [+ New project] │
├────────────────────────────────────────────────────────┤
│ ┌────────────────────┐  ┌────────────────────┐         │
│ │ Website Redesign   │  │ Q3 Roadmap         │         │
│ │ Short description… │  │ Short description… │  …      │
│ │ Owner: 3f2a91c4…   │  │ Owner: 7b4402ee…   │         │
│ └────────────────────┘  └────────────────────┘         │
├────────────────────────────────────────────────────────┤
│            [← Prev]   Page 1 of 1 (3)   [Next →]       │
└────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
ProjectListPage
├── PageHeader ("Projects" h1 + [+ New project] button)
├── ProjectCardGrid
│   └── ProjectCard (one per ProjectDto: name, description, owner UserIdBadge*)
├── PaginationControls*
└── CreateProjectModal (Modal*: name + description fields)
```

`*` = shared component — see `components.md`. `ProjectCard` is the Project entity's display component; it is used only here, so it stays in this shard.

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/projects.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectCardGrid | Caller's projects, `ProjectDto[]` sorted by name ascending | GET /api/v1/projects | On page load and on page change (`page`, `pageSize=50`) |
| PaginationControls | `meta.totalCount`, `meta.page`, `meta.pageSize` | GET /api/v1/projects | Same response as above — no extra request |
| CreateProjectModal | Created project (`ProjectDto`) | POST /api/v1/projects | On form submit |

Query key: `['projects', { page }]`. The create mutation invalidates `['projects']` and navigates to the new project's board.

## States

<!-- Use the standard patterns from index.md Section 2.5 — do not invent new loading/error UIs -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | `meta.totalCount` ≥ 1 | Card grid sorted by name; pagination row renders only when `totalCount > pageSize` |
| **Loading** | GET /api/v1/projects in flight | 6 skeleton cards matching `ProjectCard` dimensions (Section 2.5) |
| **Empty** | `meta.totalCount === 0` | `EmptyState`: "No projects yet" / "Create a project to start tracking tasks." / [New project] CTA (opens the create modal) |
| **Error** | GET failed | `ErrorBanner` with the envelope's `error.message` + Retry (refetches); `401` triggers the auth redirect (index Section 4.2) |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Open project | ProjectCard (click, or Enter — cards are focusable) | Navigate to `/projects/:projectId/board` | None (the board fetches on load) |
| Open create dialog | [+ New project] button | CreateProjectModal opens, name field focused | None until submit |
| Create project | [Create] button in modal (inline action spinner while pending) | On 201: modal closes, navigate to the new project's board | POST /api/v1/projects |
| Fix invalid input | Name/description fields | 400 `validation-error` → `error.fields` rendered as field-level errors | Response of POST /api/v1/projects |
| Resolve duplicate name | Name field | 409 `conflict` → inline field error "This name is already taken" | Response of POST /api/v1/projects |
| Change page | PaginationControls [← Prev] / [Next →] | Fetch and render the requested page | GET /api/v1/projects (`page={n}`, `pageSize=50`) |
