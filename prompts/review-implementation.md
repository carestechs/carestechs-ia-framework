# Implementation Review Prompt

---

## Purpose

Adversarially review an **implemented task** — the actual code changes — **in a fresh session**, against the task's acceptance criteria, its implementation plan, and the project's conventions. Use this prompt after a task has been implemented (Development Pipeline steps 1–5) and before it is marked complete: it is the pipeline's **step-6 gate**, and the sibling of `prompts/review-tasks.md` — that prompt reviews task *lists* before implementation begins; this one reviews the *implementation* after it lands. Recommended for tasks of complexity M and above, and for any task an orchestrator delegated to an implementation agent.

**The fresh-session mandate is the point of this prompt.** Same-session self-review is unreliable: a model re-reading its own diff with its implementation reasoning still in context tends to re-derive the same conclusions, trust its own "done" claims, and approve its own mistakes. What works is **external evidence (tests, linters, validators) treated as ground truth, plus a fresh context with no implementation history**. The reviewer MUST NOT be the session that implemented the task, and MUST NOT have the implementer's conversation, chain of reasoning, or working notes in context — only the artifacts listed under Required Context.

The reviewer's job is to find problems, not to fix them: unmet acceptance criteria, undocumented plan deviations, scope creep in the diff, convention violations, spec shards left out of sync, untested behavior. The output is a review file with a verdict and a findings table — the implementer (or a new implementation session) applies the required changes.

---

## How to Use

- **AI agents (Claude Code, etc.):** Run in a **new session** — never the session that implemented the task. Read the context files listed in your project CLAUDE.md's routing table for "Implementation review" (the task block, its plan, the implementation diff or changed files, CLAUDE.md, and the spec shards the task references), follow the sections below, and **write** the review to `tasks/<WORK-ITEM-ID>-<TASK-ID>-implementation-review.md` (e.g., `tasks/FEAT-012-T-002-implementation-review.md`).
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the [Chat Workflow Template (XML)](#chat-workflow-template-xml) appendix **in a fresh conversation**. Include this prompt's Guidance, Output Format, and Constraints sections alongside the skeleton, and paste the evidence (test/linter/validator output) — chat reviewers cannot execute tools themselves.

---

## Required Context

The reviewer's context is deliberately minimal. Load **only**:

1. **The task block under review** — the single `T-XXX` block from `tasks/<WORK-ITEM-ID>-tasks.md` (Title, Description, Acceptance Criteria, Complexity, Files to Modify/Create, Technical Notes). Not the whole task list — the review targets one task.
2. **The task's implementation plan** — `plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md`, the plan the implementation was supposed to follow.
3. **The implementation diff or the set of changed files** — as provided by the requester: e.g., the output of `git diff <base>..<head>`, a branch to inspect (diff it against its base yourself), or an explicit list of changed files to read. This is the object under review — if it was not provided and cannot be derived, stop and ask for it.
4. **CLAUDE.md** — conventions, Patterns/Anti-Patterns, error handling, testing rules, maintenance discipline, and the project's test/lint commands.
5. **The spec shards the task references** — for each entity, endpoint, or screen the task names (in its Description, Acceptance Criteria, or Files to Modify/Create), read that spec's `index.md` plus the shard, mapped via the retrieval-key naming rule: entity `TaskLabel` → `docs/data-model/entities/task-label.md` (singular); resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md` (matches the route segment); screen "Project Board" → `docs/ui-specification/screens/project-board.md`. Do not read whole spec directories.

**Explicitly forbidden context:**

- **The implementer's transcript** — the conversation, reasoning, plan-execution notes, or self-assessment that produced the diff. If you implemented this task, stop: this review must run in a different session.
- **Rationale files** (`docs/rationale/*.md`) — never loaded by default; the review judges the implementation against the contract docs, not against narrative history.

---

## Guidance

### Step 1 — Gather EXTERNAL evidence first

Before reading the diff closely, run the project's own verification tools (commands per CLAUDE.md's Quick Reference) and record their output:

```
[test command — e.g., npm test]
[lint command — e.g., npm run lint]
python .ai-framework/tools/validate-specs.py   # when the task touched spec shards
```

**Treat tool output as ground truth.** Every failing test, linter error, and validator error becomes a CONFIRMED finding — note the failure verbatim (test name + assertion message, lint rule + file/line) — do not re-litigate, soften, or second-guess it. A green suite is evidence too, but weaker: it proves only what the tests assert; whether that coverage is adequate is rubric point 6.

