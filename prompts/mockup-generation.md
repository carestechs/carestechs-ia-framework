# HTML Mockup Generation Prompt

## Purpose

Generate a self-contained HTML mockup file for stakeholder visual approval before frontend implementation. Mockups show all screen states side-by-side in a single file that opens in any browser with zero installation.

**When to use**: After completing the UI Specification and before generating feature tasks. Use for user-facing screens, complex layouts, or multi-state screens where a visual prototype aids stakeholder review.

**When to skip**: Standard CRUD layouts, screens that follow an already-approved pattern, or purely backend features.

**Note**: This is an optional workflow artifact — not a core document type. Mockups are static HTML prototypes for visual review, not functional implementations.

---

## How to Use

- **AI agents (Claude Code, etc.):** Read the context files listed in the project CLAUDE.md routing table for "UI mockup" (in particular the target screen's shard `docs/ui-specification/screens/<screen>.md` and the Design System sections from `docs/ui-specification/index.md`), follow the **Guidance**, **Output Format**, and **Constraints** sections below, and **write the output file**: `mockups/T-XXX-screen-name.html`.
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the **Chat Workflow Template (XML)** appendix — paste your documentation into the `<context>` sections, fill in the `<mockup-scope>`, and include the Guidance, Output Format, and Constraints sections of this prompt alongside it.

---

## Required Context

Context selection follows the canonical matrix — see `guides/context-compilation.md` (for manual assembly) or the project CLAUDE.md routing table (for agents).

Prompt-specific notes:

- **UI Specification** (required): the target screen's shard `docs/ui-specification/screens/<screen>.md` plus the Design System sections (2.1–2.6: colors, typography, spacing, components, states, breakpoints) from `docs/ui-specification/index.md` — not the whole spec directory.
- **CLAUDE.md** (required): design tokens, styling conventions, and frontend patterns — ensures mockup colors, fonts, and spacing match the implementation target.
- **API Specification** (recommended): response DTO shapes for the target screen's endpoints, for realistic placeholder content.
- **Component Examples Appendix** (recommended): if DDRs were compiled, include `docs/component-examples.md` — pre-approved HTML patterns for buttons, cards, forms, and states take precedence over AI invention.
- **Persona** (optional): content tone for placeholder text. **Stakeholder Definition** (optional): product name, branding, philosophy.

What NOT to include:
- Architecture document (not relevant to visual mockups)
- Data Model (use API Spec DTOs instead — they represent what the screen actually displays)
- Full documents — extract only the sections relevant to the target screen

---

## Guidance

### Technical Conventions

1. **Single self-contained HTML file** — all states shown side-by-side in a responsive grid.
2. **Fully self-contained by default (true offline):** all CSS is plain, embedded in a `<style>` block, with the design tokens from the UI Specification Design System (Section 2 of `docs/ui-specification/index.md`) declared as CSS custom properties. No external requests — no CDNs, no web-font links, no icon-font links. If DDR-compiled token values exist, use those exactly.
3. **Optional CSS framework CDN:** if CLAUDE.md declares a CSS framework, the mockup MAY load that framework's official CDN build instead of hand-writing component CSS [e.g., for Tailwind CSS, the v4 browser build: `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`, defining tokens with `@theme` in a `<style type="text/tailwindcss">` block]. Do NOT use the deprecated Tailwind v3 Play CDN (`cdn.tailwindcss.com`) with an inline `tailwind.config` JS object. Note: a CDN-based mockup requires network access on first open.
4. **Fonts:** use a system font stack unless the Design System declares specific fonts [e.g., Inter + Roboto via Google Fonts]. **Icons:** use inline SVG or Unicode glyphs unless the Design System declares an icon set [e.g., Material Icons].
5. **DDR component examples take precedence** — if a Component Examples Appendix (`docs/component-examples.md`) is provided, use those HTML patterns for buttons, cards, forms, states, etc. instead of inventing new patterns.
6. **File naming:** `mockups/T-XXX-screen-name.html` (uppercase `T-XXX` task ID, kebab-case screen name).
   - Example: `mockups/T-011-login.html`, `mockups/T-025-project-board.html`
7. **Reviewer header** at the top of the page identifying the task ID, screen name, and which states are shown.
8. **Static only** — no JavaScript logic. No event handlers, no state management, no fetch calls. (If a CSS framework CDN is used, its own script is the only allowed `<script>`.)
9. **Use realistic placeholder content** derived from API response DTO shapes when available.

### Workflow

1. **Pick a screen** from the UI Specification screen inventory (`docs/ui-specification/index.md`). Prioritize user-facing screens with novel layouts (not standard CRUD), screens with multiple states that stakeholders need to approve, and screens where the ASCII layout sketch needs visual validation.
2. **Assemble context**: the target screen's shard (`docs/ui-specification/screens/<screen>.md`), the Design System sections from `index.md`, and relevant API response DTOs.
3. **Generate the mockup** — a single HTML file at `mockups/T-XXX-screen-name.html`.
4. **Review in browser**: open the file by double-clicking. Verify all states render correctly.
5. **Share for approval**: send the HTML file to stakeholders for visual feedback. Iterate if needed.

---

## Output Format

Write the mockup to: **`mockups/T-XXX-screen-name.html`** (uppercase `T-XXX`, kebab-case screen name).

Generate a single HTML file with this structure (default: fully self-contained, plain embedded CSS):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{Task ID} {Screen Name} Mockup — {Product Name}</title>

  <!-- All styles embedded — no external requests -->
  <style>
    :root {
      /* Design tokens from the docs/ui-specification/index.md Design System (Section 2).
         Use DDR-compiled values exactly if they exist. */
      --color-primary: #...;
      --color-on-primary: #...;
      --color-surface: #...;
      --color-on-surface: #...;
      --color-outline: #...;
      --color-error: #...;
      /* ... additional tokens ... */

      /* System font stack by default. If the Design System declares fonts,
         name them first [e.g., --font-sans: "Inter", "Roboto", system-ui, sans-serif;] */
      --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--color-surface);
      color: var(--color-on-surface);
      font-family: var(--font-sans);
    }

    /* Reviewer header, states grid (responsive — stacks on small screens),
       and component styles derived from the Design System tokens. */

    /* Keyframe animations for loading states (spinners, shimmer) if needed. */
  </style>
