---
kind: screen
screen: project-members
route: /projects/:projectId/members
endpoints: [project-members, projects]
---

# Screen: Project Members

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: `/projects/:projectId/members`
**Auth**: Required (any member may view; add/remove are owner-only)
**Layout**: App shell + project tab bar — see `index.md` Section 4.1
**Planned file**: `src/ui/project-members.tsx` (component `ProjectMembersPage`)

Members are added by pasting their auth-service user UUID — there is no user search, name lookup, or invitation flow (the API exposes no user directory). Owner gating: `project.ownerId === currentUserId`.

## Layout Sketch

```
┌────────────────────────────────────────────────────────────────┐
│ Members (4)          [auth user id (UUID)…    ] [Add member]   │  ← form: owner only
├────────────────────────────────────────────────────────────────┤
│ Member            Role     Joined                              │
│ 3f2a91c4… (you)   owner    2026-07-01                    —     │
│ 7b4402ee…         member   2026-07-02              [Remove]    │  ← button: owner only
│ 9c11d3ab…         member   2026-07-05              [Remove]    │
│ …                                                              │
├────────────────────────────────────────────────────────────────┤
│             [← Prev]   Page 1 of 1 (4)   [Next →]              │
└────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
ProjectMembersPage
├── MembersHeader ("Members" h1 + count from meta.totalCount)
├── AddMemberForm (owner only: UUID text input + [Add member] button)
├── MemberTable
│   └── MemberRow (UserIdBadge*, MemberRole pill, joined date, [Remove] — owner only, never on the owner's row)
├── PaginationControls*
└── RemoveMemberConfirm (ConfirmDialog*, danger variant)
```

`*` = shared component — see `components.md`. `MemberRow` is the ProjectMember entity's display component. Role pills use the Section 2.1 semantic mapping (`owner` → primary-light/primary-dark, `member` → neutral).

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/project-members.md, projects.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| App shell header / owner gating | `ProjectDto` (name, `ownerId`) | GET /api/v1/projects/{id} | On route load (cached — shared with the board) |
| MemberTable | `ProjectMemberDto[]`, `createdAt` ascending (owner row first) | GET /api/v1/projects/{projectId}/members | On page load; on page change (`page`, `pageSize=50`) |
| AddMemberForm | Created `ProjectMemberDto` (role is always `member` — the API grants `owner` only at project creation) | POST /api/v1/projects/{projectId}/members | On [Add member] |
| RemoveMemberConfirm | — (204, no body) | DELETE /api/v1/projects/{projectId}/members/{userId} | On confirm (owner only) |

Query keys: `['project', projectId]`, `['members', projectId, { page }]`. The remove mutation invalidates `['members', projectId]` and `['tasks', projectId]` — the API unassigns that user's tasks in the same transaction, so cached task data is stale after removal.

## States

<!-- Use the standard patterns from index.md Section 2.5 — do not invent new loading/error UIs -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Members loaded | Table sorted by join date, owner first; the caller's row shows "(you)"; pagination renders only when `totalCount > pageSize` |
| **Loading** | GET members in flight | 4 skeleton table rows (Section 2.5) |
| **Empty** | `meta.totalCount === 1` (the table is never truly empty — the owner row is created with the project) | Below the single-row table, `EmptyState`: "Only you here" / "Add teammates by their auth user id." / [Add member] CTA focusing the form (owner); non-owners see the hint without a CTA |
| **Error** | GET members failed | `ErrorBanner` + Retry; project GET 403/404 → full-page error (Section 2.5) with a link back to `/projects` |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Add member | [Add member] button (owner only; action spinner while pending) | On 201: row appended, input cleared, count updates | POST /api/v1/projects/{projectId}/members with `{ userId }` |
| Fix invalid id | UUID input | 400 `validation-error` → field error "Must be a valid user UUID" | Response of POST /api/v1/projects/{projectId}/members |
| Resolve duplicate member | UUID input | 409 `conflict` → inline error "This user is already a member" | Response of POST /api/v1/projects/{projectId}/members |
| Remove member | [Remove] on a member row (owner only; hidden on the owner's own row — the API answers 409 for it) | RemoveMemberConfirm (danger): "Their assigned tasks in this project become unassigned."; on 204 the row disappears and the tasks query is invalidated | DELETE /api/v1/projects/{projectId}/members/{userId} |
| Change page | PaginationControls [← Prev] / [Next →] | Fetch and render the requested page | GET /api/v1/projects/{projectId}/members (`page={n}`, `pageSize=50`) |
| Copy a member's id | UserIdBadge (click) | Full UUID copied to the clipboard (for assigning or out-of-band coordination) | None |