Run `validate-specs.py` whenever the diff touches `docs/data-model/`, `docs/api-spec/`, or `docs/ui-specification/` — and also when the task changed a contract and the diff *should* have touched them but did not (that gap is rubric point 5).

The tools check outcomes (behavior, style, shard consistency). They cannot judge whether the right thing was built — that is Step 2.

### Step 2 — Judge the diff against the six-point rubric

Evaluate the implementation against all six points. Every point gets examined; a clean point produces no finding.

| # | Rubric Point | What to Verify |
|---|-------------|----------------|
| 1 | **AC satisfaction** | Every acceptance criterion of the task is checked against the actual diff and observed behavior — never against the implementer's claims. For each AC, locate the code (and the test) that satisfies it; an AC with no corresponding change, or whose verification fails, is unmet |
| 2 | **Plan adherence** | The implementation follows `plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md`. A deviation is not automatically wrong — but an UNDOCUMENTED deviation is a finding: it must be surfaced and justified, not silently absorbed |
| 3 | **Scope fidelity** | Nothing in the diff goes beyond the task (and its plan): no drive-by refactors, no unrelated file changes, no features smuggled in. Out-of-scope work belongs in its own task |
| 4 | **Convention compliance** | The diff follows CLAUDE.md: Patterns to Follow applied, Anti-Patterns to Avoid absent, naming conventions kept, error handling per the standard pattern |
| 5 | **Spec sync** | If the task changed a contract (entity, endpoint, screen), the corresponding shard was updated in the same change set — with its "Last verified against code" stamp refreshed and a changelog row added to the spec's `index.md` (the maintenance discipline). Contract changed + shard untouched = finding |
| 6 | **Test adequacy** | New or changed behavior is covered by new or updated tests, and the tests would actually catch a regression — they assert on behavior (including the error paths the ACs name), not implementation trivia |

Interpret the rubric through the task's own fields: its Acceptance Criteria drive point 1, its Files to Modify/Create bound point 3 (files changed outside that list need a documented reason in the plan), and its Type/Workflow set expectations for points 4 and 6 (e.g., a `mockup-first` frontend task should match the approved mockup's states).

### Step 3 — Classify every finding

Each finding gets a **classification** and a **severity**:

- **CONFIRMED** — verified against evidence: failing tool output, or a direct check of the diff against the task's ACs, the plan, a loaded shard, or CLAUDE.md (cite the evidence in the finding).
- **PLAUSIBLE** — a defensible judgment call the reviewer cannot mechanically verify (suspected race condition, likely-inadequate test, borderline convention drift). Never present a PLAUSIBLE finding with CONFIRMED confidence.

Severity:

- **high** — the task is not actually done, or the change is unsafe as-is (unmet AC, failing test, contract changed without spec sync, out-of-scope change with real blast radius)
- **medium** — done but materially degraded (undocumented plan deviation, convention violation in new code, missing regression test on risky behavior)
- **low** — polish (naming drift, thin test naming, cosmetic inconsistency)

### Step 4 — Reach a verdict

Blocking is an **outcome test**, not a severity label:

