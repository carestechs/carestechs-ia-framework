# Judge Rubric — generated UI specification (case 007, TaskFlow UI-spec stage)

Score the candidate UI specification document set 1-10 against these six dimensions. The
reference output shows one known-good spec — use it as an anchor for what "good" looks
like; the candidate does not need to match it verbatim (screen-name variation like
`task-detail` vs `task-detail-panel`, or surfacing the activity feed on a different
in-scope screen, is acceptable when applied consistently). Judge substance, not wording.

1. **Screen coverage.** Every stakeholder User Flow phase is covered: project
   list/creation, task board with status/due-date/assignee visible, task editing with
   comments, member management, and the derived activity feed surfaced somewhere in the
   UI. Sign-in needs no screen — the reference documents it as a redirect to the
   external auth service; a minimal sign-in screen is acceptable only if it invents no
   credential fields or endpoints. Nothing excluded by the Scope Lock (labels/tags,
   notifications, file attachments, real-time collaboration) appears anywhere — not as
   a screen, a component, a field, an interaction, or a "future work" placeholder.
2. **Component → API correctness.** Every Component → API mapping row and every
   interaction's API call names a method + route that exists in the API spec fixture,
   used correctly (right route and verb for the action, request fields that exist on
   that endpoint). Invented endpoints (task delete, user search/profile, a stored
   notifications or events feed write, auth/login routes) are the highest-severity
   failure. Screen frontmatter `endpoints` arrays name only existing endpoint shard
   names and match the calls the shard's body actually makes.
3. **States & interactions completeness.** Every screen specifies all four states
   (default, loading, empty, error) with concrete, screen-specific behaviors — not
   boilerplate repeated verbatim — and its interactions are specific: UI element →
   result → API call (or explicit "None"). Edge behaviors that the specs imply are
   handled somewhere (e.g., duplicate-name/member conflicts surfaced inline, member
   removal warning about unassignment, error-code-to-message mapping).
4. **Design-system quality.** Sections 2.1–2.6 are present under the exact numbering,
   tokens are concrete and coherent (real hex values, a consistent spacing base, a
   typography scale), an explicit accessibility decision exists, and the State Patterns
   table is usable as a cross-screen standard that the screen shards actually reference.
5. **Sharding, frontmatter & stamps correctness.** Cross-cutting content lives only in
   `index.md` (which has no frontmatter); exactly one screen per shard and no screen
   specified in the index; every screen shard opens with well-formed flat-key
   frontmatter (`kind: screen`, `screen` equal to the kebab-case filename, `route`,
   `endpoints` inline array) and `components.md` with `kind: component-inventory`; the
   Screen Inventory lists exactly the shipped shards; every file carries the filled
   freshness stamp directly under its H1.
6. **Conventions fidelity.** Matches the project ground truth (CLAUDE.md,
   ARCHITECTURE.md, data model, API spec): React 18 function components and TanStack
   Query (no other framework's modules or component libraries), kebab-case filenames /
   PascalCase components, the `{ "data": ... }` / `{ "error": { "code", ... } }`
   envelope when payloads are described, `/api/v1` routes, opaque user UUIDs with no
   names/avatars/profile UI (no local User entity), day-precision `YYYY-MM-DD` due
   dates with no time-of-day UI, no task position/ordering field (drag changes status
   only), and an activity feed derived on read (no event store, no feed writes).
   Contradictions and invented conventions are penalized.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.
