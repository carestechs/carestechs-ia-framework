---
description: Derive the UI Specification from strategic docs and the API spec (writes docs/ui-specification/)
---

Read `.ai-framework/prompts/ui-spec-generation.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "UI spec generation" (plus any optional files that apply).
2. `$ARGUMENTS` optionally names specific screens to focus on. If empty, generate the full UI specification.
3. Generate the spec following the prompt template's structure and quality criteria.
4. Write the output files per the routing table's Output column: `docs/ui-specification/` (`index.md` + `screens/*.md` + `components.md`) — do not leave results only in chat.
5. Run `python .ai-framework/tools/validate-specs.py --root .` and fix every error (frontmatter, cross-references, stamps).