- **revise** — any failing test, linter/validator error, or unmet acceptance criterion; or any CONFIRMED finding meaning the change as shipped is **wrong** (contradicts the task, the plan's contract, or a spec shard), **unverified** (behavior an AC demands proof of that no test covers), or leaves **spec shards out of sync** with the merged code.
- **approve** — everything else, including CONFIRMED findings whose cost is convention, style, sizing, or polish: record them under `## Advisories`. PLAUSIBLE findings never block on their own, whatever their severity.

(Code+tests reviews converge measurably faster than prose reviews, but the same outcome-anchored bar applies so both review prompts share one blocking rule.)

Do not fix the code yourself. The review file is the deliverable; fixes happen in a separate step (typically the implementer's session) against the required-changes checklist, followed by a re-review of the changed areas.

---

## Output Format

**Output file:** `tasks/<WORK-ITEM-ID>-<TASK-ID>-implementation-review.md` (e.g., `tasks/FEAT-002-T-002-implementation-review.md`). AI agents write this file — the review is not just chat output.

> **Work-item-qualified filename.** Task IDs restart at `T-001` in every task list, so an
> unqualified artifact name does not say which work item owns it. Include the work-item id
> (e.g. `FEAT-002-T-001-...`): `next-step.py` refuses to use an unqualified artifact as
> evidence when another task list declares the same ID, because crediting another work
> item's artifact skips real work. Legacy unqualified names still work while the ID is unique.


Structure:

**Header** — the task reviewed (ID + task-list file), the plan file, what diff was reviewed (ref range, branch, or file list), review date, and the **evidence summary**: test results (passed/failed counts), linter results, and `validate-specs.py` results when run.

**`## Verdict`** — `approve` or `revise`, followed by a 1–3 sentence justification naming the decisive findings. An `approve` may carry advisories — the verdict word stays exactly `approve` (the orchestrator contract's verdict regex is unchanged).

**`## Findings`** — one table, one row per finding:

```markdown
| ID | Severity | Class | AC/Plan Ref | Finding | Required Change |
|----|----------|-------|-------------|---------|-----------------|
| R-1 | high | CONFIRMED | AC-3 | [what is wrong + the evidence that confirms it] | [the specific change] |
| R-2 | low | PLAUSIBLE | CLAUDE.md Anti-Patterns | [what looks wrong + why] | [the suggested change] |
```

- `ID`: `R-1`, `R-2`, … sequential.
- `AC/Plan Ref`: the acceptance criterion (`AC-3`), plan step, CLAUDE.md section, or shard the finding is judged against (or `—` for diff-level findings such as scope creep).
- `Finding`: what is wrong and why — a **pointer into the diff** (file, function/hunk) plus the evidence; CONFIRMED findings cite tool output, a shard, the task, the plan, or CLAUDE.md; PLAUSIBLE findings state the reasoning.
- `Required Change`: the concrete edit that resolves the finding — described, not written out as code.

**`## Required Changes Before Completion`** — present when verdict = `revise`: a checklist distilled from the findings that block approval (every finding that met the Step 4 blocking bar, every failing test, every unmet AC), phrased as actionable edits:

```markdown
## Required Changes Before Completion

- [ ] R-1: [actionable edit]
- [ ] R-2: [actionable edit]
```

**`## Advisories`** — present under either verdict when non-blocking findings exist: a short list distilled from the findings that did not meet the blocking bar. Disposition contract: advisories are never silently dropped — they stay recorded in this committed review; the implementer/acceptor may fold cheap ones in before completion; substantial ones become new work items. A PLAUSIBLE or low finding may be promoted into the blocking checklist only with an explicit reason stated in the finding.

---

## Constraints

- **Fresh context only** — never review an implementation in the session that produced it; never load the implementer's transcript or `docs/rationale/` files
- **Evidence before judgment** — tests, linters, and (when shards are touched) `validate-specs.py` run first; their failures are CONFIRMED findings verbatim, not re-argued
- **Output budget** — the review stays under ~120 lines; findings are pointers into the diff (file + location + evidence), never rewrites — do not paste large diff hunks or draft replacement code
- **Review, don't fix** — the reviewer changes no code, no specs, no task list; all changes flow through the required-changes checklist
- **No re-planning** — judge the implementation against the existing plan; if the plan itself was wrong, say so in a finding, but do not produce a new plan
- **Evidence discipline** — every CONFIRMED finding cites its evidence; every PLAUSIBLE finding is labeled as such; no finding without an AC/plan/convention reference or an explicit diff-level scope
- **No scope expansion** — do not demand work beyond the task and its ACs; flagging a genuinely unmet AC is rubric point 1, inventing new requirements is not
- **Complete rubric coverage** — all six rubric points are examined every time; absence of findings on a point means it passed, not that it was skipped

---

## Post-Generation Checklist

After writing the review, verify:

- [ ] External evidence was gathered first (test suite, linters, `validate-specs.py` when the task touched spec shards) and appears in the header; every tool failure surfaced as a CONFIRMED finding, quoted verbatim
- [ ] All six rubric points were examined
- [ ] Every finding has ID, severity, CONFIRMED/PLAUSIBLE class, an AC/plan/convention reference, a pointer into the diff, and a required change
- [ ] The verdict follows the Step 4 rules (a finding meets the outcome-anchored blocking bar, a failing test, or an unmet AC ⇒ `revise`; otherwise `approve`)
- [ ] Verdict = `revise` ⇒ the Required Changes Before Completion checklist is present and covers every blocking finding
- [ ] Non-blocking findings (whatever their severity) are recorded under `## Advisories`, not silently dropped and not smuggled into the blocking checklist
- [ ] The review is ≤ ~120 lines and contains no rewritten code
- [ ] No implementer transcript or rationale file was loaded during the review
- [ ] Review saved to `tasks/<WORK-ITEM-ID>-<TASK-ID>-implementation-review.md` (agents)

---

## Chat Workflow Template (XML)

Use in a **fresh conversation** — do not paste this into the conversation that implemented the task.

```xml
<implementation-review-request>

<context>

<task-block>
<!-- REQUIRED: The single task under review, copied from tasks/<WORK-ITEM-ID>-tasks.md -->
[Paste the full T-XXX task block]
</task-block>

<implementation-plan>
<!-- REQUIRED: The plan the implementation was supposed to follow -->
[Paste full plans/plan-<WORK-ITEM-ID>-T-XXX-short-title.md content]
</implementation-plan>

<implementation-diff>
<!-- REQUIRED: The code changes under review -->
[Paste the git diff <base>..<head> output, or the full content of each changed file]
</implementation-diff>

<code-conventions>
<!-- REQUIRED: CLAUDE.md for patterns, anti-patterns, error handling, testing rules -->
[Paste CLAUDE.md content]
</code-conventions>

<spec-shards>
<!-- REQUIRED when the task references entities/endpoints/screens: each spec's
     index.md + ONLY the shards the task names, mapped via the retrieval-key
     naming rule. Do not paste whole spec directories. -->
[Paste referenced entity / endpoint / screen shards + their index.md files]
</spec-shards>

<evidence>
<!-- REQUIRED: Raw output of the external tools — chat reviewers cannot execute
     them, so the orchestrator/human runs them and pastes results:
     the project's test suite, its linters, and (when spec shards were touched)
     python .ai-framework/tools/validate-specs.py -->
[Paste test / linter / validator output]
</evidence>

<!-- DO NOT include: the implementing conversation, its reasoning, or docs/rationale/ files -->

</context>

<task-type>Implementation Review</task-type>

<request>
Adversarially review this implementation against the six-point rubric from
prompts/review-implementation.md. Treat the pasted evidence as ground truth. Produce
the review in the Output Format (Verdict, Findings table, Required Changes checklist).
</request>

</implementation-review-request>
```

---

## Example

Excerpt of `tasks/FEAT-012-T-002-implementation-review.md` — reviewing the implementation of T-002 ("Implement label CRUD endpoints") from TaskFlow's FEAT-001 task list:

```markdown
# Implementation Review: T-002 Implement Label CRUD Endpoints

**Task:** T-002 (tasks/FEAT-001-tasks.md) · **Plan:** plans/plan-FEAT-001-T-002-label-crud-endpoints.md
**Diff:** git diff main..feat/FEAT-001-labels · **Reviewed:** 2026-03-05
**Evidence:** tests 41 passed / 1 failed · lint 0 errors · validate-specs 0 errors

## Verdict

**revise** — R-1 is a CONFIRMED unmet acceptance criterion backed by a failing test:
duplicate label names return 200 instead of the error catalog's 409. R-2 is advisory.

## Findings

| ID | Severity | Class | AC/Plan Ref | Finding | Required Change |
|----|----------|-------|-------------|---------|-----------------|
| R-1 | high | CONFIRMED | AC-3 | AC-3 requires duplicate label names to be rejected with the Error Catalog's 409 `label-name-conflict` (docs/api-spec/index.md). The `POST /api/labels` handler in the diff (src/api/labels.ts) never checks for an existing name — it inserts and returns 200. Evidence: test `labels.test.ts › rejects duplicate name with 409` FAILS (expected 409, received 200). | Add the duplicate-name check, return the catalog's 409 `label-name-conflict`, and make the failing test pass. |
| R-2 | low | PLAUSIBLE | CLAUDE.md Anti-Patterns | The validation logic that does exist (name length, color format) sits inline in the route handler in src/api/labels.ts. CLAUDE.md's Anti-Patterns to Avoid says "Don't put business logic in route handlers." The checks are thin, so this is flagged as a judgment call, not a verified violation. | Consider moving label validation into the service layer alongside the R-1 fix. |

## Required Changes Before Completion

- [ ] R-1: Reject duplicate label names with the Error Catalog's 409 `label-name-conflict`;
      `labels.test.ts › rejects duplicate name with 409` must pass.
```

Note the shape: the CONFIRMED finding is anchored to an AC, cites the failing test verbatim and the shard that defines the expected error, and points into the diff without rewriting it; the PLAUSIBLE finding is labeled as a judgment call and stays out of the blocking checklist. With R-1 fixed and the suite green, a follow-up review would return `approve`.
