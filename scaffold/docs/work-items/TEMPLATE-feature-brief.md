<!-- Copy this file to docs/work-items/FEAT-XXX-short-title.md (next free ID) before filling. -->

# Feature Brief: FEAT-XXX — [Feature Name]

> **Purpose**: Describe a feature at a high level before breaking it down into implementation tasks.
> **Template reference**: `.ai-framework/templates/feature-brief.md`

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | FEAT-XXX |
| **Name** | <!-- TODO: Short, descriptive feature name --> |
| **Target Version** | <!-- TODO: Version number or "Continuous" --> |
| **Status** | Not Started <!-- Not Started · In Progress · Tasks Generated · Blocked · Completed · Cancelled --> |
| **Priority** | <!-- TODO: Critical · High · Medium · Low --> |
| **Requested By** | <!-- TODO: Who requested this --> |
| **Date Created** | <!-- TODO: YYYY-MM-DD --> |

---

## 2. User Story

**As a** <!-- TODO: persona name from docs/personas/ -->, **I want to** <!-- TODO: action/capability -->, **so that** <!-- TODO: benefit/outcome -->.

---

## 3. Goal

<!-- TODO: One sentence describing what success looks like for this feature -->

---

## 4. Feature Scope

### 4.1 Included

<!-- TODO: List capabilities included in this feature -->
-
-
-

### 4.2 Excluded

<!-- TODO: List explicitly excluded capabilities and why -->
-
-

---

## 5. Acceptance Criteria

<!-- TODO: Testable conditions — each must be objectively verifiable -->
- **AC-1**:
- **AC-2**:
- **AC-3**:

---

## 6. Key Entities and Business Rules

<!-- TODO: Which data model entities does this feature touch? Reference docs/data-model/ (index + entity shards) -->

| Entity | Role in Feature | Key Business Rules |
|--------|----------------|--------------------|
| <!-- TODO --> | | |

<!-- Retrieval key: Entity names in this table map mechanically to spec shards — entity `TaskLabel` → `docs/data-model/entities/task-label.md` (kebab-case, singular). Task generation reads `docs/data-model/index.md` plus ONLY the entity shards named here, so list every entity the feature touches. (HTML comment so the example path never trips validate-specs reference checks in a filled brief.) -->

**New entities required:** <!-- TODO: None, or list new entities needing shards under docs/data-model/entities/ -->

---

## 7. API Impact

<!-- TODO: Which API endpoints are involved? Reference docs/api-spec/ (index + endpoint shards) -->

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| <!-- TODO --> | | | |

<!-- Retrieval key: Endpoint paths in this table map mechanically to spec shards — resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md` (matches the route segment, plural). Task generation reads `docs/api-spec/index.md` plus ONLY the endpoint shards named here, so list every resource the feature touches. -->

**New endpoints required:** <!-- TODO: None, or list new endpoints needing shards created or extended under docs/api-spec/endpoints/ -->

---

## 8. UI Impact

<!-- TODO: Which screens/components are affected? Reference docs/ui-specification/ (index + screen shards + components.md) -->

| Screen / Component | Status | Description |
|--------------------|--------|-------------|
| <!-- TODO --> | | |

<!-- Retrieval key: Screen names in this table map mechanically to spec shards — screen "Project Board" → `docs/ui-specification/screens/project-board.md` (kebab-case). Task generation reads `docs/ui-specification/index.md` plus ONLY the screen shards named here (and `components.md` when shared components are listed), so name every screen and shared component the feature touches. -->

**New screens required:** <!-- TODO: None, or list new screens needing shards under docs/ui-specification/screens/ -->

---

## 9. Edge Cases

<!-- TODO: Non-obvious scenarios — think about empty states, boundaries, concurrency, permissions, errors -->
-
-

---

## 10. Constraints

<!-- TODO: Technical, business, or timeline constraints -->
-
-

**Non-Functional Requirements (optional):** <!-- TODO: Performance, security, accessibility, or scalability requirements specific to this feature — delete if none beyond the global standards -->

---

## 11. Motivation and Priority Justification

**Motivation:** <!-- TODO: What triggered this feature -->

**Impact if delayed:** <!-- TODO: What happens if we don't build this now -->

**Dependencies on this feature:** <!-- TODO: Other work items blocked by this -->

---

## 12. Traceability

| Reference | Link |
|-----------|------|
| **Persona** | <!-- TODO: docs/personas/[name].md --> |
| **Stakeholder Scope Item** | <!-- TODO: Which scope lock item this addresses --> |
| **Success Metric** | <!-- TODO: Which success metric this contributes to --> |
| **Related Work Items** | <!-- TODO: FEAT/BUG/IMP IDs --> |
