---
description: Generate a static HTML mockup for a screen (writes mockups/T-XXX-screen-name.html)
---

Read `.ai-framework/prompts/mockup-generation.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "UI mockup" — the target screen's shard `docs/ui-specification/screens/<screen>.md` and the Design System from `docs/ui-specification/index.md`, plus `CLAUDE.md`.
2. `$ARGUMENTS` is the target — a task ID (e.g., `T-012`) and/or a screen name from the UI spec's Screen Inventory. If empty, ask which screen to mock up.
3. Generate the mockup following the prompt template's rules (self-contained HTML, Design System tokens).
4. Write the output file per the routing table's Output column: `mockups/T-XXX-screen-name.html` — do not leave results only in chat.
