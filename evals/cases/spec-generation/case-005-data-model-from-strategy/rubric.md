# Judge Rubric — generated data model (case 005, TaskFlow strategy stage)

Score the candidate data model document set 1-10 against these six dimensions. The
reference output shows one known-good model — use it as an anchor for what "good" looks
like; the candidate does not need to match it verbatim (entity-name variation like
`ProjectMember` vs `Membership` is acceptable when applied consistently). Judge
substance, not wording.

1. **Scope coverage.** Every Scope Lock inclusion (projects; tasks with status, due
   date, assignee; project membership; task comments) maps to at least one entity, and
   nothing excluded (labels/tags, notifications, file attachments, real-time
   collaboration) appears anywhere — not as an entity, a shard, a field, an enum value,
   or a "future work" placeholder. A stored event/activity-log entity contradicts the
   stakeholder's derive-on-read decision and counts as scope creep.
2. **Field quality.** Field sets are sufficient for the described flows, and every type
   is specific (varchar with explicit limits, not bare string). Constraints
   (required/optional, defaults, uniqueness) are stated and sensible; the task status
   enum covers the flow; the due date is day-precision per the stakeholder flow; audit
   timestamps appear on every entity.
3. **Relationships & delete semantics.** The relationship set is coherent (Project 1:N
   Task, Project 1:N membership, Task 1:N Comment), each with an explicit foreign key
   and a stated cascade behavior. Delete rules leave no orphaned rows or undefined
   states — including what happens to task assignments when a member is removed.
4. **Conventions fidelity.** Matches the project ground truth (CLAUDE.md and
   ARCHITECTURE.md): plural snake_case tables, snake_case columns, UUID v4 PKs in a
   column named `id`, `created_at`/`updated_at` timestamptz (UTC), explicit varchar
   limits, hard deletes, single `Core` module ownership, and opaque auth-service user
   UUIDs with **no local User entity**. Contradictions and invented conventions are
   penalized.
5. **Sharding correctness.** Cross-cutting content (shared decisions, conventions,
   relationships overview, usage notes, changelog) lives only in `index.md`; exactly
   one entity per shard and no entity defined in the index; every shard opens with
   well-formed flat-key frontmatter (`kind: entity`, PascalCase `name` whose kebab-case
   equals the filename, `module`, empty `endpoints`/`screens` arrays); filenames are
   kebab-case singular; every file carries the filled freshness stamp directly under
   its H1.
6. **Usability.** An api-spec generation session could start from this output alone:
   module ownership, field types, relationships, enums, and business rules are complete
   and self-consistent enough to derive CRUD endpoints and DTOs without re-reading the
   stakeholder definition.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.
