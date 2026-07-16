# Case 008 — Generate the Project Board Mockup for T-031 (Mockup Generation)

Instructions for the agent producing this case's output. **All relative paths below are relative to this directory** (`evals/cases/mockup-generation/case-008-project-board-mockup/`).

## Setup

- This case continues the TaskFlow pipeline: the golden UI specification is **case 007's reference output** and the project CLAUDE.md lives in **case 005's fixture** — note the sibling depth of both paths below. Read them in place; do not copy or modify them.
- Treat `../../ui-spec-generation/case-007-ui-spec-from-specs/reference/docs/ui-specification/` as the project's `docs/ui-specification/`.
- The nominal task is **T-031 — Project Board mockup** (mockup-first workflow: the mockup precedes frontend implementation and exists for stakeholder visual approval). There is no task file; the scope pinned in this document stands in for it.
- Target screen: **Project Board** (`screens/project-board.md`), route `/projects/:projectId/board`.
- States to render: **default, loading, empty, error — all four side-by-side** in one page.

## Context to Read

1. `../../ui-spec-generation/case-007-ui-spec-from-specs/reference/docs/ui-specification/screens/project-board.md` — the target screen's shard: layout sketch, component hierarchy, states table, interactions (including the keyboard "Move to…" alternative).
2. `../../ui-spec-generation/case-007-ui-spec-from-specs/reference/docs/ui-specification/index.md` — the Design System sections **2.1–2.6** (colors, typography, spacing, component library, state patterns, breakpoints) **and Section 4 Shared Layouts** (app shell the board sits in).
3. `../../ui-spec-generation/case-007-ui-spec-from-specs/reference/docs/ui-specification/components.md` — the shared components this screen uses (`UserBadge`, `EmptyState`, `ErrorBanner`, `Dialog`) and their visual variants.
4. `../../spec-generation/case-005-data-model-from-strategy/input/CLAUDE.md` — project conventions (TaskFlow stack, naming, opaque auth-service user UUIDs / no local User entity).

## Procedure

1. Follow `../../../../prompts/mockup-generation.md` **end-to-end** — its Required Context notes, Guidance (Technical Conventions and Workflow), **Output Format**, Constraints, and Post-Generation Checklist.
2. **Fully self-contained single HTML file**: all CSS plain and embedded in one `<style>` block, with the Design System tokens declared as CSS custom properties using the **exact values** from `index.md` Section 2 (no invented colors, sizes, or spacing). System font stack — this Design System declares no fonts. Icons, if any, as **inline SVG** or Unicode glyphs. **No external requests of any kind**: no CDNs, no web fonts, no `<link>` or `<script src>` tags, and no `http://`/`https://` URLs anywhere in the file — including inside comments and SVG `xmlns` attributes (inline SVG in an HTML document does not need `xmlns`; omit it).
3. **Layout must match the screen shard**'s Layout Sketch and Component Hierarchy: BoardToolbar (project name, assignee filter, New task button, Members link, Activity toggle), three status columns (To Do / In Progress / Done) of TaskCards, and the Activity Feed drawer **collapsed by default**. TaskCard per the shard: title, assignee `UserBadge` (or the "Unassigned" placeholder variant), and a due-date chip that is `warning`-colored when the calendar date is past.
4. Each of the four states follows the shard's States table and `index.md` Section 2.5 patterns: default with a few realistic sample cards; loading as skeleton placeholders matching the content layout; empty as the `EmptyState` component (heading + description + CTA — never blank); error as the `ErrorBanner` with a retry button above the columns.
5. **Honor the WCAG keyboard-alternative decision** from the ui-spec: the drag-and-drop status change has a "Move to…" menu equivalent — it must appear **at least as a visible affordance** on the cards (e.g., a "Move to…" button; showing the menu itself statically open on one card is welcome).
6. **Static only** — no JavaScript: no `<script>`, no event handlers, no state logic. CSS keyframe animation for loading skeletons is fine.
7. Include the **reviewer header** at the top of the page identifying the task ID (T-031), the screen name, and the four states shown side-by-side.
8. Stay inside the screen shard's scope: no other screens' content, no invented features, and never user names/emails/avatars — users render only as opaque-UUID `UserBadge`s.

## Output

Write the mockup to `output/mockup.html` (relative to this directory). It replaces the framework's `mockups/T-031-project-board.html` inside the harness — the file **is** the deliverable, not chat output.

## Self-Check Before Finishing

"Open the file in a browser" is not available headless. Instead, run these checks on your own output and fix every hit before finishing:

```
grep -niE "https?://|<link[[:space:]]|<script[[:space:]]+src" output/mockup.html   # must print nothing (watch for SVG xmlns and URLs in comments)
grep -niE "<script" output/mockup.html                                             # must print nothing (static mockup — no JS at all)
grep -ciE "<section" output/mockup.html                                            # must be >= 4 (one labeled section per state)
```

Then confirm by re-reading the file: all four state sections (Default, Loading, Empty, Error) exist as **visually distinct, labeled sections in one side-by-side grid** — not merely words appearing somewhere — and every CSS custom property value matches `index.md` Section 2 verbatim. Finally, re-check the **Post-Generation Checklist** in `../../../../prompts/mockup-generation.md` and fix every item that does not hold.
