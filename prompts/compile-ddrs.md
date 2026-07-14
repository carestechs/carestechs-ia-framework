# Compile DDRs into Project Templates

## Purpose

Read selected Design Decision Records (DDRs) — their Decision, Rationale, and Constraints sections — and derive template content using derivation rules. Output pre-filled template sections that can be pasted into project docs, so the Design System, component patterns, and state handling are consistent before you write a single line of UI code.

**When to use**: When bootstrapping a new project with a desired visual identity and shared design decisions from a shared DDR repo. The DDR repo location is organization-specific (as configured by your organization) — skip this prompt if you have no DDR repo. Run this after compiling ADRs and before filling in templates (see `guides/getting-started.md`).

---

## How to Use

- **AI agents (Claude Code, etc.):** Read each DDR file the user specifies (from your organization's DDR repo or local paths) — and the profile file first, if one is specified, to get the DDR list and override values. Follow the **Guidance**, **Output Format**, and **Constraints** sections below, read the target templates from `.ai-framework/templates/` for the correct heading structure, and output the compiled sections. **Write the Component Examples Appendix to `docs/component-examples.md`**; paste the other sections into the project docs (or write them directly into the target docs when asked).
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the **Chat Workflow Template (XML)** appendix — paste your DDR files into the `<ddrs>` block and include the Guidance, Output Format, and Constraints sections of this prompt alongside it.

---

## Required Context

Compile prompts have their own input set — see the DDR Compilation section of `guides/context-compilation.md` for the canonical recipe.

Prompt-specific notes:

| Input | Priority | What to Include |
|-------|----------|-----------------|
| DDR files | Required | All DDR files the user wants to compile (or a profile that references them) |
| Profile file | Optional | A profile from the DDR repo for curated token values (see Profile Format Reference below) |
| `.ai-framework/templates/` | Recommended | Target templates for correct heading structure (agents read these directly) |

What NOT to include:
- Project docs (`docs/`) — DDR compilation pre-fills templates, it doesn't read existing project docs
- ADR files — ADR compilation is a separate step using `compile-adrs.md`
- Prompt templates for other task types — this prompt is self-contained

---

## Guidance

### DDR Derivation Rules

These rules teach the AI how to transform generic DDR content (Decision, Rationale, Constraints, Examples) into template sections. The rules derive everything from the standard DDR format — no extra metadata is needed in the DDRs.

#### Rule 1: Every DDR → ui-specification.md Key UI Decisions

**Input:** DDR title + Decision + first Rationale bullet
**Output:** One row in the Key UI Decisions table (Section 1.2)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| *DDR title (short form)* | *Decision statement (condensed)* | *First Rationale bullet (condensed)* |

*Every* selected DDR produces exactly one row, regardless of category.

#### Rule 2: Category Targeting

The DDR's **Category** field determines which additional template sections it targets, beyond the Key UI Decisions table:

| Category | Target Documents | Target Sections |
|----------|-----------------|-----------------|
| `design-tokens` | ui-specification.md | Brand Colors (2.1), Typography Scale (2.2), Spacing Scale (2.3) |
| `components` | ui-specification.md, CLAUDE.md | Component Library (2.4); Design Patterns to Follow |
| `layout` | ui-specification.md | Shared Layouts (Section 4) constraints |
| `interactions` | CLAUDE.md | Design Patterns to Follow, Design Anti-Patterns to Avoid |
| `states` | ui-specification.md | State Patterns (2.5) |
| `accessibility` | CLAUDE.md | Design Patterns to Follow, Design Anti-Patterns to Avoid |
| `responsive` | ui-specification.md | Responsive Breakpoints (2.6) |

The CLAUDE.md target headings are exactly `#### Design Patterns to Follow` and `#### Design Anti-Patterns to Avoid` — match them verbatim when merging.

#### Rule 3: Constraints → CLAUDE.md Design Patterns / Anti-Patterns

**Input:** Constraint bullets from "Constraints (non-negotiable for AI)"
**Output:** CLAUDE.md entries under the `#### Design Patterns to Follow` / `#### Design Anti-Patterns to Avoid` subsections

- Constraints with **positive phrasing** (MUST, ALWAYS, use, ensure, each, every, all) → **Design Patterns to Follow** bullet
- Constraints with **negative phrasing** (NEVER, MUST NOT, do not, no direct, avoid) → **Design Anti-Patterns to Avoid** bullet

Format each derived entry as: `- **[Short label]:** [constraint text] <!-- from: ddr-file.md -->` — the trailing HTML comment is the only traceability marker (never inline `(from: ...)` text).

When a constraint contains both a positive and negative aspect, split it into one Pattern entry and one Anti-Pattern entry.

#### Rule 4: design-tokens DDRs → ui-specification.md Design System

**Input:** DDRs with `Category: design-tokens`
**Output:**

- **Brand Colors** (2.1) — Populate the color token table from color-palette DDR. If a profile provides override hex values, use those instead of placeholders.
- **Typography Scale** (2.2) — Populate font family, size, weight, line-height from typography-scale DDR. Profile overrides apply.
- **Spacing Scale** (2.3) — Populate spacing token table from spacing-scale DDR.
- Additional design-tokens DDRs (shadows, border-radius, opacity, transitions) → add rows to an **Additional Tokens** table below 2.3, or incorporate into existing tables where natural.

#### Rule 5: components DDRs → ui-specification.md Component Library + CLAUDE.md Design Patterns

**Input:** DDRs with `Category: components`
**Output:**

- **Component Library** (2.4) — One row per component DDR with the component name, variants, and key customization notes from the Decision section
- **CLAUDE.md Design Patterns to Follow** — Positive constraints from each component DDR
- **CLAUDE.md Design Anti-Patterns to Avoid** — Negative constraints from each component DDR
- **Component Examples Appendix** — Collect all Examples sections from component DDRs into a reference appendix (for use by the mockup prompt) — see Rule 9

#### Rule 6: states DDRs → ui-specification.md State Patterns (Section 2.5)

**Input:** DDRs with `Category: states`
**Output:**

- The **State Patterns** table (Section 2.5):

| State | Pattern | Key Constraints | Example Reference |
|-------|---------|----------------|-------------------|
| *Loading (skeleton)* | *Skeleton placeholders matching content layout* | *From skeleton-loading DDR constraints* | *See Component Examples Appendix* |
| *Loading (action)* | *Inline spinner for button/form actions* | *From spinner DDR constraints* | *See Component Examples Appendix* |
| *Empty* | *Centered heading + description + CTA* | *From empty-state DDR constraints* | *See Component Examples Appendix* |
| *Error* | *Inline banner with retry / full-page error* | *From error-state DDR constraints* | *See Component Examples Appendix* |

#### Rule 7: layout DDRs → ui-specification.md Shared Layouts

**Input:** DDRs with `Category: layout`
**Output:**

- **Shared Layouts** (Section 4) — Add constraint annotations to the existing layout section:
  - Sidebar width, collapse behavior, persistence from sidebar-navigation DDR
  - Content max-width and centering from content-width DDR
  - Page-level padding values from page-padding DDR

Format as constraint comments within the layout descriptions.

#### Rule 8: responsive DDRs → ui-specification.md Responsive Breakpoints (Section 2.6)

**Input:** DDRs with `Category: responsive`
**Output:**

- The **Responsive Breakpoints** table (Section 2.6):

| Breakpoint | Width | Tailwind Prefix | Primary Use |
|------------|-------|-----------------|-------------|
| *Mobile* | *< 640px* | *(base)* | *Single column, stacked layout* |
| *Tablet* | *640px - 1023px* | *sm:, md:* | *Collapsed sidebar, 2-column* |
| *Desktop* | *1024px+* | *lg:, xl:* | *Full sidebar, multi-column* |

- Include the chosen responsive strategy (mobile-first or desktop-first) as a note below the table.

#### Rule 9: Examples Sections → Component Examples Appendix

**Input:** All DDRs with non-empty Examples sections (typically `components` and `states` categories)
**Output:**

- A **Component Examples Appendix** — a collected reference of all HTML/CSS examples, organized by category, that the mockup generation prompt can reference. Written to **`docs/component-examples.md`**.
- Each example block should include the DDR source file name and the example title.

### Step 0: Validate Dependencies

Before compiling, check each DDR's `Requires` and `Conflicts with` fields:

1. **Missing dependencies**: If a DDR lists a `Requires` that is NOT in the selected DDR set, emit a **warning** at the top of the output: `⚠ [ddr-file] requires [missing-ddr] which is not in the selected set. Include it or remove the dependent DDR.`
2. **Conflicting DDRs**: If two selected DDRs list each other in `Conflicts with`, emit an **error** at the top of the output: `❌ [ddr-a] conflicts with [ddr-b]. Remove one before compiling.`
3. **If using a profile**: Read the profile to determine which DDRs are included. Warn if any DDR listed in the profile is missing from the DDR repo.

Proceed with compilation only after listing all warnings/errors. If there are errors (conflicts), stop and ask the user to resolve them. Warnings (missing dependencies) can proceed but should be surfaced.

### Step 1: Apply Profile Overrides (if applicable)

If a profile is provided:
1. Read the profile's override values for design tokens (colors, fonts, spacing, etc.)
2. Use profile values instead of DDR placeholder/default values when populating token tables
3. Note the profile name in the output header for traceability

### Step 2: Derive and Compile

Read all provided DDR files and apply the Derivation Rules to generate pre-filled template fragments for each target document.

For each target document:
1. Use the exact heading structure from the corresponding template in `.ai-framework/templates/`
2. Apply Rule 1 (every DDR → ui-specification.md Key UI Decisions row)
3. Apply Rule 2 (category targeting) to determine additional target sections
4. Apply Rules 3-9 to derive Design System tables, Patterns, Anti-Patterns, State Patterns, Responsive Breakpoints, and Component Examples
5. Merge content from all DDRs that target the same section (e.g., combine all design-tokens into the Design System section)
6. De-duplicate if multiple DDRs contribute the same rule
7. Mark remaining project-specific sections with `<!-- TODO: [description] -->` scaffolds
8. Preserve the DDR source in an HTML comment (e.g., `<!-- from: color-palette.md -->`) for traceability

### DDR Format Reference

Each DDR file in the DDR repo follows this standard structure. The compilation prompt derives all template content from Decision, Rationale, Constraints, and Examples — no extra metadata is needed:

```markdown
# [Decision Title]

**Category:** design-tokens | components | layout | interactions | states | accessibility | responsive
**Status:** Active
**Requires:** [DDR file paths this decision depends on — omit if none]
**Conflicts with:** [DDR file paths that are mutually exclusive — omit if none]

## Decision

[1-2 sentences: what was decided]

## Rationale

- [Why this decision was made]
- [What alternatives were considered]

## Constraints (non-negotiable for AI)

- [Hard rule 1 — MUST/NEVER phrasing for compilation]
- [Hard rule 2]

## Examples

[Inline HTML/CSS code blocks — required for components and states categories]
```

The derivation rules use Category to determine target document sections and Constraint phrasing (MUST/NEVER) to determine whether content becomes a Pattern or Anti-Pattern.

### Profile Format Reference

A profile is a curated list of DDRs with specific token overrides for a visual identity, stored in the DDR repo (location is organization-specific):

```markdown
# [Profile Name]

**Description:** [One sentence describing the visual identity]
**Target:** [What kind of projects this profile is for]

## Included DDRs

[List of DDR file paths to compile]

## Token Overrides

[Override values for design tokens — colors, fonts, spacing]
[These values replace DDR defaults when compiling]
```

---

## Output Format

Generate one block per target document. Each block contains merged sections from all applicable DDRs (derived via the Derivation Rules), with TODO placeholders for project-specific content.

Output ONLY the sections that derivation rules fill, plus TODO scaffolds for the rest. Do not generate project-specific content (screen inventory, screen specifications, shared components).

### Output: ui-specification.md sections

Merge into these sections from the `ui-specification.md` template:
- **Key UI Decisions** (1.2) — one row per DDR (Rule 1)
- **Brand Colors** (2.1) — from design-tokens/color-palette DDR (Rule 4), with profile overrides
- **Typography Scale** (2.2) — from design-tokens/typography-scale DDR (Rule 4), with profile overrides
- **Spacing Scale** (2.3) — from design-tokens/spacing-scale DDR (Rule 4)
- **Component Library** (2.4) — one row per components-category DDR (Rule 5)
- **State Patterns** (2.5) — from states-category DDRs (Rule 6)
- **Responsive Breakpoints** (2.6) — from responsive-category DDRs (Rule 8)
- **Shared Layouts** (4) — layout constraints from layout-category DDRs (Rule 7)

Leave all other sections (Screen Inventory, Screen Specifications, Shared Components) as TODO scaffolds.

### Output: CLAUDE.md sections

Merge into these sections from the `claude-md.md` template:
- **Design Patterns to Follow** (`#### Design Patterns to Follow`) — derived from positive-phrased Constraints (Rule 3), especially from components, interactions, and accessibility DDRs
- **Design Anti-Patterns to Avoid** (`#### Design Anti-Patterns to Avoid`) — derived from negative-phrased Constraints (Rule 3)

Leave all other sections (Project Overview, Common Commands, Code Patterns, etc.) as TODO scaffolds.

### Output: Component Examples Appendix → `docs/component-examples.md`

Collect all Examples sections from DDRs (Rule 9) into **`docs/component-examples.md`**:
- Organized by category (components, then states)
- Each example block labeled with source DDR file name
- HTML/CSS code blocks preserved exactly as written in the DDR

This appendix is referenced by the mockup generation prompt for visual consistency.

---

## Constraints

- Output ONLY sections that the derivation rules fill — mark everything project-specific with `<!-- TODO: ... -->` scaffolds, never invented content
- Heading structure must match the templates in `.ai-framework/templates/` exactly (in particular `#### Design Patterns to Follow` / `#### Design Anti-Patterns to Avoid` in CLAUDE.md)
- Traceability uses HTML comments only (`<!-- from: ddr-file.md -->`) — never inline `(from: ...)` text
- Profile override values replace DDR defaults — never mix the two for the same token
- Preserve DDR example code blocks exactly as written — do not restyle or "improve" them
- De-duplicate rows/bullets when multiple DDRs contribute the same rule

---

## Post-Generation Checklist

After the AI generates compiled template sections:

- [ ] Every DDR has a row in ui-specification.md Key UI Decisions (Rule 1)
- [ ] design-tokens DDRs populate the Design System tables — colors, typography, spacing (Rule 4)
- [ ] components DDRs populate Component Library table (Rule 5)
- [ ] states DDRs populate the State Patterns table (Section 2.5) with 4 columns (Rule 6)
- [ ] layout DDRs annotate Shared Layouts section with constraint comments (Rule 7)
- [ ] responsive DDRs populate the Responsive Breakpoints table (Section 2.6) (Rule 8)
- [ ] All Examples sections collected into `docs/component-examples.md` (Rule 9)
- [ ] Every DDR's Constraints appear as Design Patterns or Anti-Patterns in CLAUDE.md (Rule 3)
- [ ] Profile override values are used instead of DDR defaults (if profile provided)
- [ ] No duplicate rows in merged tables
- [ ] DDR sources are traceable via HTML comments (e.g., `<!-- from: color-palette.md -->`)
- [ ] TODO scaffolds exist for all project-specific sections (screens, components, etc.)
- [ ] Output heading structure matches `.ai-framework/templates/`
- [ ] Paste compiled sections into your project docs and fill in the TODO scaffolds

---

## Chat Workflow Template (XML)

Copy this skeleton, paste your DDR files into the `<ddrs>` block, and submit together with the Guidance, Output Format, and Constraints sections above.

```xml
<ddr-compilation-request>

<ddrs>
<!-- REQUIRED: Paste or list the DDR files to compile.
     Each DDR should follow the standard DDR format with Category, Decision,
     Rationale, Constraints, and Examples sections.
     Alternatively, specify a profile file that lists the DDRs to include. -->
[Paste DDR file contents here, or list file paths for agents to read]
</ddrs>

<profile>
<!-- OPTIONAL: If using a profile, paste the profile file here.
     The profile lists which DDRs to include and provides override values
     for design tokens (colors, fonts, spacing). -->
[Paste profile contents, or specify profile file path for agents to read]
</profile>

<templates>
<!-- RECOMMENDED: Include the target templates so the output matches their structure.
     Agents read these directly from .ai-framework/templates/. -->
[Paste relevant templates from .ai-framework/templates/ if using chat workflow]
</templates>

<request>
Compile these DDRs into pre-filled template sections, following the Guidance,
Output Format, and Constraints from prompts/compile-ddrs.md (Step 0 validation first).
</request>

</ddr-compilation-request>
```

---

## Example

Compiling a "Corporate Clean" profile (illustrative — profile and DDR names come from your organization's DDR repo).

### Input (abbreviated)

The agent reads the profile plus every DDR file it lists from the organization's DDR repo. Excerpt showing two representative DDRs and the profile:

```xml
<ddr-compilation-request>

<ddrs>
# Color Palette — Semantic Color Token System
**Category:** design-tokens
**Status:** Active
## Decision
Use semantic color tokens (primary, secondary, success, warning, error, neutral).
## Rationale
- Semantic tokens decouple brand colors from component markup, enabling theme changes
  by modifying token values rather than searching every file for hex values.
## Constraints (non-negotiable for AI)
- MUST reference color tokens in component markup, never raw hex values
- NEVER use raw hex values in component markup — always reference tokens

# Buttons — Variants, Sizes, and States
**Category:** components
**Status:** Active
**Requires:** ddrs/design-tokens/color-palette.md
## Decision
Use 4 button variants: primary, secondary, ghost, destructive. 3 sizes: sm, md, lg.
## Rationale
- Four variants cover all interaction contexts without needing custom components.
## Constraints (non-negotiable for AI)
- MUST include a visible keyboard focus ring on all button variants
- NEVER use more than one primary button per view section
## Examples
<!-- Primary button example -->
<button class="btn btn-primary">Save</button>

[... remaining DDR files listed in the profile ...]
</ddrs>

<profile>
# Corporate Clean Profile
**Description:** Professional design for B2B/enterprise applications
**Target:** Enterprise SaaS, admin dashboards, internal tools

## Token Overrides
| Token | Hex | Usage |
|-------|-----|-------|
| primary | #2563EB | Primary actions, active states |
| error | #DC2626 | Error states |

| Property | Value |
|----------|-------|
| Heading/Body font | Inter |
| body | 0.875rem (14px) / weight 400 / line-height 1.5 |
</profile>

<request>
Compile these DDRs with the corporate-clean profile overrides.
</request>

</ddr-compilation-request>
```

### Derived Output (excerpt)

**ui-specification.md — Key UI Decisions** *(Rule 1: every DDR → one row)*

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Color palette | Semantic tokens with #2563EB primary | Decouples brand colors from markup <!-- from: color-palette.md --> |
| Button variants | Primary/secondary/ghost/destructive × 3 sizes | All interaction contexts covered <!-- from: buttons.md --> |
| ... | *(one row per remaining DDR)* | ... |

**ui-specification.md — Brand Colors** *(Rule 4: design-tokens, with profile overrides)*

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #2563EB | Primary actions, active states <!-- from: color-palette.md, override: corporate-clean --> |
| `error` | #DC2626 | Error states, destructive actions <!-- from: color-palette.md, override: corporate-clean --> |
| ... | ... | ... |

**CLAUDE.md — `#### Design Patterns to Follow`** *(Rule 3: positive-phrased constraints)*

- **Semantic color tokens:** MUST reference color tokens in component markup, never raw hex values <!-- from: color-palette.md -->
- **Button focus rings:** MUST include a visible keyboard focus ring on all button variants <!-- from: buttons.md -->

**CLAUDE.md — `#### Design Anti-Patterns to Avoid`** *(Rule 3: negative-phrased constraints)*

- **No raw hex values:** NEVER use raw hex in component markup — always reference tokens <!-- from: color-palette.md -->
- **No multiple primary buttons:** NEVER use more than one primary button per view section <!-- from: buttons.md -->

**`docs/component-examples.md` — Component Examples Appendix** *(Rule 9)*

```markdown
#### From: buttons.md (components)
<button class="btn btn-primary">Save</button>
```

*(The full run also populates Typography Scale 2.2, Spacing Scale 2.3, Component Library 2.4, State Patterns 2.5, Responsive Breakpoints 2.6, and Shared Layouts constraints — one block per rule, in the same style as above.)*
