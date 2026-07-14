# Stakeholder Definition Document Template

> **Purpose**: Define what we are building, why we are building it, and what the first version will and will not do. This document serves as the product north star for AI task generation.

> **Context budget note:** This document is loaded into AI context. Keep it contract-style —
> tables, schemas, rules, one example each. Move narrative and history to `docs/rationale/`
> and link it; rationale files are never loaded by default.

---

## 1. Executive Summary

> *A concise statement of the product's purpose and success criteria.*

This document defines **what we are building, why we are building it, and what [version] will and will not do**.

The product is a **[product type/category]** designed to:
- [Core value proposition 1]
- [Core value proposition 2]
- [Core value proposition 3]
- [Core value proposition 4]

[Version] is intentionally narrow. Its goal is **[primary goal], not [explicitly excluded goal]**.

**Success means:**
- [Measurable success criterion 1]
- [Measurable success criterion 2]
- [Measurable success criterion 3]
- [Measurable success criterion 4]

---

## 2. Core Business Problem

> *Describe the problem space the product addresses.*

[Current solution/approach] today suffers from:
- [Pain point 1]
- [Pain point 2]
- [Pain point 3]
- [Pain point 4]

**[User type 1]** wants [desired outcome 1].
**[User type 2]** wants [desired outcome 2].

This platform solves both by [how the solution addresses both needs].

---

## 3. Product Philosophy

### 3.1 Guiding Principles

> *The non-negotiable design principles that inform all decisions.*

- **[Principle 1 name]**: [Explanation]
- **[Principle 2 name]**: [Explanation]
- **[Principle 3 name]**: [Explanation]
- **[Principle 4 name]**: [Explanation]
- **[Principle 5 name]**: [Explanation]

### 3.2 What We Intentionally Avoid in [Version]

> *Explicit scope exclusions to prevent feature creep.*

- [Excluded feature 1]
- [Excluded feature 2]
- [Excluded feature 3]
- [Excluded feature 4]
- [Excluded feature 5]

---

## 4. [Dominant Stakeholder Concern] Strategy (Optional)

> *If your product has a dominant stakeholder concern — compliance, performance, cost, data privacy, reliability, offline support — describe the strategy for it here. Rename the heading to the actual concern (e.g., "Payment Strategy", "Data Privacy Strategy"). Delete this section if no single concern dominates.*

### 4.1 The Concern and the Chosen Approach

**The concern:** [Name the concern and why stakeholders care — e.g., "Restaurant owners fear losing orders during peak hours if the system goes down"]

**The approach in [version]:** [The deliberate choice made for this version — including simpler options that were chosen over more ambitious ones, and what was explicitly ruled out]

### 4.2 Why This Works

- [Rationale 1 — e.g., matches the actual scale of first customers]
- [Rationale 2 — e.g., avoids infrastructure the team cannot operate yet]
- [Rationale 3 — e.g., keeps the launch date realistic]

[If the approach is intentionally limited, say so explicitly — e.g., "This is a deliberate choice, not an oversight. Revisit when [trigger/version]."]

---

## 5. UX Strategy Overview

> *High-level approach to user experience — the interaction model a stakeholder would care about, not screen-by-screen detail (that lives in the UI Specification).*

### 5.1 Primary Interaction Model

**How users get things done:** [The core interaction pattern — e.g., "a single board with drag-and-drop", "a guided step-by-step wizard", "a conversational flow in a messaging app"]

**Why this model fits the persona:**
- [Reason tied to the persona's skills or context — e.g., "non-technical users need one linear path, not a dashboard of options"]
- [Reason tied to the usage scenario — e.g., "used one-handed on a phone during the busiest hour of the day"]

**Key UX commitments:** [The 2-4 experience qualities the product promises — e.g., "no core action takes more than 3 taps", "every state is recoverable, no dead ends". These become constraints on UI tasks.]

---

## 6. [Asset/Resource] Strategy (Optional)

> *If the product depends on a shared pool of assets or resources — image libraries, content templates, seeded catalogs, starter data — describe how they are sourced, organized, and governed. Rename the heading to the actual asset (e.g., "Image Library Strategy"). Delete this section if not applicable.*

**What the platform provides and why:** [The asset/resource supplied centrally, and the quality or consistency goal it protects — e.g., "a curated image library so menus look professional regardless of the owner's photography skills"]

**Categories:**

- [Category 1] ([examples])
- [Category 2] ([examples])
- [Category 3] ([examples])

**Governance:** [Who can add or modify assets, what customization users are allowed, and any licensing/quality constraints]

---

## 7. Complete User Flow

> *Document the user journey phase by phase.*

### Phase 1 - [Phase Name]

**[Step Name]**
- [Element/component]
- [Actions available]: [Action 1] / [Action 2]

**[Step Name] (Optional)**
- [Element/component]
- [Transition]: [Action]

---

### Phase 2 - [Phase Name]

1. **[Step]**
   - [Interaction type]: [Options]

2. **[Step]**
   - [Logic explanation]
   - [Interaction type]: [Options]

3. **[Step]**
   - [Interaction type]: [Options]

---

### Phase 3 - [Phase Name]

[Continue pattern for remaining phases...]

---

## 8. Backend Responsibilities

> *Define what the backend system must guarantee.*

- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]
- [Responsibility 4]
- [Responsibility 5]

**The frontend [role]. The backend [role].**

---

## 9. Success Metrics for [Version]

> *Quantifiable measures of success.*

- [Metric 1 with target]
- [Metric 2 with target]
- [Metric 3 with target]
- [Metric 4 with target]

---

## 10. Scope Lock ([Version] Contract)

> *Explicit scope boundaries - what's in, what's out.*

**Included:**
- [In-scope item 1]
- [In-scope item 2]
- [In-scope item 3]
- [In-scope item 4]

**Excluded:**
- [Out-of-scope item 1]
- [Out-of-scope item 2]
- [Out-of-scope item 3]
- [Out-of-scope item 4]

Any additions move to [next version].

> **Note — Continuous Development Model:**
> The structure above uses the **versioned model**, which is the default for initial launch. After delivering the first version, projects may switch to the **continuous model** — where features flow independently through a lifecycle (Not Planned → Under Consideration → Current Work → Released) instead of being batched into version-scoped releases. See `guides/release-lifecycle.md` for the transition process and alternative stakeholder definition structure.

---

## 11. Final Note to Stakeholders

This product is not trying to do everything.

It is designed to do **one thing exceptionally well**:

> [Single-sentence value proposition that captures the essence]

This document represents the **agreed foundation** for development and launch.

---

## Usage Notes for AI Task Generation

When generating tasks from this document:

1. **Respect Scope Lock**: Never generate tasks for features explicitly excluded
2. **Align with Principles**: All generated tasks should embody the guiding principles
3. **Target Metrics**: Tasks should demonstrably contribute to success metrics
4. **Backend/Frontend Split**: Respect the responsibility division when assigning work
5. **Phase Awareness**: Understand where each task fits in the user flow
