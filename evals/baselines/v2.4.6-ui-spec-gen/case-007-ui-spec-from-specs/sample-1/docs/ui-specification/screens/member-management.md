---
kind: screen
screen: member-management
route: /projects/:projectId/members
endpoints: [projects, project-members]
---

# Screen: Member Management

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: `/projects/:projectId/members`
**Auth**: Required
**Layout**: App shell — see `index.md` Section 4.1
**Screen file (planned)**: `src/ui/member-management.tsx` → `MemberManagementPage`

The project's member list (Members tab of `ProjectHeader`), with owner-only add and remove — user-flow step 3 ("Manage membership"). There is **no user search or profile endpoint**: members are added by pasting their auth-service user UUID, and rows display only `UserIdBadge`s. Roles are display-only — the API defines no role-change endpoint (the single `owner` row is created with the project), so no role editor exists.

## Layout Sketch

```
┌──────────────────────────────────────────────────────────────┐
│ App bar (shell)                                              │
├──────────────────────────────────────────────────────────────┤
│ ProjectHeader: ‹ Projects  Apollo           [Board] [Members]│
├──────────────────────────────────────────────────────────────┤
│  Members (4)                                  [+ Add member] │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ User                     Role      Joined              │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ [3f2a91c4… you]          owner     Jul 10              │  │
│  │ [9f31c2a8…]              member    Jul 11    [Remove]  │  │
│  │ [b2c47e01…]              member    Jul 12    [Remove]  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                        ‹ Page 1 of 1 ›       │
└──────────────────────────────────────────────────────────────┘
```

"Add member" and the Remove buttons render only for the owner; the owner's own row never shows Remove (the API rejects it with 409). Non-owners see a read-only list.

## Component Hierarchy

```
MemberManagementPage
├── ProjectHeader                       (shared — project name + Board/Members tabs)
├── MembersToolbar
│   ├── SectionTitle ("Members (N)")
│   └── AddMemberButton                 (owner only)
├── MemberTable
│   └── MemberRow (×N)
│       ├── UserIdBadge                 (shared — "you" marker on the caller's row)
│       ├── RoleBadge                   (owner / member — `secondary` accent for owner)
│       └── RemoveMemberButton          (owner only; absent on the owner's row)
├── PaginationControls                  (shared — pager variant)
├── AddMemberDialog → ModalDialog       (shared)
└── RemoveMemberConfirm → ConfirmDialog (shared)
```

`SkeletonBlock`, `EmptyState`, and `ErrorBanner` (shared) render per the States table.

## Component → API Mapping

Endpoints live in `docs/api-spec/endpoints/project-members.md` and `docs/api-spec/endpoints/projects.md`; all responses use the envelope.

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectHeader | `{ data: ProjectDto }` — name for the header; `ownerId` for owner-only UI | GET /api/v1/projects/{id} | On page load (shares the board's cached query) |
| MemberTable | `{ data: ProjectMemberDto[], meta }` — `createdAt` ascending (owner first) | GET /api/v1/projects/{projectId}/members | On page load; on page change |
| AddMemberDialog | `{ data: ProjectMemberDto }` — the created membership | POST /api/v1/projects/{projectId}/members | On dialog submit |
| RemoveMemberConfirm | 204 No Content | DELETE /api/v1/projects/{projectId}/members/{userId} | On confirm |

## States

Patterns from `index.md` Section 2.5.

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Members loaded | Table sorted as returned (owner first); `PaginationControls` when `meta.totalCount > meta.pageSize` |
| **Loading** | Member fetch in flight | 4 skeleton rows (`SkeletonBlock` row variant), `aria-busy` |
| **Empty** | Only the owner's row exists (`meta.totalCount === 1`) — the list can never be truly empty, since the owner row is created with the project | Below the single-row table, `EmptyState` (compact): "It's just you so far" / "Add teammates by their user id to start collaborating." / CTA "Add member" (owner only) |
| **Error** | Fetch failed (non-401) | `ErrorBanner` with Retry in place of the table; 403 `forbidden` (caller lost membership): "You are no longer a member of this project" + link back to `/projects`; 401 triggers the auth redirect |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Click "Add member" | Toolbar primary button (owner only; also the Empty-state CTA) | Opens AddMemberDialog: one field for the auth-service user UUID (client-validates UUID format before enabling submit — there is no user search endpoint to look ids up) | None until submit |
| Submit add member | Dialog "Add" button | On 201: close dialog, append the row (role `member` — the API never grants `owner` here) | POST /api/v1/projects/{projectId}/members |
| Add fails — already a member | Dialog userId field | Dialog stays open; field-level error "This user is already a member" (`conflict`, 409) | — (response of the POST above) |
| Add fails — invalid id | Dialog userId field | Field-level error from `error.fields` (`validation-error`, 400) | — (response of the POST above) |
| Click "Remove" on a member row | RemoveMemberButton (owner only) | Opens RemoveMemberConfirm: "Remove this member? Their assigned tasks in this project will become unassigned." | None until confirm |
| Confirm removal | ConfirmDialog danger button | On 204: remove the row; board task caches are invalidated so unassigned cards refresh | DELETE /api/v1/projects/{projectId}/members/{userId} |
| Change page | PaginationControls | Fetches the selected page (`page` query param) | GET /api/v1/projects/{projectId}/members |
| Switch to Board tab | ProjectHeader tab | Navigate to `/projects/:projectId` | None |
