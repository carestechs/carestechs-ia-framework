# Judge Rubric — compiled ADR template sections (case 009, python-react stack profile)

Score the candidate's four compiled section blocks (CLAUDE.md, ARCHITECTURE.md,
data-model index, api-spec index) 1-10 against these six dimensions. The reference
output shows one known-good compilation — use it as an anchor for what "good" looks
like; the candidate does not need to match it verbatim (label wording, bullet merging
of closely related constraints from the same ADR, and row ordering may vary). Judge
substance, not wording. The 18 frozen ADRs under `input/adr-repo/adrs/` are the sole
legitimate derivation source.

1. **Rule-1 completeness.** Every one of the 18 frozen ADRs is represented: exactly one
   row per ADR in the ARCHITECTURE Key Architectural Decisions table (no ADR missing,
   none duplicated), and every ADR's constraints surface as Patterns/Anti-Patterns.
   Nothing is derived from an ADR that is not in the frozen set, from the profile's
   prose, or from general knowledge — a decision row or constraint bullet with no
   corresponding frozen ADR is invention and is penalized heavily.
2. **Derivation fidelity.** Constraints land in the sections the rules dictate:
   positive-phrased constraints in Patterns to Follow, negative-phrased in
   Anti-Patterns to Avoid (mixed constraints split), database-category content in the
   data-model index (Key Modeling Decisions + Database Conventions), api-category
   content in the api-spec index (Key API Decisions + Common Conventions), naming rules
   in the Naming Conventions table (only where an ADR explicitly states one). Wording
   stays faithful to the source ADR — technical specifics (types, flags, thresholds
   like `pageSize` max 100 or the 15-60 min token lifetime) must not be altered,
   weakened, or embellished.
3. **Traceability.** Every derived bullet and table row carries an HTML comment of the
   form `<!-- from: adrs/<category>/<file>.md -->` that resolves to a frozen ADR file;
   de-duplicated entries cite every contributing ADR. Inline `(from: ...)` text, bare
   filenames that don't resolve, or derived lines with no marker are penalized.
4. **Scaffold discipline.** Sections the derivation rules do not fill are present only
   as `<!-- TODO: ... -->` scaffolds. Zero project-specific content is invented — no
   product overview, entities, endpoints, screens, commands, error catalogs, or naming
   conventions the ADRs do not state. Content lifted from the profile's prose (solution
   structure, cross-cutting concerns) rather than from ADR Decision/Rationale/
   Constraints counts as invention.
5. **Heading/format exactness.** The CLAUDE.md block uses exactly `### Patterns to
   Follow` and `### Anti-Patterns to Avoid`; the Naming Conventions table uses
   Element/Convention/Example columns; the three decision tables use
   Decision/Choice/Rationale columns; section headings match the target templates
   (`templates/claude-md.md`, `architecture.md`, `data-model.md`, `api-spec.md`).
6. **Dependency-validation correctness.** Step 0 was performed and its clean result is
   reported (this fixture has closed `Requires` chains, no mutual conflicts, and all
   profile-Required ADRs selected). False warnings/errors, fabricated missing
   dependencies, or no evidence that validation happened are penalized.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.
