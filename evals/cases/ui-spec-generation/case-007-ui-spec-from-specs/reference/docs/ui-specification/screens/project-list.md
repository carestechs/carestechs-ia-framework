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
**Layout**: App shell — see `index.md` Section 4.1
**Code**: `src/ui/project-list.tsx` (planned)

## Layout Sketch

```
┌──────────────────────────────────────────────────────────┐
│ Toolbar: "Projects" (h1)              [ + New project ]  │
├──────────────────────────────────────────────────────────┤
│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐   │
│ │ ProjectCard   │ │ ProjectCard   │ │ ProjectCard   │   │
│ │ name          │ │ name          │ │ name          │   │
│ │ description   │ │ description   │ │ description   │   │
│ │ ⬤ owner badge │ │ ⬤ owner badge │ │ ⬤ owner badge │ ⋮ │
│ └───────────────┘ └───────────────┘ └───────────────┘   │
└──────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
ProjectListPage
├── ProjectListToolbar
│   └── NewProjectButton
├── ProjectCard (×N — screen-specific)
│   ├── UserBadge (owner — shared, see components.md)
│   └── CardMenu (rename / delete — rendered only when the caller is the owner)
├── Dialog (shared — create form, rename form, delete confirmation)
├── EmptyState (shared)
└── ErrorBanner (shared)
```

`ProjectCard` shows the project name, its description (truncated to two lines), and the owner's `UserBadge`. The overflow `CardMenu` appears only when `ProjectDto.ownerId` equals the caller's user id (JWT subject).

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/projects.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectListPage | Caller's projects | GET /api/v1/projects | On load; refetch after any mutation |
| Dialog (create) | New project | POST /api/v1/projects | On create form submit |
| Dialog (rename) | Updated name/description | PATCH /api/v1/projects/{id} | On rename form submit (owner only) |
| Dialog (delete, destructive) | Project removal | DELETE /api/v1/projects/{id} | On confirm (owner only) |

## States

<!-- Use the standard patterns from index.md Section 2.5 -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Projects loaded | Card grid sorted by name (server order), owner badge on each card |
| **Loading** | List query in flight | Skeleton card grid matching card dimensions |
| **Empty** | Caller belongs to no projects | `EmptyState`: "No projects yet" + "Create your first project" CTA opening the create Dialog |
| **Error** | List query failed | `ErrorBanner` with retry above the grid area |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Click a project card | ProjectCard | Navigate to /projects/:projectId/board | None (the board issues its own queries) |
| Click "New project" | Toolbar button | Create Dialog opens (name required, description optional) | None until submit |
| Submit create form | Dialog primary action | Dialog closes; new card appears; navigate to its board | POST /api/v1/projects |
| Submit with a taken name | Dialog primary action | Dialog stays open; inline `conflict` message on the name field | POST /api/v1/projects (409) |
| Choose "Rename" (owner) | CardMenu item | Rename Dialog pre-filled; card updates on save | PATCH /api/v1/projects/{id} |
| Choose "Delete" (owner) | CardMenu item → destructive Dialog | Card removed after confirm; dialog warns tasks and comments are deleted too | DELETE /api/v1/projects/{id} |
