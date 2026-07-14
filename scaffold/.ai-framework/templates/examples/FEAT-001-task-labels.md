<!-- Reference example — for real work items, copy the blank template from docs/work-items/, not this file. -->

# Feature Brief: Task Labels

> **Product**: TaskFlow — a small web-based task tracker (projects, tasks, labels, notifications) with a REST API backend and SPA frontend.

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | FEAT-001 |
| **Name** | Task Labels |
| **Target Version** | v1.1 |
| **Status** | Tasks Generated <!-- enum: Not Started · In Progress · Tasks Generated · Blocked · Completed · Cancelled --> |
| **Priority** | High |
| **Requested By** | User feedback — 3 of 5 pilot teams asked for a way to group tasks across board columns |
| **Date Created** | 2026-02-10 |

---

## 2. User Story

**As a** Maya (team lead persona), **I want to** attach colored labels to tasks, **so that** I can visually group related work and filter the project board to one theme at a time.

---

## 3. Goal

A team lead can create project-scoped labels, assign them to tasks, and filter the board by label — making cross-column themes (e.g., "frontend", "urgent", "client-request") visible at a glance.

---

## 4. Feature Scope

### 4.1 Included

- Create, rename, recolor, and delete labels within a project (project-scoped)
- Assign multiple labels to a task (up to 10 per task) from the task detail panel
- Display label chips on task cards on the project board
- Filter the project board by a single selected label
- Label colors chosen from a fixed 12-color palette

### 4.2 Excluded

- Global / cross-project labels — each project owns its labels; sharing adds permission complexity that no pilot team asked for
- Label-based automation (e.g., "auto-assign when labeled") — belongs to a future automation feature
- Custom hex colors — a fixed palette guarantees chip contrast and keeps the picker simple
- Multi-label (AND/OR) filter combinations — single-label filter covers the reported need; revisit if usage data shows demand

---

## 5. Acceptance Criteria

- **AC-1**: A project member can create a label with a name (1–30 chars) and a palette color; the label immediately appears in the project's label list
- **AC-2**: A user can assign and remove labels on a task from the task detail panel; changes persist and appear on the board card without a page reload
- **AC-3**: Selecting a label in the board filter shows only tasks carrying that label; clearing the filter restores the full board
- **AC-4**: Renaming or recoloring a label updates every task card that displays it
- **AC-5**: Deleting a label removes it from all tasks after an explicit confirmation dialog stating how many tasks are affected
- **AC-6**: Attempting to create a duplicate label name within the same project returns a validation error and the UI shows an inline message

---

## 6. Key Entities and Business Rules

| Entity | Role in Feature | Key Business Rules |
|--------|----------------|--------------------|
| Label (new) | Created/managed per project; carries name + palette color | Name unique within project (case-insensitive); color must be one of the 12 palette tokens; deleting cascades to assignments only, never to tasks |
| TaskLabel (new join) | Connects tasks to labels (N:M) | Max 10 labels per task; assignment requires both task and label to belong to the same project |
| Task (existing, modified) | Displays and filters by assigned labels | No changes to task fields; board query gains an optional label filter |
| Project (existing) | Owns labels | Label list is visible to all project members; create/rename/delete restricted to members with edit rights |

**New entities required:** Label, TaskLabel (join table) — `docs/data-model.md` must be updated before task generation (flagged: Labels module section missing).

---

## 7. API Impact

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| /api/v1/projects/{projectId}/labels | GET | New | List labels for a project |
| /api/v1/projects/{projectId}/labels | POST | New | Create label (name + color); 409 on duplicate name |
| /api/v1/labels/{id} | PUT | New | Rename / recolor label |
| /api/v1/labels/{id} | DELETE | New | Delete label; removes all assignments |
| /api/v1/tasks/{id}/labels | PUT | New | Replace the set of labels on a task (array of label IDs) |
| /api/v1/projects/{projectId}/tasks | GET | Modified | Gains optional `labelId` query parameter for board filtering |

**New endpoints required:** All five label endpoints above — `docs/api-spec.md` needs a new "Labels" resource section under the Projects module.

