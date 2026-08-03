# Feature Brief Template

> **Purpose**: Describe a feature at a high level before breaking it down into implementation tasks. This document bridges the gap between strategic documentation (Stakeholder Definition, Specs) and tactical task generation, ensuring every feature is scoped, justified, and traceable before work begins.
> **When to use**: Before running the feature task generation prompt. One Feature Brief per feature.

> **Context budget note:** This document is loaded into AI context. Keep it contract-style —
> tables, schemas, rules, one example each. Move narrative and history to `docs/rationale/`
> and link it; rationale files are never loaded by default.

---

## 1. Identity

> *Unique identifier and basic metadata for tracking and prioritization.*

| Field | Value |
|-------|-------|
| **ID** | FEAT-[XXX] |
| **Name** | [Feature name — short, descriptive] |
| **Target Version** | [Version or "Continuous"] |
| **Status** | [Not Started · In Progress · Tasks Generated · Blocked · Completed · Cancelled] |
| **Priority** | [Critical · High · Medium · Low] |
| **Requested By** | [Who requested this — stakeholder, user feedback, internal team] |
| **Date Created** | [YYYY-MM-DD] |

<!-- TODO: Fill in all identity fields. Use a sequential ID (FEAT-001, FEAT-002, etc.) -->

---

## 2. User Story

> *Who benefits, what they can do, and why it matters.*

**As a** [persona name], **I want to** [action/capability], **so that** [benefit/outcome].

<!-- TODO: Reference a specific persona from docs/personas/. If multiple personas benefit, list the primary one here and note others in Section 9 (Traceability). -->

---

## 3. Goal

> *One sentence describing what success looks like for this feature.*

[Primary goal — what must be true when this feature is complete]

---

## 4. Feature Scope

> *Explicit boundaries for this specific feature. This is NOT the product scope lock (that lives in the Stakeholder Definition) — this is the scope of this individual feature.*

### 4.1 Included

- [Capability or behavior included in this feature]
- [Capability or behavior included in this feature]
- [Capability or behavior included in this feature]

### 4.2 Excluded

> *What this feature intentionally does NOT do — prevents scope creep during task generation.*

- [Explicitly excluded capability — and why]
- [Explicitly excluded capability — and why]

<!-- TODO: Be specific about exclusions. "No admin panel" is better than "keep it simple". -->

---

## 5. Acceptance Criteria

> *Testable conditions that must all be true for this feature to be considered complete. These directly feed into task acceptance criteria during generation.*

- **AC-1**: [Testable criterion]
- **AC-2**: [Testable criterion]
- **AC-3**: [Testable criterion]
- **AC-4**: [Testable criterion]

<!-- TODO: Each criterion must be objectively verifiable — "user sees X", "system returns Y", "database contains Z". Avoid subjective criteria like "feels fast". -->

---

## 6. Key Entities and Business Rules

> *Which data model entities does this feature touch? What business rules govern behavior? Reference `docs/data-model/` (index + entity shards) for full entity definitions.*

| Entity | Role in Feature | Key Business Rules |
|--------|----------------|--------------------|
| [Entity 1] | [How this feature uses/creates/modifies it] | [Rules that apply — validation, constraints, state transitions] |
| [Entity 2] | [How this feature uses/creates/modifies it] | [Rules that apply] |

<!-- Retrieval key: Entity names in this table map mechanically to spec shards — entity `TaskLabel` → `docs/data-model/entities/task-label.md` (kebab-case, singular). Task generation reads `docs/data-model/index.md` plus ONLY the entity shards named here, so list every entity the feature touches. (HTML comment so the example path never trips validate-specs reference checks in a filled brief.) -->

<!-- TODO: Repeat rows for each entity involved. If the feature requires a NEW entity without a shard under docs/data-model/entities/, note it here and flag that a new entity shard is needed. -->

**New entities required:** [None · List new entities that need shards created under `docs/data-model/entities/`]

---

## 7. API Impact

> *Which API endpoints does this feature require? Reference `docs/api-spec/` (index + endpoint shards) for full endpoint definitions.*

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| [/api/v1/resource] | [GET · POST · PUT · DELETE] | [Existing · New · Modified] | [Brief description of what changes or what it does] |

<!-- Retrieval key: Endpoint paths in this table map mechanically to spec shards — resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md` (matches the route segment, plural). Task generation reads `docs/api-spec/index.md` plus ONLY the endpoint shards named here, so list every resource the feature touches. -->

<!-- TODO: If the feature requires NEW endpoints without a shard under docs/api-spec/endpoints/, note them here and flag that a new resource shard is needed. -->

**New endpoints required:** [None · List new endpoints that need shards created or extended under `docs/api-spec/endpoints/`]

---

## 8. UI Impact

> *Which screens and components does this feature affect? Reference `docs/ui-specification/` (index + screen shards + `components.md`) for full screen definitions.*

| Screen / Component | Status | Description |
|--------------------|--------|-------------|
| [Screen or component name] | [Existing · New · Modified] | [What changes or what it shows] |

<!-- Retrieval key: Screen names in this table map mechanically to spec shards — screen "Project Board" → `docs/ui-specification/screens/project-board.md` (kebab-case). Task generation reads `docs/ui-specification/index.md` plus ONLY the screen shards named here (and `components.md` when shared components are listed), so name every screen and shared component the feature touches. -->

<!-- TODO: If the feature requires NEW screens without a shard under docs/ui-specification/screens/, note them here. New screens will likely trigger `mockup-first` workflow on related tasks. -->

**New screens required:** [None · List new screens that need shards created under `docs/ui-specification/screens/`]

---

## 9. Edge Cases

> *Non-obvious scenarios that task generation must account for.*

- [Edge case 1 — describe the scenario and expected behavior]
- [Edge case 2 — describe the scenario and expected behavior]
- [Edge case 3 — describe the scenario and expected behavior]

<!-- TODO: Think about: empty states, boundary values, concurrent operations, permission boundaries, error recovery, offline behavior. -->

---

## 10. Constraints

> *Technical, business, or timeline constraints that limit how this feature can be implemented.*

- [Constraint 1 — e.g., "Must work within WhatsApp Flows JSON structure"]
- [Constraint 2 — e.g., "Cannot add new external dependencies"]
- [Constraint 3 — e.g., "Must be backward-compatible with existing API clients"]

**Non-Functional Requirements (optional):** [Performance, security, accessibility, or scalability requirements specific to this feature — e.g., "List renders 500 items in under 200ms", "New UI meets WCAG 2.1 AA". Delete if none beyond the global standards.]

---

## 11. Motivation and Priority Justification

> *Why this feature, why now? This helps AI prioritize tasks within the feature and helps humans prioritize features against each other.*

**Motivation:** [What triggered this feature — user request, metric decline, strategic goal, dependency for another feature]

**Impact if delayed:** [What happens if we don't build this now]

**Dependencies on this feature:** [Other features or work items that are blocked until this is done]

---

## 12. Traceability

> *Links this feature back to strategic documentation. Ensures every feature is grounded in product vision and user needs.*

| Reference | Link |
|-----------|------|
| **Persona** | [Which persona(s) this serves — reference `docs/personas/[name].md`] |
| **Stakeholder Scope Item** | [Which item in the Stakeholder Definition's scope lock this addresses] |
| **Success Metric** | [Which success metric from the Stakeholder Definition this contributes to] |
| **Related Work Items** | [Other FEAT/BUG/IMP IDs that relate to this feature] |

<!-- TODO: Every feature should trace back to at least one scope item and one success metric. If it doesn't, question whether it belongs in the current version. -->

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
