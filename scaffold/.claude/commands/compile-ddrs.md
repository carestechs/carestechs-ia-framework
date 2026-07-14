---
description: Compile Design Decision Records into the UI spec and CLAUDE.md (writes docs/component-examples.md)
---

Read `.ai-framework/prompts/compile-ddrs.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "DDR compilation" — the DDR files from the shared DDR repo and `.ai-framework/templates/`.
2. `$ARGUMENTS` is the target — a path to the DDR repo/files or a profile name to compile. If empty, ask where the DDR files live.
3. Compile the applicable DDR constraints following the prompt template.
4. Write the output per the routing table's Output column: `docs/component-examples.md`, plus updated `docs/ui-specification.md` and `CLAUDE.md` design sections — do not leave results only in chat.
