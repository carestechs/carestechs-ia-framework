# Judge Rubric — feature task list for FEAT-001 (Task Labels)

Score the candidate task list 1-10 against these six dimensions. The reference output
shows one known-good decomposition — use it as an anchor for what "good" looks like;
the candidate does not need to match it verbatim, judge substance.

1. **Decomposition granularity.** Each task does one thing, carries exactly one Type,
   and no task is a grab-bag ("implement the feature") or trivially small. Complexity
   values are plausible for the described work.
2. **Dependency logic.** The order is buildable: entities/migration before endpoints,
   endpoints before UI that calls them, tests able to run last. No dependency points
   forward without reason; no false parallelism (UI task not depending on the endpoint
   it consumes).
3. **Acceptance-criteria mapping.** Every one of the work item's 6 ACs is covered by at
   least one task, and the coverage table attributes them plausibly (the task's content
   actually addresses the AC it claims).
4. **Scope fidelity.** Nothing beyond the brief: no extra features, no refactors of
   unrelated code, no invented entities/endpoints/screens beyond those the impact
   tables mark as (new).
5. **Plan-ability.** Files to Modify/Create and Technical Notes are concrete enough
   that a planning session could start from the task block alone without re-deriving
   the feature.
6. **Spec fidelity.** Technical details match the project ground truth provided
   (routes including the base path, response envelope, error-catalog codes, entity
   field names and types, palette/token constraints, naming conventions). Penalize
   contradictions with the ground truth and invented conventions; details not
   derivable from any provided context should be flagged as open questions, not
   guessed.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.
