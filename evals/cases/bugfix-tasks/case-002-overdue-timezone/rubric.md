# Judge Rubric — bug fix task list for BUG-001 (Overdue Filter Timezone)

Score the candidate task list 1-10 against these five dimensions. The reference output
shows one known-good decomposition — use it as an anchor for what "good" looks like;
the candidate does not need to match it verbatim, judge substance.

1. **Investigation before fix.** Phase 1 `Investigation` tasks (Workflow
   `investigation-first`) come first and every fix task depends on them. The
   investigation reproduces the bug from the report's steps and isolates the actual
   failing comparison; the fix addresses the identified root cause (the overdue
   predicate ignoring the user's timezone), not the symptom (e.g., hiding the wrong
   rows client-side, or fudging the filter output).
2. **Fix scoped to the root cause.** The fix touches the overdue predicate path and
   nothing else: no refactoring of unrelated code, no new features, no speculative
   "improve date handling everywhere" work beyond what the audit dimension below
   explicitly covers.
3. **Regression coverage.** A test task covers the exact reported scenario (UTC-8 user,
   task due today, local evening) plus boundary conditions — the day-boundary instants
   in the user's timezone (23:59:59 local vs 00:00:00 local of the next day) and at
   least one positive-offset timezone. A fix without a test that would have caught this
   bug is a serious deficiency.
4. **Related-area audit.** An investigation task checks whether the same defect class —
   date comparisons done in UTC where user-local semantics are required — exists
   elsewhere in the fixture (other repository queries, client/server disagreement on
   the card chip), with findings documented. Auditing is examining and documenting, not
   preemptively rewriting.
5. **Schema and plan-ability.** Canonical task schema (field list and order, one Type
   per task, plain-ID Dependencies forming the three-phase order, S/M/L/XL complexity,
   budgets respected), concrete fixture file paths in Files to Modify/Create, and a
   Summary Section — enough that a planning session could start from the task blocks
   alone.

Note on the producer-contract step: `prompts/bugfix-tasks.md` mandates a "verify the
contract empirically against the producer" first investigation step **only for bugs
that cross a system boundary**. BUG-001 is internal — the evidence shows the `tz`
parameter arriving intact at the API and the defect confined to the app's own
predicate — so the absence of a producer-contract verification task is correct here;
do not penalize it, and do not reward an invented external-contract step.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.