</head>

<body>

  <!-- Reviewer header -->
  <header class="reviewer-header">
    <h1>
      {Task ID} {Screen Name} Mockup
      <span>— {State 1}, {State 2}, ... shown side-by-side</span>
    </h1>
  </header>

  <!-- States grid: one <section> per state, side-by-side; stacks on small screens -->
  <main class="states-grid">

    <section>
      <h2>{State Name}</h2>
      <div>
        <!-- Screen content for this state -->
      </div>
    </section>

    <!-- Repeat for each state -->

  </main>

</body>
</html>
```

**Framework variant:** if CLAUDE.md declares a CSS framework, you MAY replace the hand-written component CSS with the framework's official CDN build and its utility/component classes [e.g., Tailwind v4 browser build `@tailwindcss/browser` with an `@theme` token block]. The design tokens and layout must still come from the UI Specification Design System.

---

## Constraints

- **Zero-install**: the file must open and render correctly in any modern browser by double-clicking — no build step, no npm, no local dependencies. The default (plain embedded CSS) also works fully offline; a declared-framework CDN variant requires network access on first open.
- **Actual design tokens**: colors, fonts, and spacing must match the UI Specification Design System — do not invent new values.
- **Styles live in the embedded `<style>` block** (or the declared framework's utility classes) — avoid per-element `style=""` attributes.
- **No JavaScript logic**: the file is a static visual prototype only (a declared CSS framework's own CDN script is the only exception).
- **Grid layout**: all states rendered side-by-side in a responsive grid (stacks on small screens).

---

## Post-Generation Checklist

After the AI generates a mockup file, verify:

- [ ] File opens in a browser by double-clicking (no build step required); the plain-CSS default also renders with no network connection
- [ ] All requested states are visible and correctly labeled
- [ ] Design tokens (colors, fonts, spacing) match the UI Specification Design System
- [ ] Layout matches the ASCII sketch from the UI Specification
- [ ] Placeholder content is realistic (derived from API DTOs when available)
- [ ] File is named correctly: `mockups/T-XXX-screen-name.html`
- [ ] Reviewer header at top identifies the task ID and states
- [ ] No JavaScript logic (only a declared CSS framework's own CDN script, if used)
- [ ] Fonts fall back to the system stack unless the Design System declares specific fonts
- [ ] Responsive grid: states stack vertically on small screens

---

## Chat Workflow Template (XML)

Copy this skeleton, paste your documentation into the `<context>` sections, fill in the `<mockup-scope>`, and submit together with the Guidance, Output Format, and Constraints sections above.

```xml
<mockup-generation-request>

