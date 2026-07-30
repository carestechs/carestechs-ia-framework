# Stakeholder Definition

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

## 1. Executive Summary

<!-- TODO: Fill in the three essentials -->

- **What:** <!-- What type of product is this? e.g., "A web app that..." -->
- **Value Proposition:** <!-- One sentence: what value does it deliver? -->
- **Success Criteria:** <!-- How do you know v1 worked? 1-3 measurable outcomes -->

## 2. Core Business Problem

<!-- TODO: What pain are you solving and for whom? 2-3 sentences. -->

**Current Pain Points:**
- <!-- Pain point 1 -->
- <!-- Pain point 2 -->

**Desired Outcome:**
<!-- What does the world look like after your product exists? -->

## 3. Product Philosophy

### 3.1 Guiding Principles

<!-- TODO: What are 3-5 guiding principles that drive every decision? -->

1. **[Principle Name]:** <!-- e.g., "Simplicity over features — every screen should have one obvious action" -->
2. **[Principle Name]:** <!-- e.g., "Reliability over speed — users trust us because it always works" -->
3. **[Principle Name]:** <!-- e.g., "Convention over configuration — sane defaults, minimal setup" -->

### 3.2 What We Intentionally Avoid in [Version]

<!-- TODO: The anti-scope at philosophy level — approaches or ambitions deliberately ruled out for this version, so AI never suggests them. Distinct from the Scope Lock (§10): that lists features; this lists directions. -->

- <!-- e.g., "No real-time collaboration — single-user editing keeps v1 simple" -->
- <!-- e.g., "No plugin system — we own the whole experience until the core is proven" -->

## 4. [Dominant Stakeholder Concern] Strategy (Optional)

<!-- TODO: If one concern dominates (compliance, performance, cost, privacy, reliability), rename this heading to it and describe the chosen approach + why it works. DELETE this section if no single concern dominates. -->

- **The concern:** <!-- What stakeholders worry about and why -->
- **The approach in [version]:** <!-- The deliberate choice, incl. what was ruled out -->
- **Why this works:** <!-- 1-3 rationale points, e.g., "matches the actual scale of first customers" -->

## 5. UX Strategy Overview

<!-- TODO: The interaction model a stakeholder cares about — not screen detail (that lives in the UI Specification). -->

- **How users get things done:** <!-- Core interaction pattern, e.g., "a single board with drag-and-drop" -->
- **Why this model fits the persona:** <!-- e.g., "non-technical users need one linear path" -->
- **Key UX commitments:** <!-- 2-4 experience promises, e.g., "no core action takes more than 3 taps" — these become constraints on UI tasks -->

## 6. [Asset/Resource] Strategy (Optional)

<!-- TODO: If the product depends on shared assets (image libraries, content templates, seeded catalogs), rename this heading and describe what is provided, its categories, and governance. DELETE this section if not applicable. -->

## 7. Complete User Flow

<!-- TODO: Describe the core user journey in 4-6 steps -->

1. **Entry:** <!-- How does the user arrive? -->
2. **Onboarding:** <!-- What happens first? -->
3. **Core Action:** <!-- What is the main thing they do? -->
4. **Value Moment:** <!-- When do they first feel the benefit? -->
5. **Return Trigger:** <!-- Why do they come back? -->

## 8. Backend Responsibilities

<!-- TODO: What must the backend system guarantee? Calculations, authoritative state, integrity rules -->

- <!-- e.g., All price calculations happen server-side -->
- <!-- e.g., The backend is the single source of truth for order state -->

**The frontend [role]. The backend [role].**

## 9. Success Metrics for [Version]

<!-- TODO: How will you measure whether this version succeeded? -->

| Metric | Target | How Measured |
|--------|--------|--------------|
| <!-- e.g., User activation rate --> | <!-- e.g., 60% within first week --> | <!-- e.g., Analytics event tracking --> |
| <!-- e.g., Task completion time --> | <!-- e.g., <5 minutes for core flow --> | <!-- e.g., Session recordings --> |
| <!-- e.g., User retention --> | <!-- e.g., 40% weekly return rate --> | <!-- e.g., Cohort analysis --> |

## 10. Scope Lock ([Version] Contract)

> Explicit boundaries prevent feature creep. Be specific.

**Included:**
- <!-- Feature/capability 1 -->
- <!-- Feature/capability 2 -->
- <!-- Feature/capability 3 -->

**Excluded:**
- <!-- Thing you won't build yet and why -->
- <!-- Thing you won't build yet and why -->

> **Note — Continuous Development Model:** The structure above uses the **versioned model** (default for initial launch). After the first version ships, projects may switch to the **continuous model** — features flow through a lifecycle (Not Planned → Under Consideration → Current Work → Released) instead of version-scoped releases. See `.ai-framework/guides/release-lifecycle.md` for the transition process.

## 11. Final Note to Stakeholders

This product is designed to do **one thing exceptionally well**:

> <!-- TODO: Single-sentence value proposition that captures the essence -->

This document represents the **agreed foundation** for development and launch.

## Usage Notes for AI Task Generation

> These notes help AI assistants generate tasks aligned with product vision.

- **Always respect the Scope Lock.** Do not suggest features listed as out of scope.
- **Align with Product Philosophy.** Every task should reflect the guiding principles above.
- **Target Success Metrics.** Prioritize work that moves the needle on the metrics listed.
- **Respect the Backend/Frontend split** in Section 8 when assigning work.
- **Reference this document** when making prioritization or scope decisions.
