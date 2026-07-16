# Judge Rubric — implementation plan for T-002 (Label CRUD endpoints)

Score the candidate plan 1-10 against these six dimensions. The reference output shows
one known-good plan — use it as an anchor for what "good" looks like; the candidate
does not need to match it verbatim, judge substance.

1. **Task fidelity.** The plan covers exactly T-002 — the five label CRUD operations,
   route registration, and the labels endpoint shard — and nothing owned by other
   tasks: no migrations or repository work (T-001), no task-label assignment endpoints
   or task-response changes (T-003), no UI (T-004–T-006), no test suites (T-007).
   Every file in T-002's Files to Modify/Create is covered by at least one step.
2. **Step quality.** ≤ 10 implementation steps, each naming a real file, an explicit
   action (Create / Modify / Delete), and a specific change; steps are in buildable
   dependency order (router and schemas before registration; code before the spec
   shard that documents it). No step is vague ("implement the endpoints") or a
   placeholder.
3. **Conventions fidelity.** Technical details match the project ground truth: routes
   under the `/api/v1` base path; every success response in the `{ "data": ... }`
   envelope with `meta` on lists; errors as catalog codes only — duplicate names map
   to `conflict` (409), schema-validation failures to `validation-error` (400); SQL
   confined to `src/db/` repositories; kebab-case filenames and camelCase JSON keys.
   Penalize contradictions with the ground truth and invented conventions; details
   not derivable from the provided context should be flagged or deferred to a named
   source, not guessed.
4. **Verification.** The plan's verification items map concretely to T-002's two
   acceptance criteria (standard envelope on all five operations; duplicate-name
   error from the error catalog) — checkable actions, not restatements of the ACs.
5. **Budget.** Within the plan budget (≤ ~150 lines, ≤ 10 steps) without padding,
   boilerplate repetition, or pasted spec excerpts that add no planning value.
6. **Plan-ability.** An implementation session could execute the plan without
   re-deriving decisions: routes, status codes, error mapping, response shapes, and
   spec-doc updates are pinned down or explicitly deferred to a named source.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.
