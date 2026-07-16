---
kind: screen
screen: project-members
route: /projects/:projectId/members
endpoints: [project-members, projects]
---

# Screen: Project Members

> **Last verified against code:** 2026-07-16 (commit `fixture7`)

**Route**: /projects/:projectId/members
**Auth**: Required
**Layout**: App shell + ProjectSubnav (see `index.md` Section 4.1)

The project's explicit member list. Owner-only controls (add/remove) appear when the caller's user id equals the project's `ownerId`. Members are added by their opaque auth-service UUID — there is no user search or profile lookup (no such endpoint exists). Covers user flow phase 3.

## Layout Sketch

```
┌ ProjectSubnav: ‹Project name›   [Board] [Members]* [Activity] ┐
│ Members (4)                                  [+ Add member]   │  ← owner only
├───────────────────────────────────────────────────────────────┤
│ Member            │ Role   │ Joined      │                    │
│ ‹UserIdChip (you)›│ owner  │ 2026-07-01  │                    │
│ ‹UserIdChip›      │ member │ 2026-07-02  │        [Remove]    │  ← owner only
│ ‹UserIdChip›      │ member │ 2026-07-05  │        [Remove]    │
├───────────────────────────────────────────────────────────────┤
│                     ‹Pagination — meta.totalCount›            │
└───────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
ProjectMembersPage                  — src/ui/project-members.tsx (one React file per screen)
├── ProjectSubnav                   — shared (components.md); fetches the project
├── MembersHeader                   — count + AddMemberButton (owner only)
├── MemberTable
│   └── MemberRow                   — UserIdChip (userId), RoleBadge (owner|member), joined date,
│                                     Remove button (owner only; never on the owner's row)
├── Pagination                      — shared (components.md)
├── AddMemberDialog                 — shared Dialog wrapper: userId (UUID) input
├── ConfirmDialog                   — shared (components.md), danger variant (remove member)
├── ErrorBanner / Skeleton          — shared (components.md)
```

## Component → API Mapping

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| ProjectSubnav | Project header (`ProjectDto` — `ownerId` gates owner controls) | GET /api/v1/projects/{id} | On page load |
| MemberTable | Members (`ProjectMemberDto[]`, `createdAt` ascending — owner first) | GET /api/v1/projects/{projectId}/members?page&pageSize | On page load, on page change |
| AddMemberDialog | Created membership (`ProjectMemberDto`) | POST /api/v1/projects/{projectId}/members | On form submit |
| ConfirmDialog (remove) | — | DELETE /api/v1/projects/{projectId}/members/{userId} | On confirm |

> Responses use the envelope from `docs/api-spec/index.md` Section 2.1. `userId` values are opaque auth-service UUIDs — rendered by `UserIdChip`, never resolved to names or emails.

## States

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Members loaded | Table sorted `createdAt` ascending (owner's row first, per API sort); "(you)" suffix on the caller's chip; Remove buttons only for the owner, and never on the owner's own row |
| **Loading** | GET members in flight | 4 Skeleton table rows matching column layout (Section 2.5 pattern) |
| **Empty** | `meta.totalCount` = 1 (a project always has its owner row) | Table shows the owner row plus an inline hint: "Just you so far — add teammates by their user id." with CTA (owner only) opening AddMemberDialog. A zero-member list cannot occur |
| **Error** | GET members (or project) failed | ErrorBanner with message mapped from `error.code` + Retry; `403 forbidden` / `404 not-found` render the full-page error pattern with "Back to projects" (Section 2.5) |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Click "+ Add member" | Header button (owner only) | Open AddMemberDialog: one field for the auth-service user UUID, with client-side UUID format check | None until submit |
| Submit new member | Dialog "Add" button | On 201: close dialog, row appears with role `member`, invalidate `['members', projectId]` | POST /api/v1/projects/{projectId}/members |
| Submit malformed id | Dialog "Add" button | 400 `validation-error`: render `error.fields.userId` message under the field | POST /api/v1/projects/{projectId}/members |
| Submit existing member | Dialog "Add" button | 409 `conflict`: inline "This user is already a member" under the field | POST /api/v1/projects/{projectId}/members |
| Remove a member | Row "Remove" (owner only) → ConfirmDialog (danger) warning "their assigned tasks in this project become unassigned" | On 204: row disappears; invalidate `['members', projectId]` and `['tasks', projectId]` (assignments were nulled server-side) | DELETE /api/v1/projects/{projectId}/members/{userId} |
| Change page | Pagination controls | Fetch and render the requested page | GET /api/v1/projects/{projectId}/members?page={n} |

> Roles are display-only: the API has no role-change endpoint, and the owner row can never be removed (the UI never offers it; the API would answer 409 `conflict`). Do not invent role management UI.
