# Rationale Files

Narrative, history, and decision rationale live here — one topic per file (`docs/rationale/<topic>.md`).
Contract docs (specs, `docs/ARCHITECTURE.md`, `CLAUDE.md`) link here as `Why: see docs/rationale/<topic>.md` instead of carrying prose.
These files are NEVER loaded as AI context — no routing-table row or prompt may list them.
Keep the contract docs themselves to tables, schemas, and rules.
