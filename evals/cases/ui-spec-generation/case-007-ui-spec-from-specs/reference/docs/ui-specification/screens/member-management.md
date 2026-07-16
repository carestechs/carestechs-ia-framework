---
kind: screen
screen: member-management
route: /projects/:projectId/members
endpoints: [projects, project-members]
---

# Screen: Member Management

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects/:projectId/members
**Auth**: Required
**Layout**: App shell — see `index.md` Section 4.1
**Code**: `src/ui/member-management.tsx` (planned)

## Layout Sketch

```
┌──────────────────────────────────────────────────────────┐
│ ← Back to board        Members — {project name} (h1)     │
├──────────────────────────────────────────────────────────┤
│ [ auth user id (UUID)              ] [ Add member ]      │  ← owner only
├──────────────────────────────────────────────────────────┤
│ ⬤ UserBadge   role: owner    joined 2026-07-01           │
│ ⬤ UserBadge   role: member   joined 2026-07-03  [Remove] │
│ ⬤ UserBadge   role: member   joined 2026-07-10  [Remove] │
└──────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
MemberManagementPage
├── PageHeader
│   └── BackLink (→ /projects/:projectId/board)
├── AddMemberForm (rendered only when the caller is the owner)
├── MemberTable
│   └── MemberRow (×N)
│       ├── UserBadge (shared)
│       ├── RoleTag (owner | member)
│       └── RemoveButton (owner only; hidden on the owner's own row)
├── Dialog (shared — destructive removal confirmation)
├── EmptyState (shared — defensive only, see States)
└── ErrorBanner (shared)
```

The caller's role is derived from the loaded member list (the row whose `userId` equals the JWT subject); owner-only surfaces (`AddMemberForm`, `RemoveButton`) are hidden for plain members, and the API enforces it regardless (`forbidden`).

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/{projects,project-members}.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| MemberManagementPage | Project name and ownerId for the header | GET /api/v1/projects/{id} | On load |
| MemberTable | Membership rows | GET /api/v1/projects/{projectId}/members | On load; refetch after add/remove |
| AddMemberForm | New membership | POST /api/v1/projects/{projectId}/members | On submit (owner only) |
| RemoveButton | Membership removal | DELETE /api/v1/projects/{projectId}/members/{userId} | On confirm in destructive Dialog (owner only) |

## States

<!-- Use the standard patterns from index.md Section 2.5 -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Members loaded | Table sorted by join date, owner row first; owner sees form + remove buttons |
| **Loading** | Member query in flight | Skeleton rows matching table layout; form disabled |
| **Empty** | Query returns zero rows | Cannot occur in practice — a project always retains its owner's row; defensively render `EmptyState` ("No members found") with a retry CTA |
| **Error** | Member or project query failed | `ErrorBanner` with retry above the table |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Paste an auth user id and submit | AddMemberForm | New row appears with role `member`; input clears | POST /api/v1/projects/{projectId}/members |
| Submit an id that is already a member | AddMemberForm | Inline `conflict` message under the input; row list unchanged | POST /api/v1/projects/{projectId}/members (409) |
| Submit a malformed id | AddMemberForm | Inline `validation-error` message; no request retry until edited | POST /api/v1/projects/{projectId}/members (400) |
| Click "Remove" on a member | MemberRow → destructive Dialog | Dialog warns: "Their assigned tasks in this project become unassigned"; row disappears after confirm | DELETE /api/v1/projects/{projectId}/members/{userId} |
| Attempt to remove the owner | — | Not offered: the owner's row renders no RemoveButton (API would answer `conflict`) | None |
| Click "Back to board" | BackLink | Navigate to /projects/:projectId/board | None |