---

## 8. UI Impact

| Screen / Component | Status | Description |
|--------------------|--------|-------------|
| Project Board | Modified | Task cards render up to 3 label chips (+N overflow indicator); toolbar gains a label filter dropdown |
| Task Detail Panel | Modified | New "Labels" field with a multi-select picker showing chip previews |
| Label Management Dialog | New | Create/rename/recolor/delete labels; opened from board toolbar and project settings |
| LabelChip (shared component) | New | Reusable chip rendering label name + color, used by board cards, detail panel, and picker |

**New screens required:** Label Management Dialog — must be added to `docs/ui-specification.md`; related frontend tasks should be classified `mockup-first`.

---

## 9. Edge Cases

- Deleting a label that is assigned to tasks — confirmation dialog must state the affected task count; assignments are removed, tasks untouched
- Filtering by a label with zero matching tasks — board shows the standard empty state with a "Clear filter" action, not a blank board
- Assigning the 11th label to a task — API returns a validation error; picker disables further selection at 10 with an explanatory tooltip
- Two users renaming the same label concurrently — last write wins; stale client receives the updated name on next board refresh
- Duplicate name differing only by case ("Urgent" vs "urgent") — rejected as duplicate (case-insensitive uniqueness)
- Label filter active while the filtered label is deleted by another user — board refetch clears the filter and shows a notice

---

## 10. Constraints

- Must not slow initial board load — labels are included in the existing board tasks response, not fetched per card
- No new external dependencies for the color picker; use the design-system palette tokens from `docs/ui-specification.md` Section 2.1
- Board filtering must remain server-side (query parameter) so results stay correct with pagination

**Non-Functional Requirements (optional):** Label filter round-trip (select → filtered board rendered) under 300ms at P95 for boards up to 500 tasks; label chips must meet WCAG 2.1 AA contrast (4.5:1) for chip text on every palette color.

---

## 11. Motivation and Priority Justification

**Motivation:** Pilot feedback — teams currently encode themes in task title prefixes ("[FE] Fix header"), which breaks search and looks noisy. Labels are the most-requested feature from the v1.0 pilot survey (3 of 5 teams, 11 individual requests).

**Impact if delayed:** Title-prefix workaround keeps degrading search quality and onboarding demos; two pilot teams flagged labels as a condition for rolling TaskFlow out to their wider org.

**Dependencies on this feature:** FEAT-005 (Saved board views) assumes labels exist as a filterable dimension.

---

## 12. Traceability

| Reference | Link |
|-----------|------|
| **Persona** | Maya, the team lead — `docs/personas/primary-user.md` |
| **Stakeholder Scope Item** | Scope Lock "Included: visual organization of tasks on the board" (`docs/stakeholder-definition.md` §10) |
| **Success Metric** | "A team lead finds all tasks for a theme in under 10 seconds" (`docs/stakeholder-definition.md` §9) |
| **Related Work Items** | FEAT-005 (Saved board views — depends on this), IMP-001 (notification extraction — no overlap, coordinate merge order) |

---

## 13. Usage Notes for AI Task Generation

When generating tasks from this Feature Brief:

1. **Scope enforcement**: Only generate tasks for capabilities listed in Section 4.1 (Included). Do not generate tasks for items in Section 4.2 (Excluded).
2. **Acceptance criteria coverage**: Every AC in Section 5 must be addressed by at least one generated task's acceptance criteria.
3. **Entity awareness**: Check Section 6 for new entities. If new entities are required, generate data model tasks before feature logic tasks.
4. **API awareness**: Check Section 7 for new endpoints. If new endpoints are required, generate API tasks before frontend integration tasks.
5. **UI awareness**: Check Section 8 for new screens. New screens should trigger `mockup-first` workflow classification on related tasks.
6. **Edge case coverage**: Every edge case in Section 9 must be addressed — either as a dedicated task or as acceptance criteria within a related task.
7. **Constraint respect**: All constraints in Section 10 must be respected across all generated tasks.
8. **Traceability**: Include the Feature Brief ID (FEAT-XXX) in the task generation output summary for cross-referencing.