<context>

<ui-specification>
<!-- REQUIRED: The target screen's shard from docs/ui-specification/screens/,
     including the ASCII layout sketch, component hierarchy, states, and interactions.
     Also include the Design System sections (colors, typography, spacing) from
     docs/ui-specification/index.md for token accuracy. -->
[Paste the target screen's shard: docs/ui-specification/screens/<screen>.md]
[Paste the Design System sections (Section 2) from docs/ui-specification/index.md]
</ui-specification>

<code-conventions>
<!-- REQUIRED: Design tokens, styling conventions, and frontend patterns from CLAUDE.md.
     Ensures mockup colors, fonts, and spacing match the implementation target. -->
[Paste relevant sections from CLAUDE.md]
</code-conventions>

<api-spec>
<!-- RECOMMENDED: Response DTO shapes for the target screen's endpoints.
     Enables realistic placeholder content in the mockup. -->
[Paste relevant endpoint response DTOs from docs/api-spec/endpoints/<resource>.md]
</api-spec>

<persona>
<!-- OPTIONAL: Content tone and language for placeholder text. -->
[Paste persona details if available]
</persona>

<stakeholder-definition>
<!-- OPTIONAL: Product name, branding, and philosophy for visual consistency. -->
[Paste relevant sections from docs/stakeholder-definition.md]
</stakeholder-definition>

<component-examples>
<!-- RECOMMENDED: If DDRs were compiled, include the Component Examples Appendix
     (docs/component-examples.md). These provide pre-approved HTML patterns for
     buttons, cards, forms, loading states, empty states, and error states.
     DDR component examples take precedence over AI invention. -->
[Paste Component Examples Appendix from docs/component-examples.md, if available]
</component-examples>

</context>

<mockup-scope>
Screen Name: [Name from UI Specification screen inventory]
Task ID: [T-XXX — the task this mockup supports]
Route: [Route path, e.g., /login, /projects/:id/board]
States to Render: [List states to show, e.g., Default, Loading, Empty, Error]
Viewport: [Target viewport, e.g., Desktop (1280px), or Responsive]
</mockup-scope>

</mockup-generation-request>
```

---

## Example

Login page mockup (this example project's Design System declares Inter/Roboto fonts and a Tailwind styling convention — substitute your own):

```xml
<mockup-generation-request>

<context>

<ui-specification>
## Design System (excerpt)
- Primary: #005cbb
- On-Primary: #ffffff
- Surface: #faf9fd
- On-Surface: #1a1b1f
- Surface-Container: #ffffff
- Outline: #74777f
- Error: #ba1a1a
- Font: Inter (headings), Roboto (body)

## Login Screen (from docs/ui-specification/screens/login.md)
Route: /login
Auth: Public

### Layout Sketch
┌──────────────────────────────────────┐
│              (centered)              │
│         ┌──────────────────┐         │
│         │    [icon: logo]  │         │
│         │   "TecherPlannr"  │         │
│         │   ─────────────  │         │
│         │ [Sign in w/ Google] │       │
│         └──────────────────┘         │
└──────────────────────────────────────┘

### States
- Default: Card centered, button enabled
- Loading: Button disabled, spinner, "Signing in..."
- Error: Error text below button, button re-enabled
</ui-specification>

<code-conventions>
- Tailwind CSS for all styling
- Inter + Roboto fonts (declared in the Design System)
</code-conventions>

</context>

<mockup-scope>
Screen Name: Login
Task ID: T-011
Route: /login
States to Render: Default, Loading, Error
Viewport: Desktop (1280px)
</mockup-scope>

</mockup-generation-request>
```

**Output:** `mockups/T-011-login.html` — a single HTML file showing all 3 login states side-by-side.
