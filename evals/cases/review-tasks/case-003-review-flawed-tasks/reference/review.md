<!-- Known-good reference output — not used by any judge check in this case; kept as
     the hand-written anchor showing a review that catches all four planted defects. -->

# Task List Review: FEAT-001 Task Labels

**Task list:** input/tasks/FEAT-001-tasks.md · **Work item:** input/docs/work-items/FEAT-001-task-labels.md
**Reviewed:** 2026-07-15 · **validate-tasks:** 0 errors, 1 warning (coverage table has 5 rows but the work item defines 6 acceptance criteria) · **validate-specs:** 0 errors, 0 warnings

## Verdict

**revise** — R-1 (dependency inversion: the dialog is buildable before the endpoints it calls exist) and R-2 (out-of-scope analytics export endpoint) are CONFIRMED high-severity findings; R-3 and R-4 are CONFIRMED medium. All six rubric points were examined; points not listed below (reference reality, sizing) passed.

## Findings

| ID | Severity | Class | Task(s) | Finding | Required Change |
|----|----------|-------|---------|---------|-----------------|
| R-1 | high | CONFIRMED | T-002, T-004 | Dependency inversion. T-002's own Description and Acceptance Criteria consume all five label endpoints (list/create under `/api/v1/projects/{projectId}/labels`, rename-recolor/delete under `/api/v1/labels/{id}`), but its Dependencies list only T-001 (Database). Those endpoints are created only in T-004 (`src/api/labels.ts` is marked (new) in T-004's files). Building T-002 after T-001 alone leaves the dialog calling endpoints that do not exist — an unbuildable intermediate state (rubric point 4). | Add T-004 to T-002's Dependencies (`T-001, T-004` or just `T-004`, since T-004 already depends on T-001). |
| R-2 | high | CONFIRMED | T-005, T-007 | Scope creep. T-005 adds `GET /api/v1/labels/export` (label usage analytics CSV). No such capability appears in the work item's §4.1 Included list, and no such endpoint appears in the §7 API impact table; its Rationale cites no acceptance criterion, and the coverage table maps no AC to it (rubric point 2). T-007's Description and Acceptance Criteria also test this export. | Delete T-005 (raise it as a separate work item if wanted); remove T-005 from T-007's Dependencies and drop the export cases from T-007's Description/ACs. |
| R-3 | medium | CONFIRMED | T-003 | Type mismatch. T-003 is declared `Type: Backend` and grouped under the Backend heading, but its Description (chips on cards, detail-panel picker) and every file it touches are frontend work: `src/ui/components/label-chip.tsx` (new), `src/ui/components/task-card.tsx`, `src/ui/task-detail-panel.tsx`, `src/ui/project-board.tsx`. Per CLAUDE.md's structure table, `src/ui/` is the React frontend; the canonical schema requires the single Type to match the work. | Change T-003's Type to `Frontend` and move it under the Frontend group. Given it renders new user-facing UI declared in the work item's §8 UI impact, also reconsider `mockup-first` for its Workflow. |
| R-4 | medium | CONFIRMED | — | AC coverage gap. The Acceptance Criteria Coverage table has 5 rows while the work item defines 6 ACs — AC-5 (deleting a label removes it from all tasks after a confirmation dialog stating the affected-task count) has no row. validate-tasks flags exactly this (1 warning). The behavior itself is present in T-002's and T-008's acceptance criteria, so this is a table omission, not missing work — but the mandatory coverage table must attribute every AC (rubric point 1). | Add a row mapping AC-5 to the tasks that implement and verify it (T-002, T-004, T-008). |

## Required Changes Before Implementation

- [ ] R-1: Add T-004 to T-002's Dependencies so the dialog is built only after the label endpoints exist.
- [ ] R-2: Delete T-005 (out-of-scope analytics export); remove it from T-007's Dependencies and strip the export test cases from T-007.
- [ ] R-3: Retype T-003 to `Frontend`, regroup it under Frontend, and reconsider `mockup-first` for its Workflow.
- [ ] R-4: Add the missing AC-5 row to the Acceptance Criteria Coverage table (covered by T-002, T-004, T-008).
