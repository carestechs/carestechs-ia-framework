---
description: Compile Architecture Decision Records into project docs (updates CLAUDE.md sections)
---

Read `.ai-framework/prompts/compile-adrs.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "ADR compilation" — the ADR files from the shared ADR repo and `.ai-framework/templates/`.
2. `$ARGUMENTS` is the target — a path to the ADR repo/files or a profile name to compile. If empty, ask where the ADR files live.
3. Compile the applicable ADR constraints following the prompt template.
4. Write the output per the routing table's Output column: updated `CLAUDE.md` sections — do not leave results only in chat.
