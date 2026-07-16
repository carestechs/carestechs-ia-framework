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
**Layout**: App shell — see `index.md` Section 4.1
**Screen file (planned)**: `src/ui/project-list.tsx` → `ProjectListPage`

The entry screen (`/` redirects here): the caller's projects, sorted by name ascending as the API returns them, with project creation and owner-only rename/delete. Covers user-flow step 2 ("Create or open a project").

## Layout Sketch

```
┌──────────────────────────────────────────────────────────────┐
│ App bar (shell)                                              │
├──────────────────────────────────────────────────────────────┤
│  Projects                                    [+ New project] │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Name ▲        Description          Owner       Updated │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Apollo        Launch checklist     [9f31c2a8…] Jul 15 ⋮│  │
│  │ Billing rev.  —                    [3f2a91c4… you] …  ⋮│  │
│  │ Website       Marketing site       [3f2a91c4… you] …  ⋮│  │
│  └────────────────────────────────────────────────────────┘  │
│                                        ‹ Page 1 of 1 ›       │
└──────────────────────────────────────────────────────────────┘
```

Row overflow menu (⋮) appears only on projects the caller owns (`ownerId` equals the JWT subject): Rename, Delete.

## Component Hierarchy

```
ProjectListPage
├── PageToolbar
│   ├── PageTitle ("Projects")
│   └── NewProjectButton
├── ProjectTable
│   └── ProjectRow (×N)
│       ├── ProjectNameLink            → navigates to the board
│       ├── OwnerCell → UserIdBadge    (shared — components.md)
│       └── RowActionsMenu             (owner only: Rename, Delete)
├── PaginationControls                 (shared — pager variant)
├── CreateProjectDialog  → ModalDialog (shared)
├── RenameProjectDialog  → ModalDialog (shared)
└── DeleteProjectConfirm → ConfirmDialog (shared)
```

`SkeletonBlock`, `EmptyState`, and `ErrorBanner` (shared) render in place of `ProjectTable` per the States table.

## Component → API Mapping

Endpoints live in `docs/api-spec/endpoints/projects.md`; all responses use the envelope (`{ data }`, lists add `meta`).

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectTable | `{ data: ProjectDto[], meta }` — caller's projects, name ascending | GET /api/v1/projects | On page load; on page change |
| CreateProjectDialog | `{ data: ProjectDto }` — the created project | POST /api/v1/projects | On dialog submit |
| RenameProjectDialog | `{ data: ProjectDto }` — the updated project | PATCH /api/v1/projects/{id} | On dialog submit |
| DeleteProjectConfirm | 204 No Content | DELETE /api/v1/projects/{id} | On confirm |

## States

Patterns from `index.md` Section 2.5.

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Projects loaded, at least one exists | Table of `ProjectRow`s; `PaginationControls` when `meta.totalCount > meta.pageSize` |
| **Loading** | `GET /api/v1/projects` in flight | 5 skeleton rows (`SkeletonBlock` row variant) in the table body, `aria-busy` |
| **Empty** | `meta.totalCount === 0` | `EmptyState`: "No projects yet" / "Create a project to start tracking tasks with your team." / CTA "New project" (opens CreateProjectDialog) |
| **Error** | Request failed (non-401) | `ErrorBanner` with the Error Catalog message and a Retry button; 401 triggers the auth redirect (index Section 4.2) |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Click "New project" | Toolbar primary button (also the Empty-state CTA) | Opens CreateProjectDialog (name required 1–120 chars, optional description) | None until submit |
| Submit create form | Dialog "Create" button | On 201: close dialog, navigate to the new project's board (`/projects/:projectId`) | POST /api/v1/projects |
| Create fails — duplicate name | Dialog name field | Dialog stays open; field-level error "A project with this name already exists" (`conflict`, 409 — names are unique case-insensitively) | — (response of the POST above) |
| Click a project row | ProjectNameLink / row | Navigate to `/projects/:projectId` (Project Board fetches its own data) | None |
| Open row menu → "Rename" | RowActionsMenu item (owner only) | Opens RenameProjectDialog prefilled with current name/description | None until submit |
| Submit rename form | Dialog "Save" button | On 200: close dialog, update row in place; 409 duplicate name shows the same field-level error as create | PATCH /api/v1/projects/{id} |
| Open row menu → "Delete" | RowActionsMenu item (owner only) | Opens DeleteProjectConfirm: "Delete project? This permanently removes all its tasks, comments, and memberships." | None until confirm |
| Confirm delete | ConfirmDialog danger button | On 204: remove row; show Empty state if it was the last project | DELETE /api/v1/projects/{id} |
| Change page | PaginationControls | Fetches the selected page (`page` query param), replaces table contents | GET /api/v1/projects |
