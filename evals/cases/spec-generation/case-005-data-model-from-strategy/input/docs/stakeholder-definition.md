# Stakeholder Definition — TaskFlow (V1)

> *Subset of the framework stakeholder template — sections a strategy-stage fixture does not need are omitted; numbering is sequential over the retained sections.*

## 1. Executive Summary

This document defines **what we are building, why we are building it, and what V1 will and will not do**.

The product is a **small web-based task tracker for teams** designed to:
- Give every team a shared project with clear task ownership
- Make task state (status, due date, assignee) explicit and always current
- Keep discussion attached to the task it concerns
- Show what changed in a project without asking anyone

V1 is intentionally narrow. Its goal is **dependable core tracking, not a full collaboration suite**.

**Success means:**
- A new team creates a project, adds members, and tracks its first task in under 10 minutes
- "Who owns this and when is it due?" is answerable from the task list alone

---

## 2. Product Philosophy

### 2.1 Guiding Principles

- **Explicit membership**: every project has an explicit member list; only members can see or touch a project's data.
- **State over chat**: task status, due date, and assignee are structured fields, never prose conventions buried in comments.
- **Derive, don't duplicate**: the project activity feed is computed on read from existing task and comment records — V1 stores no separate event log.

---

## 3. Complete User Flow

1. **Sign in** — the user authenticates against the external auth service; the app receives an opaque user id (UUID) and stores nothing else about the user.
2. **Create or open a project** — the creator becomes the project owner and its first member.
3. **Manage membership** — the owner adds or removes members by their auth user id; each membership carries a role (owner or member).
4. **Create and update tasks** — any member creates tasks with a title, optional description, a status, and an optional **day-precision due date** (a calendar date; no time of day).
5. **Assign tasks** — a task is assigned to exactly one current project member, or left unassigned.
6. **Discuss and review** — members comment on tasks; the project activity feed lists recent task and comment changes, newest first.

---

## 4. Backend Responsibilities

- Manage projects: create, rename, delete — deleting a project removes everything inside it.
- Manage tasks within a project: status transitions, day-precision due dates, a single optional assignee.
- Enforce per-project membership: every read and write is scoped to projects the caller is a member of.
- Manage membership records: one record per (project, user) pair, carrying an owner/member role.
- Store comments on tasks, attributed to their author and ordered by time.
- Serve a per-project activity feed **derived on read** from task and comment records — no dedicated event table in V1.

**The frontend renders and edits. The backend owns all state, validation, and access rules.**

---

## 5. Success Metrics for V1

- ≥ 80% of tasks carry an assignee within one day of creation (ownership is actually used).
- A comment is visible in the project activity feed on the next page load (no stale reads).

---

## 6. Scope Lock (V1 Contract)

**Included:**
- Projects
- Tasks (status, due date, assignee)
- Project membership
- Task comments

**Excluded:**
- Labels/tags
- Notifications
- File attachments
- Real-time collaboration
