---
description: Derive the Data Model and API Spec from strategic docs (writes docs/data-model.md, docs/api-spec.md)
---

Read `.ai-framework/prompts/spec-generation.md` and follow it end-to-end.

1. Read the required context files listed in the CLAUDE.md routing table row "Spec generation" (plus any optional files that apply).
2. `$ARGUMENTS` optionally narrows the target — `data-model` or `api-spec` to generate just one spec. If empty, generate both.
3. Generate the spec(s) following the prompt template's structure and quality criteria.
4. Write the output files per the routing table's Output column: `docs/data-model.md` and `docs/api-spec.md` — do not leave results only in chat.
