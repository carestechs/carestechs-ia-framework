---
kind: screen
screen: task-detail-panel
route: /projects/:projectId/tasks/:taskId
endpoints: [tasks]
---

# Screen: Task Detail Panel

> **Last verified against code:** 2026-07-14 (commit `fixture1`)

**Route**: /projects/:projectId/tasks/:taskId
**Auth**: Required
**Layout**: App shell — overlay panel sliding over the Project Board (see `index.md` Section 4.1)
**Code**: `src/ui/task-detail-panel.tsx`

## Layout Sketch

```
                              ┌───────────────────────────┐
  (Project Board, dimmed)     │ PanelHeader: title · ✕    │
                              ├───────────────────────────┤
                              │ Status dropdown           │
                              │ Assignee · Due date       │
                              │ Description (markdown)    │
                              │                           │
                              └───────────────────────────┘
```

## Component Hierarchy

```
TaskDetailPanel
├── PanelHeader (editable title, close button)
├── TaskFieldsForm (status, assignee, due date)
├── DescriptionEditor (markdown textarea + preview)
└── Dialog (shared — discard-unsaved-changes confirmation)
```

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/tasks.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| TaskDetailPanel | Full task | GET /api/v1/tasks/{id} | On panel open |
| PanelHeader / TaskFieldsForm / DescriptionEditor | Field update | PATCH /api/v1/tasks/{id} | On field blur / dropdown change / save |

## States

<!-- Use the standard patterns from index.md Section 2.5 -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Task loaded | All fields editable inline |
| **Loading** | Task query in flight | Skeleton rows matching the field layout |
| **Empty** | — | Not applicable — panel always shows one task |
| **Error** | Task query failed or task deleted | Inline error banner with retry + close actions |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| Edit title and blur | PanelHeader input | Title saves; board card updates via query invalidation | PATCH /api/v1/tasks/{id} |
| Change status | TaskFieldsForm dropdown | Task moves to the new board column behind the panel | PATCH /api/v1/tasks/{id} |
| Edit description and save | DescriptionEditor | Markdown body persists | PATCH /api/v1/tasks/{id} |
| Close with unsaved description edits | ✕ button | `Dialog` asks to discard or keep editing | None |
| Close panel | ✕ button / Escape | Route returns to /projects/:projectId/board | None |
